# nm/eu-nm：符号与链接地址

适用：查函数起始地址、symbol+offset、目标模块符号。前提：ELF 符号表可用，文件构建匹配。

```bash
nm -n /path/to/vmlinux
nm -n /path/to/module.ko
```

`-n` 按数值排序，输出值、符号类型和名称。代码符号常见 T/t；相邻符号地址差不保证函数真正大小，可能有别名、对齐和链接布局。符号名存在不保证 DWARF 类型/行信息存在，System.map 也不能补全这些信息。

vmlinux 地址是链接地址；dump 的运行地址由 KASLR/模块装载改变。模块 .ko 为 ET_REL 时，值可能按 section 相对解释，不能对全部符号按一条全局绝对地址排序推断运行布局。

已有 crash 会话优先 `sym ADDRESS` 或 `sym NAME`，避免手动二分大列表并忘记重定位。eu-nm 可作替代，具体显示方式按本地帮助核对。

误判：地址匹配到最近符号只提供候选，需函数范围、section、反汇编与现场上下文确认。

来源：[GNU nm](https://sourceware.org/binutils/docs/binutils/nm.html)、[crash sym](https://crash-utility.github.io/help_pages/sym.html)。
