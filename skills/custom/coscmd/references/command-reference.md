# COSCMD 命令参考

本参考依据项目根目录 `COSCMD 工具.md` 整理。参数以当前安装版本的 `coscmd <subcommand> -h` 输出为准。

## 1. 环境、安装与帮助

支持 Windows、Linux、macOS；本地字符集应为 UTF-8，系统时间应与标准时间同步。依赖 Python 2.7 或 Python 3 和较新版本的 pip。Python 3.12 使用 pip 安装依赖可能失败，优先考虑源码安装。

```bash
# 推荐安装、升级和查看版本
pip install coscmd
pip install coscmd -U
coscmd --version

# 源码安装
git clone https://github.com/tencentyun/coscmd.git
cd coscmd
python setup.py install

# 在联网机器准备离线包
mkdir coscmd-packages
pip download coscmd -d coscmd-packages
tar -czvf coscmd-packages.tar.gz coscmd-packages

# 在离线机器安装；两台机器的 Python 版本应一致
tar -xzvf coscmd-packages.tar.gz
pip install coscmd --no-index -f coscmd-packages

# 帮助
coscmd -h
coscmd upload -h
```

Windows 安装后可能需要把 Python 安装目录及其 `Scripts` 子目录加入 `PATH`。

## 2. 配置

推荐使用临时密钥与最小权限。默认配置文件为 `~/.cos.conf`。

```bash
coscmd config \
  -a <SECRET_ID> \
  -s <SECRET_KEY> \
  -t <TEMP_TOKEN> \
  -b <BucketName-APPID> \
  -r <REGION>
```

主要参数：

- `-a`：SecretId，必需。
- `-s`：SecretKey，必需。
- `-t`：临时密钥 Token；使用临时密钥时配置。
- `-b`：Bucket，格式必须为 `BucketName-APPID`，必需。
- `-r`：Region，必需，除非使用 Endpoint。
- `-e`：自定义 Endpoint；设置后 Region 失效。默认域名格式 `cos.<region>.myqcloud.com`，全球加速为 `cos.accelerate.myqcloud.com`。
- `-m`：最大线程数，默认 5。
- `-p`：分块大小，单位 MB，默认 1，范围 1–1000。
- `--do-not-use-ssl`：使用 HTTP。
- `--anonymous`：匿名请求，不携带签名。

配置示例（不要把真实密钥提交到仓库）：

```bash
coscmd config -a <SECRET_ID> -s <SECRET_KEY> \
  -b configure-bucket-1250000000 -r ap-chengdu
```

典型配置文件：

```ini
[common]
secret_id = <SECRET_ID>
secret_key = <SECRET_KEY>
bucket = configure-bucket-1250000000
region = ap-chengdu
max_thread = 5
part_size = 1
retry = 5
timeout = 60
schema = https
verify = md5
anonymous = False
```

`timeout` 单位为秒；`schema` 可为 `http` 或 `https`；`anonymous` 可为 `True` 或 `False`。

## 3. 全局选项

全局选项放在子命令之前：

```bash
coscmd -b <BucketName-APPID> -r <region> <action> ...
coscmd -c <config_path> -l <log_path> <action> ...
coscmd -d <action> ...       # debug，输出详细信息
coscmd -s <action> ...       # silence，不输出信息；最低版本 1.8.6.24
```

其他全局选项：

- `--log_size <MB>`：单个日志文件最大大小，默认 1 MB。
- `--log_backup_count <N>`：日志备份数量。
- `-v` / `--version`：版本。

注意全局 `-s` 表示静默模式，而 upload/download 子命令中的 `-s` 表示同步模式；位置不同，含义不同。

## 4. Bucket 管理

```bash
# 创建 Bucket；应显式指定 Bucket 和 Region
coscmd -b examplebucket-1250000000 -r ap-beijing createbucket

# 删除空 Bucket
coscmd -b examplebucket-1250000000 -r ap-beijing deletebucket

# 强制删除非空 Bucket
coscmd -b examplebucket-1250000000 -r ap-beijing deletebucket -f
```

`deletebucket -f` 会删除 Bucket 内所有对象、历史版本和上传碎片，属于高风险操作。

## 5. 上传

### 文件

