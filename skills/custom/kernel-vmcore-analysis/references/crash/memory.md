# 内存、slab、页表与不可读数据

适用：OOM、分配失败、slab 异常、页状态、用户虚拟地址和 page fault。前提：页大小、物理布局、页表层级、符号与 dump 过滤策略已检查。

```text
kmem -i
kmem -s
kmem -z
kmem -V
kmem -v
kmem -s kmalloc-64
kmem -S kmalloc-64
kmem ffff888012340000
vm 1234
vtop -c 1234 7f1234500000
pte 8000000012345067
```

`kmem -i` 是总量概览，`-s` 是 slab/cache 汇总；`-S` 展开对象/跟踪数据，应限定 cache，可能很大。`-z` 看 zone，`-V` 看 vm_stat 类统计，`-v` 看 vmalloc 映射；`kmem ADDRESS` 定位地址所属页或 slab。全局 `kmem -p` 遍历页结构，只有确需枚举且已评估规模时执行。

`vm PID` 看 VMA/用户地址空间；`vtop -c PID VA` 在对应任务上下文做虚实转换；`pte VALUE` 解码 PTE 数值，不能把页表项的地址当数值。核对 huge page、swap/migration entry 与架构位定义。`vtop` 成功只证明转换路径可解析，不证明物理页数据被 dump 保存。

OOM 应结合日志的分配 order、GFP、触发上下文、zone/cgroup 与可回收性；总 free 不为零也可能发生高阶分配失败、低端 zone 枯竭或 memcg OOM。cache 计数大并不等于泄漏；需对象归属、历史基线或多次快照。

不可读数据的处理顺序：确认地址类型与任务上下文 → 检查 KASLR/模块重定位和匹配类型 → 确认 dump 段/bitmap、过滤与文件是否完整 → 再考虑坏指针。dump 排除了 user/cache/free 页时，cmdline、文件缓存或已释放对象可能无法读取；不存在恢复被丢弃原始内容的通用转换。

对象损坏需检查 slab 分配器实现、对象是否已释放、邻接对象、redzone/poison 配置与实际类型。poison 值只在匹配配置和对象生命周期下有意义。页/folio 布局、引用计数和 compound page 字段依版本变化，读 [pahole](../elf/pahole.md)，不要用旧 offset 解释新内核。

来源：[kmem](https://crash-utility.github.io/help_pages/kmem.html)、[vm](https://crash-utility.github.io/help_pages/vm.html)、[vtop](https://crash-utility.github.io/help_pages/vtop.html)、[pte](https://crash-utility.github.io/help_pages/pte.html)。
