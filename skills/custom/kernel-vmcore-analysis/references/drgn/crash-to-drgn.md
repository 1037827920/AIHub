# drgn-crash 与 crash → Python

适用：熟悉 crash 命令，希望获得 Python 实现或进入编程分析。前提：本地安装了 drgn-crash，命令兼容实现可用；不是所有 crash 参数、扩展和输出都完全一致。

```bash
drgn-crash /path/to/vmlinux /path/to/vmcore
```

```text
help
help bt
bt 1234
bt 1234 --drgn
ps --drgn
drgn
```

`--drgn` 是兼容界面内命令的选项，用来打印等价 drgn 代码，不是 `drgn-crash --drgn` 的通用启动参数。查看当前命令帮助，复制代码前理解其选择上下文、参数和类型依赖。`drgn` 无参数进入常规交互模式，也可带表达式执行 Python。

迁移思路：先确定 crash 输出里关注的 PID/CPU/地址 → 在支持的命令后加 `--drgn` → 验证返回的对象/字段 → 加显式导入与 prog 参数 → 扩展筛选、关联和错误处理。`bt PID` 对应任务的 stack_trace；任务枚举对应 pid helpers；结构读取对应 prog/类型对象。不可把 crash 命令字符串直接当 Python API。

导出的例子可依赖 CLI 默认 helper namespace；独立脚本仍需初始化 Program、显式加载 dump/符号，见 [overview](overview.md)。如果兼容命令尚未实现，用原生 crash 或 drgn API；不要为了统一界面强制转换已有工作流。

误判：能生成代码不证明 dump 页完整；新版本文档中的命令在旧安装中可能不存在。输出样式相似也不意味着算法/支持范围完全相同。

来源：[drgn-crash man page](https://drgn.readthedocs.io/en/latest/man/drgn-crash.html)、[兼容命令文档](https://drgn.readthedocs.io/en/latest/crash_compatibility.html)。
