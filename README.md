# Python Maze Game

A terminal maze game with three difficulty levels. Guide `P` to `E` without walking through the `#` walls.

## Run

Install Python 3.10 or newer. No third-party packages are required.
From this folder, run:

```sh
python main.py
```

On Windows, `py main.py` also works if the Python launcher is installed.

## Play

- Choose `1` (Easy), `2` (Medium), or `3` (Hard).
- Type `W` (up), `A` (left), `S` (down), or `D` (right), then press Enter.
- Uppercase letters and surrounding spaces are accepted.
- Walls and invalid commands do not count as moves.
- Type `Q` at the difficulty or movement prompt to quit. Ctrl+C or end of input also exits cleanly.
- Reach `E` to see your move count and elapsed time. Enter `y` to start another round.

## Best scores

Each difficulty has its own record. Fewer moves wins; equal move counts are compared by elapsed time rounded to tenths of a second. Timing starts when the round begins.

Records are stored in `best_scores.json` beside `main.py`, regardless of the launch folder. This personal data file is ignored by Git. Missing or malformed records do not prevent play; the next saved record may replace an unreadable file. A save failure is reported without crashing the game.

## Files

- `main.py`: maze layouts, gameplay, and score persistence.
- `test_game.py`: standard-library automated tests.
- `.gitignore`: excludes local scores, Python caches, and virtual environments.

## Test

```sh
python -m unittest discover -v
```

Tests solve all three mazes, exercise replay and input handling, and check score persistence and ranking. Tests use temporary score files and leave personal records untouched.
