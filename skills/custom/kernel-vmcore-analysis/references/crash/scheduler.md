# 调度、runqueue 与 lockup

适用：soft lockup、CPU 饥饿、RT/CFS 限流、任务长时间不被调度。前提：目标内核 rq 布局受支持；快照时间可能在 panic 后，虚机还要考虑 vCPU 被宿主暂停或抢占。

```text
runq
runq -c 3
runq -t
runq -T
runq -m
runq -g
bt -a
ps -m
timer
```

普通 `runq` 看当前任务和排队实体；`-c` 限定 CPU。`-t` 显示 rq 与当前任务的调度时间字段；`-T` 比较各 CPU 与最近 rq 时间戳的相对差。`-m` 将当前任务运行时长格式化。`-g` 看 task_group 层次与节流标记。这些时间来自内核调度字段及工具解释，不是独立墙钟采样，也不等于可以直接证明某函数循环持续时长。

先将 watchdog 日志中的 CPU/PID 与 `bt -a`/`runq` 对齐。检查是否在禁抢占/关中断区间、等待自旋锁，是否 RT 任务挤占其他 runnable 任务，是否任务组限流。必要时 `struct rq <address>` 查实际字段，字段列表来自当前类型；不要将新调度器结构按旧版本解析。

如果大量任务 runnable 但 CPU 的 current 是 idle，考虑采集时刻、CPU online 状态、迁移、rq 更新中途和不一致快照；先排除符号问题再判断调度损坏。`timer` 可关联 watchdog、定时器及延迟唤醒，但有 timer 不代表回调已经执行，timer 列表也不是所有工作队列的完整描述。

误判：一个 CPU 时间戳滞后不直接证明 hard lockup；休眠、离线 CPU、tickless 和 panic 停机也会出现差异。guest 的 soft lockup 可能由宿主 vCPU 调度延迟引起，guest dump 本身不能证明宿主原因。需要结合宿主调度/暂停记录。读 [IRQ/CPU](irq-cpu.md) 识别中断与采集上下文。

来源：[runq](https://crash-utility.github.io/help_pages/runq.html)、[timer](https://crash-utility.github.io/help_pages/timer.html)、[Linux lockup watchdog](https://docs.kernel.org/admin-guide/lockup-watchdogs.html)。
