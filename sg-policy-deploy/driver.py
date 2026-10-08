#!/usr/bin/env python3
"""
华为云安全组端口策略开通驱动脚本

从工单（文本/图片/YAML）中解析策略信息，自动：
1. 查询以目的 IP 命名的安全组 (sg-{dest_ip})
2. 如果不存在则自动创建
3. 清理描述中带有 valid_until 且已过期的旧规则
4. 添加安全组规则（不会删除或修改未过期的已有规则）
5. 输出开通结果

安全原则（fail-closed）:
- action 缺失时直接报错退出，不再默认 allow
- source_ip 为必填字段，不再默认 0.0.0.0/0
- 所有 IP / CIDR / 端口在调用 API 前做格式校验

使用方式:
  python driver.py --text '<工单文本>' --dry-run   # 先 dry-run，人工确认
  python driver.py --text '<工单文本>'             # 人工确认后再真实执行
  python driver.py --image /path/to/ticket.png
  python driver.py --file /path/to/ticket.yaml

环境变量:
  HW_CLOUD_AK         华为云 Access Key
  HW_CLOUD_SK         华为云 Secret Key
  HW_CLOUD_PROJECT_ID 华为云项目 ID
  HW_CLOUD_REGION     区域 (默认 cn-east-3)
"""

import argparse
import ipaddress
import json
import os
import re
import sys
from datetime import datetime, date

# lazy imports for huaweicloud SDK — only needed when making API calls
# yaml is only needed for --file input
# PIL/pytesseract are only needed for --image input

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

DIRECTION_MAP = {
    "INGRESS": "ingress",
    "ingress": "ingress",
    "入方向": "ingress",
    "入站": "ingress",
    "EGRESS": "egress",
    "egress": "egress",
    "出方向": "egress",
    "出站": "egress",
}

ACTION_MAP = {
    "allow": "allow",
    "ALLOW": "allow",
    "允许": "allow",
    "permit": "allow",
    "deny": "deny",
    "DENY": "deny",
    "拒绝": "deny",
    "禁止": "deny",
    "reject": "deny",
}

PROTOCOL_MAP = {
    "tcp": "tcp",
    "TCP": "tcp",
    "udp": "udp",
    "UDP": "udp",
    "icmp": "icmp",
    "ICMP": "icmp",
    "icmpv6": "icmpv6",
    "ICMPV6": "icmpv6",
}

# 过期标记写入规则 description，用于 cleanup_expired 扫描
EXPIRY_MARKER = "valid_until:"

# 支持的有效期日期格式（按优先级尝试）
EXPIRY_DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d",
    "%Y-%m-%dT%H:%M:%S",
)


# ---------------------------------------------------------------------------
# 华为云客户端
# ---------------------------------------------------------------------------

def get_vpc_client():
    """从环境变量读取认证信息并创建 VpcClient"""
    from huaweicloudsdkcore.auth.credentials import BasicCredentials
    from huaweicloudsdkvpc.v3 import VpcClient

    ak = os.environ.get("HW_CLOUD_AK")
    sk = os.environ.get("HW_CLOUD_SK")
    project_id = os.environ.get("HW_CLOUD_PROJECT_ID")
    region = os.environ.get("HW_CLOUD_REGION", "cn-east-3")

    if not all([ak, sk, project_id]):
        raise RuntimeError(
            "请设置环境变量 HW_CLOUD_AK, HW_CLOUD_SK, HW_CLOUD_PROJECT_ID"
        )

    credentials = BasicCredentials(ak, sk, project_id)
    client = VpcClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(region) \
        .build()
    return client


# ---------------------------------------------------------------------------
# 工单解析
# ---------------------------------------------------------------------------