```bash
coscmd upload <localpath> <cospath>
coscmd upload D:/picture.jpg doc/

# 存储类型
coscmd upload D:/picture.jpg doc/ \
  -H "{'x-cos-storage-class':'Archive'}"

# 自定义元数据
coscmd upload D:/picture.jpg doc/ \
  -H "{'x-cos-meta-example':'example'}"

# 限速 800 Kb/s
coscmd upload D:/doc/file.zip doc/ \
  -H "{'x-cos-traffic-limit':'819200'}"
```

`-H` 的内容必须为 JSON 格式。`x-cos-traffic-limit` 范围为 819200–838860800 bit/s，即 800 Kb/s–800 Mb/s。

### 目录与同步

```bash
# 递归上传
coscmd upload -r D:/doc /

# MD5 同步，跳过相同文件
coscmd upload -rs D:/doc doc

# 只比较同名文件大小
coscmd upload -rs --skipmd5 D:/doc doc

# COS 目标镜像本地，删除目标端多余文件
coscmd upload -rs --delete D:/doc /

# 排除或仅包含指定文件
coscmd upload -rs D:/doc / --ignore "*.txt,*.doc"
coscmd upload -rs D:/doc / --include "*.txt,*.doc"

# 排除指定文件夹
coscmd upload -rs D:/doc / --ignore "D:/doc/ignore_folder/*"
```

目录上传注意事项：

- Windows 推荐使用 cmd 或 PowerShell，避免 Git Bash 路径转换导致目标错误。
- `--ignore` 和 `--include` 支持 shell 通配及逗号分隔的多条规则；规则建议用双引号包裹。
- `--delete` 会删除 COS 目标端多余对象。
- 同步 MD5 依赖对象的 `x-cos-meta-md5`；COSCMD 1.8.3.2 之后上传的对象默认携带。
- `--skipmd5` 只比较文件大小，并且上传时不携带 `x-cos-meta-md5`。
- 当前版本中超过 100 MB 的文件自动分块上传；1.8.6.31 以前阈值为 10 MB。
- 分块上传支持断点续传并逐块校验 MD5。
- 不支持上传软链接，需改用 COSCLI。

## 6. 查询与对象信息

```bash
# 查询指定前缀
coscmd list doc/

# 查询全部并递归统计数量、大小
coscmd list -ar
coscmd list examplefolder/ -ar

# 限制结果数量
coscmd list -n <num> <cospath>

# 查询历史版本
coscmd list -v

# 查看对象元信息
coscmd info doc/picture.jpg
```

`list` 中 `-a` 表示全部，`-r` 表示递归并在末尾统计，空 COS 路径表示 Bucket 根目录。

## 7. 下载

### 文件

```bash
coscmd download <cospath> <localpath>
coscmd download doc/picture.jpg D:/picture.jpg
coscmd download doc/picture.jpg D:/

# 指定版本
coscmd download picture.jpg \
  --versionId <VERSION_ID> D:/

# 限速 800 Kb/s
coscmd download doc/picture.jpg D:/picture.jpg \
  -H "{'x-cos-traffic-limit':'819200'}"
```

### 目录与同步

```bash
# 递归下载
coscmd download -r doc D:/folder/

# 排除目录
coscmd download -r / D:/ --ignore "doc/*"

# 覆盖本地同名文件
coscmd download -rf / D:/examplefolder/

# MD5 同步
coscmd download -rs / D:/examplefolder

# 只比较文件大小
coscmd download -rs --skipmd5 / D:/examplefolder

# 本地目标镜像 COS，删除本地多余文件
coscmd download -rs --delete / D:/doc

# 排除或仅下载指定文件
coscmd download -rs / D:/examplefolder --ignore "*.txt,*.doc"
coscmd download -rs / D:/examplefolder --include "*.txt,*.doc"
```

本地存在同名文件时默认失败，`-f` 才会覆盖。MD5 同步依赖对象的 `x-cos-meta-md5`。`--delete` 会删除本地目标目录中 COS 源端已不存在的文件。

## 8. 签名 URL

```bash
coscmd signurl <cospath>
coscmd signurl doc/picture.jpg
coscmd signurl doc/picture.jpg -t 100
```

`-t` 指定有效期，单位为秒，默认 10000 秒。

## 9. 删除对象

```bash
# 删除单个对象
coscmd delete doc/exampleobject.txt

# 删除指定版本
coscmd delete doc/exampleobject.txt --versionId <VERSION_ID>

# 递归删除目录
coscmd delete -r doc/

# 删除目录下所有版本
coscmd delete -r doc/ --versions

# 跳过确认
coscmd delete -rf doc/
```

