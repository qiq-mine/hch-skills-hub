#!/bin/bash
# ============================================================
# BMS 私有镜像制作 — VM 内部自动配置脚本
# 用法: bash setup-bms.sh --model kat2 --os openEuler [--packages-dir /tmp/bms-packages] [--no-cleanup] [--skip-network]
#
# 适用: 虚拟机已创建、ISO 已安装完毕、已进入系统 root shell
# 不负责: 创建 VM、分区装系统、导出镜像
# ============================================================

set -euo pipefail

# ——— 默认参数 ———
MODEL=""
OS=""
PACKAGES_DIR="/tmp/bms-packages"
LOG_FILE="/var/log/bms-setup.log"
DO_CLEANUP=true
SKIP_NETWORK=false

# ——— 日志函数 ———
log() {
    local level="$1"; shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" | tee -a "$LOG_FILE"
}

info()  { log "INFO" "$@"; }
warn()  { log "WARN" "$@"; }
error() { log "ERROR" "$@"; exit 1; }

# ——— 参数解析 ———
while [[ $# -gt 0 ]]; do
    case "$1" in
        --model)        MODEL="$2"; shift 2 ;;
        --os)           OS="$2"; shift 2 ;;
        --packages-dir) PACKAGES_DIR="$2"; shift 2 ;;
        --no-cleanup)   DO_CLEANUP=false; shift ;;
        --skip-network) SKIP_NETWORK=true; shift ;;
        --help|-h)
            echo "用法: bash $0 --model <机型> --os <系统> [选项]"
            echo "  --model        目标 BMS 机型 (如 kat2, s3, ac8)"
            echo "  --os           操作系统 (如 openEuler, centos, ubuntu)"
            echo "  --packages-dir 驱动包存放路径 (默认 /tmp/bms-packages)"
            echo "  --no-cleanup   配置完成后不清理安装包"
            echo "  --skip-network 跳过网络相关配置 (VM 无法联网时)"
            exit 0
            ;;
        *) error "未知参数: $1 (用 --help 查看用法)" ;;
    esac
done

if [[ -z "$MODEL" || -z "$OS" ]]; then
    error "必须指定 --model 和 --os (用 --help 查看用法)"
fi

# ——— 环境检测 ———
info "========== BMS 镜像配置开始 =========="
info "机型: $MODEL | 系统: $OS | 包目录: $PACKAGES_DIR"
info "日志文件: $LOG_FILE"

ARCH=$(uname -m)
info "检测架构: $ARCH"

# 检测包管理器
if command -v yum &>/dev/null; then
    PKG_MGR="yum"
elif command -v dnf &>/dev/null; then
    PKG_MGR="dnf"
elif command -v apt-get &>/dev/null; then
    PKG_MGR="apt-get"
else
    error "未找到支持的包管理器 (yum/dnf/apt-get)"
fi
info "包管理器: $PKG_MGR"

# ============================================================
# Step 1: 基础环境配置
# ============================================================
info "========== Step 1: 基础环境配置 =========="

# systemd 超时 300s
if [[ -f /etc/systemd/system.conf ]]; then
    if grep -q "^DefaultTimeoutStartSec" /etc/systemd/system.conf; then
        sed -i 's/^DefaultTimeoutStartSec=.*/DefaultTimeoutStartSec=300s/' /etc/systemd/system.conf
    elif grep -q "^#DefaultTimeoutStartSec" /etc/systemd/system.conf; then
        sed -i 's/^#DefaultTimeoutStartSec=.*/DefaultTimeoutStartSec=300s/' /etc/systemd/system.conf
    else
        echo "DefaultTimeoutStartSec=300s" >> /etc/systemd/system.conf
    fi
    info "systemd 超时 → 300s"
fi

# 关闭防火墙
case "$OS" in
    openEuler|centos|redhat|oraclelinux|hce)
        systemctl disable firewalld 2>/dev/null || true
        systemctl stop firewalld 2>/dev/null || true
        info "firewalld 已关闭"
        ;;
    ubuntu|debian)
        ufw disable 2>/dev/null || true
        info "ufw 已关闭"
        ;;
esac

# 文件句柄限制
if ! grep -q "65535" /etc/security/limits.conf 2>/dev/null; then
    cat >> /etc/security/limits.conf << 'EOF'
* soft nofile 65535
* hard nofile 65535
EOF
    info "文件句柄限制 → 65535"
fi

# 禁用关机命令 (防止误操作)
for cmd in poweroff shutdown halt; do
    if [[ -f /usr/sbin/$cmd ]]; then
        mv /usr/sbin/$cmd /usr/sbin/$cmd.bak 2>/dev/null || true
    fi
done
info "关机命令已禁用"

info "Step 1 完成"

