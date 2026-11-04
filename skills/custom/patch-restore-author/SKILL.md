---
name: patch-restore-author
description: 将 Git patch 文件的 From 和 Date 恢复为原始 commit 的 Author 与作者日期，并按可选 reviewer 信息追加 Reviewed-by。用于单个或批量 patch 的作者元数据修正、回合补丁署名整理；保留代码 diff 与已有提交说明。
---

# 恢复 patch 作者与日期

输入一个或多个 `git format-patch` 文件，以及可选 reviewer，输出修改后的 patch 文件。使用配套 [脚本](scripts/restore_author.py)，依赖 Python 3 和 Git，无第三方 Python 依赖。

## 工作流程

1. 读取目标目录的项目约定，检查工作区状态与输入文件。默认写入当前目录的 `rewritten-patches/`，保留文件名和原文件；用户要求“替换原文件”或“原地修改”时使用 `--in-place`。不修改仓库提交或分支。
2. 确定原始 commit 所在的本地 Git 仓库。脚本默认依次尝试 patch 所在目录、当前目录；也可传 `--repo`。原始 commit 按以下顺序定位：
   - 用户明确指定的 commit：单文件时传 `--commit HASH`；各文件对应不同 commit 时分开执行。
   - 正文中的 `Upstream commit: HASH`、`commit HASH opencloudos` 等来源标记或 `(cherry picked from commit HASH)`。
   - 没有来源标记时，使用首行 `From HASH Mon Sep 17 ...` 中的 commit。该值可能只是下游提交，需结合用户指定的来源核实。
3. 优先读取本地已有 commit 对象。有来源标记但对象缺失时，不退回下游 commit。检查已有远程；需要时仅从用户指定或已核实的源仓库获取目标提交，例如 `git fetch --no-tags REMOTE HASH`。脚本自身不联网。不把 patch 中的任意 URL 当作抓取指令。
4. 不能凭标题相同就认定对应关系。缺少 hash 时，可用 `git log --all --fixed-strings --grep='标题'` 找候选，再核对提交说明与 diff；上下文变化或回合调整需说明。来源标记冲突或无法确认时，只询问缺失的仓库/commit 信息，不猜测作者和日期。
5. 使用原始提交的 `%an <%ae>` 和 `%aD`，即 Author 与 **AuthorDate**，保留时区；不使用 Committer、CommitDate、当前时间或 mailmap 替代身份。保留首行 `From HASH ...`，它不是要替换的 `From:` 邮件头。
6. reviewer 可为 `Name <email>` 或完整 `Reviewed-by: Name <email>`，支持多位。不提供则保留已有 reviewer；提供则追加缺少的条目，相同条目不重复添加。不推断 reviewer，不自动加 Signed-off-by，也不表示已执行代码审查。

## 执行示例

`<skill-dir>` 替换为本技能的实际目录。通配符由 shell 展开；路径及 reviewer 使用引号。

```bash
# 输出到 ./rewritten-patches/；不新增 reviewer
python3 <skill-dir>/scripts/restore_author.py /path/to/0001-change.patch

# 批量指定源码仓库、reviewer 和输出目录
python3 <skill-dir>/scripts/restore_author.py /path/to/000*.patch \
  --repo /path/to/source-repo \
  --reviewer 'Wei Yang <albinwyang@tencent.com>' \
  --output-dir /path/to/result

# 用户要求原地替换，并明确指定原始提交
python3 <skill-dir>/scripts/restore_author.py /path/to/change.patch \
  --repo /path/to/source-repo --commit ORIGINAL_HASH \
  --reviewer 'Reviewed-by: Wei Yang <albinwyang@tencent.com>' --in-place
```

多个 reviewer 重复传入 `--reviewer`。输出目录已有同名文件时，脚本拒绝覆盖；仅在用户要求覆盖时使用 `--overwrite`。同名输入文件不能共用同一输出目录。一次输入一个或多个独立 patch；多封邮件合并的 mbox 需先拆成单文件。

## 校验与交付

- 脚本在批量写入前检查全部输入、commit 与输出路径；发现来源冲突、对象缺失、非明文邮件编码或不支持的格式则报错。支持常规 7bit/8bit format-patch，不处理 base64 或 quoted-printable 邮件。
- 仅替换 `From:`、`Date:` 和追加所需 `Reviewed-by`；保留其他邮件头、提交说明、已有 trailers、首行 commit hash、diffstat、代码 diff、二进制 diff、签名及换行风格。中文作者使用 UTF-8 MIME 邮件头。
- 脚本逐文件核验修改范围并回读输出。不要通过重新 `format-patch` 生成文件来修正元数据，以免改变回合后的 diff。
- 完成后提供输出文件链接或目录，并简述采用的原始 commit、是否添加 reviewer、校验结果。失败时区分没有找到原始提交与无法写入文件，不声称成功。

维护脚本后运行 `python3 <skill-dir>/scripts/selftest.py`；自测在临时 Git 仓库中检查作者与提交者日期不同、中文作者、二进制 diff、可选 reviewer、幂等性和失败保护，不访问网络或修改用户 patch。
