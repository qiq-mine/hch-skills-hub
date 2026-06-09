---
name: bms-create-ims
description: "华为云裸金属服务器 (BMS) 私有镜像制作指南 —— 虚拟机内部配置阶段。This skill covers OS installation, partitioning, driver setup, Cloud-Init configuration, security hardening, and cleanup inside the VM. The user handles VM creation and final image export. Triggers: 裸金属服务器, BMS, 私有镜像制作, Cloud-Init, Hi1822, vroce, HPD, bms-network-config, UltraPath, FusionServer/TaiShan drivers, serial console login, partition schemes."
agent_created: true
---

# 裸金属服务器 BMS 私有镜像制作 —— 虚拟机内部配置

## Overview

本技能覆盖裸金属服务器镜像制作的**核心配置阶段**：虚拟机已经创建好、ISO 已挂载，
你需要进入 VM 内部完成操作系统的安装、分区、驱动配置、Cloud-Init、安全加固、
远程登录、环境清理等所有工作。

**范围边界**：
- 不包括：创建虚拟机（ISO 镜像服务 / virt-manager）、导出/转换镜像
- 只负责：VM 内部从分区装系统到最终清理的全部配置步骤

## When to Use This Skill

- 裸金属服务器镜像制作中的 VM 内部配置阶段
- 安装配置 Cloud-Init 用于 BMS 环境
- 安装裸金属服务器驱动（Hi1822、IB、vroce、HPD、UltraPath 等）
- 为 BMS 做 BIOS/UEFI 分区方案
- 配置串口控制台远程登录
- 安全加固与环境清理
- 根据机型确定需要哪些驱动

## Workflow

### 推荐：Agent 自动化模式

如果你有可 SSH 进 VM 的 agent，将 `scripts/setup-bms.sh` 和所有驱动包一起传入 VM
的 `/tmp/bms-packages/`，然后 agent 只需执行一行命令：

```bash
bash /tmp/bms-packages/setup-bms.sh --model kat2 --os openEuler
```

脚本会按顺序自动完成全部配置（基础环境 → Cloud-Init → 驱动 → 安全 → 串口 → 清理），
日志输出到 `/var/log/bms-setup.log`。如果 VM 暂时无法联网：

```bash
bash /tmp/bms-packages/setup-bms.sh --model kat2 --os openEuler --skip-network
```

脚本特性：
- **幂等** — 每步检查是否已执行，可安全重复跑
- **容错** — 非关键失败记 WARN 不中断
- **全量日志** — `/var/log/bms-setup.log`

### 手动模式（Step by Step）

如果选择人工操作或 agent 逐条执行，以下是完整步骤序列。

---

### Pre-Flight: 软件包准备与传入 VM

在开始配置之前，需要先把目标机型所需的软件包下载到本地，再传入 VM。

#### 第一步：根据机型确定需要的软件包

先向用户确认目标 BMS 机型（如 s3、ac8、h2 等），然后查询 `references/driver_mapping.md`
确定该机型需要哪些驱动。常见的包分类如下：

| 类别 | 典型包名 / 文件名 | 来源 |
|------|------------------|------|
| bms-network-config | `bms-network-config-*.rpm` 或 `*.deb` | 华为 support |
| SDI 卡驱动 | `kmod-scsi_ep_front-*.rpm` | 华为 support |
| Hi1822 网卡驱动 | `kmod-hinic-*.rpm` | 华为 support |
| IB 驱动 | `MLNX_OFED_LINUX-*.tgz` | NVIDIA 官网 |
| OFED 驱动 | `MLNX_OFED_LINUX-5.8-*.tgz` | NVIDIA 官网 |
| vroce 前端驱动 | `hiroce3-*.rpm`, `hinic3-*.rpm` 等 | 华为 support |
| HPD 热插拔 | `hotplug-daemon-*.rpm` | 华为 support |
| CloudResetPwdAgent | `CloudResetPwdAgent.zip` | 华为 support |
| UltraPath | `OceanStor_UltraPath_*.tar.gz` | 华为 support |

> **核心原则：只下载目标机型需要的包，不要全量下载。**

#### 第二步：传入 VM