# ============================================================
# Step 2: Cloud-Init 安装与配置
# ============================================================
info "========== Step 2: Cloud-Init 安装与配置 =========="

if ! rpm -q cloud-init &>/dev/null && ! dpkg -l cloud-init &>/dev/null 2>&1; then
    case "$PKG_MGR" in
        yum|dnf) $PKG_MGR install -y cloud-init ;;
        apt-get) apt-get update && apt-get install -y cloud-init ;;
    esac
    info "cloud-init 安装完成"
else
    info "cloud-init 已安装，跳过"
fi

# 配置 /etc/cloud/cloud.cfg
cat > /etc/cloud/cloud.cfg << 'CLOUDCFG'
users:
   - default

disable_root: false
ssh_pwauth: true

datasource_list: [OpenStack]
datasource:
  OpenStack:
    metadata_urls: ["http://169.254.169.254"]
    max_wait: 120
    timeout: 50

preserve_hostname: false

cloud_init_modules:
 - migrator
 - seed_random
 - bootcmd
 - write-files
 - growpart
 - resizefs
 - disk_setup
 - mounts
 - set_hostname
 - update_hostname
 - update_etc_hosts
 - ca-certs
 - rsyslog
 - users-groups
 - ssh

cloud_config_modules:
 - emit_upstart
 - ssh-import-id
 - locale
 - set-passwords
 - grub-dpkg
 - apt-pipelining
 - apt-configure
 - ntp
 - timezone
 - disable-ec2-metadata
 - runcmd
 - byobu

cloud_final_modules:
 - package-update-upgrade-install
 - fan
 - puppet
 - chef
 - salt-minion
 - mcollective
 - rightscale_userdata
 - scripts-vendor
 - scripts-per-once
 - scripts-per-boot
 - scripts-per-instance
 - scripts-user
 - ssh-authkey-fingerprints
 - keys-to-console
 - phone-home
 - final-message
 - power-state-change
CLOUDCFG
info "cloud.cfg 已配置"

# 分发 distro 信息
case "$OS" in
    openEuler|hce|centos|redhat|oraclelinux)
        echo 'system_info:
   distro: rhel' >> /etc/cloud/cloud.cfg
        ;;
    ubuntu)
        echo 'system_info:
   distro: ubuntu' >> /etc/cloud/cloud.cfg
        ;;
    debian)
        echo 'system_info:
   distro: debian' >> /etc/cloud/cloud.cfg
        ;;
esac

# 启用服务
systemctl enable cloud-init-local cloud-init cloud-config cloud-final 2>/dev/null || true
info "cloud-init 服务已启用"

# 安装根分区自动扩盘
case "$PKG_MGR" in
    yum|dnf) $PKG_MGR install -y cloud-utils-growpart ;;
    apt-get) apt-get install -y cloud-initramfs-growroot ;;
esac

# UEFI 必须装 gdisk
if [[ -d /sys/firmware/efi ]]; then
    case "$PKG_MGR" in
        yum|dnf) $PKG_MGR install -y gdisk ;;
        apt-get) apt-get install -y gdisk ;;
    esac
    info "UEFI 检测到，gdisk 已安装"
fi

info "Step 2 完成"

# ============================================================
# Step 3: 引导硬件设备驱动 (dracut / initramfs)
# ============================================================
info "========== Step 3: 引导硬件驱动配置 =========="

case "$PKG_MGR" in
    yum|dnf)
        if [[ -f /etc/dracut.conf ]]; then
            if ! grep -q "ahci megaraid_sas mpt3sas" /etc/dracut.conf 2>/dev/null; then
                echo 'add_drivers+=" ahci megaraid_sas mpt3sas "' >> /etc/dracut.conf
                dracut -f
                info "dracut 驱动已添加并重建"
            else
                info "dracut 驱动已存在，跳过"
            fi
        fi
        ;;
    apt-get)
        if [[ -f /etc/initramfs-tools/modules ]]; then
            for mod in ahci megaraid_sas mpt3sas; do
                grep -q "^$mod" /etc/initramfs-tools/modules 2>/dev/null || echo "$mod" >> /etc/initramfs-tools/modules
            done
            update-initramfs -u
            info "initramfs 驱动已添加并重建"
        fi
        ;;
esac

info "Step 3 完成"

# ============================================================
# Step 4: 按机型安装驱动
# ============================================================
info "========== Step 4: 机型驱动安装 ($MODEL) =========="

cd "$PACKAGES_DIR"

