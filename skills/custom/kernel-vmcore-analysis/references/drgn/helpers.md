# Linux helpers 与可复用遍历

适用：任务、链表、per-CPU、文件和其他子系统对象关联。前提：先确认本地模块与签名；下列 pid helpers 的显式 Program 调用兼容本环境，其他 helper 按安装版本查询。

```python
import inspect
from drgn.helpers.linux.pid import find_task, for_each_task
from drgn.helpers.linux.list import list_for_each_entry
print(inspect.signature(find_task))
print(inspect.signature(for_each_task))
print(inspect.signature(list_for_each_entry))
```

任务枚举不要硬编码状态位。先读取实际 `task_struct`/源码，再选筛选字段：

```python
from drgn import FaultError
from drgn.helpers.linux.pid import for_each_task
for index, task in enumerate(for_each_task(prog)):
    if index >= 100000:
        print("partial: task limit reached")
        break
    try:
        print(hex(int(task)), int(task.pid), task.comm.string_())
    except FaultError as error:
        print("unreadable task", hex(int(task)), str(error))
```

此示例处理任务字段读取失败；iterator 自身读 next 时仍可能失败，调用者还应在外层捕获并将整次枚举标记为 partial。不要借异常吞掉损坏节点后发布总量。

```python
from drgn.helpers.linux.list import list_for_each_entry
head = prog["init_task"].tasks.address_of_()
for task in list_for_each_entry("struct task_struct", head, "tasks"):
    print(int(task.pid))
```

通用 helper 不等于防损坏遍历器；上例仅用于已验证链表结构，小范围探索也应加界限。需要 recover owner、container_of、rbtree/xarray、per_cpu 或文件路径时按官方 Helpers 的对应模块阅读，不自行模拟旧版布局。helper 的对象参数可能是 struct 值、指针或字段 address_of_，调用前检查签名。

`prog.stack_trace(task)` 返回栈；`trace[frame_index]["variable"]` 仅在 DWARF 和保存现场能恢复变量时使用。优化、内联、寄存器不可用和过滤的用户页可能导致局部变量/cmdline 读取失败。命名空间相关 PID helper 参数也应按当前版本确认；不要把初始 namespace PID 与容器 PID 混用。

批量输出保留 TASK 地址、PID、comm、相关对象地址和 partial/error 信息；只对实际读到的对象计数。若遍历预算耗尽，应缩小范围而非无限重试。

来源：[Helpers](https://drgn.readthedocs.io/en/latest/helpers.html)、[StackTrace API](https://drgn.readthedocs.io/en/latest/api_reference.html#drgn.StackTrace)。