在宿主机的文件传输工具（Xftp / FileZilla / WinSCP）中：

1. 连接到目标 VM 的 IP，使用 root 账号
2. 在 VM 中创建统一存放目录：
   ```bash
   mkdir -p /tmp/bms-packages
   ```
3. 把所有下载的驱动包**连同 `scripts/setup-bms.sh`** 拖入 `/tmp/bms-packages/`
4. 确认文件完整：
   ```bash
   ls -lh /tmp/bms-packages/
   ```

如果使用命令行 SCP（宿主机为 Linux）：
```bash
scp bms-network-config-*.rpm root@<VM_IP>:/tmp/bms-packages/
scp kmod-hinic-*.rpm root@<VM_IP>:/tmp/bms-packages/
# ... 逐个传入
```

#### 第三步：校验完整性（可选）

对关键包做 sha256 校验，防止传输损坏：
```bash
cd /tmp/bms-packages
sha256sum *.rpm *.tgz
```

---

### Step 1: OS Installation — 安装操作系统并分区

分区规则详见 `references/partition_guide.md`。核心约束：

- 使用 **MBR** 分区表
- 主分区数量 **≤ 3 个**
- **根分区必须是最后一个主分区**（自动扩盘依赖）
- UEFI 启动：需额外创建 `/boot/efi` 作为第一个分区

| 启动方式 | 典型分区方案 |
|----------|-------------|
| BIOS | boot → swap → `/` (根分区最后) |
| BIOS | swap → `/` |
| BIOS | `/` only |
| BIOS | 扩展分区 + LVM + `/` |
| UEFI | `/boot/efi` → swap → `/` |
| UEFI | `/boot/efi` → `/` |
| UEFI | `/boot/efi` → 扩展分区(LVM) → `/` |

**Ubuntu 18.04 / Debian 8.6 特别注意**：
- 必须使用 **server 版** ISO，不能用 live-server
- 手动分区，每项选择 "Primary"
- 根分区保证是最后创建的分区

---

### Step 2: UEFI Boot File Fix（仅 UEFI 启动）

装完系统后、重启前，把引导文件复制到标准路径：

**ARM**：
```bash
cp /boot/efi/EFI/$os_version/grubaa64.efi /boot/efi/EFI/BOOT/BOOTAA64.EFI
```

**x86**：
```bash
cp /boot/efi/EFI/$os_version/grubx64.efi /boot/efi/EFI/BOOT/BOOTX64.EFI
```

`$os_version` 替换为实际目录名（如 `centos`、`redhat`、`ubuntu` 等）。

---

### Step 3: Base Environment — 基础环境配置

逐项完成以下配置：

1. **安装基础组件** — Debian 需装 ifconfig、dhclient 等
2. **配置网络** — ifconfig / dhclient 确保能联网
3. **systemd 超时** → 300s
4. **关闭防火墙**：
   - RHEL 系：`systemctl disable firewalld`
   - Ubuntu/Debian：`ufw disable`
5. **网络管理工具**：
   - RHEL 系 → NetworkManager
   - Ubuntu → netplan
6. **删除本地用户**（可选，安全建议）
7. **grub 超时**（Debian 特需）
8. **文件句柄限制** → 65535
9. **禁用关机命令**：重命名/移除 `shutdown`、`poweroff`、`halt`
10. **密码有效期策略**

---

### Step 4: Cloud-Init — 安装与配置

#### 4.1 安装

| 系统 | 安装方式 |
|------|---------|
| RedHat/CentOS/Oracle Linux | `yum install cloud-init` |
| Ubuntu/Debian | `apt-get install cloud-init` |
| openEuler/HCE 2.0 | 配置 yum 源后 `yum install cloud-init` |
| 备选 | pip 安装 cloud-init 0.7.9+ 源码包 |

#### 4.2 配置 `/etc/cloud/cloud.cfg`

必须修改的项：
```yaml
disable_root: false
ssh_pwauth: true
preserve_hostname: false
datasource_list: [OpenStack]
```
在 `cloud_final_modules` 中添加 `- power-state-change`。

根据系统设置 `system_info.distro`（rhel / ubuntu / debian 等）。

