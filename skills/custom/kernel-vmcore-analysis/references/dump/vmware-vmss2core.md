# VMware vmss2core

适用：收到 Linux guest 的 .vmss/.vmem 或带内存 snapshot 的 .vmsn/.vmem。前提：工具来源可信、支持目标 guest/架构，文件属于同一 snapshot/suspend 现场，不只有孤立 .vmem。

```bash
/path/to/vmss2core-Linux64 -N /path/to/guest.vmss /path/to/guest.vmem
```

对 .vmsn 使用对应 snapshot 文件。`-N` 指 guest 是 Linux，而非分析主机 OS；具体 -N 变体按该版本 usage 和官方说明，不盲目切换。工具会创建转换输出（常见 vmss.core），在用户选定的新工作目录执行，避免覆盖原件或旧转换结果。

记录工具版本、输入配对与输出路径。转换失败先查配对、snapshot 是否含内存、文件完整性与支持范围；不把任意 .vmem 当 vmcore。输出仍需匹配 guest vmlinux/模块，检查 ELF/notes 和分析器加载诊断。

误判：转换成功不证明符号匹配；跨 snapshot 混用同名文件会产生错误现场。此工具为 P3 特殊环境入口，不作为 Linux/kdump 常规路径。

来源：[Broadcom snapshot conversion](https://knowledge.broadcom.com/external/article/323788/converting-a-snapshot-file-to-memory-dum.html)、[Linux vmss2core 示例](https://knowledge.broadcom.com/external/article/344974/vmss2core.html)。
