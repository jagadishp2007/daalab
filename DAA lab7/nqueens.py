"""
N-Queens solver.

Core backtracking logic, kept separate from the web layer so it can be
reused from the CLI script (nqueens_cli.py) or the Flask app (app.py).
"""


def is_safe(board, row, col):
    for prev_row in range(row):
        placed = board[prev_row]
        if placed == col:  # Same column
            return False
        if abs(prev_row - row) == abs(placed - col):  # Same diagonal
            return False
    return True


def solve_n_queens(n, max_solutions=None):
    """
    Solve the N-Queens problem.

    Args:
        n: board size / number of queens.
        max_solutions: optional cap on how many solutions to collect
                       (backtrack_count still reflects the full search
                       unless you also want an early exit — see note below).

    Returns:
        (solutions, backtrack_count)
        solutions: list of boards, each board is a list where board[row] = col
        backtrack_count: number of times the search backtracked
    """
    board = [-1] * n
    solutions = []
    backtrack_count = [0]

    def backtrack(row):
        if max_solutions is not None and len(solutions) >= max_solutions:
            return
        if row == n:
            solutions.append(board[:])
            return
        for col in range(n):
            if is_safe(board, row, col):
                board[row] = col
                backtrack(row + 1)
                board[row] = -1  # Undo
            backtrack_count[0] += 1

    backtrack(0)
    return solutions, backtrack_count[0]


def board_to_text(solution, n):
    """Render a single solution as a text grid (for CLI / plain-text display)."""
    lines = []
    border = ' +' + '---+' * n
    lines.append(border)
    for row in range(n):
        cells = []
        for col in range(n):
            cells.append(' Q |' if solution[row] == col else ' . |')
        lines.append(' |' + ''.join(cells))
        lines.append(border)
    return '\n'.join(lines)
