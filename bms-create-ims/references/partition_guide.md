# 分区方案指南

## 核心原则

- 使用 **MBR 分区表**
- 主分区数量 **≤ 3**
- **根分区必须为最后一个主分区**（用于自动扩盘）

## BIOS 启动分区方案

| 方案 | 分区结构 |
|------|----------|
| 方案一 | /boot + swap + / (根分区) |
| 方案二 | swap + / (根分区) |
| 方案三 | / (根分区) |
| 方案四 | 扩展分区 + LVM |

## UEFI 启动分区方案

| 方案 | 分区结构 |
|------|----------|
| 方案一 | /boot/efi + swap + / (根分区) |
| 方案二 | /boot/efi + / (根分区) |
| 方案三 | /boot/efi + 扩展分区(LVM) + / (根分区) |

## UEFI 启动引导文件修改

安装完成后、重启前，必须修改引导文件：

**ARM 架构**:
```bash
cp /boot/efi/EFI/$os_version/grubaa64.efi /boot/efi/EFI/BOOT/BOOTAA64.EFI
```

**x86 架构**:
```bash
cp /boot/efi/EFI/$os_version/grubx64.efi /boot/efi/EFI/BOOT/BOOTX64.EFI
```

其中 `$os_version` 根据实际系统替换（如 centos、redhat 等）。

## 特殊系统说明

### Ubuntu 18.04 / Debian 8.6
- 使用 server 版 ISO（非 live-server）
- 手动分区，选择 "Primary"
- 确保根分区为最后一个分区

### 磁盘大小建议
- 磁盘建议 **6G 以内**
- 格式：raw 或 qcow2
- 内存 ≥ 4096 MiB
- CPU ≥ 4 核
