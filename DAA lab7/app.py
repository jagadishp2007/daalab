import os
from flask import Flask, render_template, request

from nqueens import solve_n_queens

app = Flask(__name__)

MAX_N = 14          # guard rail: N-Queens search grows very fast beyond this
MAX_BOARDS_SHOWN = 30  # don't dump thousands of boards into one page


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    n_value = ""

    if request.method == "POST":
        n_value = request.form.get("n", "").strip()
        if not n_value.isdigit():
            error = "Please enter a positive whole number."
        else:
            n = int(n_value)
            if n <= 0:
                error = "N must be greater than 0."
            elif n > MAX_N:
                error = f"For performance, N is capped at {MAX_N} on this demo."
            else:
                solutions, backtracks = solve_n_queens(n)
                shown = solutions[:MAX_BOARDS_SHOWN]
                result = {
                    "n": n,
                    "count": len(solutions),
                    "backtracks": backtracks,
                    "boards": shown,
                    "truncated": len(solutions) - len(shown),
                }

    return render_template("index.html", result=result, error=error, n_value=n_value)


if __name__ == "__main__":
    # Render sets the PORT env var; default to 5000 for local runs.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