def parse_work_order_text(text: str) -> dict:
    """从文本工单中解析策略字段"""
    fields = {
        "action": None,
        "protocol": None,
        "source_ip": None,
        "dest_ip": None,
        "dest_domain": None,
        "dest_port": None,
        "reason": None,
        "expiry": None,
        "direction": None,
    }

    # 字段名映射（支持多种中文/英文写法）
    key_map = {
        "动作": "action", "action": "action", "操作": "action", "策略": "action",
        "协议": "protocol", "protocol": "protocol",
        "方向": "direction", "direction": "direction",
        "源ip": "source_ip", "源IP": "source_ip", "源地址": "source_ip",
        "source_ip": "source_ip", "source ip": "source_ip",
        "目的ip": "dest_ip", "目的IP": "dest_ip", "目标ip": "dest_ip",
        "目标IP": "dest_ip", "目标地址": "dest_ip", "目的地址": "dest_ip",
        "dest_ip": "dest_ip", "dest ip": "dest_ip",
        "目的域名": "dest_domain", "目标域名": "dest_domain",
        "dest_domain": "dest_domain", "domain": "dest_domain",
        "目的端口": "dest_port", "目标端口": "dest_port", "端口": "dest_port",
        "dest_port": "dest_port", "port": "dest_port",
        "开通原因": "reason", "原因": "reason", "reason": "reason", "说明": "reason",
        "策略有效期": "expiry", "有效期": "expiry", "expiry": "expiry",
        "valid_until": "expiry", "过期时间": "expiry",
    }

    for line in text.strip().splitlines():
        line = line.strip()
        if not line or "：" not in line and ":" not in line:
            continue

        # 分割 key:value（支持中文冒号和英文冒号）
        parts = re.split(r"[：:]", line, maxsplit=1)
        if len(parts) != 2:
            continue

        raw_key = parts[0].strip().lower()
        raw_value = parts[1].strip()

        # 匹配字段名
        matched_key = None
        for alias, field in key_map.items():
            if raw_key == alias.lower():
                matched_key = field
                break

        if matched_key and raw_value:
            fields[matched_key] = raw_value

    return fields


def parse_work_order_yaml(filepath: str) -> dict:
    """从 YAML 文件中解析工单"""
    import yaml

    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("YAML 文件内容必须是字典格式")

    field_map = {
        "action": "action",
        "protocol": "protocol",
        "direction": "direction",
        "source_ip": "source_ip",
        "dest_ip": "dest_ip",
        "dest_domain": "dest_domain",
        "dest_port": "dest_port",
        "reason": "reason",
        "expiry": "expiry",
    }

    result = {v: None for v in field_map.values()}
    for key, value in data.items():
        lkey = key.lower().replace("-", "_")
        if lkey in field_map:
            result[lkey] = str(value) if value is not None else None

    return result


def parse_work_order_image(image_path: str) -> dict:
    """通过 OCR 从图片工单中解析文本，再调用文本解析"""
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        raise RuntimeError(
            "图片 OCR 需要安装: pip install pillow pytesseract\n"
            "以及 tesseract-ocr 系统包: apt-get install tesseract-ocr"
        )

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    img = Image.open(image_path)
    # 尝试中文 OCR（优先），回退英文
    try:
        text = pytesseract.image_to_string(img, lang="chi_sim+eng")
    except Exception:
        text = pytesseract.image_to_string(img, lang="eng")

    if not text.strip():
        raise RuntimeError("OCR 未能从图片中识别到任何文本，请检查图片质量")

    print(f"[OCR 识别结果]\n{text}\n")
    return parse_work_order_text(text)


# ---------------------------------------------------------------------------
# 校验工具
# ---------------------------------------------------------------------------

