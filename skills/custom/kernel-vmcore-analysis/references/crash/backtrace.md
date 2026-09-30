# 回溯、异常上下文与故障指令

适用：panic、Oops、BUG、NMI、栈损坏及异常 RIP/PC。前提：符号与 unwind 支持匹配，模块地址已按 dump 中的加载位置解析。

```text
log
bt
bt -a
bt 1234
bt -f 1234
bt -l 1234
sym ffffffff81234567
dis ffffffff81234567
rd -x ffff888012340000 8
```

`bt -a` 看每 CPU 的活跃任务；`bt PID` 查看特定任务；`-f` 加入栈帧内容，`-l` 尝试源码行信息。先用普通回溯，再按需展开原始数据；选项和架构专有模式查 `help bt`。`rd` 示例读取八个默认大小的值，默认 word 宽度依架构，确需固定宽度时查本地帮助使用相应位宽选项。

分析顺序：从日志确定异常类型和寄存器 → 找真正故障帧 → 解析函数+偏移 → 小范围反汇编 → 依据指令操作数和当时寄存器计算访问地址 → 检查对象与调用者。x86 的 CR2 属于 page fault 上下文，其他异常/其他架构不能套用。内核 BUG/WARN 和主动 panic 也不必然是非法访存。

`RIP: foo+0x32/0x80` 中的偏移可用于在匹配 ELF 中查函数指令；运行 RIP 在 KASLR 后不能直接交给链接地址工具。`dis` 已在 dump 上下文处理符号更方便，外部 objdump/addr2line 见 [反汇编](../elf/objdump.md) 与 [地址解析](../elf/addr2line.md)。模块 fault 先 `mod` 核对具体模块与匹配 .ko。

区分异常保存的寄存器、panic 后寄存器与普通栈中的数值；不能把任意栈槽当参数或指针。优化、内联、尾调用、ORC/帧指针差异会影响回溯与局部变量。搜索到像函数地址的值不是可靠 call chain；必须检查栈范围、异常帧与 unwind 结果。停止在不可读页，记录位置，不用猜测填补调用链。

误判：所有 CPU 卡在 stop/NMI/panic 可能只是采集后的共同状态；最后一个函数是受害点，不一定是写坏对象的起点。单 dump 通常不能确定 use-after-free 的首次释放栈。

来源：[bt](https://crash-utility.github.io/help_pages/bt.html)、[dis](https://crash-utility.github.io/help_pages/dis.html)、[sym](https://crash-utility.github.io/help_pages/sym.html)、[rd](https://crash-utility.github.io/help_pages/rd.html)。
