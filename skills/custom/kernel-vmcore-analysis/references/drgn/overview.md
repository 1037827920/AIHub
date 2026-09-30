# drgn：可编程 dump 分析

适用：任务筛选、对象遍历、跨结构关联及自定义统计。前提：安装 drgn 的 Python 环境可用，目标架构/dump 格式受当前构建支持，DWARF/模块符号匹配。压缩 kdump 支持取决于 libkdumpfile 等构建能力。

```bash
drgn --version
drgn -c /path/to/vmcore -s /path/to/vmlinux
```

交互 CLI 已建立 `prog`，并可能预导入 helper；为了可复用，示例仍显式导入：

```python
from drgn.helpers.linux.pid import find_task, for_each_task
task = find_task(prog, 1234)
print(task.comm.string_())
print(prog.stack_trace(task))
```

独立脚本使用安装 drgn 的 Python，不假设 PATH 中的 python3 与 drgn shebang 同环境：

```python
import sys
import drgn
from drgn.helpers.linux.pid import for_each_task
prog = drgn.Program()
prog.set_core_dump(sys.argv[1])
prog.load_debug_info([sys.argv[2]])
for task in for_each_task(prog):
    print(int(task.pid), task.comm.string_().decode(errors="replace"))
```

把脚本保存到用户指定输出目录后，以 `<drgn-python> script.py vmcore vmlinux` 运行。显式符号列表不保证所有模块类型都已加载；按实际故障补充匹配模块 ELF/调试信息。不要在离线 dump 脚本中调用 `set_kernel()`，它针对运行内核。

`prog["symbol"]` 得到 C 对象；`obj.member` 访问字段，`.value_()`/`int()` 转 Python 数值，`.string_()` 返回 bytes，`.address_of_()` 得到 C 指针；对象存储地址与指针值不是同一个概念。显式 Program/API 形式适合脚本，交互示例省略 prog 的 helper 调用不应机械复制。

读取异常应按对象保留：FaultError 是读取失败，不是零值；缺类型/符号与优化掉的变量要分别记录。遍历不可信链表时设数量上限、已访问地址集合并处理异常，不能把中断后的部分结果称为完整列表。详情见 [helpers](helpers.md)。

来源：[User Guide](https://drgn.readthedocs.io/en/latest/user_guide.html)、[Program API](https://drgn.readthedocs.io/en/latest/api_reference.html#drgn.Program)、[支持矩阵](https://drgn.readthedocs.io/en/latest/support_matrix.html)。
