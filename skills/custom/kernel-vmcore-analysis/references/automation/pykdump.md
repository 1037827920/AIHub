# PyKdump：已有 crash + Python 环境

适用：现有环境已部署兼容 PyKdump，需复用 hanginfo、taskinfo、xportshow 等分析工具。新批量分析优先 drgn，不自动安装扩展。

```text
extend /path/to/trusted/mpykdump.so
help
```

前提：mpykdump.so 的 crash ABI、Python 运行库与目标架构匹配，扩展来源可信且加载已授权。加载后按实际帮助发现 pycrash/Python 入口和工具，不假定所有版本都有同一命令/参数。

常用分析脚本名称包括 crashinfo、hanginfo、taskinfo、nfsshow、xportshow、scsishow、dmshow、pstree；它们属于工具包，不是 crash 内置命令。按对应版本的文档和脚本 usage 调用，先确认部署路径与注册方式。任务/锁/网络摘要要保留具体对象地址，并回到 crash 基础命令验证关键关系。

PyKdump API 能操作结构、符号和容器，但同样受类型匹配、过滤页和链表损坏影响。脚本没有输出不能证明没有故障；输出聚类也不是根因证明。扩展是在分析主机执行本地代码，不能对未知 .so 仅以“读取 dump”为由加载。

来源：[PyKdump 文档](https://pykdump.readthedocs.io/en/latest/)、[crash extend](https://crash-utility.github.io/help_pages/extend.html)。
