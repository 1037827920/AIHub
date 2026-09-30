# 锁、等待队列与 hung task

适用：任务卡在 mutex/rwsem/completion/futex/I/O 等路径，或 CPU 自旋。前提：已从日志与栈定位等待对象；通用 crash 命令不能自动证明所有类型的死锁。

```text
foreach UN bt
bt -f 1234
whatis struct mutex
struct -o mutex
struct mutex ffff888012340000
waitq ffff888012341000
struct -o rw_semaphore
```

地址分别代表已确认的 mutex 和 wait_queue_head，不能直接把 mutex 地址交给 waitq。先识别具体等待原语；mutex/rwsem 的 waiter 链表不必是通用 wait_queue_head。`waitq` 展示等待队列项及可识别任务，不是任意锁 owner 查询器。无法识别队列布局时，检查源码后用 `list` 或 drgn 遍历真实成员。

从 waiter 的栈、寄存器或可恢复局部变量取得对象地址，再验证类型/生命周期。读取 owner 的编码以当前内核源码为准，含低位标记、原子包装或匿名 reader 时不能直接强转 task_struct 指针。rwsem 的 owner 字段也不能自动枚举所有读者。

建立有地址和证据的等待图：task A 等待对象 L → L 的 owner task B → B 又等待对象 M。只有确认环上 owner/等待关系才可判断死锁；栈函数相同不代表对象相同。spinlock/queued spinlock 往往不保存可直接使用的完整 owner 身份，应结合各 CPU 栈、队列节点和源码，不杜撰 owner。

completion 可能是在等外部设备或 workqueue，不存在锁 owner；futex 还涉及用户空间和页可能被过滤。对 I/O 等待读 [文件系统](filesystem.md)，对 CPU 自旋读 [调度](scheduler.md)。lockdep 日志是额外证据，但不能把未启用 lockdep 时的无报告当成无死锁。

误判：UN 状态和单个 wait 函数只能表明当前等待；用栈上可疑数字恢复参数需验证 ABI、优化、函数偏移与对象布局。停止在缺页或不可恢复参数，并明确证据缺口。

来源：[waitq](https://crash-utility.github.io/help_pages/waitq.html)、[struct](https://crash-utility.github.io/help_pages/struct.html)、[内核锁文档](https://docs.kernel.org/locking/index.html)。
