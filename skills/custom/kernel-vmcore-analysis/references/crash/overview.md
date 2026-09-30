# crash：启动与初始分诊

适用：已有 Linux dump，需要任务、CPU、内存与模块语义。前提：分析器支持目标架构/内核/dump 格式，vmlinux 是崩溃内核的未剥离 ELF，具备相应类型信息。System.map、启动压缩镜像 vmlinuz 不能替代完整 debuginfo。

```bash
crash /path/to/vmlinux /path/to/vmcore
```

```text
sys
log
mach
bt
bt -a
ps
mod
```

先记录版本、启动警告、KERNEL/DUMPFILE/RELEASE/MACHINE/CPUS/UPTIME/PANIC。`sys` 组织全局身份；`log` 保留 panic 前后的时间线；`bt` 是当前上下文的栈，`bt -a` 检查各 CPU 活跃任务；`ps` 和 `mod` 为后续对象定位提供地址。初始上下文可能是 panic task，但不能假设总如此。

启动失败先分类：符号/版本不匹配、架构不支持、VMCOREINFO/地址转换问题、压缩算法不支持、文件被截断或尚未采集完成。记录准确错误，再核对采集来源和构建身份；不要强行忽略 mismatch 然后发布结论。相同 release 仍可能存在不同配置、编译器和 backport；build-id 缺失时不能凭空断言相同或不同。capture kernel 和当前分析主机的 uname 都不是崩溃内核身份。

批量输出可使用输入文件（仅使用当前支持的只读命令）：

```bash
crash -i /path/to/commands.txt /path/to/vmlinux /path/to/vmcore
```

输入文件最后放 `quit`，避免等待交互。长遍历先缩小到相关 CPU/PID/cache；`foreach bt`、全页枚举与无范围 search 在大 dump 上可能昂贵。每个输出记录命令、工具版本与 dump 身份。

误判：启动成功只说明工具初始化完成，不保证每个模块符号正确；日志的最后一个 WARN 不一定是根因。发现缺页后读 [内存](memory.md)，检查身份/地址时读 [VMCOREINFO](../dump/vmcoreinfo.md)。

来源：[项目 README](https://github.com/crash-utility/crash)、[sys](https://crash-utility.github.io/help_pages/sys.html)、[输入选项](https://crash-utility.github.io/help_pages/input.html)、[Red Hat 实战](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/managing_monitoring_and_updating_the_kernel/analyzing-a-core-dump)。