def validate_port_spec(port_spec: str) -> str:
    """
    校验端口规格：支持单端口 / 逗号列表 / 范围（如 80, 443,8080, 1-1000）
    返回规范化后的字符串；非法则抛 ValueError
    """
    if port_spec is None or not str(port_spec).strip():
        raise ValueError("目的端口 (dest_port) 不能为空")

    tokens = [t.strip() for t in str(port_spec).split(",") if t.strip()]
    if not tokens:
        raise ValueError(f"无法解析的端口规格: {port_spec!r}")

    normalized = []
    for token in tokens:
        if "-" in token:
            parts = token.split("-")
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                raise ValueError(f"非法端口范围: {token!r}，应为 起始-结束（如 1-1000）")
            start, end = int(parts[0]), int(parts[1])
            if not (1 <= start <= end <= 65535):
                raise ValueError(
                    f"端口范围越界: {token!r}，端口必须在 1-65535 之间且起始 <= 结束"
                )
            normalized.append(f"{start}-{end}")
        else:
            if not token.isdigit():
                raise ValueError(f"非法端口: {token!r}，应为 1-65535 的数字")
            port = int(token)
            if not 1 <= port <= 65535:
                raise ValueError(f"端口越界: {token!r}，必须在 1-65535 之间")
            normalized.append(str(port))

    return ",".join(normalized)


def parse_expiry_date(expiry_str: str):
    """解析有效期字符串为 date；无法解析返回 None（fail-safe：不删除）"""
    if not expiry_str:
        return None
    s = expiry_str.strip()
    for fmt in EXPIRY_DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    # 尝试 ISO 格式兜底
    try:
        return datetime.fromisoformat(s).date()
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# 标准化字段
# ---------------------------------------------------------------------------

def normalize_fields(fields: dict) -> dict:
    """
    标准化解析后的字段值。

    安全原则（fail-closed）:
    - action 缺失 → 报错退出，不默认 allow
    - source_ip 缺失 → 报错退出，不默认 0.0.0.0/0
    - 所有 IP / CIDR / 端口做格式校验
    """
    result = dict(fields)

    # 标准 action —— 缺失直接报错，不设默认值
    if fields.get("action"):
        action_lower = fields["action"].strip().lower()
        for alias, val in ACTION_MAP.items():
            if action_lower == alias.lower():
                result["action"] = val
                break
        else:
            raise ValueError(f"无法识别的动作: {fields['action']}，应为 允许/拒绝 或 allow/deny")
    else:
        raise ValueError(
            "动作 (action) 是必填字段：必须明确指定 允许/拒绝 (allow/deny)，"
            "不提供默认值以防误放行"
        )

    # 标准 protocol
    if fields.get("protocol"):
        proto = fields["protocol"].strip().lower()
        for alias, val in PROTOCOL_MAP.items():
            if proto == alias.lower():
                result["protocol"] = val
                break
        else:
            # 尝试作为 IP 协议号
            if proto.isdigit() and 0 <= int(proto) <= 255:
                result["protocol"] = proto
            else:
                raise ValueError(f"无法识别的协议: {fields['protocol']}")
    else:
        result["protocol"] = "tcp"  # 默认 TCP

    # 标准 direction —— 工单可显式指定方向，缺省入方向
    if fields.get("direction"):
        dir_lower = fields["direction"].strip().lower()
        for alias, val in DIRECTION_MAP.items():
            if dir_lower == alias.lower():
                result["direction"] = val
                break
        else:
            raise ValueError(
                f"无法识别的方向: {fields['direction']}，应为 入方向/出方向 或 ingress/egress"
            )
    else:
        result["direction"] = "ingress"

    # 校验并标准化 source CIDR —— 必填，不再默认 0.0.0.0/0
    if fields.get("source_ip"):
        src = fields["source_ip"].strip()
        if "/" not in src:
            src = f"{src}/32"  # 单个 IP 转为 /32
        try:
            result["source_ip"] = str(ipaddress.ip_network(src, strict=False))
        except ValueError:
            raise ValueError(f"非法源 IP/CIDR: {fields['source_ip']!r}")
    else:
        raise ValueError(
            "源 IP (source_ip) 是必填字段：必须明确指定来源 CIDR（如 10.0.0.0/24），"
            "出于安全考虑不再默认 0.0.0.0/0（全网开放）"
        )

    # 校验 dest_ip 并构建安全组名 = sg-{dest_ip}
    if fields.get("dest_ip"):
        dest = fields["dest_ip"].strip()
        try:
            ipaddress.ip_address(dest)
        except ValueError:
            raise ValueError(f"非法目的 IP: {dest!r}，应为合法 IPv4/IPv6 地址")
        result["sg_name"] = f"sg-{dest}"
    else:
        raise ValueError("目的 IP (dest_ip) 是必填字段")

    # 校验端口
    if fields.get("dest_port"):
        result["dest_port"] = validate_port_spec(fields["dest_port"])
    else:
        result["dest_port"] = ""

    # 构建描述信息（expiry 以 valid_until: 标记写入，供 cleanup_expired 扫描）
    desc_parts = []
    if fields.get("reason"):
        desc_parts.append(fields["reason"].strip())
    if fields.get("dest_domain"):
        desc_parts.append(f"dest_domain:{fields['dest_domain'].strip()}")
    if fields.get("expiry"):
        desc_parts.append(f"{EXPIRY_MARKER}{fields['expiry'].strip()}")
    result["description"] = " | ".join(desc_parts) if desc_parts else "Created by sg-policy-deploy"

    return result


