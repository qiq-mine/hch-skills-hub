---
name: sg-policy-deploy
description: "Deploy security group port policy on Huawei Cloud — parse work order (text/image), query SG by dest IP name, fail-closed validation, cleanup expired rules, add allow/deny rules. Triggers: sg-policy-deploy, /sg-policy-deploy, run-sg-policy-deploy, 安全组策略, 华为云安全组, 端口策略开通, 安全组工单."
---

# 安全组端口策略开通工作流

从开通工单（文本或图片）中提取策略信息，自动在华为云上查询以目的 IP 命名的安全组，清理已过期规则后添加新规则。

> ## ⚠️ 强制安全流程
>
> **任何生产执行前，必须先运行 `--dry-run` 输出完整 diff（含将被清理的过期规则清单），经人工确认无误后，再去掉 `--dry-run` 真实执行。**
>
> ```bash
> # 1. 先 dry-run，人工逐项核对输出
> python driver.py --text '<工单文本>' --dry-run
> # 2. 人工确认后，再真实执行
> python driver.py --text '<工单文本>'
> ```
>
> fail-closed 原则：`动作` 与 `源IP` 为必填字段，缺失时脚本直接报错退出，**不会**默认放行或默认 `0.0.0.0/0`。

**驱动脚本:** [`driver.py`](./driver.py)

## 工作流概述

```
工单（文本/图片） → 解析策略字段 → 查询目的IP安全组 → 清理过期规则 → 添加规则 → 输出结果
                                 ↓                      ↓
                         安全组不存在则创建       未过期规则完整保留
```

## 前置条件

### 1. 华为云认证

需要以下环境变量提供华为云 API 凭证：

```bash
export HW_CLOUD_AK="your-access-key"
export HW_CLOUD_SK="your-secret-key"
export HW_CLOUD_PROJECT_ID="your-project-id"
export HW_CLOUD_REGION="cn-east-3"     # 根据实际区域修改
```

IAM 用户需授权以下策略：
- `vpc:securityGroups:create` — 创建安全组
- `vpc:securityGroups:get` — 查询安全组
- `vpc:securityGroupRules:create` — 创建安全组规则

### 2. Python 依赖

```bash
pip install huaweicloud-sdk-python-v3 pillow pytesseract
```

> 如果工单输入是图片，需要安装 tesseract-ocr:
> ```bash
> apt-get install tesseract-ocr
> ```

## 工单输入格式

工单可以是 **文本** 或 **图片**，必须包含以下字段：

| 字段 | 示例 | 说明 |
|------|------|------|
| 动作 | `允许` 或 `拒绝` | **必填，无默认值**，缺失时脚本报错退出 |
| 协议 | `tcp` / `udp` / `icmp` | 支持的协议类型，缺省 `tcp` |
| 方向 | `入方向` / `出方向` | 可选，缺省 `ingress`（入方向） |
| 源IP | `10.0.0.0/24` | **必填，无默认值**，缺失时脚本报错退出；不再默认 `0.0.0.0/0` |
| 目的IP | `192.168.1.100` | **必填**，用于命名安全组的关键字段 |
| 目的域名 | `api.example.com` | 可选，记录在规则描述中 |
| 目的端口 | `80` 或 `443,8080` 或 `1-1000` | 单端口、列表或范围；逐项校验 1-65535 |
| 开通原因 | `生产环境Web访问` | 写入规则描述 |
| 策略有效期 | `2026-06-30` | 写入规则描述（`valid_until:` 标记），到期后自动清理 |

> **安全组命名规则:** 以目的 IP 命名，例如目的 IP 为 `192.168.1.100`，则安全组名为 `sg-192.168.1.100`。

### 文本工单示例

```
动作：允许
协议：tcp
源IP：10.0.0.0/24
目的IP：192.168.1.100
目的域名：api.example.com
目的端口：443
开通原因：生产环境HTTPS访问
策略有效期：2026-12-31
```

## 使用方式

### 直接运行 driver.py

```bash
cd <project-root>/run-sg-policy-deploy

# 文本工单
python driver.py --text '
动作：允许
协议：tcp
源IP：10.0.0.0/24
目的IP：192.168.1.100
目的域名：api.example.com
目的端口：443
开通原因：生产环境HTTPS访问
策略有效期：2026-12-31
' --dry-run   # ← 先 dry-run，人工确认后再去掉该参数真实执行

# 图片工单（需 OCR）
python driver.py --image /path/to/ticket.png

# 指定 YAML 配置文件
python driver.py --file /path/to/ticket.yaml
```

### YAML 配置文件格式

```yaml
action: allow           # allow 或 deny
protocol: tcp
source_ip: 10.0.0.0/24
dest_ip: 192.168.1.100
dest_domain: api.example.com
dest_port: "443"
reason: "生产环境HTTPS访问"
expiry: "2026-12-31"
```

