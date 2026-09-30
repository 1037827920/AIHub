# 文件系统、打开文件与块设备

适用：VFS/XFS/ext4/NFS 等路径阻塞、写回、块 I/O hang。前提：相关模块符号匹配；只有日志时先定位路径，不能宣布具体 inode/request 损坏。

```text
mount
files 1234
files -c 1234
dev
bt 1234
struct file ffff888012340000
struct inode ffff888012350000
mod
```

`mount` 提供挂载及超级块线索；`files PID` 将 fd 与 file/dentry/inode、路径关联；`files -c PID` 看任务当前目录/根相关信息。路径解析可能受命名空间、已删除 dentry 和缓存状态影响。`dev` 给出设备注册信息，本身不等于设备健康检查。

从栈区分用户读写、页回写、日志事务、块层、设备驱动、RPC 等等待位置。取得实际 file/inode/super_block/request 等对象后按匹配类型检查；bdev、request_queue、bio、blk-mq 布局跨版本变化明显。不能把新 blk-mq 队列套到旧请求链表。

建立任务 → 等待对象 → 下层工作者/设备的关系，比较多个等待任务是否共享同一 inode、事务、设备或远端 RPC。文件系统名称出现在栈中仅说明路径经过该子系统。若需要 XFS/厂商扩展，先读 [extensions](extensions.md)；加载扩展不会自动补齐缺失模块 debuginfo。

误判：文件句柄数量多不是泄漏证据；mount 不能完整描述所有 namespace 的所有视角；I/O 堵塞不一定是 guest 块驱动故障，还可能是宿主存储或远端不可达。缓存页过滤会破坏内容与路径验证，保留限制。

来源：[files](https://crash-utility.github.io/help_pages/files.html)、[mount](https://crash-utility.github.io/help_pages/mount.html)、[dev](https://crash-utility.github.io/help_pages/dev.html)、[mod](https://crash-utility.github.io/help_pages/mod.html)。