详细配置参数见 `references/cloud_init_config.md`。

#### 4.3 验证服务

确认四个服务均为 `enabled` + `active`：
```bash
systemctl status cloud-init-local cloud-init cloud-config cloud-final
```

#### 4.4 安装根分区自动扩盘工具

| 系统 | 命令 |
|------|------|
| CentOS/RedHat | `yum install cloud-utils-growpart` |
| Debian | `apt-get install cloud-initramfs-growroot` |
| UEFI 系统额外 | `gdisk`（必需） |

---

### Step 5: Boot Drivers — 引导硬件设备驱动

确保初始 ramdisk 包含必要的存储/RAID 驱动，防止启动时找不到磁盘。

**RHEL/CentOS/Oracle Linux** — 编辑 `/etc/dracut.conf`：
```
add_drivers+=" ahci megaraid_sas mpt3sas ... "
```
然后执行：`dracut -f`

**Debian/Ubuntu** — 编辑 `/etc/initramfs-tools/modules` 添加所需驱动名，然后：
```bash
update-initramfs -u
```

---

### Step 6: Model-Specific Drivers — 按机型安装驱动

先查 `references/driver_mapping.md` 确定目标机型需要哪些驱动。所有包已预放在
`/tmp/bms-packages/`（Pre-Flight 阶段传入），按需安装：

#### bms-network-config（适配 s1/s3/s4/d1/d2/m2/m3/io1/io2/h1/h2/hc2/ki1）
```bash
cd /tmp/bms-packages
rpm -ivh bms-network-config-*.rpm      # RHEL 系
dpkg -i bms-network-config_*.deb        # Debian/Ubuntu
systemctl enable bms-network-config
```

#### SDI 卡驱动（s3/s4/m2/m3/h2/hc2）
```bash
cd /tmp/bms-packages
rpm -ivh kmod-scsi_ep_front-*.rpm
```

#### Hi1822 网卡驱动（c6/s6/d6/io6/ks1/kd1/kh1）
```bash
cd /tmp/bms-packages
rpm -ivh kmod-hinic-*.rpm
modprobe hinic
```

#### IB 驱动（h1/h2/kh1）
```bash
cd /tmp/bms-packages
tar xf MLNX_OFED_LINUX-*.tgz
cd MLNX_OFED_LINUX-*
./mlnxofedinstall
```

#### IB MLX5 驱动（kat2 / ARM openEuler）
```bash
cd /tmp/bms-packages
rpm -ivh IB_NIC-CX4Lx_CX5_CX6-*-mlx5_core-*.aarch64.rpm
```

#### ComputingComponentiDriver（kat2 / ARM 鲲鹏板载驱动）
```bash
cd /tmp/bms-packages
# 解压 zip 包挂载 ISO
unzip ComputingComponentiDriver-openEuler*-Driver-ARM_*.zip
mkdir -p /mnt/onboard_driver
mount onboard_driver_openEuler*.iso /mnt/onboard_driver
# 进入 ISO 挂载点按需安装板载驱动
ls /mnt/onboard_driver/
# 安装完成后卸载
umount /mnt/onboard_driver
```

#### FusionServer / TaiShan 服务器板载驱动
- **i40e** — 板载网卡
- **mpt3sas** — SAS 控制器
- **megaraid_sas** — RAID 卡
（通常随内核或 dracut 加载，如需单独安装从 `/tmp/bms-packages/` 取）

#### UltraPath 多路径软件
参考《OceanStor UltraPath for Linux xxx 用户指南》，安装包从 `/tmp/bms-packages/` 取。

#### vroce 驱动（ac8/ki2/kc2）
```bash
cd /tmp/bms-packages
# 1. 先装 OFED 驱动（版本 5.8-3.0.7.0-LTS）
tar xf MLNX_OFED_LINUX-5.8-*.tgz
cd MLNX_OFED_LINUX-5.8-*
./mlnxofedinstall
cd /tmp/bms-packages
# 2. 再装 vroce 前端驱动
rpm -ivh hiroce3-*.rpm hinic3-*.rpm
```

