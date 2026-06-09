# 软件准备清单

## VM 内部所需软件

这些是进入 VM 后配置阶段需要用到的软件和驱动。

| 序号 | 名称 | 说明 | 获取方式 |
|------|------|------|----------|
| 1 | bms-network-config | 网络自动化配置 (ARM: aarch64.rpm) | 华为 support 网站 |
| 2 | Cloud-Init | 初始化工具 | 在线安装 (yum/apt-get/pip) |
| 3 | Hi1822 网卡驱动 | 鲲鹏 ARM 网卡驱动 (kmod-hinic) | 华为 support 网站 |
| 4 | IB 网卡驱动 (x86) | 100G Infiniband 驱动 (MLNX_OFED_LINUX) | NVIDIA 官网 |
| 5 | IB 网卡驱动 (ARM/openEuler) | IB_NIC-CX4Lx_CX5_CX6-*-aarch64.rpm (MLX5) | 华为 support 网站 |
| 6 | FusionServer 服务器驱动 | 板载网卡、RAID 卡驱动 (i40e/mpt3sas/megaraid_sas) | xfusion support |
| 7 | ComputingComponentiDriver | ARM 鲲鹏板载驱动 (zip 内含 onboard_driver ISO) | 华为 support 网站 |
| 8 | TaiShan 服务器驱动 | 网卡、RAID 卡驱动 | 华为 support |
| 9 | UltraPath 软件 | 多路径软件 | 华为 support |
| 10 | MLNX_OFED 驱动 | VROCE 依赖驱动 | NVIDIA 官网 |
| 11 | vroce 驱动 | 支持 vroce 协议网卡驱动 (hiroce3/hinic3) | 华为 support |
| 12 | HPD | 网卡热插拔驱动 | 华为 support |
| 13 | SDI 卡驱动 | kmod-scsi_ep_front | 华为 support |
| 14 | CloudResetPwdAgent | 一键式重置密码插件 | 华为 support |

> 注意：ARM (aarch64) 和 x86 (x86_64) 包不通用，务必下载对应架构版本。

## kat2 机型速查

适用 OS: openEuler 22.03 SP4，ARM 架构。

**预先下载（5 个）**：

| 包名 | 文件名参考 |
|------|-----------|
| Hi1822 网卡驱动 | `kmod-hinic-*.aarch64.rpm` |
| bms-network-config | `bms-network-config-*.aarch64.rpm` |
| IB MLX5 驱动 | `IB_NIC-CX4Lx_CX5_CX6_CX6Dx_CX6Lx-openEuler22.03SP4-mlx5_core-24.10-3.2.5-aarch64` |
| ComputingComponentiDriver | `ComputingComponentiDriver-openEuler22.03SP4-Driver-ARM_2.0.9.zip`<br>→ 解压后取 `onboard_driver_openEuler22.03SP4.iso` |
| CloudResetPwdAgent | `CloudResetPwdAgent.zip` |

**在线安装（4 个）**：
`cloud-init` / `cloud-utils-growpart` / `network-scripts` / `gdisk`

