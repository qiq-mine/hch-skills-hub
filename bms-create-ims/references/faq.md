# 常见问题 FAQ

## 1. bond0 的 vlan 子接口源 mac 问题

- **影响系统**: RedHat/CentOS 7.x
- **原因**: 内核缺陷
- **解决**: 需打内核补丁

## 2. 设置 CPU 频率调节模式

RedHat/CentOS:
```bash
CPUPOWER_START_OPTS="frequency-set -g performance"
```

Debian:
```bash
GOVERNOR="performance"
```

## 3. cloud-init-local 启动失败

- 升级 libselinux 到 2.5.7 及以上版本

## 4. 软件完整性校验

```bash
sha256sum {软件包}
```

## 5. 检查 device 是否正常运行

```bash
cat /etc/ascend_install.info
cd /usr/local/Ascend/driver/tools/
./upgrade-tool --device_index -1 --system_version
```

## 6. HPD 常用操作

| 操作 | 命令 |
|------|------|
| 查看状态 | `service hpd status` |
| 日志路径 | `/var/log/hpd/` |
| 启动 | `service hpd start` |
| 开机自启 | `systemctl enable hpd` |

## 7. 镜像格式转换

```bash
chmod +x qemu-img-hw
./qemu-img-hw convert -p -O zvhd2 input.qcow2 output.zvhd2
```

查询虚拟磁盘大小：
```bash
./qemu-img-hw info image.qcow2
```
