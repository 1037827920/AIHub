---
name: coscmd
description: 腾讯云 COSCMD 命令行工具的完整使用指南与命令生成助手。用户提到 COSCMD、腾讯云 COS 命令行、对象或目录的上传/下载/同步/删除/复制/移动、Bucket 管理、签名 URL、ACL、版本控制、归档恢复、分块碎片、COSCMD 安装配置或故障排查时，都应优先使用本 skill；即使用户没有明确说“使用 skill”，只要目标适合用 coscmd 完成也要使用。
---

# COSCMD 使用助手

依据项目根目录的 `COSCMD 工具.md` 回答并生成命令。需要精确参数或完整示例时，读取 `references/command-reference.md`；若仍有歧义，再读取原始文档。

## 工作方式

1. 识别用户的目标、操作系统、本地路径、COS 路径、Bucket（必须是 `BucketName-APPID`）和 Region。
2. 区分本地路径与 COS 对象路径。上传参数顺序是“本地 → COS”，下载是“COS → 本地”。
3. 只询问会影响命令正确性的缺失信息。可以安全使用占位符时，给出模板并明确需要替换的值。
4. 优先给出一条可复制执行的命令，再简要解释关键参数、效果和必要前置条件。
5. 用户需要跨 Bucket 操作时，把目标 Bucket/Region 放在全局参数 `-b`、`-r` 中；复制或移动的源路径使用完整 COS 域名格式。
6. 对不确定或文档未覆盖的选项，不要臆造。建议运行 `coscmd <subcommand> -h` 核实当前安装版本。

## 输出要求

- 默认用中文回答。
- 命令放在 `bash` 代码块中。
- 一个目标优先给一个推荐命令；存在明显取舍时再给备选。
- 对用户提供的路径、Bucket 和 Region 原样保留，除非格式明显错误。
- 不在回复中回显真实 SecretId、SecretKey 或临时 Token；示例一律使用占位符。
- 若用户要求直接执行命令，先确认环境中已安装并配置 COSCMD；涉及写入、覆盖、删除或移动时先说明影响范围。

## 安全规则

以下操作可能造成不可逆数据变更，生成命令时必须明确警告；如果用户要求实际执行，应先取得明确确认：

- `delete -r`、`delete -f`、`delete --versions`
- `deletebucket`，尤其 `deletebucket -f`
- `upload --delete` 或 `download --delete`
- `move`（底层先复制再删除源对象）
- 覆盖下载 `download -f`

特别注意：

- 只要输出 `move` 命令，就要明确写出两条提醒：它会在复制成功后删除源对象；源路径与目标路径不能相同，否则源文件会被删除。即使用户要求“只给必要提醒”，也不能省略。
- `deletebucket -f` 会删除 Bucket 内对象、历史版本和上传碎片。
- `--delete` 会让目标端镜像源端，并删除目标端多余文件。
- 建议使用临时密钥和最小权限，不要把密钥提交到代码仓库、日志或聊天记录。
- 默认使用 HTTPS；只有用户明确需要时才使用 `--do-not-use-ssl`。
- COSCMD 不支持上传软链接；此场景建议改用 COSCLI。

## 常见决策

### 上传与同步

- 单文件：`coscmd upload <localpath> <cospath>`
- 目录：加 `-r`
- 同步并跳过相同 MD5：加 `-s`
- 只按文件大小判断：再加 `--skipmd5`
- 让 COS 目标严格镜像本地：加 `--delete`，并提示删除风险
- 筛选文件：使用 `--ignore` 或 `--include`，通配规则建议加双引号
- 设置存储类型、元数据或限速：使用 `-H` JSON 请求头

### 下载与同步

- 单文件：`coscmd download <cospath> <localpath>`
- 目录：加 `-r`
- 覆盖同名本地文件：加 `-f`
- 同步：加 `-s`；只比较大小时加 `--skipmd5`
- 让本地严格镜像 COS：加 `--delete`，并提示会删除本地多余文件

### Bucket 与配置切换

- 默认读取 `~/.cos.conf`，日志默认写入 `~/.cos.log`。
- 临时切换 Bucket/Region：`coscmd -b <BucketName-APPID> -r <region> <action> ...`
- 指定配置和日志：`coscmd -c <config_path> -l <log_path> <action> ...`
- 全局参数必须放在子命令之前。

### 离线安装

- 用户要求按本文档安装时，默认给出文档中的 `pip download coscmd -d coscmd-packages` 和 `pip install coscmd --no-index -f coscmd-packages` 流程。
- 联网机器和离线机器的 Python 版本必须一致；还应提醒 CPU 架构和系统兼容性可能影响二进制依赖。
- 若用户需要更稳健的 Linux 部署方案，可以补充 `pip wheel`/wheelhouse 作为备选，但不要用它取代文档中的标准流程。

## 参考资料读取策略

按需读取 `references/command-reference.md` 中对应章节：

- 安装、配置和全局参数
- Bucket 管理
- 上传、下载、查询、签名 URL
- 删除、碎片清理
- 复制与移动
- ACL、版本控制、归档恢复

原始文档是最终依据；当用户询问版本差异、边界条件或参考文件未覆盖的细节时，读取项目根目录的 `COSCMD 工具.md`。
