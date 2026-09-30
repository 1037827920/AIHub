# Linux scripts/gdb helpers

适用：已建立可用 GDB 内核地址空间，希望用 lx helpers 查模块、日志和任务。前提：匹配源码、启用对应 GDB scripts 构建选项、vmlinux-gdb.py 及其 Python 模块完整。helper 最初面向实时内核调试，静态 vmcore 的支持须实际确认。

```gdb
source /path/to/matching-build/vmlinux-gdb.py
help lx-dmesg
lx-dmesg
lx-lsmod
lx-symbols /path/to/matching-modules
p $lx_task_by_pid(1234)
p $lx_current()
```

`lx-dmesg`、`lx-lsmod`、`lx-symbols` 是命令；`$lx_task_by_pid()`、`$lx_current()`、`$lx_per_cpu()`、`$lx_module()`、`$lx_thread_info()` 是 GDB convenience functions，不能全部当作裸命令执行。参数与支持能力查当前加载脚本的帮助/源码。特别是 current() 依目标寄存器上下文，离线 dump 不一定有效。

`lx-symbols` 按模块状态加载符号，必须提供匹配 .ko；不能用分析主机正在运行的模块目录。读取 dmesg 依 printk ringbuffer 布局，老 helpers 在新内核上可能失效；可退回 vmcore-dmesg/crash log。

GDB 自动加载拒绝时，只为可信构建路径配置窄范围 `add-auto-load-safe-path`；不要把整个文件系统设成 safe-path。手动 source 也会执行 Python，用户授权范围和脚本来源必须已明确。不修改全局 GDB 配置来掩盖缺依赖。

来源：[Linux GDB 官方文档](https://docs.kernel.org/process/debugging/gdb-kernel-debugging.html)、[scripts/gdb 源码](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/scripts/gdb)。
