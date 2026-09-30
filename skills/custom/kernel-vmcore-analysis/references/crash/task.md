# 任务、上下文与批量定位

适用：hung task、进程状态、内核栈聚类。前提：crash 已加载匹配符号；PID 示例需替换为 dump 内 PID，而非当前主机进程。

```text
ps
ps -m
ps -l
ps -s
ps -p 1234
ps -c 1234
task 1234
set 1234
bt
foreach UN bt
foreach bt
```

`ps` 提供 PID、PPID、CPU、TASK、状态、COMMAND 等；`ps -m` 查看距任务最近运行时间的格式化信息，`-l` 列出相应时间戳，`-s` 将 TASK 列替换为 KSTACKP；`-p`/`-c` 看父/子关系。时间字段和状态解码依内核版本，单位与来源以本地 `help ps` 为准。

`task` 展开 task_struct 与相关线程信息；`set` 改变调试器当前任务上下文，不是在 guest 上调度进程。`foreach UN bt` 聚焦不可中断任务；无筛选的 `foreach bt` 用于全局栈聚类，但输出可能巨大。保留 PID 与 TASK 地址，必要时结合命名空间和线程组身份；仅按 comm 聚合可能混合不同进程。

看同一等待函数的任务是否等待同一对象：文件、块请求、mutex、rwsem、completion 等。先从栈与类型恢复对象地址，再检查 owner/唤醒路径，读 [锁](locking.md) 和 [文件系统](filesystem.md)。字段 `state`/`__state`、线程信息的位置在内核版本间变化，应先 `struct -o task_struct` 或 `whatis`，不能写死字段偏移。

误判：UN/D 状态既可能是正常 I/O 等待，也可能是死锁；单次快照不能证明等待持续时间。`ps -m` 的时间与 hung-task 日志阈值不是同一测量。空栈或异常 PID 可能来自过滤页、栈回溯失败或不匹配符号。

来源：[ps](https://crash-utility.github.io/help_pages/ps.html)、[task](https://crash-utility.github.io/help_pages/task.html)、[set](https://crash-utility.github.io/help_pages/set.html)、[foreach](https://crash-utility.github.io/help_pages/foreach.html)。
