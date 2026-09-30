# elfutils：ELF 与独立 debuginfo

适用：已有 eu-* 工具、GNU 工具解析差异、build-id 与 debuginfo 检查。前提：查看本地版本帮助，目标格式仍须是所支持 ELF。

```bash
eu-readelf -h /path/to/vmlinux
eu-readelf -n /path/to/vmlinux
eu-addr2line -e /path/to/vmlinux -f -i 0xffffffff81234567
eu-nm -n /path/to/vmlinux
eu-unstrip -n -e /path/to/vmlinux
```

`eu-unstrip -n -e` 列出模块/调试信息关联线索，不请求重写 ELF。报告中的 build-id、文件或 debug 文件信息用于核对来源；找到了文件不意味着它与崩溃内核匹配。

需实际合并 stripped ELF 与 debuginfo 时，先确认构建身份并输出到不同文件；普通分析不必改原 vmlinux。缺少独立调试信息时优先已有构建产物，网络 debuginfod 查询和下载不属于只读预检。

eu-* 不是另一套内核语义分析器，无法自动修复物理映射、KASLR 和过滤页面。GNU 与 elfutils 输出不同要检查版本/支持，不把差异自动判定为 dump 损坏。

来源：[elfutils 官方项目](https://sourceware.org/elfutils/)、[eu-unstrip 源码与选项](https://sourceware.org/git/?p=elfutils.git;a=blob;f=src/unstrip.c;hb=HEAD)。
