# Cloud-Init 配置指南

## 安装方式

### RedHat / CentOS / Oracle Linux / Ubuntu / Debian

优先使用系统包管理器：

```bash
# CentOS/RedHat/Oracle Linux
yum install cloud-init

# Ubuntu/Debian
apt-get install cloud-init
```

备选方案：
- 使用 pip 安装源码包（如 cloud-init 0.7.9）
- 源码编译安装

### openEuler / Huawei Cloud EulerOS 2.0

```bash
# 配置 yum 源后执行
yum install cloud-init
```

## 配置文件: /etc/cloud/cloud.cfg

必须配置以下参数：

```yaml
disable_root: false
ssh_pwauth: true
preserve_hostname: false

datasource_list: [OpenStack]
# 不在 datasource_list 中保留 ConfigDrive

# 添加以下行到 cloud_init_modules 下
# - power-state-change

# system_info 部分根据 OS 类型配置 distro
# RedHat/CentOS: distro: rhel
# Ubuntu: distro: ubuntu
# Debian: distro: debian
```

## 服务状态检查

配置完成后，确认以下四个服务均为 **enabled** 且 **active**：

```bash
systemctl status cloud-init-local
systemctl status cloud-init
systemctl status cloud-config
systemctl status cloud-final
```

## 常见问题

### cloud-init-local 启动失败

- 原因：libselinux 版本过低
- 解决：升级 libselinux 到 2.5.7 及以上版本

## 根分区自动扩盘

CentOS/RedHat:
```bash
yum install cloud-utils-growpart
```

Debian:
```bash
apt-get install cloud-initramfs-growroot
```

UEFI 启动还需额外安装：
```bash
yum install gdisk   # CentOS/RedHat
apt-get install gdisk   # Debian/Ubuntu
```