批量删除默认要求输入 `y`；`-f` 跳过确认。递归删除、历史版本删除和强制删除都应先确认影响范围。

## 10. 分块上传碎片

```bash
# 查询指定前缀的碎片
coscmd listparts doc/

# 清除所有上传碎片
coscmd abort
```

## 11. 复制

源路径格式：

```text
<BucketName-APPID>.cos.<region>.myqcloud.com/<cospath>
```

```bash
# 文件，目标 Bucket 由全局 -b/-r 指定
coscmd -b <TARGET_BUCKET> -r <TARGET_REGION> copy \
  <SOURCE_BUCKET>.cos.<SOURCE_REGION>.myqcloud.com/<source_object> \
  <target_path>

# 目录
coscmd -b <TARGET_BUCKET> -r <TARGET_REGION> copy -r \
  <SOURCE_BUCKET>.cos.<SOURCE_REGION>.myqcloud.com/<source_dir> \
  <target_path>

# 修改目标对象存储类型
coscmd -b <TARGET_BUCKET> -r <TARGET_REGION> copy \
  <SOURCE_HOST>/<source_object> <target_path> \
  -H "{'x-cos-storage-class':'STANDARD_IA'}"
```

`-d` 设置 `x-cos-metadata-directive`，值为 `Copy` 或 `Replaced`，默认 `Copy`。需要替换元数据时结合 `-d Replaced` 和 `-H` 使用，并通过 `coscmd copy -h` 核对当前版本的参数顺序。

## 12. 移动

移动会先复制再删除源对象；源和目标不能相同。

```bash
# 文件
coscmd -b <TARGET_BUCKET> -r <TARGET_REGION> move \
  <SOURCE_BUCKET>.cos.<SOURCE_REGION>.myqcloud.com/<source_object> \
  <target_path>

# 目录
coscmd -b <TARGET_BUCKET> -r <TARGET_REGION> move -r \
  <SOURCE_BUCKET>.cos.<SOURCE_REGION>.myqcloud.com/<source_dir> \
  <target_path>

# 同时修改目标存储类型
coscmd -b <TARGET_BUCKET> -r <TARGET_REGION> move \
  <SOURCE_HOST>/<source_object> <target_path> \
  -H "{'x-cos-storage-class':'Archive'}"
```

`move` 同样支持 `-d Copy|Replaced` 和 `-H`。执行前核对源、目标 Bucket、Region 和对象路径。

## 13. ACL

```bash
# 授予对象读取权限
coscmd putobjectacl --grant-read <UIN> <cospath>

# 授予完全控制
coscmd putobjectacl --grant-full-control <UIN> <cospath>

# 文件夹还可授予写权限
coscmd putobjectacl --grant-write <UIN> <cospath>

# 查询对象 ACL
coscmd getobjectacl <cospath>

# Bucket ACL 的完整参数
coscmd putbucketacl -h
coscmd getbucketacl -h
```

原始文档列出了 `putbucketacl`/`getbucketacl` 子命令，但未展开其参数；必须使用子命令帮助核对，不要猜测。

## 14. Bucket 版本控制

```bash
coscmd putbucketversioning Enabled
coscmd putbucketversioning Suspended
coscmd getbucketversioning
```

版本控制启用后不能恢复到“从未启用”状态，只能暂停；暂停后新上传对象不再产生多个版本。

## 15. 恢复归档对象

```bash
# 单个对象：临时副本保留 3 天，快速取回
coscmd restore -d 3 -t Expedited picture.jpg

# 递归恢复目录
coscmd restore -r -d 3 -t Expedited examplefolder/
```

- `-d <day>`：临时副本有效天数，默认 7。
- `-t <tier>`：`Expedited`（快速）、`Standard`（标准，默认）、`Bulk`（批量）。

## 16. 连通性与排错

主命令列出了 `probe` 连接测试：

```bash
coscmd probe
coscmd probe -h
```

排错顺序：

1. `coscmd --version` 确认安装。
2. 检查 UTF-8、本机时间、Python/pip 环境。
3. 检查 Bucket 是否包含 APPID、Region 是否正确。
4. 检查配置文件路径和密钥权限；临时密钥必须包含 Token。
5. 使用 `coscmd -d <action> ...` 获取详细日志。
6. 用 `coscmd <subcommand> -h` 核对当前版本选项。
