# SkillHub

个人收集的、觉得好用的 Claude Code / Agent Skill 集合。

每个子目录是一个独立的 skill，通过 `SKILL.md` 定义能力和触发方式。把这些目录放到 Agent 能识别 skill 的位置后即可使用。

## 概览

| Skill | 作用 | 触发方式 |
| --- | --- | --- |
| [teach](#teach--教学工作区) | 把当前目录当作有状态的教学工作区，陪你在多次会话中系统学习一门技能或概念 | 显式命令 `/teach` |
| [frontend-design](#frontend-design--前端视觉设计) | 搭建或重塑 UI 时，提供有主见、不模板化的视觉设计指导（配色、排版、布局） | 描述需求自动触发 |

## 已有的 Skill

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

配套的格式说明：[MISSION-FORMAT.md](./teach/MISSION-FORMAT.md)、[RESOURCES-FORMAT.md](./teach/RESOURCES-FORMAT.md)、[LEARNING-RECORD-FORMAT.md](./teach/LEARNING-RECORD-FORMAT.md)、[GLOSSARY-FORMAT.md](./teach/GLOSSARY-FORMAT.md)。

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

## 添加新的 Skill

新建一个目录，放入 `SKILL.md`（含 `name`、`description` 等 frontmatter），需要的话再补充配套的格式说明或资源文件即可。
