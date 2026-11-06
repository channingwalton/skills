import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

import retro

HERE = Path(__file__).resolve().parent
T0 = 1_800_000_000.0  # an arbitrary epoch second inside every test window
START = T0 - 3600


def iso(t):
    return datetime.fromtimestamp(t, tz=UTC).isoformat().replace('+00:00', 'Z')


def assistant(t, *content, **extra):
    return {'type': 'assistant', 'timestamp': iso(t), 'cwd': extra.get('cwd', '/nowhere'),
            'message': {'role': 'assistant', 'content': list(content) or [{'type': 'text', 'text': 'ok'}]}}


def user(t, content, **extra):
    o = {'type': 'user', 'timestamp': iso(t), 'message': {'role': 'user', 'content': content}}
    o.update(extra)
    return o


def tool_use(id_, name, **input_):
    return {'type': 'tool_use', 'id': id_, 'name': name, 'input': input_}


def tool_result(id_, content, is_error=False):
    return {'type': 'tool_result', 'tool_use_id': id_, 'content': content, 'is_error': is_error}


class MeasureSessionTest(unittest.TestCase):
    def test_a_human_turn_spans_from_the_last_agent_output(self):
        s = retro.measure_session([assistant(T0), user(T0 + 60, 'next')], START)
        self.assertEqual(s.counts['turns'], 1)
        self.assertEqual(s.spans, [(T0, T0 + 60)])
        self.assertTrue(s.has_agent)

    def test_a_long_gap_is_capped_at_ten_minutes(self):
        s = retro.measure_session([assistant(T0), user(T0 + 3600, 'back')], START)
        self.assertEqual(s.spans, [(T0 + 3000, T0 + 3600)])

    def test_harness_text_is_not_a_human_turn(self):
        events = [assistant(T0),
                  user(T0 + 1, '<system-reminder>injected</system-reminder>'),
                  user(T0 + 2, '<task-notification>done</task-notification>'),
                  user(T0 + 3, 'meta', isMeta=True),
                  user(T0 + 4, 'summary', isCompactSummary=True),
                  user(T0 + 5, 'from a hook', origin={'kind': 'hook'})]
        self.assertEqual(retro.measure_session(events, START).counts['turns'], 0)

    def test_an_interrupt_is_counted_apart_from_turns(self):
        s = retro.measure_session([assistant(T0), user(T0 + 5, '[Request interrupted by user]')], START)
        self.assertEqual((s.counts['interrupts'], s.counts['turns']), (1, 0))

    def test_a_declined_call_spans_from_the_call(self):
        events = [assistant(T0, tool_use('a', 'Bash', command='rm -rf x')),
                  user(T0 + 30, [tool_result('a', "The user doesn't want to proceed with this tool use.")])]
        s = retro.measure_session(events, START)
        self.assertEqual((s.counts['declined'], s.counts['turns']), (1, 0))
        self.assertEqual(s.spans, [(T0, T0 + 30)])

    def test_questions_to_the_user_are_counted(self):
        s = retro.measure_session([assistant(T0, tool_use('q', 'AskUserQuestion'))], START)
        self.assertEqual(s.counts['asks'], 1)

    def test_events_before_the_window_are_dropped(self):
        s = retro.measure_session([assistant(START - 100), user(START - 50, 'old')], START)
        self.assertEqual(s.counts['turns'], 0)
        self.assertFalse(s.has_agent)

    def test_sidechain_events_are_ignored(self):
        e = assistant(T0)
        e['isSidechain'] = True
        self.assertFalse(retro.measure_session([e], START).has_agent)

    def test_git_dash_c_paths_are_collected(self):
        s = retro.measure_session(
            [assistant(T0, tool_use('g', 'Bash', command='git -C "/repo/a" status'), cwd='/work')], START)
        self.assertEqual(s.dirs, {'/work', '/repo/a'})


class UnionTest(unittest.TestCase):
    def test_overlapping_spans_count_once(self):
        self.assertEqual(retro.union([(0, 10), (5, 15), (20, 25)]), 20)


class AcceptedFromLogTest(unittest.TestCase):
    def entry(self, h, body):
        return f'{h} {body}\x00'

    def test_a_revert_removes_itself_and_the_commit_that_it_reverts(self):
        a, b, c = 'a' * 40, 'b' * 40, 'c' * 40
        log = (self.entry(c, f'Revert "x"\n\nThis reverts commit {a}.')
               + self.entry(b, 'keep') + self.entry(a, 'x'))
        self.assertEqual(retro.accepted_from_log(log, retro.AUTO), 1)

    def test_timer_commits_are_excluded(self):
        log = self.entry('a' * 40, 'vault backup: 2026-11-06') + self.entry('b' * 40, 'real')
        self.assertEqual(retro.accepted_from_log(log, retro.AUTO), 1)


class AcceptedRepoTest(unittest.TestCase):
    def test_reads_the_default_branch_of_a_real_repository(self):
        with tempfile.TemporaryDirectory() as d:
            def git(*args):
                subprocess.run(['git', '-C', d, '-c', 'user.name=t', '-c', 'user.email=t@t', *args],
                               check=True, capture_output=True)
            git('init', '-q', '-b', 'main')
            for name in ('one', 'two'):
                Path(d, name).write_text(name)
                git('add', name)
                git('commit', '-qm', name)
            git('revert', '--no-edit', 'HEAD')
            self.assertEqual(retro.accepted(d, 0, retro.AUTO), 1)


