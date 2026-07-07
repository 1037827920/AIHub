# AIHub

个人收集的、觉得好用的 Agent 增强能力集合。既包含 **skill**（放进目录即用、靠 `SKILL.md` 定义能力和触发方式），也包含 **plugin**（通过插件市场安装、常驻会话）。

## 目录布局

```
.
├── skills/      # 放进 Agent 能识别的位置即可用的 skill
│   ├── teach/
│   ├── frontend-design/
│   ├── draw-io/
│   └── writing-clearly-and-concisely/
└── plugins/     # 通过插件市场安装的插件
    └── ponytail/
```

- **skills/** — 每个子目录是一个独立 skill，含 `SKILL.md`（`name`、`description` 等 frontmatter），需要的话再补充格式说明或资源文件。
- **plugins/** — 每个子目录对应一个插件，通常附带自己的 `README.md` 说明安装与使用。

## 概览

### Skills

| Skill | 作用 | 触发方式 |
| --- | --- | --- |
| [teach](#teach--教学工作区) | 把当前目录当作有状态的教学工作区，陪你在多次会话中系统学习一门技能或概念 | 显式命令 `/teach` |
| [frontend-design](#frontend-design--前端视觉设计) | 搭建或重塑 UI 时，提供有主见、不模板化的视觉设计指导（配色、排版、布局） | 描述需求自动触发 |
| [draw-io](#draw-io--drawio-图表) | 创建、编辑和审查 draw.io 图表：`.drawio` XML 编辑、PNG 转换、布局调整、AWS 图标 | 描述需求自动触发 |
| [writing-clearly-and-concisely](#writing-clearly-and-concisely--清晰简洁地写作) | 写给人读的文字时，套用 Strunk 的写作规则并规避 AI 写作套路，让表达更清晰有力 | 描述需求自动触发 |

### Plugins

| Plugin | 作用 | 使用方式 |
| --- | --- | --- |
| [ponytail](#ponytail--克制的资深工程师) | 写代码前先按"少即是多"的阶梯做取舍，让 agent 只写任务真正需要的代码，避免过度工程 | 安装后每次会话常驻，附 `/ponytail` 系列命令 |

## Skills

### teach — 教学工作区

把当前目录当作一个有状态的教学工作区，陪你在多次会话中系统地学习一门技能或概念。

核心理念是把学习拆成三层：从高质量资源中获取 **知识**、通过交互式课程练成 **技能**、在真实社区互动中沉淀 **智慧**；并刻意用检索练习、间隔、交叉等方式提升长期记忆（storage strength）而非临场熟练（fluency strength）。

工作区里会维护这些文件：

- `MISSION.md` — 你学习这个主题的原因，用来锚定所有教学
- `RESOURCES.md` — 可信资源清单
- `./lessons/*.html` — 一节节自包含、短小精美的 HTML 课程（主要产出单元）
- `./reference/*.html` — 速查表、术语表等压缩后的参考资料
- `./learning-records/*.md` — 记录你已掌握的内容和关键洞察，用于判断下一步该教什么
- `./assets/*` — 课程间复用的组件（样式表、测验小工具等）
- `NOTES.md` — 记录你的学习偏好和临时笔记

配套的格式说明：[MISSION-FORMAT.md](./skills/teach/MISSION-FORMAT.md)、[RESOURCES-FORMAT.md](./skills/teach/RESOURCES-FORMAT.md)、[LEARNING-RECORD-FORMAT.md](./skills/teach/LEARNING-RECORD-FORMAT.md)、[GLOSSARY-FORMAT.md](./skills/teach/GLOSSARY-FORMAT.md)。

**用法**

开始一个新主题：

```
/teach 我想学习 Rust，帮我建立一个教学工作区
```

针对已有工作区继续学习：

```
/teach 继续我的 Rust 学习，给我出下一课
```

让 agent 把这个教学区的用法整理进 README：

```
这个教学区要怎么使用，整理记录到 README 中
```

### frontend-design — 前端视觉设计

在从零搭建 UI 或重塑现有界面时，提供有主见、不模板化的视觉设计指导，覆盖美学方向、配色、排版和布局。

它把自己定位成一个小型设计工作室的设计负责人：先把产品/主题、受众和页面的核心目标钉死，再从主题本身的世界里提炼出独特的设计选择，并敢于承担一个能被论证的美学风险。skill 里还专门提醒了当前 AI 生成设计常见的三种"套路"外观，帮你有意识地避开默认答案。

工作流是 **头脑风暴 → 探索 → 计划 → 自我批判 → 构建 → 再批判**：先产出一套紧凑的设计 token（配色、字体、布局、招牌元素），对照 brief 检查是否落入通用默认，修订后再严格按计划写代码。同时强调把文案当作设计材料来对待。

**用法**

这个 skill 通过描述来自动触发，在你请求做界面/视觉设计时会被调用。也可以直接提出需求，例如：

```
帮我设计一个咖啡烘焙工作室的落地页，要有独特的视觉识别
```

### draw-io — draw.io 图表

创建、编辑和审查 [draw.io](https://www.drawio.com/) 图表。适用于 `.drawio` XML 的直接编辑、导出为 PNG、坐标与布局微调，以及使用官方 AWS 图标画架构图。

它把一套画图经验固化成规则：只改 `.drawio` 源文件（PNG 由 pre-commit hook 自动生成）、字体和字号设定、箭头放到底层且不压住标签、背景框与内部元素留足 30px 边距、去掉无关装饰元素，并给出一份成图前的检查清单。还提供渐进式披露（Context / System / Component / 部署 / 数据流 / 时序图分层）等设计原则。

目录里带了配套脚本和参考资料：

- `scripts/convert-drawio-to-png.sh` — 把 `.drawio` 转成高清 PNG
- `scripts/find_aws_icon.py` — 按名称搜索 AWS 官方图标
- `references/layout-guidelines.md`、`references/aws-icons.md` — 布局与图标参考

**用法**

这个 skill 通过描述自动触发，在你需要画图或改图时被调用，例如：

```
帮我用 draw.io 画一张这个服务的 AWS 架构图
```

### writing-clearly-and-concisely — 清晰简洁地写作

在写任何给人读的文字时（文档、README、commit message、PR 描述、报错文案、UI 文案、代码注释、报告），套用 William Strunk Jr.《The Elements of Style》的经典规则，写出更清晰、更有力的表达。

它同时覆盖"该做什么"和"不该做什么"两面：一面是 Strunk 的核心原则（主动语态、正面表述、具体用词、删掉多余的词），另一面是有意识地规避 AI 写作常见的套路（浮夸修饰、空话套话、推销式形容词）。附带 `elements-of-style/` 分章详解和 `signs-of-ai-writing.md`，在上下文紧张时还建议把草稿连同相关章节交给子 agent 去做校订。

**用法**

这个 skill 通过描述自动触发，在你请求写作或改写文字时被调用，例如：

```
帮我把这段 README 改得更简洁清晰
```

## Plugins

### ponytail — 克制的资深工程师

把一位"话不多、只写一行、但代码能跑"的资深工程师塞进你的 AI agent：写代码前先沿着一条"少即是多"的阶梯做取舍，只写任务真正需要的部分，从根上避免过度工程（同时不砍校验、安全和可访问性）。

它是一个通过插件市场安装的插件，而非放进目录即用的 skill。安装、命令和各家 agent 的接入方式详见 [plugins/ponytail/README.md](./plugins/ponytail/README.md)。

## 添加新的能力

- **新增 skill**：在 `skills/` 下新建一个目录，放入 `SKILL.md`（含 `name`、`description` 等 frontmatter），需要的话再补充配套的格式说明或资源文件。
- **新增 plugin**：在 `plugins/` 下新建一个目录，放入插件文件，并配一份 `README.md` 说明它的作用与安装使用方式。