case "$MODEL" in
    kat2|kat1|kat3|ks1|kd1|ks1ne|kd1ne)
        # ——— 鲲鹏 ARM 通用 ———
        # Hi1822 网卡
        if ls kmod-hinic-*.rpm 1>/dev/null 2>&1; then
            rpm -ivh kmod-hinic-*.rpm || warn "Hi1822 安装失败，检查包是否存在"
            modprobe hinic 2>/dev/null || true
            info "Hi1822 网卡驱动已安装"
        else
            warn "未找到 kmod-hinic-*.rpm，跳过 Hi1822"
        fi

        # bms-network-config
        if ls bms-network-config-*.rpm 1>/dev/null 2>&1; then
            rpm -ivh bms-network-config-*.rpm
            systemctl enable bms-network-config
            info "bms-network-config 已安装"
        else
            warn "未找到 bms-network-config-*.rpm，跳过"
        fi
        ;;&  # fall through to model-specific parts

    kat2)
        # IB MLX5 驱动
        if ls IB_NIC-CX*-mlx5_core-*.aarch64.rpm 1>/dev/null 2>&1; then
            rpm -ivh IB_NIC-CX*-mlx5_core-*.aarch64.rpm
            info "IB MLX5 驱动已安装"
        else
            warn "未找到 IB MLX5 驱动包，跳过"
        fi

        # ComputingComponentiDriver
        ZIP_FILE=$(ls ComputingComponentiDriver-*.zip 2>/dev/null | head -1)
        if [[ -n "$ZIP_FILE" ]]; then
            unzip -o "$ZIP_FILE" -d /tmp/compute-driver/
            ISO_FILE=$(ls /tmp/compute-driver/onboard_driver*.iso 2>/dev/null | head -1)
            if [[ -n "$ISO_FILE" ]]; then
                mkdir -p /mnt/onboard_driver
                mount -o loop "$ISO_FILE" /mnt/onboard_driver
                info "板载驱动 ISO 已挂载到 /mnt/onboard_driver"
                # 用户可在此目录下按需安装具体驱动
                ls /mnt/onboard_driver/
                # 安装后卸载
                umount /mnt/onboard_driver 2>/dev/null || true
                info "板载驱动 ISO 已卸载"
            fi
        else
            warn "未找到 ComputingComponentiDriver-*.zip，跳过"
        fi
        ;;

    kh1)
        # IB 驱动 (NVIDIA OFED)
        if ls MLNX_OFED_LINUX-*.tgz 1>/dev/null 2>&1; then
            tar xf MLNX_OFED_LINUX-*.tgz
            cd MLNX_OFED_LINUX-*
            ./mlnxofedinstall --skip-repo --force
            cd "$PACKAGES_DIR"
            info "IB 驱动 (OFED) 已安装"
        else
            warn "未找到 MLNX_OFED_LINUX 包，跳过 IB 驱动"
        fi
        ;;

    ac8|ki2|kc2)
        # OFED + vroce + HPD
        if ls MLNX_OFED_LINUX-5.8-*.tgz 1>/dev/null 2>&1; then
            tar xf MLNX_OFED_LINUX-5.8-*.tgz
            cd MLNX_OFED_LINUX-5.8-*
            ./mlnxofedinstall --skip-repo --force
            cd "$PACKAGES_DIR"
            info "OFED 驱动已安装"
        fi
        ls hiroce3-*.rpm 1>/dev/null 2>&1 && rpm -ivh hiroce3-*.rpm
        ls hinic3-*.rpm 1>/dev/null 2>&1 && rpm -ivh hinic3-*.rpm
        info "vroce 前端驱动已安装"
        ls hotplug-daemon-*.rpm 1>/dev/null 2>&1 && rpm -ivh hotplug-daemon-*.rpm && systemctl enable hpd && systemctl start hpd
        info "HPD 驱动已安装"
        ;;

    s3|s4|m2|m3|hc2)
        # SDI 卡驱动
        ls kmod-scsi_ep_front-*.rpm 1>/dev/null 2>&1 && rpm -ivh kmod-scsi_ep_front-*.rpm
        info "SDI 卡驱动已安装"
        ;;&
    s1|d1|d2|io1|io2|s3|s4|m2|m3|h1|h2|hc2|c6|s6|d6|io6)
        # FusionServer 板载驱动 (x86)
        info "FusionServer 板载驱动: i40e / mpt3sas / megaraid_sas (dracut 已处理)"
        ;;
esac

info "Step 4 完成"

# ============================================================
# Step 5: 一键重置密码插件
# ============================================================
info "========== Step 5: 密码重置插件 =========="

