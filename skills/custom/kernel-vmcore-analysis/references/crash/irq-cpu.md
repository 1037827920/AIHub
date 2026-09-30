# CPU、中断、定时器与采集上下文

适用：hard lockup、IRQ storm、softirq 停滞、CPU 异常和多 CPU 栈比较。前提：架构和 CPU note 支持已确认；CPU online/possible 与实际保存寄存器数量不一定相同。

```text
mach
irq
irq -s
bt -a
runq -c 3
kmem -o
timer
```

`mach` 查看架构机器信息；`irq` 检查 IRQ 描述符/handler，`-s` 看统计，内核支持依本地帮助。计数通常是累计值，单 dump 无时间差，不能仅按最大计数宣布 IRQ storm。`kmem -o` 看 per-CPU offset，读取 per-CPU 变量时需按 CPU 和类型寻址，不把链接符号地址直接当某 CPU 实例。

联合 watchdog 日志和每 CPU 栈定位 interrupt/NMI/softirq/idle/panic stop 场景。异常帧与普通调用帧分开解释；栈中处理 watchdog 的 CPU 可能只是报告者。多个 CPU 在 spinlock 等待需要查等待对象和持有路径，不等于所有 CPU 都是根因。

`timer` 可看 pending 定时器，但不是执行历史。IRQ 亲和性、设备状态、线程化 IRQ 和 per-CPU 数据需当前类型/源码，不假定所有内核采用同一字段。CPU note 缺失、offline CPU、QEMU live 内存与寄存器一致性差都会限制结论。

误判：guest RIP 长期像 idle 不证明宿主没调度它；一个 CPU 在 stop_machine/NMI 等待可能是 panic 采集的结果。对 guest hard lockup 需记录 hypervisor 类型、采集方式及是否停机一致。

来源：[mach](https://crash-utility.github.io/help_pages/mach.html)、[irq](https://crash-utility.github.io/help_pages/irq.html)、[timer](https://crash-utility.github.io/help_pages/timer.html)、[kmem](https://crash-utility.github.io/help_pages/kmem.html)。