# ---------------------------------------------------------------------------
# 安全组操作
# ---------------------------------------------------------------------------

def find_security_group_by_name(client, sg_name: str):
    """查询安全组，返回安全组对象或 None"""
    from huaweicloudsdkcore.exceptions import exceptions
    from huaweicloudsdkvpc.v3.model import ListSecurityGroupsRequest

    request = ListSecurityGroupsRequest()
    request.name = [sg_name]
    try:
        response = client.list_security_groups(request)
        if response.security_groups:
            return response.security_groups[0]
    except exceptions.ClientRequestException as e:
        print(f"[WARN] 查询安全组列表失败: {e.error_msg}", file=sys.stderr)
    return None


def create_security_group(client, sg_name: str, dest_ip: str) -> str:
    """创建安全组，返回安全组 ID"""
    from huaweicloudsdkvpc.v3.model import (
        CreateSecurityGroupRequest,
        CreateSecurityGroupRequestBody,
        CreateSecurityGroupOption,
    )

    print(f"[INFO] 安全组 {sg_name} 不存在，正在创建...")
    request = CreateSecurityGroupRequest()
    request.body = CreateSecurityGroupRequestBody(
        security_group=CreateSecurityGroupOption(
            name=sg_name,
            description=f"Auto-created for {dest_ip} by sg-policy-deploy",
        )
    )
    response = client.create_security_group(request)
    sg_id = response.security_group.id
    print(f"[INFO] 已创建安全组 {sg_name} (ID: {sg_id})")
    return sg_id


def check_rule_exists(client, sg_id: str, fields: dict) -> bool:
    """检查是否存在完全相同的规则，避免重复添加"""
    from huaweicloudsdkvpc.v3.model import ListSecurityGroupRulesRequest

    req = ListSecurityGroupRulesRequest()
    req.security_group_id = [sg_id]
    req.action = fields["action"]
    req.protocol = [fields["protocol"]]
    if fields.get("direction"):
        req.direction = fields["direction"]

    try:
        resp = client.list_security_group_rules(req)
        if resp.security_group_rules:
            for rule in resp.security_group_rules:
                if (rule.remote_ip_prefix == fields.get("source_ip")
                        and rule.multiport == fields.get("dest_port")
                        and rule.action == fields.get("action")
                        and rule.direction == fields.get("direction")):
                    return True
    except Exception as e:
        print(f"[WARN] 查询已有规则失败: {e}", file=sys.stderr)

    return False


def extract_expiry(description: str):
    """从规则描述中提取 valid_until 标记后的日期字符串"""
    if not description or EXPIRY_MARKER not in description:
        return None
    m = re.search(re.escape(EXPIRY_MARKER) + r"\s*([^\s|]+)", description)
    return m.group(1) if m else None


