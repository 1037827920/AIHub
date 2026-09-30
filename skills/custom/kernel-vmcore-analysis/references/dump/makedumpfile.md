# makedumpfile：压缩、过滤、重组与日志

适用：过大的 vmcore、flattened stream、拆分 dump，或提取日志。前提：本地版本支持输入与压缩算法，原内核 VMCOREINFO 或匹配 vmlinux 可用，输出必须与原文件不同。

```bash
makedumpfile --help
makedumpfile -c -d 0 -x /path/to/vmlinux /path/to/vmcore /new/output/vmcore.zlib
makedumpfile --dump-dmesg /path/to/vmcore /new/output/dmesg.txt
makedumpfile --dump-dmesg -x /path/to/vmlinux /path/to/vmcore /new/output/dmesg.txt
makedumpfile -R /new/output/vmcore < /path/to/vmcore.flat
makedumpfile --reassemble /path/to/part1 /path/to/part2 /new/output/vmcore
```

日志提取缺少所需 VMCOREINFO 时才补 `-x` 或匹配的 `-i`。`-R` 从标准输入重组 flattened；不能把任意 gzip 文件当 flattened。`--reassemble` 用于该工具创建的 split dump，不是拼接任意内存片段。

`-c/-l/-p/-z` 分别选择 zlib/LZO/snappy/zstd，是否支持按帮助确认；`-E` 输出 ELF，与页压缩选项不兼容。转换不会恢复先前已被过滤的页。

过滤级别是位组合：1 零页；2 非私有缓存；4 缓存类（含私有）；8 用户数据；16 空闲页。31 组合所有这些过滤，适用于节省空间但会损失内容证据；不能作为分析内存破坏、用户地址或文件缓存问题的默认选项。`-d 0` 不请求上述过滤，但仍不能保证输入本来完整。要查看 cache/用户内容，保留首次采集的低过滤或完整现场。

VMCOREINFO 生成入口：`makedumpfile -g /new/output/vmcoreinfo -x /path/to/vmlinux`。它涉及当前运行内核和匹配构建的要求，不能在任意分析主机上给其他崩溃内核生成正确运行时布局；优先保留 dump 内 note。详细条件核对本地 man/help。

不要加 `-f` 覆盖原件；转换报错时保留输入/输出诊断，不能把部分输出交给后续分析当作成功。zlib 压缩的 kdump 不是普通 gzip 文件。

来源：[makedumpfile 官方项目及 man page](https://github.com/makedumpfile/makedumpfile)、[Linux kdump](https://docs.kernel.org/admin-guide/kdump/kdump.html)。
