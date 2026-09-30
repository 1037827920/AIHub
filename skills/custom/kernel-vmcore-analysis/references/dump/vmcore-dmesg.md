# vmcore-dmesg：快速日志分诊

适用：尚未找到 debuginfo，先提取 panic/BUG/WARN/watchdog 日志。前提：输入格式和 printk ringbuffer 布局被工具版本支持；该工具属于 kexec-tools，不是假设任何二进制内存都能读取。

```bash
vmcore-dmesg /path/to/vmcore
vmcore-dmesg /proc/vmcore
```

输出为标准输出；第二条只在 capture 环境使用。需保存时写用户指定的新文件，避免 shell 重定向覆盖已有证据。该工具以 ELF headers/VMCOREINFO 和内存内容恢复日志，不以启动 crash 为前提；本地实现不提供常规 --help 时查看 man/source，不把 `--help` 当文件路径的报错当作损坏 dump。

从日志标记首发异常、CPU/PID、RIP/PC、异常地址、taint、模块和先前相关事件。日志里出现 SysRq/人为 panic 应区分采集原因与被调查 hang。成功提取日志并不能证明任务/页数据完整，ringbuffer 中的时间通常是内核相对时间。

普通 vmcore-dmesg 对压缩 kdump/flattened 不保证支持，失败时尝试 [makedumpfile --dump-dmesg](makedumpfile.md) 或匹配 crash 的 `log`；记录格式和错误，不默认先整文件转换。

误判：日志缺失可能是环形覆盖、过滤、不支持 printk 版本或截断，不等于没有 panic；最后一条日志未必是故障发生点。

来源：[kexec-tools vmcore-dmesg 源码](https://github.com/horms/kexec-tools/blob/main/vmcore-dmesg/vmcore-dmesg.c)、[makedumpfile](https://github.com/makedumpfile/makedumpfile)。
