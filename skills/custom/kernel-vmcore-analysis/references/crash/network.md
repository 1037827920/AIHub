# 网络、socket 与协议路径

适用：网络相关 panic、socket 阻塞、softirq 堵塞与 NFS/RPC 网络侧调查。前提：网络结构/模块 debuginfo 匹配；net 命令的功能依版本，不能视为完整协议解析器。

```text
net
net -s 1234
net -S 1234
files 1234
bt 1234
whatis struct sock
struct sock ffff888012340000
```

`net` 列出识别到的网络设备信息；`-s PID` 展示任务的 socket，`-S PID` 提供结构展开。先查 `help net` 确认版本；记录 fd、socket/sock 地址和地址族。fd 与 socket 要借 file 私有数据和正确类型关联，不把所有 file 都当 socket。

从栈判断是在协议收发、内存分配、驱动、NAPI、softirq 还是等待数据。检查同一 net namespace、设备和 socket 的队列、状态及错误字段。TCP 状态与队列值需要当前类型/常量解释；不能依据主机当前 `/proc/net` 替代 dump。skb 中 head/data/tail/end 的表示随布局变化，读取 packet 前核对边界与线性/分片状态。

队列长度大可能是背压、收包风暴、消费者停滞或正常 burst，需结合 CPU 栈和 IRQ/softirq 证据。等待 socket 数据本身不能证明远端故障；guest 单快照通常不能验证宿主网络或外部连通性。

PyKdump 的 xportshow 可用于已有兼容环境，见 [PyKdump](../automation/pykdump.md)；新批量关联优先 drgn。禁止将 dump 内真实流量或凭证主动发送到外部服务。

来源：[net](https://crash-utility.github.io/help_pages/net.html)、[files](https://crash-utility.github.io/help_pages/files.html)、[Linux 网络文档](https://docs.kernel.org/networking/index.html)。
