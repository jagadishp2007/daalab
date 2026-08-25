import os
import string

from flask import Flask, render_template, request

from tsp import tsp_branch_and_bound, tsp_brute_force, INF

app = Flask(__name__)

MIN_N = 2
MAX_N = 10                 # keep the form manageable and brute-force verification feasible
BRUTE_FORCE_LIMIT = 9       # skip O(n!) verification above this

# The original 5-city example, used to prefill the grid when n == 5
SAMPLE_MATRIX_5 = [
    [None, 10, 8, 9, 7],
    [10, None, 10, 5, 6],
    [8, 10, None, 8, 9],
    [9, 5, 8, None, 6],
    [7, 6, 9, 6, None],
]


def cities_for(n):
    return list(string.ascii_uppercase[:n])


def default_value(n, i, j):
    if n == 5:
        return SAMPLE_MATRIX_5[i][j]
    return "" if i != j else None


@app.route("/", methods=["GET"])
def index():
    """Step 1: choose N, and show an editable N x N cost matrix form."""
    try:
        n = int(request.args.get("n", 5))
    except ValueError:
        n = 5
    n = max(MIN_N, min(MAX_N, n))

    cities = cities_for(n)
    grid = [[default_value(n, i, j) for j in range(n)] for i in range(n)]

    return render_template(
        "index.html",
        n=n,
        min_n=MIN_N,
        max_n=MAX_N,
        cities=cities,
        grid=grid,
        result=None,
        error=None,
    )


@app.route("/solve", methods=["POST"])
def solve():
    try:
        n = int(request.form.get("n", 0))
    except ValueError:
        n = 0

    if n < MIN_N or n > MAX_N:
        return render_template(
            "index.html", n=5, min_n=MIN_N, max_n=MAX_N,
            cities=cities_for(5),
            grid=[[default_value(5, i, j) for j in range(5)] for i in range(5)],
            result=None, error="Invalid number of cities.",
        )

    cities = cities_for(n)
    cost = [[INF] * n for _ in range(n)]
    error = None

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            raw = request.form.get(f"cell-{i}-{j}", "").strip()
            if not raw.isdigit() or int(raw) <= 0:
                error = f"Cost {cities[i]} -> {cities[j]} must be a positive whole number."
                break
            cost[i][j] = int(raw)
        if error:
            break

    grid = [
        [None if i == j else request.form.get(f"cell-{i}-{j}", "") for j in range(n)]
        for i in range(n)
    ]

    if error:
        return render_template(
            "index.html", n=n, min_n=MIN_N, max_n=MAX_N,
            cities=cities, grid=grid, result=None, error=error,
        )

    bb_path, bb_cost = tsp_branch_and_bound(cost, n)

    verification = None
    if n <= BRUTE_FORCE_LIMIT:
        _, bf_cost = tsp_brute_force(cost, n)
        verification = {"cost": bf_cost, "match": bf_cost == bb_cost}

    edges = [
        {"u": cities[bb_path[i]], "v": cities[bb_path[i + 1]], "cost": cost[bb_path[i]][bb_path[i + 1]]}
        for i in range(n)
    ]

    result = {
        "tour": " -> ".join(cities[i] for i in bb_path),
        "cost": bb_cost,
        "edges": edges,
        "verification": verification,
    }

    return render_template(
        "index.html", n=n, min_n=MIN_N, max_n=MAX_N,
        cities=cities, grid=grid, result=result, error=None,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
