# crash 命令主题索引

适用：选择下一步命令，而不是每次读取完整手册。前提：会话已加载 dump；先 `help` 发现当前内置/扩展命令，再 `help COMMAND` 确认参数。下表覆盖官方在线 help 的命令集；旧版可能没有 bpf、sbitmapq、maple tree 等能力。

| 主题 | 命令与用途 | 详细解读 |
|---|---|---|
| 系统与 CPU | `sys` 全局身份；`mach` 架构；`log` 内核日志 | [启动](overview.md)、[IRQ/CPU](irq-cpu.md) |
| 任务与上下文 | `ps` 状态/关系；`task` task/线程；`set` 当前任务；`foreach` 批量；`sig` 信号 | [任务](task.md) |
| 调用链 | `bt` 任务/CPU/异常栈 | [回溯](backtrace.md) |
| 调度与等待 | `runq` 队列/时间；`waitq` 等待项；`timer` 定时器 | [调度](scheduler.md)、[锁](locking.md) |
| 内存 | `kmem` 页/slab/zone；`vm` VMA；`swap` 交换；`ipcs` SysV IPC | [内存](memory.md) |
| 地址转换 | `vtop` 虚→实；`pte` 解码项；`ptob` 页数→字节；`btop` 字节→页数 | [内存](memory.md) |
| 类型与符号 | `struct`、`union` 结构；`whatis` 类型；`p` 表达式；`sym` 地址↔符号 | 本文示例、[pahole](../elf/pahole.md) |
| 原始数据 | `rd` 读内存；`search` 查内容；`dis` 反汇编；`gdb` 底层命令 | [回溯](backtrace.md)、[GDB](../gdb/kernel-gdb.md) |
| 容器遍历 | `list` 链表；`tree` radix/xarray/rbtree/maple；`sbitmapq` bitmap 队列 | 本文示例、[drgn helpers](../drgn/helpers.md) |
| 文件与设备 | `files` fd；`fuser` 对象使用者；`mount` 挂载；`dev` 设备 | [文件系统](filesystem.md) |
| 网络/IRQ/BPF | `net` 网络/socket；`irq` handler/统计；`bpf` BPF 对象 | [网络](network.md)、[IRQ/CPU](irq-cpu.md) |
| 模块与扩展 | `mod` 模块/目标符号；`extend` 调试器 .so | [扩展](extensions.md) |
| 计算与显示 | `eval` 表达式计算；`ascii` 字符转换；`*` 数据结构便捷显示 | `help eval`、`help ascii`、`help *` |
| 会话辅助 | `alias` 别名；`repeat` 重复命令；`help` 帮助；`q`/`exit` 退出 | `help input`、`help output` |
| 写操作 | `wr` 内存写入 | 非普通 vmcore 分析命令，见下文 |

## 类型、符号与只读内存

```text
whatis init_task
p init_task.pid
p/x jiffies
struct -o task_struct
struct task_struct.pid,comm ffff888012340000
union thread_union ffff888012350000
sym init_task
rd -64 -x ffff888012340000 8
dis schedule
```

`struct -o` 显示字段 offset；成员选择减少输出。`p` 的 GDB 表达式与进制选项需本地帮助确认。`rd -64` 固定读取宽度，内容是原始值，须结合当前类型与地址语义判断；不是看到非零值就有有效对象。union 要根据活动成员解释，不能认为所有成员同时有效。

## 遍历与范围控制

```text
list task_struct.tasks -H init_task.tasks -s task_struct.pid,comm
tree -t xarray ADDRESS
search -k -s START -e END VALUE
```

大写标识符必须替换；tree 的 ADDRESS 是工具要求的根对象地址，不是任意节点。`list` 示例以 init_task 的 tasks 成员为链表头，按当前 task_struct.tasks offset 恢复容器；用实际类型验证环链表与节点所属对象。`search` 限定范围并检查对齐；命中数字只能提供线索，不能证明引用关系。损坏链表、异常根节点和过滤页可能中断遍历，不要擅自跨过不可读指针继续计数。

## 会话与写入边界

```text
help bt
help input
help output
gdb ptype struct task_struct
quit
```

重定向和外部 shell 管道可能创建文件或执行主机命令；alias/repeat 不应隐藏这些副作用。静态 dump 上 repeat 无法产生历史变化。`wr` 是会改变支持目标内容的写命令，不用于常规分析；live 内核支持取决于平台，不能因出现在 help 就执行。只读预检和默认分析不要写目标内存。

来源：[官方命令目录](https://crash-utility.github.io/help.html)、[struct](https://crash-utility.github.io/help_pages/struct.html)、[list](https://crash-utility.github.io/help_pages/list.html)、[tree](https://crash-utility.github.io/help_pages/tree.html)、[search](https://crash-utility.github.io/help_pages/search.html)、[wr](https://crash-utility.github.io/help_pages/wr.html)。
