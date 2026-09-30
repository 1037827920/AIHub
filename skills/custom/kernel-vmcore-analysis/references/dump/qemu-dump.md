# QEMU dump-guest-memory

适用：guest hang/lockup 无 panic，用户明确需要由 hypervisor 捕获现场。前提：确认 VM、QMP/HMP 连接、目标容量/权限、采集一致性要求和运行影响；这里只提供模板，不自动暂停 guest。

QMP 模板：

```json
{"execute":"query-dump-guest-memory-capability"}
{"execute":"dump-guest-memory","arguments":{"paging":false,"protocol":"file:/new/output/vmcore.elf","format":"elf","detach":true}}
{"execute":"query-dump"}
```

先按实际 capability 选格式；detach 表示后台执行，返回成功仅代表请求已受理，必须检查 completed/failed 与保存字节数。paging=false 的物理内存 ELF 通常交 crash/drgn；paging=true 提供 GDB 所需映射，但受架构、guest 页表和主机内存开销限制，不能当成默认更完整选项。

HMP 入口：

```text
dump-guest-memory /new/output/vmcore.elf
dump-guest-memory -p /new/output/vmcore.paging.elf
dump-guest-memory -z /new/output/vmcore.flat
```

`-p` 是 paging，`-z` 是 zlib kdump，需查当前 `help dump-guest-memory`。QMP `kdump-zlib/lzo/snappy` 是 makedumpfile flattened 格式，需 `makedumpfile -R` 重组；`kdump-raw-*` 是已组装压缩 dump，支持始于较新 QEMU，不能混淆。

paging 与 begin/length 等过滤参数不能随意和非 ELF 格式组合。局部 dump 会缺少分析所需页面。运行影响/是否暂停必须按当前 QEMU 和管理层行为确认；live 内存和 CPU notes 可能不一致，必要时在授权范围中设计暂停采集及恢复步骤。

读 [VMCOREINFO](vmcoreinfo.md) 检查 guest 提供的布局。普通 QEMU dump 不是自动生成匹配 vmlinux；宿主进程 core 也不是 guest vmcore。

来源：[QMP dump reference](https://www.qemu.org/docs/master/interop/qemu-qmp-ref.html#dump-guest-memory)、[HMP monitor](https://www.qemu.org/docs/master/system/monitor.html)。
