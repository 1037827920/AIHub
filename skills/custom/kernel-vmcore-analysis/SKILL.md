---
name: kernel-vmcore-analysis
description: 分析 Linux 内核 vmcore 与虚机内存 dump，排查 panic、BUG、lockup、hung task、内存及内核子系统故障，检查匹配符号和 dump 可分析性，并指导相关采集与转换。以 crash、drgn、drgn-crash 为核心；普通用户态 core 或无内核现场的通用性能调优不适用。
---

# Linux vmcore 分析

默认用中文，保留命令、符号和字段原名。P0：crash、drgn、drgn-crash；P1：GDB、ELF 工具、pahole、日志提取及 makedumpfile；P2：采集与扩展；P3：特殊格式与替代调试器。

## 输入与流程

1. 检查已有 vmcore、崩溃内核 vmlinux/模块 debuginfo、日志、源码、架构和采集方式，只询问影响当前分析的缺失项。仅有日志时可以初步定位，但不能声称已验证内存现场。
2. 运行只读预检：`python3 <skill-dir>/scripts/preflight.py --vmcore <path> [--vmlinux <path>]`。它检查元数据和工具，不证明符号匹配或 dump 完整；非 ELF 输入转格式专用工具。
3. 按需读 [VMCOREINFO](references/dump/vmcoreinfo.md)、[ELF 检查](references/elf/readelf.md)、[crash 启动](references/crash/overview.md)。使用崩溃内核而非分析主机或 capture kernel 的符号；核对构建身份、架构、页大小及启动诊断。同 release 的 vendor backport 也可能不匹配。
4. 优先尝试 [vmcore-dmesg](references/dump/vmcore-dmesg.md)，或 makedumpfile/crash 的日志提取。工具或格式不支持时保留诊断并换可用路径。建立事件时间线，区分首发故障与 panic/NMI/转储造成的后续栈。
5. 内核语义与交互定位先用 crash；批量筛选、结构关联用 drgn；用 drgn-crash 的 `--drgn` 学习当前支持命令的 Python 映射。源码/寄存器/指令问题转 GDB 与反汇编，结构布局查匹配 DWARF/BTF。启动 drgn 时显式指定 dump，避免误分析运行中的主机。
6. 用日志、任务/CPU 栈与关联对象交叉验证。不同工具使用同一份错误符号得到相同结果，并不是独立证据。

## 按问题读取

| 问题或操作 | 资料 |
|---|---|
| 命令、地址、类型、链表 | [命令索引](references/crash/commands.md) |
| panic、异常指令、寄存器 | [回溯](references/crash/backtrace.md)、[GDB](references/gdb/kernel-gdb.md)、[objdump](references/elf/objdump.md)、[addr2line](references/elf/addr2line.md) |
| 任务状态、hung task、锁 | [任务](references/crash/task.md)、[锁](references/crash/locking.md) |
| lockup、饥饿、IRQ/CPU | [调度](references/crash/scheduler.md)、[IRQ/CPU](references/crash/irq-cpu.md) |
| OOM、slab、页、地址转换 | [内存](references/crash/memory.md)、[pahole](references/elf/pahole.md) |
| 文件系统、块设备、网络 | [文件系统](references/crash/filesystem.md)、[网络](references/crash/network.md) |
| 可编程分析 | [drgn](references/drgn/overview.md)、[helpers](references/drgn/helpers.md)、[crash → drgn](references/drgn/crash-to-drgn.md) |
| GDB 内核扩展 | [Linux GDB scripts](references/gdb/linux-gdb-scripts.md) |
| 采集、裁剪、转换 | [kdump](references/dump/kdump.md)、[makedumpfile](references/dump/makedumpfile.md)、[QEMU](references/dump/qemu-dump.md)、[libvirt](references/dump/libvirt-dump.md)、[VMware](references/dump/vmware-vmss2core.md) |
| 符号与 ELF 替代工具 | [nm](references/elf/nm.md)、[elfutils](references/elf/elfutils.md) |
| 已有 crash 自动化 | [extensions](references/crash/extensions.md)、[PyKdump](references/automation/pykdump.md)、[crash-python](references/automation/crash-python.md) |

只加载相关资料。示例地址、PID、函数名执行前换为实际值。参数、helper、字段和格式支持按安装版本核对，必要时查询本地帮助及参考文档所链官方来源。

## 分析边界

- 不凭记忆假设结构 offset、页大小、地址映射或锁 owner 编码；查当前构建的类型和源码。区分运行地址与 ELF 链接地址，分别处理 KASLR 和模块重定位。
- 缺页、过滤数据、优化掉的变量、截断与格式不支持分别记录；读取失败不等于对象为空或内存损坏。live 虚机 dump 可能存在跨 CPU/内存快照不一致。
- 保留原始 dump，转换写入不同文件。`-d 31` 损失用户数据、缓存等证据，不能适用于所有故障。
- 分析请求不自动授权触发 panic、重启、改 kdump 配置、暂停/重置 guest 或加载未知扩展；实际执行遵循用户已有授权，说明具体目标和影响。不要反复重试影响运行系统的采集。

## 输出

给出证据最充分的结论、关键日志/命令及对象地址、推断链、置信度、未排除解释。证据不足时写明缺失材料与最小验证步骤；记录符号匹配、过滤页和采集一致性限制，不编造最终 RCA。
