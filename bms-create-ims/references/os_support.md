# 操作系统兼容性列表

## x86 操作系统

| 操作系统 | 版本 | 内核版本 |
|----------|------|-----------|
| RedHat | 7.2 ~ 7.5 | 3.10.0-xxx.el7.x86_64 |
| Oracle Linux | 7.2 ~ 7.4 | 3.10.0-xxx.el7.x86_64 或 4.1.12-xxx.el7uek.x86_64 |
| CentOS | 7.2 ~ 7.9 | 3.10.0-xxx.el7.x86_64 |
| Ubuntu | 18.04.2 LTS | 4.15.0-45-generic |
| Debian | 8.6 | 3.16.0-4-amd64 |
| Huawei Cloud EulerOS | 2.0 | 5.10.0-60.18.0.50.r1083_58.hce2 |

## ARM 操作系统

| 操作系统 | 版本 | 内核版本 |
|----------|------|-----------|
| CentOS | 7.6 | 4.14.0-115.el7a.0.1.aarch64 |
| Huawei Cloud EulerOS | 2.0 | 5.10.0-60.18.0.50.r1083_58.hce2 |

## 关键注意事项

- Ubuntu 18.04 必须使用 **server 版 ISO**，不要使用 live-server
- Debian 8.6 需安装基础组件（如 ifconfig、dhclient 等网络工具）
- V6 CPU 架构必须选择 **UEFI** 启动方式
