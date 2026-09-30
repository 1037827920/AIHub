# crash-python / pycrash

适用：特定环境已经使用 crash-python，需要其 Python 语义回溯/子系统 helpers。P3 工具，不替代默认 crash/drgn 路线。

```bash
pycrash --help
pycrash /path/to/vmlinux /path/to/vmcore
pycrash -r /path/to/extracted-root /path/to/vmlinux /path/to/vmcore
pycrash -b /path/to/kernel-build /path/to/vmlinux /path/to/vmcore
```

前提：完整内核与模块 ELF/debuginfo、目标 vmcore，以及兼容运行环境。-r 是展开包的根路径，-b 指向构建目录；按本地版本验证。进入会话后 `pyhelp` 发现扩展，`bt` 检查回溯。与 PyKdump 不是同一项目，名称相似不能混用 API 或加载方式。

源码行与参数显示可能含 optimized out，说明不可恢复而不是数值为零。读取错误来自缺页/类型/地址等多种原因。老版本支持范围可能与当前内核差距较大，先验证一组已知符号/栈，再使用高级 helpers；不强制降级其他工具来迁就它。

来源：[crash-python Quick Start](https://crash-python.readthedocs.io/en/latest/)、[命令文档](https://crash-python.readthedocs.io/en/latest/user_guide.html)。
