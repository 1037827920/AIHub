# readelf/eu-readelf：格式与调试信息

适用：检查架构、段、notes、build-id、符号和 DWARF 是否存在。前提：输入确为 ELF；压缩 kdump、flattened 和压缩容器文件不直接使用这些命令。

```bash
readelf -h /path/to/vmcore
readelf -l /path/to/vmcore
readelf -n /path/to/vmcore
readelf -h /path/to/vmlinux
readelf -S /path/to/vmlinux
readelf -n /path/to/vmlinux
readelf -s /path/to/vmlinux
```

`-h` 看 class、endianness、machine 和 type；`-l` 看 PT_LOAD 的文件/物理/虚拟映射与 PT_NOTE；`-n` 看 notes；`-S` 看 section；`-s` 看符号。vmcore 通常 ET_CORE，而 vmlinux 可以 ET_EXEC 或其他受构建影响的类型；不是所有 core 都是 Linux kernel core。

`.debug_info/.debug_line` 指示相应 DWARF sections，`.gnu_debuglink` 提示独立 debuginfo，`.BTF` 不代表完整 DWARF。sections 存在不保证类型/源码行可用；必要时确认独立 debuginfo 的构建身份与加载结果。

PT_LOAD 中 filesz/memsz、物理洞和过滤策略需要工具语义；不能简单用总 RAM 大小要求文件同样大。文件段越界/短读提示截断可能，但格式或 procfs 导出也需判断。note 含 VMCOREINFO 或 PRSTATUS 不证明全部内存保存。GNU build-id 属于该 ELF，不自动代表崩溃内核。

eu-readelf 提供替代解析，先核对其帮助；详见 [elfutils](elfutils.md)。不要默认使用 `readelf -a` 输出所有内容或全文件 strings；先按问题选范围。

来源：[GNU readelf](https://sourceware.org/binutils/docs/binutils/readelf.html)、[Linux VMCOREINFO](https://docs.kernel.org/admin-guide/kdump/vmcoreinfo.html)。
