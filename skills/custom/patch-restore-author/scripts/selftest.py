#!/usr/bin/env python3
"""Exercise the CLI in a temporary Git repository; no network or user-file writes."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().with_name('restore_author.py')
REVIEW = 'Wei Yang <albinwyang@tencent.com>'


class RestoreAuthorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='patch-restore-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.env = dict(os.environ, GIT_AUTHOR_NAME='原作者',
                        GIT_AUTHOR_EMAIL='source@example.com',
                        GIT_AUTHOR_DATE='2025-03-10T11:49:46+0930',
                        GIT_COMMITTER_NAME='Committer',
                        GIT_COMMITTER_EMAIL='committer@example.com',
                        GIT_COMMITTER_DATE='2026-11-04T16:00:00+0000')
        self.git('init', '-q')
        (self.repo / 'file').write_text('base\n')
        self.git('add', '.')
        self.git('commit', '-q', '-m', 'Base')
        self.base = self.git('rev-parse', 'HEAD').strip()
        (self.repo / 'file').write_text('changed\n')
        (self.repo / 'binary').write_bytes(bytes(range(256)))
        self.git('add', '.')
        self.git('commit', '-q', '-m', 'Example change\n\nSigned-off-by: Source <source@example.com>')
        self.commit = self.git('rev-parse', 'HEAD').strip()
        self.original = self.git('format-patch', '-1', '--stdout', '--binary')
        self.input = self.root / 'input.patch'
        data = re.sub(rb'^From: [^\n]*(?:\n[ \t][^\n]*)*',
                      b'From: Downstream <downstream@example.com>', self.original, count=1, flags=re.M)
        data = re.sub(rb'^Date: .*$', b'Date: Wed, 4 Nov 2026 16:00:00 +0000', data, count=1, flags=re.M)
        self.input.write_bytes(data.replace(b'\n\n', b'\n\ncommit ' + self.commit + b' opencloudos\n\n', 1))

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], env=self.env)

    def run_cli(self, *extra, success=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.input), '--repo', str(self.repo), *extra],
            cwd=self.root, capture_output=True,
        )
        self.assertEqual(result.returncode == 0, success, result.stderr.decode())
        return self.root / 'rewritten-patches' / self.input.name

    def test_recovery_and_git_mailinfo(self):
        before = self.input.read_bytes()
        output = self.run_cli('--reviewer', REVIEW).read_bytes()
        self.assertEqual(self.input.read_bytes(), before)
        self.assertEqual(output.split(b'\n---\n', 1)[1], before.split(b'\n---\n', 1)[1])
        info = subprocess.check_output(
            ['git', 'mailinfo', str(self.root / 'message'), str(self.root / 'diff')], input=output,
        ).decode()
        self.assertIn('Author: 原作者', info)
        self.assertIn('Email: source@example.com', info)
        self.assertIn('Date: Mon, 10 Mar 2025 11:49:46 +0930', info)
        self.assertEqual(output.count(b'Reviewed-by: ' + REVIEW.encode()), 1)

    def test_optional_reviewer_and_idempotency(self):
        output = self.run_cli()
        self.assertNotIn(b'Reviewed-by:', output.read_bytes())
        self.input.write_bytes(output.read_bytes())
        self.run_cli('--in-place', '--reviewer', 'Reviewed-by: ' + REVIEW, '--reviewer', REVIEW)
        first = self.input.read_bytes()
        self.run_cli('--in-place', '--reviewer', REVIEW)
        self.assertEqual(self.input.read_bytes(), first)
        self.assertEqual(first.count(b'Reviewed-by:'), 1)

    def test_crlf_and_existing_output_protection(self):
        self.input.write_bytes(self.input.read_bytes().replace(b'\n', b'\r\n'))
        output = self.run_cli('--reviewer', REVIEW)
        content = output.read_bytes()
        self.assertNotIn(b'\n', content.replace(b'\r\n', b''))
        self.run_cli(success=False)
        self.assertEqual(output.read_bytes(), content)

    def test_envelope_fallback_and_explicit_override(self):
        self.input.write_bytes(self.original)
        self.run_cli('--in-place')
        self.input.write_bytes(self.input.read_bytes().replace(self.commit + b' Mon', b'f' * 40 + b' Mon', 1))
        self.run_cli('--in-place', '--commit', self.commit.decode())

    def test_missing_or_conflicting_source(self):
        valid = self.input.read_bytes()
        self.input.write_bytes(valid.replace(b'commit ' + self.commit, b'commit ' + b'f' * 40))
        self.run_cli(success=False)
        self.assertFalse((self.root / 'rewritten-patches').exists())
        self.input.write_bytes(valid.replace(b'\nSigned-off-by:', b'\nUpstream commit: ' + self.base + b'\n\nSigned-off-by:', 1))
        self.run_cli(success=False)

    def test_batch_preflight_and_invalid_reviewer(self):
        bad = self.root / 'bad.patch'
        bad.write_bytes(self.input.read_bytes().replace(self.commit, b'f' * 40))
        self.run_cli(str(bad), success=False)
        self.assertFalse((self.root / 'rewritten-patches').exists())
        self.run_cli('--reviewer', 'Person <p@example.com>\nInjected: header', success=False)

    def test_multi_message_and_encoded_body_rejected(self):
        valid = self.input.read_bytes()
        self.input.write_bytes(valid + valid)
        self.run_cli(success=False)
        self.input.write_bytes(valid.replace(b'\n\n', b'\nContent-Transfer-Encoding: base64\n\n', 1))
        self.run_cli(success=False)


if __name__ == '__main__':
    unittest.main()
