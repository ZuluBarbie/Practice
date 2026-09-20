import contextlib
import copy
import io
import json
from collections import deque
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import main as game


def solve(maze):
    queue = deque([(1, 1, [])])
    seen = {(1, 1)}
    while queue:
        row, col, route = queue.popleft()
        if maze[row][col] == "E":
            return route
        for key, (dr, dc) in game.DIRECTIONS.items():
            nr, nc = row + dr, col + dc
            if (0 <= nr < len(maze) and 0 <= nc < len(maze[nr])
                    and maze[nr][nc] != "#" and (nr, nc) not in seen):
                seen.add((nr, nc))
                queue.append((nr, nc, route + [key]))
    raise AssertionError("Maze has no exit route")


class GameTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "scores.json"
        self.score_patch = patch.object(game, "SCORES_PATH", self.path)
        self.score_patch.start()
        self.addCleanup(self.score_patch.stop)

    def run_game(self, commands):
        output = io.StringIO()
        with patch("builtins.input", side_effect=commands), contextlib.redirect_stdout(output):
            game.main()
        return output.getvalue()

    def test_all_levels_win_without_mutating_layouts(self):
        original = copy.deepcopy(game.MAZES)
        for level, maze in game.MAZES.items():
            with self.subTest(level=level):
                route = solve(maze)
                output = self.run_game([level, *route, "n"])
                self.assertIn("YOU ESCAPED!", output)
                self.assertEqual(game.load_scores()[level]["moves"], len(route))
        self.assertEqual(game.MAZES, original)

    def test_invalid_input_walls_and_case(self):
        route = solve(game.MAZES["1"])
        output = self.run_game(["bad", " 1 ", "?", "w", *[f" {m.upper()} " for m in route], "n"])
        self.assertIn("Invalid choice", output)
        self.assertIn("You hit a wall", output)
        self.assertIn("Please use only", output)
        self.assertEqual(game.load_scores()["1"]["moves"], len(route))

    def test_replay_completes_two_rounds(self):
        route = solve(game.MAZES["1"])
        output = self.run_game(["1", *route, "y", "1", *route, "n"])
        self.assertEqual(output.count("YOU ESCAPED!"), 2)

    def test_quit_and_interrupted_input(self):
        for commands in (["q"], ["1", "q"], [EOFError()], [KeyboardInterrupt()]):
            self.assertIn("Thanks for playing!", self.run_game(commands))
        self.assertFalse(self.path.exists())

    def test_score_ranking(self):
        previous = {"moves": 8, "time": 10.0}
        for current, expected in [({"moves": 7, "time": 20}, True),
                                  ({"moves": 8, "time": 9}, True),
                                  ({"moves": 8, "time": 10}, False),
                                  ({"moves": 9, "time": 1}, False)]:
            self.assertEqual(game.is_better_score(current, previous), expected)
        self.assertTrue(game.is_better_score(previous, None))

    def test_scores_missing_damaged_and_roundtrip(self):
        self.assertEqual(game.load_scores(), {})
        for data in ('broken', '[]', '{"1": {"moves": "bad", "time": 2}}',
                     '{"1": {"moves": 8, "time": NaN}}'):
            self.path.write_text(data, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(game.load_scores(), {})
        scores = {"1": {"moves": 8, "time": 10.0}}
        self.assertTrue(game.save_scores(scores))
        self.assertEqual(game.load_scores(), scores)

    def test_save_failure_is_reported(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertFalse(game.save_scores({}, Path(self.temp.name)))
        self.assertIn("Could not save", output.getvalue())

    def test_large_integer_time_does_not_crash_loading(self):
        scores = {"1": {"moves": 8, "time": 10 ** 400}}
        self.path.write_text(json.dumps(scores), encoding="utf-8")
        self.assertEqual(game.load_scores(), scores)

    def test_real_cli_from_another_folder(self):
        result = subprocess.run([sys.executable, str(Path(game.__file__).resolve())],
                                input="q\n", text=True, capture_output=True,
                                cwd=self.temp.name, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PYTHON MAZE GAME", result.stdout)
        self.assertIn("Thanks for playing!", result.stdout)
        self.assertFalse((Path(self.temp.name) / "best_scores.json").exists())


if __name__ == "__main__":
    unittest.main()