#### HPD 热插拔驱动（ac8/ki2/kc2）
```bash
cd /tmp/bms-packages
rpm -ivh hotplug-daemon-*.rpm
systemctl enable hpd
systemctl start hpd
```

#### network 服务（HCE 2.0 等新系统）
```bash
yum install network-scripts
```

---

### Step 7: Password Reset Plugin — 一键式重置密码插件

```bash
cd /tmp/bms-packages
unzip -o -d /home/linux/test CloudResetPwdAgent.zip
cd /home/linux/test
sh setup.sh
```

---

### Step 8: Security Config — 安全性配置

- **SSH**：`PasswordAuthentication yes`、`PermitRootLogin yes`
- **网络脚本权限**：`chmod 700 -R /opt/huawei/`
- 修改 motd / history / ntp / udev / Selinux
- 卸载 denyhosts（如存在）
- 修复主机名自动更新问题
- 安装运维工具：gcc、strace、tcpdump 等

---

### Step 9: Serial Console — 配置裸金属服务器远程登录

**x86（CentOS/RedHat）**：
```bash
# 编辑 /etc/default/grub，在 GRUB_CMDLINE_LINUX 追加：
# consoleblank=600 console=tty0 console=ttyS0,115200n8

grub2-mkconfig -o /boot/grub2/grub.cfg
systemctl enable serial-getty@ttyS0
```

**ARM（CentOS）**：
```bash
# 编辑 /etc/default/grub，在 GRUB_CMDLINE_LINUX 追加：
# consoleblank=600 console=tty0 console=ttyAMA0,115200

grub2-mkconfig -o /boot/efi/EFI/centos/grub.cfg
systemctl enable serial-getty@ttyAMA0
```

---

### Step 10: Cleanup — 清理收尾

配置完成后，交付镜像前必须清理：

- 删除所有上传到 VM 的安装包
- 清空日志：`rm -f /var/log/wtmp /var/log/btmp`
- 移除网络配置残留
- 清除命令历史：`history -c`

---

## 快速决策：按机型选驱动

无需通读全文，先查下表快速定位需要安装的驱动和参考项：

| 机型 | 启动 | 服务器驱动 | SDI | Hi1822 | IB | OFED | vroce | HPD | network-config |
|------|------|-----------|-----|--------|----|------|-------|-----|----------------|
| s3/s4/m2/m3/hc2 | BIOS | FusionServer | ✓ | - | - | - | - | - | ✓ |
| s1/d1/d2/io1/io2 | BIOS | FusionServer | - | - | - | - | - | - | ✓ |
| h1 | BIOS | FusionServer | - | - | ✓ | - | - | - | ✓ |
| h2 | BIOS | FusionServer | ✓ | - | ✓ | - | - | - | ✓ |
| c6/s6/d6/io6 | UEFI | FusionServer | - | ✓ | - | - | - | - | - |
| ks1/kd1 | UEFI | - | - | ✓ | - | - | - | - | ✓ |
| kh1 | UEFI | - | - | ✓ | ✓ | - | - | - | ✓ |
| kat2 | UEFI | ComputingComponentiDriver | - | ✓ | ✓(MLX5) | - | - | - | ✓ |
| ac8/ki2/kc2 | UEFI | - | - | - | - | ✓ | ✓ | ✓ | - |

完整驱动对应表见 `references/driver_mapping.md`。

---

## Troubleshooting

常见问题参考 `references/faq.md`：

- bond0 VLAN 子接口源 MAC 问题（RHEL/CentOS 7.x 内核缺陷）
- CPU 频率调节模式配置
- cloud-init-local 启动失败（libselinux 版本）
- 软件完整性校验（sha256sum）
- 设备状态检查
- HPD 服务管理

---

## References

- `references/os_support.md` — x86/ARM 支持的操作系统与内核版本
- `references/driver_mapping.md` — 完整的机型-驱动对应表
- `references/software_checklist.md` — 所有需要的软件与工具清单
- `references/partition_guide.md` — BIOS/UEFI 分区方案详解
- `references/cloud_init_config.md` — Cloud-Init 安装与配置详细步骤
- `references/faq.md` — 常见问题与解决方案

需要详细参数时加载对应参考文件，或在 references 中搜索关键词。