def cleanup_expired(client, sg_id: str, dry_run: bool = False) -> list:
    """
    扫描安全组内规则，删除描述中带有 valid_until 标记且已过期的规则。

    - 删除前先打印将被删除的规则清单（人工可见）
    - dry_run=True 时仅打印清单，不执行删除
    - 有效期无法解析的规则视为未过期（fail-safe，不删除）
    - 返回已删除（或 dry-run 下将删除）的规则 ID 列表
    """
    from huaweicloudsdkvpc.v3.model import (
        DeleteSecurityGroupRuleRequest,
        ListSecurityGroupRulesRequest,
    )

    expired = []
    try:
        req = ListSecurityGroupRulesRequest()
        req.security_group_id = [sg_id]
        resp = client.list_security_group_rules(req)
        rules = resp.security_group_rules or []
    except Exception as e:
        print(f"[WARN] 查询规则列表失败，跳过过期清理: {e}", file=sys.stderr)
        return expired

    today = date.today()
    for rule in rules:
        expiry_str = extract_expiry(getattr(rule, "description", "") or "")
        if not expiry_str:
            continue
        expiry_date = parse_expiry_date(expiry_str)
        if expiry_date is None:
            print(
                f"[WARN] 规则 {rule.id} 的有效期 {expiry_str!r} 无法解析，"
                "视为未过期，跳过删除",
                file=sys.stderr,
            )
            continue
        if expiry_date < today:
            expired.append(rule)

    if not expired:
        print("[INFO] 未发现已过期的规则，无需清理")
        return []

    # 先输出将被删除的规则清单
    print("\n[CLEANUP] 以下规则已过期，将被删除:")
    for rule in expired:
        print(
            f"  - id={rule.id} direction={getattr(rule, 'direction', '?')} "
            f"protocol={getattr(rule, 'protocol', '?')} port={getattr(rule, 'multiport', '?')} "
            f"source={getattr(rule, 'remote_ip_prefix', '?')} "
            f"description={getattr(rule, 'description', '')!r}"
        )

    if dry_run:
        print("[DRY RUN] 以上规则在真实执行时将被删除，本次不执行")
        return [r.id for r in expired]

    deleted = []
    for rule in expired:
        try:
            del_req = DeleteSecurityGroupRuleRequest()
            del_req.security_group_rule_id = rule.id
            client.delete_security_group_rule(del_req)
            print(f"[INFO] 已删除过期规则 {rule.id}")
            deleted.append(rule.id)
        except Exception as e:
            print(f"[ERROR] 删除过期规则 {rule.id} 失败: {e}", file=sys.stderr)

    return deleted


