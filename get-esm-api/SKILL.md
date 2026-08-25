---
name: get-esm-api
description: Call Huawei Cloud ESM API — IAM token auth, APIG AppCode, query capacity/alarms/audit logs/metrics, async billing SDR download
---

# ESM API 调用技能

调用华为云 ESM（Enterprise Service Management）API，获取云服务容量、
告警、审计日志、监控指标、计量话单等数据。

**驱动脚本:** [`driver.py`](./driver.py)

## 前置条件

### 1. 网络配置

ESM API 通过 VPCEP 内网访问，需添加 hosts 解析：

```bash
# 将 esm-api.cn-south-298.myhuaweicloud.com 解析到 VPCEP 终端节点地址
echo "<VPCEP_ENDPOINT_IP> esm-api.cn-south-298.myhuaweicloud.com" >> /etc/hosts

# 验证
ping esm-api.cn-south-298.myhuaweicloud.com -c 2
```

> `VPCEP_ENDPOINT_IP` 在 VPCEP 控制台查看：登录华为云 → VPC Endpoint →
> 找到对应的终端节点 → 查看"节点IP"。

### 2. 环境变量

```bash
export IAM_BASE_URL="https://iam-pub.<region>.xxx.com"
export IAM_USERNAME="<iam-username>"
export IAM_PASSWORD="<iam-password>"
export IAM_DOMAIN_NAME="<iam-domain-name>"
export ECS_PROJECT_ID="<project-id>"
export ESM_BASE_URL="https://esm-api.cn-south-298.myhuaweicloud.com"
export ESM_APPCODE="<apig-appcode>"
export ESM_DOMAIN_ID="<esm-tenant-id>"
```

### 3. Python 依赖

```bash
pip install httpx
```

## 认证体系

两层认证：

| 认证 | 方式 | 说明 |
|------|------|------|
| IAM Token | `X-Auth-Token` | 通过 IAM 获取，24h 过期，需刷新 |
| APIG AppCode | `x-hcso-appcode` / `X-Apig-AppCode` | 固定值，应用访问码 |

### 请求头

| Header | 来源 | 说明 |
|--------|------|------|
| `X-Auth-Token` | IAM 认证获取 | 24h 过期，需要刷新 |
| `x-hcso-appcode` | 环境配置 | 固定值 |
| `X-Apig-AppCode` | 环境配置 | 与 `x-hcso-appcode` 相同 |
| `x-hcso-domainid` | 环境配置 | ESM 租户 ID |
| `Content-Type` | 固定 | `application/json` |
| `Accept` | 固定 | `application/json` |

## Run（agent path）

使用 `driver.py`:

```bash
cd <project-root>/get-esm-api

# 查询 ECS 容量
python driver.py capacity --service-type ECS_VM

# 查询云审计日志
python driver.py audit-log --begin "2026-06-01" --end "2026-06-09"

# 查询设备资产
python driver.py device-asset

# 查询云服务告警
python driver.py alarm --service-type ECS_VM

# 查询物理主机容量
python driver.py host-capacity

# 查询主机性能数据
python driver.py host-performance --begin "2026-06-01" --end "2026-06-09"

# 异步计量话单
python driver.py billing --begin "2026-06-01" --end "2026-06-09" --output ./billing_data
```

所有命令读取环境变量 `IAM_BASE_URL` / `ESM_BASE_URL` / `ESM_APPCODE` 等。
Token 自动缓存并在 401 时刷新。

## Run（human path）

### 1. 获取 IAM Token

```bash
curl -sk -X POST "${IAM_BASE_URL}/v3/auth/tokens" \
  -H "Content-Type: application/json" \
  -d '{
    "auth": {
      "identity": {
        "methods": ["password"],
        "password": {
          "user": {
            "name": "'"${IAM_USERNAME}"'",
            "password": "'"${IAM_PASSWORD}"'",
            "domain": {"name": "'"${IAM_DOMAIN_NAME}"'"}
          }
        }
      },
      "scope": {
        "project": {"id": "'"${ECS_PROJECT_ID}"'"}
      }
    }
  }' -D - | grep -i x-subject-token
```

### 2. 查询 ECS 容量

```bash
TOKEN=$(curl -sk -X POST "${IAM_BASE_URL}/v3/auth/tokens" \
  -H "Content-Type: application/json" \
  -d '{
    "auth": {
      "identity": {
        "methods": ["password"],
        "password": {
          "user": {
            "name": "'"${IAM_USERNAME}"'",
            "password": "'"${IAM_PASSWORD}"'",
            "domain": {"name": "'"${IAM_DOMAIN_NAME}"'"}
          }
        }
      },
      "scope": {
        "project": {"id": "'"${ECS_PROJECT_ID}"'"}
      }
    }
  }' -sD - | grep -i x-subject-token | awk '{print $2}' | tr -d '\r')

curl -sk "${ESM_BASE_URL}/rest/dataapi/homs/open-api/v1/CloudService/capacity?service_type=ECS_VM&page_size=10&offset_value=0" \
  -H "X-Auth-Token: ${TOKEN}" \
  -H "x-hcso-appcode: ${ESM_APPCODE}" \
  -H "X-Apig-AppCode: ${ESM_APPCODE}" \
  -H "x-hcso-domainid: ${ESM_DOMAIN_ID}"
```

