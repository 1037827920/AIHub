# virsh dump

适用：libvirt 管理的 guest hang，用户明确请求内存采集。前提：确认连接 URI、domain 身份、宿主目标路径/权限、空间和 guest 状态。输出路径指向 hypervisor 一侧，不应假定是客户端工作目录。

```bash
virsh domstate VM
virsh help dump
virsh dump VM /new/output/vmcore --memory-only --format elf
virsh domjobinfo VM
```

默认采集可能暂停 domain；实际暂停/恢复行为依 hypervisor 和版本确认，执行前说明影响。`--live` 让 guest 在采集期间继续运行，减轻停机但快照可能不一致。`--crash` 会将 domain 停止为 crashed，`--reset` 在成功后重置；这三个选项互斥且不能擅自附加。

`--memory-only` 生成适合内核分析的内存/CPU dump；不带它可能是其他管理格式。`--format` 仅用于 memory-only，常见 elf/kdump-zlib/lzo/snappy 按当前后端支持确认。与 QMP 的 flattened 行为不可仅因名字相同就等同；检查实际文件头，再决定重组或直接分析。

长操作用 domjobinfo 或工具支持的进度观察，输出应位于新路径。取消采集也可能改变任务/guest 状态，用户未授权时不自行执行 domjobabort。采集成功后记录 domain、格式、开始/完成信息和暂停情况，再做预检/日志提取。

误判：virsh 命令返回成功不证明 debuginfo 可用或全部页面一致；不要把宿主符号交给 guest dump。

来源：[libvirt virsh dump](https://www.libvirt.org/manpages/virsh.html#dump)。
