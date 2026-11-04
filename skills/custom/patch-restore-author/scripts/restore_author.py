#!/usr/bin/env python3
"""Restore format-patch author headers from Git without regenerating diffs."""

import argparse
from email.header import decode_header, make_header
from email.parser import BytesHeaderParser
from email.utils import formataddr, parseaddr
import os
from pathlib import Path
import re
import subprocess
import tempfile


HASH = rb'[0-9a-fA-F]{7,64}'
ENVELOPE = re.compile(
    rb'^From (' + HASH + rb') Mon Sep 17 00:00:00 2001\r?$', re.M
)
SOURCE_PATTERNS = (
    rb'^Upstream commit:\s*(' + HASH + rb')\b',
    rb'^commit (' + HASH + rb')(?:[ \t]+[^\r\n]*)?\r?$',
    rb'^\s*\[\s*Upstream commit (' + HASH + rb')\s*\]',
    rb'^\s*\(cherry picked from commit (' + HASH + rb')\)',
)


def git(repo, *args):
    result = subprocess.run(
        ['git', '-C', str(repo), '-c', 'i18n.logOutputEncoding=UTF-8', *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise ValueError(result.stderr.decode('utf-8', 'replace').strip())
    return result.stdout


def find_repo(path, explicit):
    if explicit:
        return explicit
    for candidate in (path.parent, Path.cwd()):
        try:
            return Path(git(candidate, 'rev-parse', '--show-toplevel').decode().strip())
        except ValueError:
            pass
    raise ValueError('找不到 Git 仓库，请传入 --repo')


def resolve_commit(repo, value):
    if not re.fullmatch(HASH, value.encode()):
        raise ValueError(f'commit 必须是 7–64 位十六进制 hash：{value}')
    try:
        return git(repo, 'rev-parse', '--verify', value + '^{commit}').strip().decode()
    except ValueError as exc:
        raise ValueError(f'无法解析原始 commit {value}；请核实仓库并获取对象') from exc


def source_commit(repo, message, envelope, explicit):
    if explicit:
        return resolve_commit(repo, explicit)
    refs = set()
    for pattern in SOURCE_PATTERNS:
        refs.update(m.decode() for m in re.findall(pattern, message, re.M | re.I))
    if not refs:
        refs.add(envelope.decode())
    commits = {resolve_commit(repo, ref) for ref in refs}
    if len(commits) != 1:
        raise ValueError('来源 commit 标记冲突，请明确指定 --commit')
    return commits.pop()


def reviewer_value(value):
    if '\r' in value or '\n' in value:
        raise ValueError('reviewer 不能包含换行')
    value = re.sub(r'^Reviewed-by:\s*', '', value.strip(), flags=re.I)
    if not re.fullmatch(r'[^<>]+\s+<[^<>\s@]+@[^<>\s@]+>', value):
        raise ValueError('reviewer 格式应为 Name <email>')
    return value


def replace_header(headers, name, value, eol):
    pattern = re.compile(
        rb'^' + name + rb':[^\r\n]*(?:\r?\n[ \t][^\r\n]*)*', re.M | re.I
    )
    if len(list(pattern.finditer(headers))) != 1:
        raise ValueError(f'需要恰好一个 {name.decode()}: 邮件头')
    return pattern.sub(lambda _: name + b': ' + value.replace(b'\n', eol), headers)


def rewrite(data, repo, explicit, reviewers):
    envelopes = list(ENVELOPE.finditer(data))
    if len(envelopes) != 1 or envelopes[0].start() != 0:
        raise ValueError('仅支持每文件一封 git format-patch 邮件；请先拆分 mbox')
    eol = b'\r\n' if data.split(b'\n', 1)[0].endswith(b'\r') else b'\n'
    header_end = data.find(eol + eol)
    if header_end < 0:
        raise ValueError('缺少邮件头/正文分隔符')
    headers = data[:header_end]
    parsed = BytesHeaderParser().parsebytes(headers + eol + eol)
    encoding = parsed.get('Content-Transfer-Encoding', '8bit').strip().lower()
    if encoding not in ('7bit', '8bit'):
        raise ValueError(f'不支持 {encoding} 邮件编码；需要明文 format-patch')
    diff = re.search(rb'^diff --git ', data[header_end:], re.M)
    if not diff:
        raise ValueError('缺少 diff --git；不支持 cover letter 或空补丁')
    diff_start = header_end + diff.start()
    separators = list(re.finditer(rb'^---\r?\n', data[header_end:diff_start], re.M))
    if not separators:
        raise ValueError('缺少 format-patch 的 --- 分隔行')
    separator = header_end + separators[-1].start()
    message_start = header_end + len(eol) * 2
    message = data[message_start:separator]
    commit = source_commit(repo, message, envelopes[0].group(1), explicit)
    metadata = git(repo, 'show', '-s', '--format=%an%x00%ae%x00%aD', commit).rstrip(b'\n')
    name, email, date = metadata.decode('utf-8').split('\0')
    author_text = f'{name} <{email}>'
    author_header = formataddr((name, email), charset='utf-8').encode('ascii')
    date = date.encode('ascii')
    updated_headers = replace_header(headers, b'From', author_header, eol)
    updated_headers = replace_header(updated_headers, b'Date', date, eol)
    existing = {
        b' '.join(value.split())
        for value in re.findall(rb'^Reviewed-by:[ \t]*([^\r\n]+)', message, re.M | re.I)
    }
    additions = []
    for reviewer in reviewers:
        key = ' '.join(reviewer.split()).encode('utf-8')
        if key not in existing:
            additions.append(b'Reviewed-by: ' + reviewer.encode('utf-8'))
            existing.add(key)
    if encoding == '7bit' and any(not line.isascii() for line in additions):
        raise ValueError('7bit 正文不能追加非 ASCII reviewer；请先转换为 UTF-8 8bit 邮件')
    updated_message = message
    if additions:
        core = message.rstrip(b'\r\n')
        trailing = message[len(core):]
        last_paragraph = core.split(eol + eol)[-1]
        has_trailers = re.search(rb'^[A-Za-z][A-Za-z0-9-]*: ', last_paragraph, re.M)
        joiner = eol if has_trailers else eol + eol
        insertion = joiner + eol.join(additions)
        updated_message = core + insertion + trailing
        if updated_message[:len(core)] + updated_message[len(core) + len(insertion):] != message:
            raise ValueError('校验失败：提交说明发生变化')
    suffix = data[separator:]
    result = updated_headers + eol + eol + updated_message + suffix
    def normalized_headers(value):
        for name in (b'From', b'Date'):
            value = replace_header(value, name, b'IGNORED', eol)
        return value
    if normalized_headers(headers) != normalized_headers(updated_headers):
        raise ValueError('校验失败：其他邮件头发生变化')
    result_headers = BytesHeaderParser().parsebytes(updated_headers + eol + eol)
    decoded_author = str(make_header(decode_header(result_headers['From'])))
    if parseaddr(decoded_author) != (name, email) or result_headers['Date'] != date.decode():
        raise ValueError('校验失败：输出的作者/日期与原始 commit 不一致')
    if result[-len(suffix):] != suffix:
        raise ValueError('校验失败：diffstat/diff/签名发生变化')
    return result, commit, author_text, date.decode()


def write_output(dest, content, mode):
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False) as stream:
            temp = Path(stream.name)
            stream.write(content)
        temp.chmod(mode & 0o777)
        os.replace(temp, dest)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
    if dest.read_bytes() != content:
        raise ValueError(f'写入后回读校验失败：{dest}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('patches', nargs='+', type=Path)
    parser.add_argument('--repo', type=Path, help='原始 commit 所在的 Git 仓库')
    parser.add_argument('--commit', help='覆盖自动来源定位；仅限单文件')
    parser.add_argument('--reviewer', action='append', default=[])
    output = parser.add_mutually_exclusive_group()
    output.add_argument('--output-dir', type=Path, default=Path('rewritten-patches'))
    output.add_argument('--in-place', action='store_true')
    parser.add_argument('--overwrite', action='store_true', help='允许覆盖输出目录的同名文件')
    args = parser.parse_args()
    try:
        if args.commit and len(args.patches) != 1:
            raise ValueError('--commit 仅限单文件；批量文件请使用各自的来源标记')
        reviewers = [reviewer_value(value) for value in args.reviewer]
        inputs = [path.resolve() for path in args.patches]
        if len(set(inputs)) != len(inputs):
            raise ValueError('输入文件重复')
        prepared = []
        destinations = set()
        for path in inputs:
            old = path.read_bytes()
            repo = find_repo(path, args.repo)
            new, commit, author, date = rewrite(old, repo, args.commit, reviewers)
            dest = path if args.in_place else (args.output_dir / path.name).resolve()
            if dest in destinations:
                raise ValueError(f'输出文件名冲突：{dest}')
            if not args.in_place and dest in inputs:
                raise ValueError('输出路径覆盖输入文件；原地修改请使用 --in-place')
            if not args.in_place and dest.exists() and not args.overwrite:
                raise ValueError(f'输出已存在：{dest}；更换目录或明确使用 --overwrite')
            if dest.exists() and not dest.is_file():
                raise ValueError(f'输出不是普通文件：{dest}')
            destinations.add(dest)
            prepared.append((path, dest, old, new, commit, author, date))
        for path, dest, old, new, commit, author, date in prepared:
            if path.read_bytes() != old:
                raise ValueError(f'输入在处理期间被修改：{path}')
            write_output(dest, new, path.stat().st_mode)
            print(f'{path.name}\n  commit: {commit}\n  From: {author}\n  Date: {date}\n  output: {dest}', flush=True)
    except (OSError, ValueError, UnicodeError) as exc:
        parser.exit(1, f'错误：{exc}\n')


if __name__ == '__main__':
    main()