## API 端点

| 功能 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 云服务容量查询 | GET | `/rest/dataapi/homs/open-api/v1/CloudService/capacity` | 参数: service_type, begin_time, end_time, page_size, offset_value |
| 云审计日志查询 | GET | `/rest/dataapi/homs/open-api/v1/cloudAuditlog` | |
| 设备资产信息 | GET | `/rest/dataapi/homs/open-api/v1/DeviceAsset/info` | |
| 云服务告警查询 | GET | `/rest/dataapi/homs/open-api/v1/CloudServiceAlarm/info` | |
| 设备告警查询 | GET | `/rest/dataapi/homs/open-api/v1/DeviceAlarm/info` | |
| 物理主机容量 | GET | `/rest/dataapi/homs/open-api/v1/host-physical/capacity` | |
| 主机监控指标 | GET | `/rest/dataapi/homs/open-api/v1/host/metricdata` | |
| 主机性能数据 | GET | `/rest/dataapi/homs/open-api/v1/host/performancedata` | |
| 计量话单 | POST | `/meter/v1/{domain_id}/query-jobs` | 三步异步流程（见下方） |

### 计量话单三步流程

```bash
# Step 1: 创建查询任务
JOB_RESP=$(curl -sk -X POST "${ESM_BASE_URL}/meter/v1/${ESM_DOMAIN_ID}/query-jobs" \
  -H "X-Auth-Token: ${TOKEN}" \
  -H "x-hcso-appcode: ${ESM_APPCODE}" \
  -H "Content-Type: application/json" \
  -d '{"begin_time": "2026-06-01", "end_time": "2026-06-09"}')
JOB_ID=$(echo "$JOB_RESP" | jq -r '.job_id')

# Step 2: 轮询任务状态
curl -sk "${ESM_BASE_URL}/meter/v1/${ESM_DOMAIN_ID}/query-jobs/${JOB_ID}" \
  -H "X-Auth-Token: ${TOKEN}" \
  -H "x-hcso-appcode: ${ESM_APPCODE}"

# Step 3: 获取话单
curl -sk "${ESM_BASE_URL}/meter/v1/${ESM_DOMAIN_ID}/query-jobs/${JOB_ID}/sdr" \
  -H "X-Auth-Token: ${TOKEN}" \
  -H "x-hcso-appcode: ${ESM_APPCODE}"
```

## 驱动脚本设计

`driver.py` 中的 `EsmClient` 核心设计：

- **Token 缓存 + async Lock** — 避免并发刷新风暴
- **401 自动重试** — 检测到 401 时失效缓存、刷新 Token 后重试一次
- **SSL 跳过验证** — 内网 VPCEP 证书场景
- **请求超时 30s**

```python
class EsmClient:
    def __init__(self):
        self._token: Optional[str] = None
        self._token_lock = asyncio.Lock()

    async def _get_token(self, *, refresh: bool = False) -> str:
        # 带缓存 + async Lock 避免并发刷新风暴

    async def _request(self, method, path, params=None) -> dict:
        # 401 时自动刷新 Token 重试一次
        for attempt in range(2):
            ...
            if resp.status_code == 401 and attempt == 0:
                self._invalidate_token()
                continue
            resp.raise_for_status()
            return resp.json()
```

## Gotchas

- **Token 在响应头 `x-subject-token` 中**，不在响应体里。
- **`x-hcso-appcode` 和 `X-Apig-AppCode` 值相同**，两个都必须传。
- **内网 VPCEP 场景需配置 hosts**，否则域名解析指向公网 IP 导致连接失败。
- **Token 24h 过期**，建议使用 `driver.py`（自动缓存刷新），避免手动频繁获取。
- **计量话单是异步任务**，需先创建 job，轮询完成后再获取数据。

## Troubleshooting

| 现象 | 原因 | 解决 |
|------|------|------|
| 401 重试仍失败 | IAM 凭据错误 | 检查环境变量中 IAM_USERNAME / IAM_PASSWORD |
| 401 空 token | scope 参数错误 | 检查 ECS_PROJECT_ID |
| 连接超时 | 网络不通 | 确认 hosts 中 VPCEP 解析正确 |
| `invalid appcode` | AppCode 错误 | 确认 ESM_APPCODE |
| 域名解析到公网 IP | 未配置 hosts | 添加 `echo "<VPCEP_IP> esm-api.cn-south-298.myhuaweicloud.com" >> /etc/hosts` |
| SSL 证书错误 | 内网证书 | `driver.py` 已跳过 SSL 验证；curl 使用 `-sk` 参数 |

## References

- ESM 相关代码：`ops-flower-service/app/utils/esm_client.py`
