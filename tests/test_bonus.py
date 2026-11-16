"""보너스 기능·기존 JSON 호환·실제 프로세스 회귀 검증."""
from datetime import datetime
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from game import QuizGame
from quiz import Quiz
import test_game


class BonusTests(unittest.TestCase):
    setUp = test_game.GameTests.setUp
    def test_random_subset_and_original_order(self):
        original = self.game.quizzes.copy()
        with patch('game.random.sample', return_value=[original[4], original[1]]) as sample:
            with patch('builtins.input', side_effect=['2', '1', '2']):
                self.game.play()
            sample.assert_called_once_with(original, 2)
        self.assertEqual(self.game.quizzes, original)
        self.assertEqual(self.game.history[-1]['total'], 2)
        self.assertEqual(self.game.history[-1]['score'], 100)

    def test_count_validation(self):
        with patch('builtins.input', side_effect=['abc', '', '0', '6', ' 1 ', '1']):
            self.game.play()
        self.assertEqual(self.game.history[-1]['total'], 1)

    def test_hint_repeated_only_one_penalty(self):
        with patch('builtins.input', side_effect=['1', '0', '0', '1']):
            self.game.play()
        self.assertEqual(self.game.history[-1]['hints_used'], 1)
        self.assertEqual(self.game.history[-1]['score'], 90)
        self.assertIn('추가 감점은 없습니다', self.output.getvalue())

    def test_hint_penalty_floor_zero(self):
        with patch('builtins.input', side_effect=['1', '0', '2']):
            self.game.play()
        self.assertEqual(self.game.history[-1]['score'], 0)

    def test_multiple_hints(self):
        with patch('builtins.input', side_effect=['2', '0', '1', '0', '2']):
            self.game.play()
        self.assertEqual(self.game.history[-1]['score'], 80)
        self.assertEqual(self.game.history[-1]['hints_used'], 2)

    def test_old_quiz_hint_fallback_excludes_answer(self):
        for answer in range(1, 5):
            self.output.seek(0)
            self.output.truncate()
            q = Quiz.from_dict({'question': 'q', 'choices': ['a']*4, 'answer': answer})
            q.show_hint()
            self.assertNotIn(f'{answer}번', self.output.getvalue())
        with self.assertRaises(ValueError):
            Quiz('q', ['a']*4, 1, None)

    def test_custom_hint_persists(self):
        with patch('builtins.input', side_effect=['q', 'a', 'b', 'c', 'd', '1', '  custom  ']):
            self.game.add_quiz()
        self.assertEqual(QuizGame(self.path).quizzes[-1].hint, 'custom')

    def test_legacy_state_preserves_all_data(self):
        old = {'quizzes': [dict(question='기존 문제', choices=['가','나','다','라'], answer=2)],
               'best_score': 100}
        self.path.write_text(json.dumps(old, ensure_ascii=False), encoding='utf-8')
        restored = QuizGame(self.path)
        self.assertEqual(restored.best_score, 100)
        self.assertEqual(restored.quizzes[0].question, '기존 문제')
        self.assertEqual(restored.history, [])
        restored.save_state()
        self.assertEqual(QuizGame(self.path).best_score, 100)

    def test_history_restart_and_timestamp(self):
        with patch('builtins.input', side_effect=['1', '1']):
            self.game.play()
        with patch('builtins.input', side_effect=['1', '2']):
            self.game.play()
        restored = QuizGame(self.path)
        self.assertEqual([r['score'] for r in restored.history], [100, 0])
        stamp = datetime.fromisoformat(restored.history[-1]['played_at'])
        self.assertEqual(stamp.utcoffset().total_seconds(), 9 * 3600)
        restored.show_history()
        output = self.output.getvalue()
        self.assertIn('총 2회', output)
        self.assertIn('1문제 중 0개 정답', output)

    def test_history_empty_and_interruption(self):
        self.game.show_history()
        self.assertIn('아직 저장된 점수 기록이 없습니다', self.output.getvalue())
        with patch('builtins.input', side_effect=['1', '1', '0', EOFError]):
            self.game.run()
        self.assertEqual(QuizGame(self.path).history, [])

    def test_malformed_history_recovers(self):
        valid = {'played_at': '2026-11-16T00:00:00+09:00', 'total': 1,
                 'correct': 1, 'hints_used': 0, 'score': 100}
        cases = [None, {}, [None], [{}]]
        for field, value in [('played_at', 'no date'), ('played_at', 0),
                             ('played_at', '2026-11-16T00:00:00'),
                             ('total', 0), ('total', True), ('correct', 2),
                             ('hints_used', -1), ('hints_used', 2), ('score', 80)]:
            cases.append([{**valid, field: value}])
        for history in cases:
            with self.subTest(history=history):
                self.path.write_text(json.dumps({'quizzes': [], 'best_score': 100,
                                                 'history': history}), encoding='utf-8')
                restored = QuizGame(self.path)
                self.assertEqual(len(restored.quizzes), 5)
                self.assertEqual(restored.history, [])

    def test_delete_cancel_and_confirm(self):
        original = self.game.quizzes.copy()
        for inputs in [['0'], ['1', '2']]:
            with patch('builtins.input', side_effect=inputs):
                self.game.delete_quiz()
            self.assertEqual(self.game.quizzes, original)
        with patch('builtins.input', side_effect=['abc', '9', '2', '1']):
            self.game.delete_quiz()
        restored = QuizGame(self.path)
        self.assertEqual(len(restored.quizzes), 4)
        self.assertNotIn(original[1].question, [q.question for q in restored.quizzes])

    def test_delete_last_and_empty(self):
        self.game.quizzes = self.game.quizzes[:1]
        with patch('builtins.input', side_effect=['1', '1']):
            self.game.delete_quiz()
        restored = QuizGame(self.path)
        restored.delete_quiz()
        restored.play()
        self.assertEqual(restored.quizzes, [])

    def test_delete_interrupt_no_mutation(self):
        self.game.save_state()
        with patch('builtins.input', side_effect=['6', '1', EOFError]):
            self.game.run()
        self.assertEqual(len(QuizGame(self.path).quizzes), 5)

    def test_delete_write_failure(self):
        self.game.save_state()
        with patch.object(self.game, 'save_state', return_value=False):
            with patch('builtins.input', side_effect=['1', '1']):
                self.game.delete_quiz()
        self.assertEqual(len(self.game.quizzes), 4)
        self.assertEqual(len(QuizGame(self.path).quizzes), 5)
        self.assertIn('파일 저장은 실패했습니다', self.output.getvalue())

    def test_history_saved_after_delete(self):
        with patch('builtins.input', side_effect=['1', '1']):
            self.game.play()
        with patch('builtins.input', side_effect=['1', '1']):
            self.game.delete_quiz()
        restored = QuizGame(self.path)
        self.assertEqual(restored.history[0]['total'], 1)
        self.assertEqual(restored.best_score, 100)


class BonusProcessTests(unittest.TestCase):
    setUp = test_game.ProcessTests.setUp
    run_cli = test_game.ProcessTests.run_cli
    def test_actual_bonus_cli_roundtrip(self):
        state = {'quizzes': [dict(question='테스트', choices=['가','나','다','라'],
                                 answer=1, hint='커스텀 힌트')], 'best_score': None}
        (self.root / 'state.json').write_text(json.dumps(state), encoding='utf-8')
        output = self.run_cli('1\n1\n0\n0\n1\n7\n6\n1\n2\n5\n')
        self.assertIn('커스텀 힌트', output)
        self.assertIn('90점', output)
        self.assertIn('총 1회', output)
        output = self.run_cli('7\n6\n1\n1\n3\n5\n')
        self.assertIn('90점', output)
        self.assertIn('퀴즈를 삭제하고 저장했습니다', output)
        saved = json.loads((self.root / 'state.json').read_text(encoding='utf-8'))
        self.assertEqual(saved['quizzes'], [])
        self.assertEqual(saved['history'][0]['hints_used'], 1)
        self.assertEqual(saved['best_score'], 90)


if __name__ == '__main__':
    unittest.main(verbosity=2)
