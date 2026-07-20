"""
CS5303 - DAA Lab | Ex. No. 5
To Find Min-Max Value by Applying Divide and Conquer Technique

REST API + frontend wrapper comparing the Divide & Conquer min-max
algorithm against the naive linear-scan approach.
Deployable on Render as a Web Service.
"""

import random
import time

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


# ----------------------------
# Algorithms
# ----------------------------
# Note: the comparison counter is threaded through return values rather
# than a module-level global, so concurrent requests on the deployed
# server don't corrupt each other's counts.

def min_max_dc(arr, low, high):
    # Base case: single element
    if low == high:
        return arr[low], arr[low], 0

    # Base case: two elements
    if high == low + 1:
        if arr[low] < arr[high]:
            return arr[low], arr[high], 1
        return arr[high], arr[low], 1

    # Divide
    mid = (low + high) // 2
    lmin, lmax, lc = min_max_dc(arr, low, mid)
    rmin, rmax, rc = min_max_dc(arr, mid + 1, high)

    # Conquer: combine with 2 comparisons
    comparisons = lc + rc
    comparisons += 1
    overall_min = lmin if lmin < rmin else rmin
    comparisons += 1
    overall_max = lmax if lmax > rmax else rmax

    return overall_min, overall_max, comparisons


def min_max_naive(arr):
    mn, mx = arr[0], arr[0]
    comps = 0
    for x in arr[1:]:
        comps += 1
        if x < mn:
            mn = x
        comps += 1
        if x > mx:
            mx = x
    return mn, mx, comps


def formula_comparisons(n):
    """Theoretical D&C comparison count: 3n/2 - 2 (for n >= 2)."""
    if n < 2:
        return 0
    return (3 * n) // 2 - 2


DEFAULT_ARRAY = [3, 1, 7, 4, 9, 2, 8, 5, 6, 0]


# ----------------------------
# Routes
# ----------------------------

@app.get("/")
def ui():
    return render_template("index.html")


@app.get("/api")
def index():
    return jsonify({
        "service": "Min-Max Divide & Conquer API",
        "endpoints": {
            "GET /": "interactive frontend",
            "GET /api": "this help message",
            "GET /health": "health check",
            "POST /minmax": "body: {\"array\": [numbers]} -> min, max, D&C comparisons, naive comparisons, timing",
            "GET /benchmark": "optional query param: sizes (comma-separated, default 10,100,1000,10000) -> comparison table on random arrays",
        },
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/minmax")
def minmax():
    data = request.get_json(silent=True) or {}
    arr = data.get("array")

    if not isinstance(arr, list) or len(arr) == 0:
        return jsonify({"error": "'array' must be a non-empty list of numbers."}), 400
    if not all(isinstance(x, (int, float)) for x in arr):
        return jsonify({"error": "All elements of 'array' must be numbers."}), 400

    t0 = time.perf_counter()
    dc_min, dc_max, dc_comps = min_max_dc(arr, 0, len(arr) - 1)
    dc_time = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    naive_min, naive_max, naive_comps = min_max_naive(arr)
    naive_time = (time.perf_counter() - t0) * 1000

    return jsonify({
        "array": arr,
        "n": len(arr),
        "min": dc_min,
        "max": dc_max,
        "dc": {"comparisons": dc_comps, "time_ms": round(dc_time, 4)},
        "naive": {"comparisons": naive_comps, "time_ms": round(naive_time, 4)},
        "formula_comparisons": formula_comparisons(len(arr)),
    })


@app.get("/benchmark")
def benchmark():
    sizes_param = request.args.get("sizes", "10,100,1000,10000")
    try:
        sizes = [int(s) for s in sizes_param.split(",") if s.strip()]
    except ValueError:
        return jsonify({"error": "'sizes' must be a comma-separated list of integers."}), 400

    sizes = [max(1, min(s, 200000)) for s in sizes]  # guard against abuse

    table = []
    for size in sizes:
        arr = [random.randint(1, 10000) for _ in range(size)]
        _, _, dc_comps = min_max_dc(arr, 0, len(arr) - 1)
        _, _, naive_comps = min_max_naive(arr)
        table.append({
            "size": size,
            "dc_comparisons": dc_comps,
            "naive_comparisons": naive_comps,
            "formula_comparisons": formula_comparisons(size),
        })

    return jsonify({"benchmark": table})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
