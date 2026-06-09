#!/usr/bin/env python3
"""
ESM API 调用驱动 — 自动获取 IAM Token、调用 ESM 各 API 端点

Usage:
  export IAM_BASE_URL="https://iam-pub.<region>.xxx.com"
  export IAM_USERNAME="<user>" IAM_PASSWORD="<pass>" IAM_DOMAIN_NAME="<domain>"
  export ECS_PROJECT_ID="<project-id>"
  export ESM_BASE_URL="https://esm-api.cn-south-298.myhuaweicloud.com"
  export ESM_APPCODE="<appcode>" ESM_DOMAIN_ID="<domain-id>"

  python driver.py capacity --service-type ECS_VM
  python driver.py audit-log --begin "2026-06-01" --end "2026-06-09"
  python driver.py billing --begin "2026-06-01" --end "2026-06-30" --output ./data
"""

import argparse
import json
import logging
import os
import sys
import time
from typing import Optional

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("esm")


# ======================================================================
# Config
# ======================================================================

def env_or_exit(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        logger.error("Missing required env var: %s", key)
        sys.exit(1)
    return val


class Config:
    IAM_BASE_URL = os.environ.get("IAM_BASE_URL", "").rstrip("/")
    IAM_USERNAME = os.environ.get("IAM_USERNAME", "")
    IAM_PASSWORD = os.environ.get("IAM_PASSWORD", "")
    IAM_DOMAIN_NAME = os.environ.get("IAM_DOMAIN_NAME", "")
    ECS_PROJECT_ID = os.environ.get("ECS_PROJECT_ID", "")
    ESM_BASE_URL = os.environ.get("ESM_BASE_URL", "").rstrip("/")
    ESM_APPCODE = os.environ.get("ESM_APPCODE", "")
    ESM_DOMAIN_ID = os.environ.get("ESM_DOMAIN_ID", "")


# ======================================================================
# ESM Client
# ======================================================================

class EsmClient:
    """ESM API 客户端 — 自动 Token 管理"""

    def __init__(self):
        self._token: Optional[str] = None

    # ---- Token ----

    def _get_token(self) -> str:
        """获取 IAM Token"""
        url = f"{Config.IAM_BASE_URL}/v3/auth/tokens"
        payload = {
            "auth": {
                "identity": {
                    "methods": ["password"],
                    "password": {
                        "user": {
                            "name": Config.IAM_USERNAME,
                            "password": Config.IAM_PASSWORD,
                            "domain": {"name": Config.IAM_DOMAIN_NAME},
                        }
                    },
                },
                "scope": {"project": {"id": Config.ECS_PROJECT_ID}},
            }
        }
        logger.info("获取 IAM Token ...")
        resp = httpx.post(url, json=payload, verify=False, timeout=30)
        resp.raise_for_status()
        token = resp.headers.get("x-subject-token", "")
        if not token:
            raise RuntimeError("IAM 响应中未找到 x-subject-token")
        self._token = token
        return token

    def _ensure_token(self) -> str:
        """确保有有效 Token"""
        if not self._token:
            return self._get_token()
        return self._token

    def _invalidate_token(self):
        self._token = None

    # ---- Request ----

    def _headers(self) -> dict:
        return {
            "X-Auth-Token": self._ensure_token(),
            "x-hcso-appcode": Config.ESM_APPCODE,
            "X-Apig-AppCode": Config.ESM_APPCODE,
            "x-hcso-domainid": Config.ESM_DOMAIN_ID,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{Config.ESM_BASE_URL}{path}"
        headers = kwargs.pop("headers", {})
        full_headers = {**self._headers(), **headers}

        for attempt in range(2):
            try:
                resp = httpx.request(
                    method, url, headers=full_headers,
                    verify=False, timeout=30, **kwargs,
                )
                if resp.status_code == 401 and attempt == 0:
                    logger.warning("Token 失效 (401)，正在刷新 ...")
                    self._invalidate_token()
                    full_headers["X-Auth-Token"] = self._ensure_token()
                    continue
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401 and attempt == 0:
                    logger.warning("Token 失效 (401)，正在刷新 ...")
                    self._invalidate_token()
                    full_headers["X-Auth-Token"] = self._ensure_token()
                    continue
                raise

    # ---- API ----

    def query_capacity(self, service_type: str = "ECS_VM",
                       begin: str = "", end: str = "",
                       page_size: int = 10, offset: int = 0) -> dict:
        """云服务容量查询"""
        params = {"service_type": service_type, "page_size": page_size, "offset_value": offset}
        if begin:
            params["begin_time"] = begin
        if end:
            params["end_time"] = end
        return self._request("GET", "/rest/dataapi/homs/open-api/v1/CloudService/capacity", params=params)

    def query_audit_log(self, begin: str = "", end: str = "",
                        page_size: int = 10, offset: int = 0) -> dict:
        """云审计日志查询"""
        params = {"page_size": page_size, "offset_value": offset}
        if begin:
            params["begin_time"] = begin
        if end:
            params["end_time"] = end
        return self._request("GET", "/rest/dataapi/homs/open-api/v1/cloudAuditlog", params=params)

    def query_device_asset(self) -> dict:
        """设备资产信息查询"""
        return self._request("GET", "/rest/dataapi/homs/open-api/v1/DeviceAsset/info")

    def query_alarm(self, service_type: str = "ECS_VM") -> dict:
        """云服务告警查询"""
        params = {"service_type": service_type}
        return self._request("GET", "/rest/dataapi/homs/open-api/v1/CloudServiceAlarm/info", params=params)

    def query_device_alarm(self) -> dict:
        """设备告警查询"""
        return self._request("GET", "/rest/dataapi/homs/open-api/v1/DeviceAlarm/info")

    def query_host_capacity(self) -> dict:
        """物理主机容量查询"""
        return self._request("GET", "/rest/dataapi/homs/open-api/v1/host-physical/capacity")

    def query_host_metrics(self) -> dict:
        """主机监控指标数据"""
        return self._request("GET", "/rest/dataapi/homs/open-api/v1/host/metricdata")

    def query_host_performance(self, begin: str = "", end: str = "") -> dict:
        """主机性能数据"""
        params = {}
        if begin:
            params["begin_time"] = begin
        if end:
            params["end_time"] = end
        return self._request("GET", "/rest/dataapi/homs/open-api/v1/host/performancedata", params=params)

    # ---- 计量话单（三步异步） ----

    def billing_create_job(self, begin: str, end: str) -> str:
        """Step 1: 创建话单查询任务"""
        logger.info("创建话单查询任务: %s ~ %s", begin, end)
        payload = {"begin_time": begin, "end_time": end}
        resp = self._request(
            "POST", f"/meter/v1/{Config.ESM_DOMAIN_ID}/query-jobs",
            json=payload,
        )
        job_id = resp.get("job_id", "")
        logger.info("任务创建成功, job_id: %s", job_id)
        return job_id

    def billing_query_job(self, job_id: str) -> dict:
        """Step 2: 查询任务状态"""
        return self._request(
            "GET", f"/meter/v1/{Config.ESM_DOMAIN_ID}/query-jobs/{job_id}",
        )

    def billing_get_sdr(self, job_id: str, page_size: int = 100, offset: int = 0) -> dict:
        """Step 3: 获取话单数据"""
        params = {"page_size": page_size, "offset_value": offset}
        return self._request(
            "GET", f"/meter/v1/{Config.ESM_DOMAIN_ID}/query-jobs/{job_id}/sdr",
            params=params,
        )

    def billing_collect(self, begin: str, end: str, output_dir: str = "."):
        """全流程：创建任务 → 轮询完成 → 下载话单"""
        job_id = self.billing_create_job(begin, end)
        if not job_id:
            logger.error("创建话单任务失败")
            return

        # 轮询
        logger.info("等待任务完成 ...")
        for _ in range(60):  # max 60 * 10s = 10min
            status = self.billing_query_job(job_id)
            state = status.get("status", status.get("state", ""))
            if state in ("done", "success", "completed", "finished"):
                logger.info("任务完成: %s", state)
                break
            elif state in ("failed", "error"):
                logger.error("任务失败: %s", json.dumps(status, ensure_ascii=False))
                return
            time.sleep(10)
        else:
            logger.error("任务超时")
            return

        # 分页获取话单
        all_records = []
        offset = 0
        while True:
            data = self.billing_get_sdr(job_id, page_size=1000, offset=offset)
            records = data.get("sdr", data.get("records", []))
            if not records:
                break
            all_records.extend(records)
            offset += len(records)
            logger.info("已获取 %d 条话单", len(all_records))

        # 保存
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"billing_{begin}_{end}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(all_records, f, ensure_ascii=False, indent=2)
        logger.info("话单已保存: %s (共 %d 条)", path, len(all_records))


# ======================================================================
# CLI
# ======================================================================

def main():
    parser = argparse.ArgumentParser(description="ESM API 调用工具")
    sub = parser.add_subparsers(dest="command")

    # capacity
    p_cap = sub.add_parser("capacity", help="云服务容量查询")
    p_cap.add_argument("--service-type", default="ECS_VM")
    p_cap.add_argument("--begin")
    p_cap.add_argument("--end")
    p_cap.add_argument("--page-size", type=int, default=10)
    p_cap.add_argument("--offset", type=int, default=0)

    # audit-log
    p_audit = sub.add_parser("audit-log", help="云审计日志查询")
    p_audit.add_argument("--begin")
    p_audit.add_argument("--end")
    p_audit.add_argument("--page-size", type=int, default=10)
    p_audit.add_argument("--offset", type=int, default=0)

    # device-asset
    sub.add_parser("device-asset", help="设备资产信息查询")

    # alarm
    p_alarm = sub.add_parser("alarm", help="云服务告警查询")
    p_alarm.add_argument("--service-type", default="ECS_VM")

    # device-alarm
    sub.add_parser("device-alarm", help="设备告警查询")

    # host-capacity
    sub.add_parser("host-capacity", help="物理主机容量查询")

    # host-metrics
    sub.add_parser("host-metrics", help="主机监控指标数据")

    # host-performance
    p_perf = sub.add_parser("host-performance", help="主机性能数据")
    p_perf.add_argument("--begin")
    p_perf.add_argument("--end")

    # billing
    p_bill = sub.add_parser("billing", help="计量话单（三步异步）")
    p_bill.add_argument("--begin", required=True)
    p_bill.add_argument("--end", required=True)
    p_bill.add_argument("--output", default=".")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    client = EsmClient()

    try:
        if args.command == "capacity":
            result = client.query_capacity(
                args.service_type, args.begin or "", args.end or "",
                args.page_size, args.offset,
            )
        elif args.command == "audit-log":
            result = client.query_audit_log(args.begin or "", args.end or "", args.page_size, args.offset)
        elif args.command == "device-asset":
            result = client.query_device_asset()
        elif args.command == "alarm":
            result = client.query_alarm(args.service_type)
        elif args.command == "device-alarm":
            result = client.query_device_alarm()
        elif args.command == "host-capacity":
            result = client.query_host_capacity()
        elif args.command == "host-metrics":
            result = client.query_host_metrics()
        elif args.command == "host-performance":
            result = client.query_host_performance(args.begin or "", args.end or "")
        elif args.command == "billing":
            client.billing_collect(args.begin, args.end, args.output)
            return
        else:
            return

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except httpx.HTTPStatusError as e:
        logger.error("HTTP %s: %s", e.response.status_code, e.response.text[:500])
        sys.exit(1)
    except httpx.RequestError as e:
        logger.error("请求失败: %s", e)
        sys.exit(1)
    except RuntimeError as e:
        logger.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
