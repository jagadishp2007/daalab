from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


def matrix_chain_order(dims):
    """
    Matrix Chain Multiplication using DP
    dims: list of dimensions, matrix i has dims[i-1] x dims[i]
    Time: O(n^3), Space: O(n^2)
    """
    n = len(dims) - 1
    # m[i][j] = minimum multiplications for matrices i..j
    m = [[0] * (n + 1) for _ in range(n + 1)]
    s = [[0] * (n + 1) for _ in range(n + 1)]

    # l is the chain length
    for l in range(2, n + 1):
        for i in range(1, n - l + 2):
            j = i + l - 1
            m[i][j] = float('inf')
            for k in range(i, j):
                cost = m[i][k] + m[k + 1][j] + dims[i - 1] * dims[k] * dims[j]
                if cost < m[i][j]:
                    m[i][j] = cost
                    s[i][j] = k
    return m, s


def print_optimal_parens(s, i, j):
    if i == j:
        return f'A{i}'
    k = s[i][j]
    left = print_optimal_parens(s, i, k)
    right = print_optimal_parens(s, k + 1, j)
    return f'({left} x {right})'


def build_paren_tree(s, i, j):
    """Recursive tree structure for frontend visualization."""
    if i == j:
        return {"label": f"A{i}", "leaf": True}
    k = s[i][j]
    return {
        "label": f"A{i}..A{j}",
        "leaf": False,
        "split": k,
        "left": build_paren_tree(s, i, k),
        "right": build_paren_tree(s, k + 1, j),
    }


@app.route("/")
def index():
    return jsonify({
        "service": "Matrix Chain Multiplication API",
        "endpoints": {
            "GET /": "this help message",
            "GET /ui": "interactive frontend",
            "GET /health": "health check",
            "POST /solve": 'body: {"dims": [10, 30, 5, 60, 10]} -> min cost, optimal parenthesization, DP tables, tree'
        }
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/ui")
def ui():
    return render_template("ui.html")


@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json(force=True, silent=True) or {}
    dims = data.get("dims")

    if not dims or not isinstance(dims, list) or len(dims) < 2:
        return jsonify({"error": "Provide 'dims' as a list of at least 2 integers, e.g. [10,30,5,60,10]"}), 400
    try:
        dims = [int(d) for d in dims]
        if any(d <= 0 for d in dims):
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "All dims must be positive integers"}), 400

    n = len(dims) - 1
    m, s = matrix_chain_order(dims)

    matrices = [f"A{i+1} ({dims[i]}x{dims[i+1]})" for i in range(n)]

    return jsonify({
        "dims": dims,
        "matrices": matrices,
        "num_matrices": n,
        "min_multiplications": m[1][n],
        "optimal_parenthesization": print_optimal_parens(s, 1, n),
        "m_table": m,
        "s_table": s,
        "tree": build_paren_tree(s, 1, n),
    })


if __name__ == "__main__":
    app.run(debug=True)