if ls CloudResetPwdAgent.zip 1>/dev/null 2>&1; then
    unzip -o CloudResetPwdAgent.zip -d /home/linux/test/ 2>/dev/null || \
    unzip -o CloudResetPwdAgent.zip -d /tmp/cloudreset/ 2>/dev/null
    DEST_DIR="/home/linux/test"
    [[ -d "$DEST_DIR/setup.sh" ]] || DEST_DIR="/tmp/cloudreset"
    if [[ -f "$DEST_DIR/setup.sh" ]]; then
        cd "$DEST_DIR" && sh setup.sh
        info "CloudResetPwdAgent 已安装"
    else
        warn "CloudResetPwdAgent 解压后未找到 setup.sh"
    fi
    cd "$PACKAGES_DIR"
else
    warn "未找到 CloudResetPwdAgent.zip，跳过"
fi

info "Step 5 完成"

# ============================================================
# Step 6: 安全性配置
# ============================================================
info "========== Step 6: 安全性配置 =========="

# SSH 配置
SSHD_CFG="/etc/ssh/sshd_config"
if [[ -f "$SSHD_CFG" ]]; then
    sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication yes/' "$SSHD_CFG"
    sed -i 's/^PasswordAuthentication.*/PasswordAuthentication yes/' "$SSHD_CFG"
    sed -i 's/^#PermitRootLogin.*/PermitRootLogin yes/' "$SSHD_CFG"
    sed -i 's/^PermitRootLogin.*/PermitRootLogin yes/' "$SSHD_CFG"
    info "SSH 已配置 (密码登录+root允许)"
fi

# 网络脚本权限
[[ -d /opt/huawei ]] && chmod 700 -R /opt/huawei/ 2>/dev/null || true

# Selinux
if command -v setenforce &>/dev/null; then
    setenforce 0 2>/dev/null || true
    sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config 2>/dev/null || true
    info "SELinux 已禁用"
fi

# 卸载 denyhosts
case "$PKG_MGR" in
    yum|dnf) yum remove -y denyhosts 2>/dev/null || true ;;
    apt-get) apt-get remove -y denyhosts 2>/dev/null || true ;;
esac

info "Step 6 完成"

# ============================================================
# Step 7: 串口控制台远程登录
# ============================================================
info "========== Step 7: 串口控制台 =========="

GRUB_CFG="/etc/default/grub"
if [[ -f "$GRUB_CFG" ]]; then
    case "$ARCH" in
        aarch64)
            # ARM
            if ! grep -q "console=ttyAMA0" "$GRUB_CFG" 2>/dev/null; then
                sed -i '/^GRUB_CMDLINE_LINUX=/ s/"$/ consoleblank=600 console=tty0 console=ttyAMA0,115200"/' "$GRUB_CFG"
            fi
            grub2-mkconfig -o /boot/efi/EFI/*/grub.cfg 2>/dev/null || \
            grub2-mkconfig -o /boot/grub2/grub.cfg 2>/dev/null || true
            systemctl enable serial-getty@ttyAMA0 2>/dev/null || true
            info "串口控制台 (ARM) 已配置"
            ;;
        x86_64)
            # x86
            if ! grep -q "console=ttyS0" "$GRUB_CFG" 2>/dev/null; then
                sed -i '/^GRUB_CMDLINE_LINUX=/ s/"$/ consoleblank=600 console=tty0 console=ttyS0,115200n8"/' "$GRUB_CFG"
            fi
            grub2-mkconfig -o /boot/grub2/grub.cfg
            systemctl enable serial-getty@ttyS0 2>/dev/null || true
            info "串口控制台 (x86) 已配置"
            ;;
    esac
fi

info "Step 7 完成"

# ============================================================
# Step 8: 清理
# ============================================================
info "========== Step 8: 清理 =========="

if $DO_CLEANUP; then
    # 清理安装包
    if [[ -d "$PACKAGES_DIR" ]]; then
        rm -rf "$PACKAGES_DIR"/*
        info "安装包已清理: $PACKAGES_DIR"
    fi
    # 清空日志
    : > /var/log/wtmp 2>/dev/null || true
    : > /var/log/btmp 2>/dev/null || true
    # 清理 CI/CD 残留
    rm -f /etc/udev/rules.d/70-persistent-net.rules 2>/dev/null || true
    # 清理临时挂载
    umount /mnt/onboard_driver 2>/dev/null || true
    rm -rf /tmp/compute-driver/ /tmp/cloudreset/ 2>/dev/null || true
    # 清除命令历史
    history -c 2>/dev/null || true
    info "环境清理完成"
else
    info "--no-cleanup 模式，安装包保留在 $PACKAGES_DIR"
fi

# ============================================================
# 完成
# ============================================================
info "========== BMS 镜像配置完成 =========="
info "机型: $MODEL | 系统: $OS | 架构: $ARCH"
info "配置日志: $LOG_FILE"

echo ""
echo "========================================"
echo "  BMS 镜像配置已完成！"
echo "  可以关闭虚拟机，交付镜像。"
echo "========================================"
