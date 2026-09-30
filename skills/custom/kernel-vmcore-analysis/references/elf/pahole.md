# pahole：当前构建的结构布局

适用：task_struct、rq、page、inode 等字段偏移，vendor backport/KABI 差异。前提：匹配的 DWARF 或工具支持的 BTF 类型来源，模块类型可能在对应 .ko/debuginfo。

```bash
pahole -C task_struct /path/to/vmlinux
pahole -C rq /path/to/vmlinux
pahole -C page /path/to/vmlinux
pahole -C xfs_inode /path/to/xfs.ko
```

查看字段 offset、大小、padding/hole 和嵌套类型。同时核对退出码和 stderr：本机验证中工具可打印 DWARF 类型，再因缺少 .BTF 而返回非零状态，不能只凭 stdout 声称整次成功。保留诊断并用 crash/GDB/drgn 类型显示交叉验证，不将工具异常视为 dump 损坏。分析时使用 crash `struct -o`、GDB `ptype` 或 drgn type 交叉检查。结构对象的字段值来自 dump，pahole 只提供布局，不表示有现场实例。

字段缺失先核对类型来自哪个模块、是否独立 debuginfo、DWARF/BTF 支持与类型裁剪，不尝试旧 offset 来填补未知布局。BTF 可以提供类型，但不能替代完整局部变量/源码行 DWARF；同名结构可能因配置不同而变化。

不要执行 BTF 编码/写 ELF 的模式来进行只读检查；这里仅用 -C 显示。没有可用类型时，保留限制并索取匹配构建材料，不能从通用版本号推断偏移。

来源：[dwarves/pahole 项目](https://github.com/acmel/dwarves)、[pahole man page 源码](https://github.com/acmel/dwarves/blob/master/man-pages/pahole.1)。
