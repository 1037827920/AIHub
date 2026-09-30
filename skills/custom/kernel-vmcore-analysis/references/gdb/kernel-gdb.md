# GDB：源码、寄存器与指令

适用：底层表达式、结构、源码、DWARF 和反汇编。前提：目标是 GDB 可读的 ELF core，地址映射可用且符号匹配；物理映射的 vmcore 与压缩 kdump 不保证可被普通 GDB 正确解析。

```bash
gdb -nx /path/to/vmlinux /path/to/vmcore
```

```gdb
info files
ptype struct task_struct
p/x init_task.pid
disassemble /r schedule
x/8gx 0xffff888012340000
info registers
bt
```

GDB 的默认线程/寄存器来自它识别的 core notes，不应认为能完整表示所有 Linux task。vmcore 的 PT_LOAD 若是物理地址，普通 GDB 的内核虚拟读数可能失败；此时用 crash/drgn，而不是编造有效寄存器。QEMU paging dump 见 [QEMU](../dump/qemu-dump.md)。

```gdb
set substitute-path /build/kernel /local/matching-source
list *schedule
```

源码路径替换只解决路径，不解决代码版本。KASLR 和模块动态装载需要正确重定位；直接加载链接 vmlinux 后用运行 RIP 查行可能错误。`info registers` 无值时不能从任意栈槽补造。`ptype` 看类型，`x` 的 g 是 8 字节，不适用于所有数据宽度。

dump 是静态快照，不尝试 continue、单步、断点来获取历史执行；不写内存。GDB 的源码行可能覆盖多条指令，优化/内联还会令变量不可用，必须结合故障指令和实际保存的寄存器。

来源：[Linux kdump 分析工具](https://docs.kernel.org/admin-guide/kdump/kdump.html)、[GDB core files](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Core-File-Generation.html)、[GDB 数据检查](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Data.html)。
