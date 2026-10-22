# AIHub 维护指南

## 项目定位

AIHub 是个人维护的 Agent 能力与配置集合，主要收录 skill、插件说明和 Codex 配置。仓库没有统一的应用入口、构建流程或测试命令；验证应针对本次修改涉及的文件。

默认使用中文编写仓库级说明，保留命令、路径、代码标识符和 skill 名称的原文。外部资源沿用原有语言与风格。

## 目录约定

- `skills/custom/`：自行构建和维护的 skill。
- `skills/external/`：引入的外部 skill；`alphaear/` 是包含多个独立 skill 的技能组。
- `plugins/`：插件或插件安装使用说明。目前 `ponytail/` 仅包含 `README.md`，不包含插件实现。
- `codex-config/config.toml`：收集的 Codex 配置，包含环境相关设置。
- `README.md`：能力索引、目录树和使用说明。
- `auto-commit.sh`：暂存全部改动、提交并推送的快捷脚本。

## 修改约定

1. 修改前阅读目标目录的 `SKILL.md`、`README.md` 及相关引用文件，按现有组织方式做最小必要改动。
2. 每个独立 skill 保留 `SKILL.md` 入口及 YAML frontmatter 中的 `name`、`description`。名称应与调用方式一致；目录名不一定等于 skill 名，例如 `fitness-diet-planner-free/` 对应 `fitness-diet-planner`。
3. 脚本放入所属 skill 的 `scripts/`，参考资料放入 `references/`；格式说明、模板、资源和评测文件沿用所在目录的约定。
4. 修改外部 skill 时保留来源、上游链接、许可证和署名，避免顺带重排或改写无关的外部文件。
5. 新增、删除、重命名或移动能力后，同步更新根 README 的目录树、概览表、数量、详情和链接。统计独立 skill 时以 `SKILL.md` 为准，技能组目录不重复计数。
6. 文档使用相对路径链接；命令示例明确参数和占位符，不把示例输出写成已验证的结果。
7. 配置变更保留与任务无关的用户设置；凭据使用占位符或环境变量，不提交真实密钥、token 或密码。

## 验证方式

从仓库根目录执行，按改动选择检查：

- 所有改动：运行 `git diff --check`，并检查 `git diff` 与 `git status --short`，确认修改范围。
- README 或目录调整：用 `rg --files skills -g SKILL.md` 核对能力清单，检查目录树、相对链接和概览锚点是否匹配实际文件与标题。
- Skill 入口：检查 YAML frontmatter 和引用路径。可运行 `python3 skills/external/skill-creator/scripts/quick_validate.py <skill目录>`；该工具依赖 PyYAML，仅校验基本格式，不能替代功能验证。
- Python 脚本：检查修改文件的语法，并运行所属 skill 的相关自测或测试；依赖与环境要求以该 skill 的说明为准。
- 训练饮食计算器：相关逻辑变更后运行 `python3 skills/external/fitness-diet-planner-free/scripts/selftest.py`。
- Shell 脚本：运行 `bash -n <脚本路径>` 检查语法，并按需进行不产生外部副作用的功能验证。
- TOML 或 JSON：使用可用的解析器检查修改文件的格式；不要在验证日志中输出凭据。

纯文档改动只需核对内容、链接和差异，无需运行不相关的模型、API 调用或性能采集。缺少依赖或测试环境时，说明未执行的检查及原因。

## 提交与交付

完成后简要说明改动和实际执行的验证。只有用户要求提交或推送时才执行相应操作；`auto-commit.sh` 会执行 `git add .` 和 `git push`，不能用作验证命令。需要提交时先检查暂存范围，避免带入与本次任务无关的修改。
