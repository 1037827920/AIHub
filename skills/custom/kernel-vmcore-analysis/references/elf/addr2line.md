# addr2line/eu-addr2line：地址到源码

适用：panic 地址、函数偏移、内联调用定位。前提：匹配 ELF/DWARF，输入是该 ELF 的链接地址或正确 section 相对地址。

```bash
addr2line -e /path/to/vmlinux -f -i 0xffffffff81234567
addr2line -e /path/to/module.ko -j .text -f -i 0x32
```

`-f` 输出函数，`-i` 展开内联链。第二条只适用于地址确实属于该模块 .text，0x32 是 section 相对偏移；它不等于任意 foo+0x32，需要加 foo 在该 section 的偏移。符号 foo 的 ELF 链接地址可由 nm/objdump 查。

KASLR 下先由分析器确认内核 relocation；只有已确认关系时才把运行地址换算成链接地址。模块有独立加载区和多个 section，需要单独处理。返回 `??:0` 可能是缺 DWARF、错误地址空间、符号错配或不在代码段，不能据此认定地址无效。

行号映射不证明实际执行过全部该行逻辑，内联与优化也会合并范围。最终 fault 用 [objdump](objdump.md) 的指令和寄存器验证。eu-addr2line 的选项按本地帮助确认，不能假定和 GNU 全部相同。

来源：[GNU addr2line](https://sourceware.org/binutils/docs/binutils/addr2line.html)、[elfutils](https://sourceware.org/elfutils/)。