## 驱动脚本说明

`driver.py` 按以下步骤执行：

### 步骤 1: 解析工单输入

```python
# 文本 → 字典解析
# 图片 → OCR(pytesseract) → 文本 → 字典解析
# YAML → yaml.safe_load
```

### 步骤 2: 查询安全组

```python
# 以目的 IP 构建安全组名: sg-{dest_ip}
sg_name = f"sg-{dest_ip}"

# 调用华为云 VPC API v3 查询
request = ListSecurityGroupsRequest()
request.name = [sg_name]
response = client.list_security_groups(request)
```

### 步骤 3: 确定方向

方向由工单的 `方向` 字段显式指定（`入方向`/`出方向` 或 `ingress`/`egress`），缺省为 `ingress`（入方向）。

### 步骤 4: 清理已过期规则（删除前先打印清单）

真实执行时，脚本会先扫描该安全组内所有规则：凡描述中带有 `valid_until:` 标记且日期已过的规则，会先打印完整清单再删除。有效期无法解析的规则视为未过期（fail-safe，不删除）。`--dry-run` 模式下仅提示该行为，不执行删除。

### 步骤 5: 添加规则（去重后添加）

```python
rule = CreateSecurityGroupRuleOption(
    security_group_id=sg.id,
    direction="ingress" | "egress",
    protocol=protocol,
    multiport=port,
    remote_ip_prefix=source_cidr,
    action=action,        # "allow" 或 "deny"
    priority=1,
    description=description  # 包含开通原因、有效期、目的域名
)
request = CreateSecurityGroupRuleRequest()
request.body = CreateSecurityGroupRuleRequestBody(security_group_rule=rule)
client.create_security_group_rule(request)
```

### 步骤 6: 输出结果

```json
{
  "status": "success",
  "security_group": "sg-192.168.1.100",
  "security_group_id": "sg-id-xxx",
  "rule_id": "rule-id-xxx",
  "action": "allow",
  "protocol": "tcp",
  "source": "10.0.0.0/24",
  "port": "443",
  "direction": "ingress",
  "description": "生产环境HTTPS访问 | valid_until:2026-12-31 | dest_domain:api.example.com"
}
```

## 重要说明

### 规则删除策略：仅清理已过期规则

脚本只会删除满足以下**全部**条件的规则：

1. 规则描述中带有 `valid_until:` 标记；
2. 标记后的日期早于今天。

删除前会先打印完整清单。未标记有效期、或有效期无法解析的规则**永远不会**被删除。其他未过期规则完整保留。

### 安全组不存在时自动创建

如果查询不到以目的 IP 命名的安全组，会自动创建：

```python
create_sg_request = CreateSecurityGroupRequest()
create_sg_request.body = CreateSecurityGroupRequestBody(
    security_group=CreateSecurityGroupOption(
        name=f"sg-{dest_ip}",
        description=f"Auto-created for {dest_ip} by sg-policy-deploy"
    )
)
new_sg = client.create_security_group(create_sg_request)
```

### 规则去重

添加前会检查是否已存在完全相同的规则（相同 protocol + multiport + remote_ip_prefix + action + direction），避免重复添加。

## 排查指南

| 现象 | 原因 | 措施 |
|------|------|------|
| `Invalid authentication` | AK/SK 错误或过期 | 检查 `HW_CLOUD_AK` 和 `HW_CLOUD_SK` |
| `Security group rule limit exceeded` | 安全组规则数达上限 | 在华为云控制台申请配额提升 |
| `Invalid input` | 端口格式错误 | 检查 multiport 格式（单端口/范围/逗号列表） |
| `Endpoint not found` | Region 错误 | 确认 `HW_CLOUD_REGION` 与项目所在区域一致 |
| OCR 识别乱码 | 图片清晰度不足 | 使用高质量的工单截图，避免倾斜/模糊 |
| `SecurityGroup not found` | 安全组尚未创建 | driver 会自动创建，无需手动干预 |

## 参考文档

- [华为云 VPC API v3 — 创建安全组规则](https://support.huaweicloud.com/intl/en-us/api-vpc/vpc_apiv3_0016.html)
- [华为云 VPC API v3 — 查询安全组列表](https://support.huaweicloud.com/intl/zh-cn/ae-ad-1-api-vpc/vpc_apiv3_0011.html)
- [华为云 VPC API v3 — 创建安全组](https://support.huaweicloud.com/intl/en-us/ally-visitor-1-api-vpc/vpc_apiv3_0010.html)
- [huaweicloud-sdk-python-v3](https://github.com/huaweicloud/huaweicloud-sdk-python-v3)
