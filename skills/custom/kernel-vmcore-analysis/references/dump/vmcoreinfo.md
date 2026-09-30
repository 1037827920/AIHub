# VMCOREINFO、地址布局与符号匹配

适用：KASLR、页大小、结构偏移、物理/虚拟地址转换以及分析器初始化失败。前提：区分 ELF note、压缩格式内保存的 note 与独立文本 VMCOREINFO。

```bash
readelf -h /path/to/vmcore
readelf -l /path/to/vmcore
readelf -n /path/to/vmcore
readelf -n /path/to/vmlinux
```

仅对 ELF 输入执行；readelf 未把描述内容解码成文本时，用分析器或限界 ELF-note parser 读取 VMCOREINFO，不能靠全文件 strings 命中值断言身份。预检脚本只提取有限 note 的 OSRELEASE/PAGESIZE/KERNELOFFSET 摘要，超出预算明确跳过。

VMCOREINFO 含内核 release、页大小、符号、SIZE/OFFSET/NUMBER 等信息。x86_64 的 phys_base、页表参数与 KERNELOFFSET，arm64 的 VA_BITS/kimage_voffset 等是架构相关，字段集合依版本/配置变化；不得将任意 VMCOREINFO 当完整 DWARF 或通用地址转换公式。

`PRSTATUS` 类 note 保存 CPU 寄存器现场，`VMCOREINFO` 描述内核布局，GNU build-id 描述所属 ELF 构建身份。vmcore 自身可能没有崩溃内核 build-id；看见某个 dump ELF 的 GNU note 也不能自动等同于 vmlinux build-id。只有采集链明确标识来源时才比较。

KASLR 使运行地址与链接地址分离，优先让 crash/drgn 在 dump 上解析。外部 addr2line 需要正确换算；模块必须独立使用模块加载地址和 section 布局，不能减去内核统一偏移。

QEMU vmcoreinfo device 是 guest 发布 note 的通道，存在设备不保证 guest 已提供有效信息，需检查实际 note。缺 note 不立即判定 dump 无效，其他工具可能有替代布局推导；如果地址推导无法验证，停止解释相关对象。

来源：[Linux VMCOREINFO](https://docs.kernel.org/admin-guide/kdump/vmcoreinfo.html)、[QEMU VMCoreInfo device](https://www.qemu.org/docs/master/specs/vmcoreinfo.html)。
