# kdump/kexec：生成链路与未生成 dump 排查

适用：理解 dump 来源，或用户明确请求排查 kdump 采集失败。前提：先确认发行版、架构、内核配置和服务实现；不会因为分析已有 dump 就改运行系统。

链路：production kernel 预留 crashkernel 内存 → `kexec -p` 加载 capture kernel → panic 后切换 → capture kernel 暴露原内存的 `/proc/vmcore` → 保存/过滤为文件。capture kernel 的 release 与原内核可以不同，分析使用原内核符号。

只读起点：

```bash
cat /proc/cmdline
cat /sys/kernel/kexec_crash_loaded
cat /sys/kernel/kexec_crash_size
```

路径不存在时记录平台/配置差异；loaded 为 1 仅表示已加载，不证明存储、网络或 panic 触发链路能成功。检查 crashkernel 预留、捕获内核/ initramfs 驱动、目标容量和上次 capture 日志。发行版服务命令按本地确认，不假设所有系统都叫 kdump.service。

下面仅是用户授权的 capture 环境保存示例，输出路径须确认容量且不存在：

```bash
makedumpfile -c -d 0 /proc/vmcore /new/output/vmcore
```

`/proc/vmcore` 是 capture kernel 暴露的原内存，不是任意主机上都存在的文件。配置 kexec、改 boot 参数、重启和 SysRq crash 会改变运行系统，只有明确请求与授权时才制定并执行操作；分析阶段不安排破坏性试验。

误判：没有 vmcore 不证明内核未崩溃；预留不足、设备不可达或 capture kernel 再次失败都可能丢失现场。选择过滤级别见 [makedumpfile](makedumpfile.md)。

来源：[Linux kdump 官方文档](https://docs.kernel.org/admin-guide/kdump/kdump.html)、[kexec-tools](https://git.kernel.org/pub/scm/utils/kernel/kexec/kexec-tools.git/)。