class AuditTest(unittest.TestCase):
    def run_audit(self, *sessions):
        return retro.audit([(f's{i}', events) for i, events in enumerate(sessions)], START)

    def test_images_are_counted_apart_from_characters(self):
        image = {'type': 'image', 'source': {'data': 'x' * 250_000}}
        a = self.run_audit([assistant(T0, tool_use('r', 'Read', file_path='/s.png')),
                            user(T0 + 1, [tool_result('r', [image])])])
        self.assertEqual(a.images, 1)
        self.assertEqual(a.oversize, 0)
        self.assertLess(a.tool_out['Read'], 100)

    def test_record_only_attachments_are_skipped(self):
        a = self.run_audit([{'type': 'attachment', 'timestamp': iso(T0),
                             'attachment': {'type': 'prompt_snapshot', 'text': 'x' * 1000}}])
        self.assertEqual(a.cat['hook/attachment'], 0)

    def test_a_reread_of_the_same_slice_is_a_duplicate_but_a_new_chunk_is_not(self):
        events = [assistant(T0, tool_use('1', 'Read', file_path='/f', offset=1, limit=10)),
                  user(T0, [tool_result('1', 'aaaa')]),
                  assistant(T0, tool_use('2', 'Read', file_path='/f', offset=11, limit=10)),
                  user(T0, [tool_result('2', 'bbbb')]),
                  assistant(T0, tool_use('3', 'Read', file_path='/f', offset=1, limit=10)),
                  user(T0, [tool_result('3', 'cccc')])]
        self.assertEqual(self.run_audit(events).dup, 4)

    def test_injected_reminders_are_split_from_user_text(self):
        a = self.run_audit([user(T0, [{'type': 'text', 'text': 'hi <system-reminder>xyz</system-reminder>'}])])
        self.assertEqual(a.cat['injected_reminder'], len('<system-reminder>xyz</system-reminder>'))
        self.assertEqual(a.cat['user_text'], len('hi '))

    def test_an_attachment_repeated_across_sessions_is_boilerplate(self):
        att = {'type': 'attachment', 'timestamp': iso(T0), 'attachment': {'type': 'skill_listing', 'x': 'y'}}
        a = self.run_audit([att], [att], [att])
        self.assertEqual(a.boilerplate(), 2 * len(json.dumps(att['attachment'])))

    def test_events_before_the_window_are_dropped(self):
        a = self.run_audit([assistant(START - 10)])
        self.assertEqual(a.active, 0)


class RestartRowTest(unittest.TestCase):
    def test_first_is_the_first_human_prompt_and_last_is_the_final_text(self):
        row = retro.restart_row([user(T0, '<command-name>/x</command-name>'),
                                 user(T0 + 1, 'Fix   the build'),
                                 assistant(T0 + 2, {'type': 'text', 'text': 'Working on it'})], START)
        self.assertEqual(row, (T0 + 2, 'Fix the build', '[assistant] Working on it'))

    def test_a_session_that_ended_before_the_window_is_not_a_row(self):
        self.assertIsNone(retro.restart_row([user(START - 5, 'old')], START))


class SelectTest(unittest.TestCase):
    def test_skips_sdk_self_old_and_optionally_subagent_transcripts(self):
        start = datetime.now(UTC).timestamp() - 3600
        with tempfile.TemporaryDirectory() as d:
            def write(rel, events, mtime=None):
                p = Path(d, rel)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('\n'.join(json.dumps(e) for e in events))
                if mtime is not None:
                    os.utime(p, (mtime, mtime))
                return str(p)
            keep = write('proj/a.jsonl', [{'entrypoint': 'cli'}])
            sub = write('proj/x/subagents/b.jsonl', [])
            write('proj/sdk.jsonl', [{'entrypoint': 'sdk-py'}])
            write('-me-retro/c.jsonl', [])
            write('proj/old.jsonl', [], mtime=start - 10)
            self.assertEqual(sorted(retro.select(d, start, '-me-retro', skip_subagents=False)), sorted([keep, sub]))
            self.assertEqual(retro.select(d, start, '-me-retro', skip_subagents=True), [keep])


class CliTest(unittest.TestCase):
    def test_measure_prints_the_window_totals(self):
        with tempfile.TemporaryDirectory() as d:
            now = datetime.now(UTC).timestamp()
            events = [assistant(now - 120), user(now - 60, 'next')]
            Path(d, 'p').mkdir()
            Path(d, 'p', 's.jsonl').write_text('\n'.join(json.dumps(e) for e in events))
            out = subprocess.run([sys.executable, str(HERE / 'retro.py'), 'measure', '--days', '1', '--root', d],
                                 check=False, capture_output=True, text=True, timeout=30)
            self.assertEqual(out.returncode, 0, msg=out.stderr)
            self.assertIn('sessions=1  human turns=1', out.stdout)

    def test_self_accepts_a_project_dir_that_starts_with_a_dash(self):
        with tempfile.TemporaryDirectory() as d:
            out = subprocess.run([sys.executable, str(HERE / 'retro.py'), 'restarts', '--days', '1',
                                  '--root', d, '--self', '-Users-me-dev-skills'],
                                 check=False, capture_output=True, text=True, timeout=30)
            self.assertEqual(out.returncode, 0, msg=out.stderr)

    def test_days_is_required(self):
        out = subprocess.run([sys.executable, str(HERE / 'retro.py'), 'context'],
                             check=False, capture_output=True, text=True, timeout=30)
        self.assertEqual(out.returncode, 2)


if __name__ == '__main__':
    unittest.main()
