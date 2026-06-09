# 裸金属服务器规格与驱动对应关系

| 机型 | 启动方式 | 服务器驱动 | SDI卡驱动 | Hi1822驱动 | IB驱动 | MLNX_OFED | vroce | HPD | bms-network-config |
|------|----------|------------|------------|-------------|--------|-----------|-------|-----|---------------------|
| s3/s4/m2/m3/hc2 | BIOS | FusionServer | 需要 | - | - | - | - | - | 需要 |
| s1/d1/d2/io1/io2 | BIOS | FusionServer | - | - | - | - | - | - | 需要 |
| h1 | BIOS | FusionServer | - | - | 需要 | - | - | - | 需要 |
| h2 | BIOS | FusionServer | 需要 | - | 需要 | - | - | - | 需要 |
| c6/s6/d6/io6 | UEFI | FusionServer | - | 需要 | - | - | - | - | - |
| ks1/kd1 | UEFI | - | - | 需要 | - | - | - | - | 需要 |
| kh1 | UEFI | - | - | 需要 | 需要 | - | - | - | 需要 |
| kat2 | UEFI | ComputingComponentiDriver | - | 需要 | 需要(MLX5) | - | - | - | 需要 |
| ac8/ki2/kc2 | UEFI | - | - | - | - | 需要 | 需要 | 需要 | - |

## 驱动说明

- **FusionServer 服务器驱动**: 板载网卡驱动（i40e）、RAID卡驱动（mpt3sas、megaraid_sas），仅 x86 BIOS 机型
- **ComputingComponentiDriver**: ARM 鲲鹏机型板载驱动（openEuler），打包为 ISO 镜像
- **SDI 卡驱动**: kmod-scsi_ep_front，适用 s3/s4/m2/m3/h2/hc2
- **Hi1822 网卡驱动**: kmod-hinic，加载命令 `modprobe hinic`
- **IB 驱动**: 100G Infiniband 驱动（通用）；ARM/openEuler 机型使用专用 MLX5 IB 驱动包（如 IB_NIC-CX4Lx_CX5_CX6-*.aarch64.rpm）
- **MLNX_OFED**: VROCE 依赖驱动，版本 5.8-3.0.7.0-LTS
- **vroce 驱动**: 支持 vroce 协议的网卡前端驱动（hiroce3、hinic3 等）
- **HPD**: 网卡热插拔驱动，服务名 hpd
- **bms-network-config**: 网络自动化配置，适用 s1/s3/s4/d1/d2/m2/m3/io1/io2/h1/h2/hc2/ki1/kat2 等规格

## 驱动获取方式

| 驱动/软件 | 获取来源 |
|-----------|----------|
| bms-network-config | 华为 support 网站 |
| Hi1822 网卡驱动 | 华为 support 网站 |
| IB 网卡驱动 (x86) | NVIDIA 官网 |
| IB 网卡驱动 (ARM/openEuler MLX5) | 华为 support 网站 |
| FusionServer 服务器驱动 | xfusion support |
| ComputingComponentiDriver (ARM) | 华为 support 网站（zip 包内含 ISO） |
| TaiShan 服务器驱动 | 华为 support |
| UltraPath 软件 | 华为 support |
| MLNX_OFED 驱动 | NVIDIA 官网 |
| vroce 驱动 | 华为 support |
| HPD | 华为 support |
