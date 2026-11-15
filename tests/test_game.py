"""표준 라이브러리만 사용하는 기능/오류/프로세스 통합 테스트."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from game import QuizGame
from input_helpers import read_number, read_text
from quiz import Quiz

ROOT = Path(__file__).resolve().parents[1]


class GameTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'state.json'
        self.output = io.StringIO()
        self.redirect = contextlib.redirect_stdout(self.output)
        self.redirect.__enter__()
        self.addCleanup(self.redirect.__exit__, None, None, None)
        self.game = QuizGame(self.path)

    def test_defaults(self):
        self.assertGreaterEqual(len(self.game.quizzes), 5)
        self.assertTrue(all(isinstance(q, Quiz) for q in self.game.quizzes))

    def test_quiz_display_and_answers(self):
        q = self.game.quizzes[0]
        q.display()
        self.assertIn(q.question, self.output.getvalue())
        self.assertIn('4. ', self.output.getvalue())
        self.assertTrue(q.check_answer(1))
        self.assertFalse(q.check_answer(2))
        self.assertFalse(q.check_answer(True))

    def test_quiz_schema(self):
        for args in [('', ['a']*4, 1), ('q', ['a']*3, 1),
                     ('q', ['a', 'b', '', 'd'], 1), ('q', ['a']*4, 0),
                     ('q', ['a']*4, True), ('q', 'abcd', 1)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                Quiz(*args)

    def test_invalid_numbers_and_whitespace(self):
        with patch('builtins.input', side_effect=['abc', '', '9', '0', ' 2 ']):
            self.assertEqual(read_number('?', 1, 5), 2)
        self.assertGreaterEqual(self.output.getvalue().count('입력하세요'), 4)

    def test_required_text(self):
        with patch('builtins.input', side_effect=['', '   ', '  질문  ']):
            self.assertEqual(read_text('?'), '질문')

    def test_add_and_restart(self):
        with patch('builtins.input', side_effect=['새 문제', '가', '나', '다', '라', 'x', '5', ' 3 ']):
            self.game.add_quiz()
        restored = QuizGame(self.path)
        self.assertEqual(len(restored.quizzes), 6)
        self.assertEqual(restored.quizzes[-1].answer, 3)
        self.assertIn('새 문제', self.path.read_text(encoding='utf-8'))

    def test_interrupted_add_does_not_append(self):
        for error in [EOFError, KeyboardInterrupt]:
            with self.subTest(error=error), patch('builtins.input', side_effect=['2', '미완성', error]):
                self.game.run()
            self.assertEqual(len(QuizGame(self.path).quizzes), 5)

    def test_play_perfect_and_lower_score(self):
        with patch('builtins.input', side_effect=['1', '2', '3', '4', '1']):
            self.game.play()
        self.assertEqual(self.game.best_score, 100)
        with patch('builtins.input', return_value='4'):
            self.game.play()
        self.assertEqual(QuizGame(self.path).best_score, 100)
        self.assertIn('오답입니다', self.output.getvalue())
        self.assertIn('5문제 중 5문제 정답', self.output.getvalue())

    def test_zero_score_is_played(self):
        self.game.show_score()
        self.assertIn('아직 완료한 퀴즈가 없습니다', self.output.getvalue())
        with patch('builtins.input', side_effect=['2', '1', '1', '1', '2']):
            self.game.play()
        restored = QuizGame(self.path)
        self.assertEqual(restored.best_score, 0)
        restored.show_score()
        self.assertIn('최고 점수: 0점', self.output.getvalue())

    def test_empty_quizzes(self):
        self.game.quizzes = []
        self.game.play()
        self.game.list_quizzes()
        self.game.save_state()
        self.assertEqual(QuizGame(self.path).quizzes, [])
        self.assertIsNone(self.game.best_score)

    def test_list(self):
        self.game.list_quizzes()
        self.assertIn('총 5개', self.output.getvalue())
        self.assertIn('[5]', self.output.getvalue())

    def test_missing_file_recovered_on_exit(self):
        with patch('builtins.input', return_value='5'):
            self.game.run()
        self.assertTrue(self.path.exists())
        self.assertEqual(len(json.loads(self.path.read_text(encoding='utf-8'))['quizzes']), 5)

    def test_corrupt_json_and_schema(self):
        bad_values = ['{broken', '[]', '{}',
                      '{"quizzes": {}, "best_score": null}',
                      '{"quizzes": [], "best_score": true}',
                      '{"quizzes": [], "best_score": 101}',
                      '{"quizzes": [], "best_score": -1}',
                      '{"quizzes": [], "best_score": "3"}',
                      '{"quizzes": [null], "best_score": 0}',
                      '{"quizzes": [{}], "best_score": 0}']
        for bad in bad_values:
            with self.subTest(bad=bad):
                self.path.write_text(bad, encoding='utf-8')
                restored = QuizGame(self.path)
                self.assertEqual(len(restored.quizzes), 5)
                self.assertIsNone(restored.best_score)
                self.assertTrue(restored.save_state())
                json.loads(self.path.read_text(encoding='utf-8'))

    def test_invalid_utf8(self):
        self.path.write_bytes(b'\xff\xfe')
        self.assertEqual(len(QuizGame(self.path).quizzes), 5)

    def test_read_permission_error(self):
        with patch.object(Path, 'open', side_effect=PermissionError('test read denial')):
            restored = QuizGame(self.path)
        self.assertEqual(len(restored.quizzes), 5)
        self.assertIn('읽을 수 없어', self.output.getvalue())

    def test_write_permission_error(self):
        with patch('game.tempfile.NamedTemporaryFile', side_effect=PermissionError('test write denial')):
            self.assertFalse(self.game.save_state())
        self.assertIn('저장하지 못했습니다', self.output.getvalue())

    def test_atomic_replace_failure_preserves_old_file(self):
        self.game.save_state()
        before = self.path.read_bytes()
        self.game.best_score = 100
        with patch.object(Path, 'replace', side_effect=OSError('test replacement failure')):
            self.assertFalse(self.game.save_state())
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.path.parent.glob('.state-*.tmp')), [])

    def test_menu_interrupts_save_and_exit(self):
        for error in [EOFError, KeyboardInterrupt]:
            with self.subTest(error=error), patch('builtins.input', side_effect=error):
                self.game.run()
            self.assertTrue(self.path.exists())
        self.assertIn('안전하게 종료', self.output.getvalue())

    def test_interrupted_play_retains_previous_best(self):
        self.game.best_score = 40
        with patch('builtins.input', side_effect=['1', '1', EOFError]):
            self.game.run()
        self.assertEqual(QuizGame(self.path).best_score, 40)

    def test_state_path_is_project_root(self):
        with patch.object(QuizGame, 'load_state'):
            game = QuizGame()
        self.assertEqual(game.state_path, ROOT / 'state.json')


class ProcessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ['main.py', 'game.py', 'quiz.py', 'defaults.py', 'input_helpers.py']:
            shutil.copy2(ROOT / name, self.root / name)

    def run_cli(self, text):
        result = subprocess.run([sys.executable, '-X', 'utf8', str(self.root / 'main.py')],
                                input=text, text=True, encoding='utf-8',
                                capture_output=True, cwd=self.root.parent, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        return result.stdout

    def test_actual_cli_add_play_restart(self):
        output = self.run_cli('abc\n\n9\n 2 \n추가 문제\n가\n나\n다\n라\n2\n3\n1\n1\n2\n3\n4\n1\n2\n4\n5\n')
        self.assertIn('총 6개', output)
        self.assertIn('6문제 중 6문제 정답', output)
        self.assertIn('최고 점수: 100점', output)
        restarted = self.run_cli('3\n4\n5\n')
        self.assertIn('추가 문제', restarted)
        self.assertIn('최고 점수: 100점', restarted)

    def test_actual_eof(self):
        self.assertIn('안전하게 종료', self.run_cli(''))
        self.assertTrue((self.root / 'state.json').exists())

    @unittest.skipUnless(os.name == 'posix', '실제 SIGINT 검증은 WSL/Linux에서 수행')
    def test_actual_ctrl_c(self):
        process = subprocess.Popen([sys.executable, '-X', 'utf8', '-u', str(self.root / 'main.py')],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, encoding='utf-8')
        try:
            # 메뉴 입력 프롬프트까지 읽고 실제 Ctrl+C와 같은 SIGINT를 전송한다.
            output = ''
            while not output.endswith('메뉴 번호를 선택하세요 (1~5): '):
                character = process.stdout.read(1)
                self.assertTrue(character, output)
                output += character
            process.send_signal(signal.SIGINT)
            tail, errors = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, errors)
            self.assertIn('안전하게 종료', tail)
            self.assertNotIn('Traceback', errors)
            self.assertTrue((self.root / 'state.json').exists())
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()


if __name__ == '__main__':
    unittest.main(verbosity=2)
