# objdump：故障指令与源码

适用：RIP/PC 指令级分析、foo+offset 与源码对应。前提：匹配 ELF、目标架构反汇编器，以及链接地址/运行地址换算已确认。

```bash
objdump -d --disassemble=schedule /path/to/vmlinux
objdump -dS --start-address=0xffffffff81234000 --stop-address=0xffffffff81234100 /path/to/vmlinux
objdump -h /path/to/module.ko
```

`--disassemble=函数名` 仅用于本地帮助确认支持该参数的版本；本机旧版不支持，使用已确认函数起点/结束位置的 start/stop 地址范围替代。`-d` 反汇编代码；`-S` 混合源码（取决于 DWARF 和可访问的匹配源码）；start/stop 控制链接地址范围。先缩小到故障函数/附近指令，避免整份 vmlinux 的巨大输出。

故障访问地址由指令操作数与对应异常寄存器计算。load/store、间接 call、显式 trap 要区别；源码行附近有某指针变量不证明它就是 fault operand。x86 非定长指令必须从正确边界解码，不能随意从 RIP 前若干字节开始认定指令。

内核 KASLR 运行地址需还原为链接地址；foo+0x32 可用匹配 ELF 的 foo 链接地址+偏移。模块 ET_REL 的 section 相对地址与运行加载位置不同，用 crash/drgn 解析或按实际 section 重定位，不对模块套内核统一偏移。

误判：源码混合输出的顺序会被优化改变；看到 NULL 比较附近的源码不说明 fault 是 NULL deref。需要日志保存寄存器和现场对象。

来源：[GNU objdump](https://sourceware.org/binutils/docs/binutils/objdump.html)、[crash dis](https://crash-utility.github.io/help_pages/dis.html)。