def add_security_group_rule(client, sg_id: str, fields: dict) -> str:
    """添加安全组规则，返回规则 ID"""
    from huaweicloudsdkvpc.v3.model import (
        CreateSecurityGroupRuleRequest,
        CreateSecurityGroupRuleRequestBody,
        CreateSecurityGroupRuleOption,
    )

    request = CreateSecurityGroupRuleRequest()
    rule_body = CreateSecurityGroupRuleOption(
        security_group_id=sg_id,
        direction=fields.get("direction", "ingress"),
        protocol=fields["protocol"],
        multiport=fields["dest_port"],
        remote_ip_prefix=fields["source_ip"],
        description=fields["description"],
        action=fields["action"],
        priority=fields.get("priority", 1),
        enabled=True,
    )
    request.body = CreateSecurityGroupRuleRequestBody(
        security_group_rule=rule_body
    )

    response = client.create_security_group_rule(request)
    rule_id = response.security_group_rule.id
    print(f"[INFO] 已添加规则 (ID: {rule_id})")
    return rule_id


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def deploy_policy(fields: dict, dry_run: bool = False) -> dict:
    """
    执行端口策略开通主流程

    参数:
        fields: 标准化的策略字段字典（normalize_fields 已做 fail-closed 校验）
        dry_run: 仅打印操作而不真正执行 API 调用

    返回:
        结果字典
    """
    print(f"\n{'='*60}")
    print("  安全组端口策略开通")
    print(f"{'='*60}\n")

    # 输出解析结果
    print("[工单解析结果]")
    for k, v in fields.items():
        print(f"  {k}: {v}")
    print()

    if dry_run:
        print("[DRY RUN] 模式，仅打印，不执行 API 调用")
        print("[DRY RUN] 注意：真实执行时会自动清理已过期规则"
              f"（规则描述含 {EXPIRY_MARKER} 且日期已过）")
        return {"status": "dry_run", "fields": fields}

    # 创建客户端
    client = get_vpc_client()
    sg_name = fields["sg_name"]
    dest_ip = fields["dest_ip"]
    source_ip = fields["source_ip"]  # normalize_fields 已保证必填
    action = fields["action"]
    protocol = fields["protocol"]
    port = fields.get("dest_port", "")
    direction = fields.get("direction", "ingress")
    print(f"[INFO] 规则方向: {direction}")

    # 步骤 1: 查询安全组
    sg = find_security_group_by_name(client, sg_name)
    if sg:
        sg_id = sg.id
        print(f"[INFO] 已找到安全组 {sg_name} (ID: {sg_id})")
    else:
        # 步骤 2 (条件): 创建安全组
        sg_id = create_security_group(client, sg_name, dest_ip)

    # 步骤 3: 清理已过期规则（删除前会先打印清单）
    cleaned = cleanup_expired(client, sg_id, dry_run=False)

    # 步骤 4: 去重检查
    if check_rule_exists(client, sg_id, fields):
        print(f"[INFO] 规则已存在，跳过添加")
        return {
            "status": "skipped",
            "reason": "rule_already_exists",
            "security_group": sg_name,
            "security_group_id": sg_id,
            "cleaned_expired_rules": cleaned,
        }

    # 步骤 5: 添加规则
    rule_id = add_security_group_rule(client, sg_id, fields)

    # 步骤 6: 输出结果
    result = {
        "status": "success",
        "security_group": sg_name,
        "security_group_id": sg_id,
        "rule_id": rule_id,
        "action": action,
        "protocol": protocol,
        "source": source_ip,
        "port": port,
        "direction": direction,
        "description": fields["description"],
        "cleaned_expired_rules": cleaned,
    }

    print(f"\n{'='*60}")
    print("  开通完成")
    print(f"{'='*60}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()

    return result


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="华为云安全组端口策略开通工作流"
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--text", help="工单文本内容（字符串）")
    input_group.add_argument("--image", help="工单图片路径（OCR 识别）")
    input_group.add_argument("--file", help="工单 YAML 文件路径")
    parser.add_argument("--dry-run", action="store_true", help="仅打印操作，不执行 API 调用")
    parser.add_argument("--output", "-o", help="将结果输出到指定 JSON 文件")

    args = parser.parse_args()

    # 解析工单
    if args.text:
        raw = parse_work_order_text(args.text)
    elif args.image:
        raw = parse_work_order_image(args.image)
    elif args.file:
        raw = parse_work_order_yaml(args.file)
    else:
        parser.error("请指定 --text, --image 或 --file")

    # 标准化（含 fail-closed 校验：action / source_ip / dest_ip / 端口）
    try:
        fields = normalize_fields(raw)
    except ValueError as e:
        print(f"[ERROR] 工单校验失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 执行部署
    try:
        result = deploy_policy(fields, dry_run=args.dry_run)
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        err_msg = str(e)
        # Try to extract Huawei Cloud API error detail
        if hasattr(e, "error_msg"):
            err_msg = e.error_msg
        print(f"[ERROR] 华为云 API 调用失败: {err_msg}", file=sys.stderr)
        sys.exit(1)

    # 输出文件
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 结果已保存至: {args.output}")


if __name__ == "__main__":
    main()
