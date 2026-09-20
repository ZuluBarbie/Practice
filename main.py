import time
import json
import math
from pathlib import Path

MAZES = {
    "1": [
        ["#", "#", "#", "#", "#", "#", "#"],
        ["#", "P", " ", " ", "#", " ", "#"],
        ["#", "#", "#", " ", "#", " ", "#"],
        ["#", " ", " ", " ", " ", " ", "#"],
        ["#", " ", "#", "#", "#", " ", "#"],
        ["#", " ", " ", " ", "#", "E", "#"],
        ["#", "#", "#", "#", "#", "#", "#"]
    ],

    "2": [
        ["#", "#", "#", "#", "#", "#", "#", "#", "#"],
        ["#", "P", " ", "#", " ", " ", " ", " ", "#"],
        ["#", " ", " ", "#", " ", "#", "#", " ", "#"],
        ["#", "#", " ", " ", " ", "#", " ", " ", "#"],
        ["#", " ", "#", "#", " ", "#", " ", "#", "#"],
        ["#", " ", " ", " ", " ", "#", " ", " ", "#"],
        ["#", " ", "#", "#", "#", "#", " ", " ", "#"],
        ["#", " ", " ", " ", " ", " ", " ", "E", "#"],
        ["#", "#", "#", "#", "#", "#", "#", "#", "#"]
    ],

    "3": [
        ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
        ["#", "P", " ", " ", "#", " ", " ", " ", " ", " ", "#"],
        ["#", "#", "#", " ", "#", " ", "#", "#", "#", " ", "#"],
        ["#", " ", " ", " ", "#", " ", "#", " ", " ", " ", "#"],
        ["#", " ", "#", "#", "#", " ", "#", " ", "#", "#", "#"],
        ["#", " ", " ", " ", " ", " ", "#", " ", " ", " ", "#"],
        ["#", " ", "#", "#", "#", "#", "#", " ", "#", " ", "#"],
        ["#", " ", "#", " ", " ", " ", " ", " ", "#", " ", "#"],
        ["#", " ", "#", " ", "#", "#", "#", "#", "#", " ", "#"],
        ["#", " ", " ", " ", " ", " ", " ", "#", "E", " ", "#"],
        ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"]
    ]
}

SCORES_PATH = Path(__file__).resolve().with_name("best_scores.json")
DIRECTIONS = {"w": (-1, 0), "a": (0, -1), "s": (1, 0), "d": (0, 1)}


def display_maze(maze):
    for row in maze:
        print(" ".join(row))


def load_scores(path=None):
    """Read valid records without letting damaged scores prevent play."""
    path = SCORES_PATH if path is None else Path(path)
    try:
        scores = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, ValueError, UnicodeError):
        print("Could not read best scores; starting without saved records.")
        return {}
    if not isinstance(scores, dict):
        return {}
    return {
        level: score for level, score in scores.items()
        if level in MAZES and isinstance(score, dict)
        and type(score.get("moves")) is int and score["moves"] > 0
        and type(score.get("time")) in (int, float)
        and score["time"] >= 0
        and (type(score["time"]) is int or math.isfinite(score["time"]))
    }


def save_scores(scores, path=None):
    path = SCORES_PATH if path is None else Path(path)
    try:
        path.write_text(json.dumps(scores, indent=4) + "\n", encoding="utf-8")
    except OSError:
        print("Could not save your best score.")
        return False
    return True


def is_better_score(current, previous):
    return previous is None or (current["moves"], current["time"]) < (
        previous["moves"], previous["time"]
    )


def play_round(difficulty, best_scores):
    maze = [row[:] for row in MAZES[difficulty]]
    player_row, player_col = 1, 1
    moves = 0
    start_time = time.perf_counter()
    while True:
        print()
        display_maze(maze)
        print(f"\nMoves: {moves}")
        move = input("Move using W, A, S, D (Q to quit): ").strip().lower()
        if move == "q":
            return False
        if move not in DIRECTIONS:
            print("Please use only W, A, S, D, or Q.")
            continue
        dr, dc = DIRECTIONS[move]
        new_row, new_col = player_row + dr, player_col + dc
        if (not 0 <= new_row < len(maze)
                or not 0 <= new_col < len(maze[new_row])
                or maze[new_row][new_col] == "#"):
            print("You hit a wall!")
            continue
        moves += 1
        if maze[new_row][new_col] == "E":
            elapsed = round(time.perf_counter() - start_time, 1)
            print(f"\nYOU ESCAPED!\nMoves: {moves}\nTime: {elapsed:.1f} seconds")
            current = {"moves": moves, "time": elapsed}
            previous = best_scores.get(difficulty)
            if is_better_score(current, previous):
                best_scores[difficulty] = current
                print("NEW BEST SCORE!")
                save_scores(best_scores)
            else:
                print(f"\nBest score:\nMoves: {previous['moves']}"
                      f"\nTime: {previous['time']} seconds")
            return True
        maze[player_row][player_col] = " "
        player_row, player_col = new_row, new_col
        maze[player_row][player_col] = "P"


def main():
    best_scores = load_scores()
    try:
        while True:
            print("=== PYTHON MAZE GAME ===\n1. Easy\n2. Medium\n3. Hard")
            difficulty = input("Choose difficulty (Q to quit): ").strip().lower()
            while difficulty not in MAZES and difficulty != "q":
                print("Invalid choice.")
                difficulty = input("Choose 1, 2, or 3 (Q to quit): ").strip().lower()
            if difficulty == "q" or not play_round(difficulty, best_scores):
                break
            if input("\nWould you like to play again? (y/n): ").strip().lower() != "y":
                break
            print("\nStarting a new game...")
    except (EOFError, KeyboardInterrupt):
        print()
    print("\nThanks for playing!")


if __name__ == "__main__":
    main()
