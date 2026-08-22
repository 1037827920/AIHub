# AIHub

个人收集的、觉得好用的 Agent 增强能力集合。既包含 **skill**（放进目录即用、靠 `SKILL.md` 定义能力和触发方式），也包含 **plugin**（通过插件市场安装、常驻会话）。

## 目录布局

```
.
├── skills/                  # 放进 Agent 能识别的位置即可用的 skill
│   ├── custom/              # 自己构建的 skill
│   │   └── coscmd/
│   └── external/            # 收集或引入的外部 skill
│       ├── teach/
│       ├── skill-creator/
│       ├── frontend-design/
│       ├── draw-io/
│       ├── alphaear/
│       └── writing-clearly-and-concisely/
└── plugins/     # 通过插件市场安装的插件
    └── ponytail/
```

- **skills/custom/** — 自己构建和维护的 skill。
- **skills/external/** — 从官方、社区或其他来源收集的 skill。
- 每个 skill 目录都含 `SKILL.md`（`name`、`description` 等 frontmatter），需要时再补充格式说明或资源文件。
- **plugins/** — 每个子目录对应一个插件，通常附带自己的 `README.md` 说明安装与使用。

## 概览

### Skills

| Skill | 分类 | 作用 | 触发方式 |
| --- | --- | --- | --- |
| [coscmd](#coscmd--腾讯云-cos-命令行) | 自建 | 生成和解释 COSCMD 安装、配置及 Bucket/Object 操作命令，并提示删除、覆盖、移动等风险 | 描述 COSCMD 或腾讯云 COS 命令行需求时自动触发 |
| [teach](#teach--教学工作区) | 外部 | 把当前目录当作有状态的教学工作区，陪你在多次会话中系统学习一门技能或概念 | 显式命令 `/teach` |
| [skill-creator](#skill-creator--skill-创建与优化) | 外部 | 创建、修改和评测 skill，并通过对照测试与触发评测持续优化效果 | 创建或改进 skill 时自动触发 |
| [frontend-design](#frontend-design--前端视觉设计) | 外部 | 搭建或重塑 UI 时，提供有主见、不模板化的视觉设计指导（配色、排版、布局） | 描述需求自动触发 |
| [draw-io](#draw-io--drawio-图表) | 外部 | 创建、编辑和审查 draw.io 图表：`.drawio` XML 编辑、PNG 转换、布局调整、AWS 图标 | 描述需求自动触发 |
| [alphaear-stock](#alphaear-stock--股票代码与行情) | 外部 / AlphaEar | 搜索 A 股、港股、美股代码，获取历史行情和基础面信息 | 询问股票代码、近期价格变化或公司股票信息时自动触发 |
| [alphaear-news](#alphaear-news--财经新闻与预测市场) | 外部 / AlphaEar | 拉取实时财经热点、聚合多源趋势，并获取 Polymarket 预测市场数据 | 需要实时财经新闻、热点趋势或预测市场摘要时自动触发 |
| [alphaear-search](#alphaear-search--财经搜索与本地-rag) | 外部 / AlphaEar | 统一财经搜索入口，支持 Jina、DuckDuckGo、百度和本地新闻库检索 | 需要财经网页搜索或本地资料检索时自动触发 |
| [alphaear-sentiment](#alphaear-sentiment--财经文本情绪分析) | 外部 / AlphaEar | 用 FinBERT 或 LLM 判断财经文本的正负中性、分数和理由 | 分析新闻、公告、研报片段的市场情绪时自动触发 |
| [alphaear-predictor](#alphaear-predictor--市场时间序列预测) | 外部 / AlphaEar | 使用 Kronos 做金融市场时间序列预测，并结合新闻情绪调整结果 | 需要行情预测、趋势预估或新闻修正预测时自动触发 |
| [alphaear-signal-tracker](#alphaear-signal-tracker--投资信号追踪) | 外部 / AlphaEar | 跟踪投资信号在新信息下被强化、削弱、证伪或保持不变 | 监控投资逻辑和更新信号置信度时自动触发 |
| [alphaear-reporter](#alphaear-reporter--金融报告生成) | 外部 / AlphaEar | 将财经信号和分析材料整理为结构化专业报告，并生成图表配置 | 需要把金融分析压缩成报告、摘要或章节时自动触发 |
| [alphaear-logic-visualizer](#alphaear-logic-visualizer--金融逻辑可视化) | 外部 / AlphaEar | 生成 draw.io 兼容的金融传导链、投资逻辑图和流程图 | 需要解释复杂金融逻辑链路或画图时自动触发 |
| [alphaear-deepear-lite](#alphaear-deepear-lite--deepear-lite-实时信号) | 外部 / AlphaEar | 从 DeepEar Lite 拉取最新高频金融信号、置信度、摘要和来源 | 需要快速查看 DeepEar Lite 仪表盘信号时自动触发 |
| [writing-clearly-and-concisely](#writing-clearly-and-concisely--清晰简洁地写作) | 外部 | 写给人读的文字时，套用 Strunk 的写作规则并规避 AI 写作套路，让表达更清晰有力 | 描述需求自动触发 |

### Plugins

| Plugin | 作用 | 使用方式 |
| --- | --- | --- |
| [ponytail](#ponytail--克制的资深工程师) | 写代码前先按"少即是多"的阶梯做取舍，让 agent 只写任务真正需要的代码，避免过度工程 | 安装后每次会话常驻，附 `/ponytail` 系列命令 |

## Skills

### coscmd — 腾讯云 COS 命令行

依据腾讯云 COSCMD 文档生成可直接执行的安装、配置和对象存储命令，覆盖上传、下载、同步、查询、删除、复制、移动、签名 URL、ACL、版本控制、归档恢复及分块碎片清理。

skill 会区分全局参数和子命令参数，检查 Bucket、Region、本地路径与 COS 路径，并对 `--delete`、强制删除、覆盖下载和 `move` 等高风险操作明确提示影响范围。完整命令参考位于 `skills/custom/coscmd/references/command-reference.md`。

**用法**

描述目标即可自动触发，例如：

```
用 coscmd 把 D:/project 同步上传到 archive-1250000000 的 backup/project，忽略 .log 文件
```

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

配套的格式说明：[MISSION-FORMAT.md](./skills/external/teach/MISSION-FORMAT.md)、[RESOURCES-FORMAT.md](./skills/external/teach/RESOURCES-FORMAT.md)、[LEARNING-RECORD-FORMAT.md](./skills/external/teach/LEARNING-RECORD-FORMAT.md)、[GLOSSARY-FORMAT.md](./skills/external/teach/GLOSSARY-FORMAT.md)。

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

### skill-creator — skill 创建与优化

用于从零创建 skill，或修改、评测和优化已有 skill。它覆盖完整迭代流程：明确目标与触发场景、编写 `SKILL.md`、设计测试用例、对比启用 skill 与基线时的输出，再根据人工反馈和量化结果继续改进。

目录内包含评测和打包工具：

- `scripts/run_eval.py`、`scripts/run_loop.py` — 运行触发评测和描述优化循环
- `scripts/aggregate_benchmark.py` — 汇总通过率、耗时和 token 消耗
- `eval-viewer/` — 生成可视化评审页面
- `agents/` — 提供评分、分析和盲测对比的子 agent 指令
- `references/schemas.md` — 评测、评分和 benchmark 文件格式

**用法**

这个 skill 会在创建或改进 skill 时自动触发，也可以直接点名，例如：

```
帮我创建一个用于审查数据库迁移的 skill，并设计几组测试用例
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

### AlphaEar — 金融市场分析技能组

`skills/external/alphaear/` 下是一组面向金融市场研究的组合 skill，覆盖数据获取、搜索、情绪、预测、信号追踪、报告生成和逻辑可视化。它们可以单独触发，也可以在复杂任务里互相配合，例如先用 `alphaear-news` 和 `alphaear-search` 收集信息，再用 `alphaear-sentiment`、`alphaear-predictor`、`alphaear-signal-tracker` 做判断，最后交给 `alphaear-reporter` 输出报告。

> 这些能力会访问实时数据、第三方 API 或本地模型；预测和信号分析只用于研究与辅助判断，不构成投资建议。

#### alphaear-stock — 股票代码与行情

搜索 A 股、港股、美股股票代码，并获取历史 OHLCV 行情和基础面信息。主要工具是 `scripts/stock_tools.py` 中的 `StockTools`，支持 `search_ticker`、`get_stock_price` 和 `get_stock_fundamentals`。

依赖包括 `pandas`、`requests`、`akshare`、`yfinance`。美股数据来自 Yahoo Finance，网络不可达时可能需要配置代理；A 股和港股数据主要通过 AkShare / 东方财富获取。

**用法**

```
帮我查一下 600519 最近一个月的行情和基本面
```

#### alphaear-news — 财经新闻与预测市场

拉取实时财经热点、聚合多源趋势，并获取 Polymarket 预测市场数据。`NewsNowTools.fetch_hot_news` 可按来源抓取热点，`get_unified_trends` 可合并多源趋势；`PolymarketTools.get_market_summary` 可输出活跃预测市场摘要。

可用新闻来源见 `skills/external/alphaear/alphaear-news/references/sources.md`。

**用法**

```
汇总今天微博、华尔街见闻和财联社的主要财经热点
```

#### alphaear-search — 财经搜索与本地 RAG

统一财经搜索入口，支持 Jina、DuckDuckGo、百度和本地新闻库检索。`SearchTools.search` 可指定 `jina`、`ddg`、`baidu`、`local`，`aggregate_search` 可聚合多引擎结果；本地检索通过 `hybrid_search.py` 查询 `daily_news` 数据库。

**用法**

```
搜索英伟达最新财报和市场反应，并优先复用已有本地新闻
```

#### alphaear-sentiment — 财经文本情绪分析

面向金融文本做情绪判断，输出 `positive`、`negative` 或 `neutral` 标签、-1.0 到 1.0 的分数和简短理由。短文本和批处理可用本地 FinBERT；需要更强推理时，用 skill 中的 LLM prompt 做人工式判断，再按需写回数据库。

**用法**

```
分析这条新闻对半导体板块的情绪影响，并给出分数和理由
```

#### alphaear-predictor — 市场时间序列预测

使用 Kronos 进行金融市场时间序列预测，并可结合新闻情绪对技术预测做主观修正。核心工具是 `KronosPredictorUtility`，支持生成基础预测，再通过 `references/PROMPTS.md` 中的预测调整 prompt 融合新闻逻辑。

依赖 `torch`、`transformers`、`sentence-transformers`、`pandas`、`numpy`、`scikit-learn`。模型权重只应来自可信来源；可通过 `EMBEDDING_MODEL`、`KRONOS_MODEL_PATH` 配置模型路径。

**用法**

```
基于最近行情和新闻，预测 600519 未来 7 天走势
```

#### alphaear-signal-tracker — 投资信号追踪

跟踪投资信号在新市场信息下的演化，判断信号是被强化、削弱、证伪还是基本不变，并更新置信度与强度。它会结合 `alphaear-search` 和 `alphaear-stock` 获取事实和价格，再用 `references/PROMPTS.md` 中的研究、分析和追踪 prompt 做判断。

**用法**

```
跟踪这个 AI 算力供需改善信号，看看最新新闻是强化还是削弱它
```

#### alphaear-reporter — 金融报告生成

把财经信号、搜索结果、行情变化和分析材料整理成结构化专业报告。工作流包括信号聚类、分章节写作和最终组装；需要图表时可用 `scripts/visualizer.py` 或在报告中生成 `json-chart` 配置。

**用法**

```
把这些市场信号整理成一份结构化周报，包含核心观点、证据和风险
```

#### alphaear-logic-visualizer — 金融逻辑可视化

生成 draw.io 兼容的金融逻辑图，适合展示投资假设、产业链传导、宏观到资产价格的影响路径。它使用 `references/PROMPTS.md` 生成 XML，再通过 `scripts/visualizer.py` 渲染为可查看的 HTML。

**用法**

```
把“美元走弱 -> 大宗商品上涨 -> 资源股盈利改善”的传导链画成 draw.io 图
```

#### alphaear-deepear-lite — DeepEar Lite 实时信号

从 DeepEar Lite 的实时数据源拉取最新金融信号，包含标题、摘要、情绪、置信度、推理链和来源链接。它不依赖本地数据库，主要通过 `scripts/deepear_lite.py` 中的 `DeepEarLiteTools.fetch_latest_signals` 获取数据。

**用法**

```
拉取 DeepEar Lite 最新金融信号，并按置信度排序总结
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

- **新增自建 skill**：在 `skills/custom/` 下新建目录。
- **新增外部 skill**：放入 `skills/external/`，并尽量在其 README 中保留来源、许可证和上游链接。
- 每个 skill 目录都应包含 `SKILL.md`（含 `name`、`description` 等 frontmatter），需要时再补充格式说明或资源文件。
- **新增 plugin**：在 `plugins/` 下新建一个目录，放入插件文件，并配一份 `README.md` 说明它的作用与安装使用方式。
