# crash 扩展与模块符号

适用：已有 PyKdump、文件系统、设备或厂商专有扩展；首版不实现新 .so。前提：扩展来源可信，与 crash ABI、Python/其他运行库、目标架构兼容。

```text
help extend
extend
extend /path/to/trusted-extension.so
help
mod
mod -s module_name /path/to/module_name.ko
```

`extend` 查看扩展，带路径加载扩展代码；随后查新增命令帮助。加载 .so 是在分析主机执行代码，不是只读解析一个普通数据文件。仅在用户任务确需且已有授权时加载已知扩展，不自行下载并执行未知二进制。加载失败记录链接/ABI 诊断，不盲目换版本反复尝试。

`mod` 显示 dump 中模块；`mod -s` 加载某模块的符号，以内存中的模块位置进行重定位。.ko 和独立 debuginfo 必须对应崩溃时的模块构建；加载同名模块不证明匹配。`extend` 与 `mod -s` 是不同机制，前者添调试器命令，后者添目标符号。

PyKdump 见 [专门资料](../automation/pykdump.md)。TencentOS、XFS、virtio 等专用命令仅在实际扩展已存在时使用；不要把设想中的命令写成可执行内置命令。

来源：[extend](https://crash-utility.github.io/help_pages/extend.html)、[mod](https://crash-utility.github.io/help_pages/mod.html)、[扩展开发入口](https://crash-utility.github.io/extensions.html)。
