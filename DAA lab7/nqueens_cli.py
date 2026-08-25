"""
Command-line N-Queens solver — takes N as user input.

Run with:
    python nqueens_cli.py
"""

from nqueens import solve_n_queens, board_to_text

MAX_BOARDS_TO_PRINT = 20  # avoid flooding the terminal for large N


def get_n_from_user():
    while True:
        raw = input("Enter board size N (number of queens, e.g. 4, 6, 8): ").strip()
        if not raw.isdigit():
            print("Please enter a positive whole number.")
            continue
        n = int(raw)
        if n <= 0:
            print("N must be greater than 0.")
            continue
        if n == 2 or n == 3:
            print(f"Note: N={n} has no solutions, but the search will still run.")
        return n


def main():
    n = get_n_from_user()

    show_boards = False
    if n <= 10:
        choice = input("Show all solution boards? (y/n): ").strip().lower()
        show_boards = choice.startswith('y')
    else:
        print(f"N={n} is large — skipping full board display, showing summary only.")

    print(f"\nSolving N={n} ...")
    solutions, backtracks = solve_n_queens(n)

    print(f"\nN={n}: {len(solutions)} solutions, {backtracks} backtracks")

    if show_boards and solutions:
        limit = min(len(solutions), MAX_BOARDS_TO_PRINT)
        print(f"\nShowing {limit} of {len(solutions)} solution(s):")
        for i, sol in enumerate(solutions[:limit], 1):
            print(f"\nSolution {i}: {sol}")
            print(board_to_text(sol, n))
        if len(solutions) > limit:
            print(f"\n... {len(solutions) - limit} more solution(s) not shown.")


if __name__ == "__main__":
    main()
