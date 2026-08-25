import os

from flask import Flask, render_template, request

from quicksort import (
    deterministic_quicksort, randomized_quicksort,
    run_sort_safe, make_test_cases,
)

app = Flask(__name__)

DEFAULT_N = "1000"
# Deterministic quicksort's worst case (Sorted/Reverse input) is O(n^2).
# Capped low enough that even the worst case finishes in a couple seconds
# on a free-tier web server, and recursion depth (== n in the worst case)
# stays comfortable even with the larger thread stack.
MAX_N = 3000
MAX_CUSTOM_ITEMS = 3000


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    n_raw = DEFAULT_N
    custom_raw = ""

    if request.method == "POST":
        n_raw = request.form.get("n", "").strip()
        custom_raw = request.form.get("custom", "").strip()

        try:
            if not n_raw.isdigit():
                raise ValueError("N must be a positive whole number.")
            n = int(n_raw)
            if n < 1 or n > MAX_N:
                raise ValueError(f"N must be between 1 and {MAX_N} (worst case is O(n^2)).")

            test_cases = make_test_cases(n)

            if custom_raw:
                parts = [p for p in custom_raw.replace(",", " ").split() if p]
                if len(parts) > MAX_CUSTOM_ITEMS:
                    raise ValueError(f"Custom array is limited to {MAX_CUSTOM_ITEMS} items.")
                try:
                    custom_arr = [int(p) for p in parts]
                except ValueError:
                    raise ValueError("Custom array must contain only integers.")
                if custom_arr:
                    test_cases["Custom"] = custom_arr

            rows = []
            for name, arr in test_cases.items():
                d_comps, d_time = run_sort_safe(deterministic_quicksort, arr[:])
                r_comps, r_time = run_sort_safe(randomized_quicksort, arr[:])
                rows.append({
                    "name": name,
                    "d_comps": d_comps, "d_time": round(d_time, 2),
                    "r_comps": r_comps, "r_time": round(r_time, 2),
                })

            result = {"n": n, "rows": rows}

        except ValueError as e:
            error = str(e)
        except RuntimeError as e:
            error = f"Sort failed: {e}"

    return render_template(
        "index.html",
        result=result, error=error,
        n_raw=n_raw, custom_raw=custom_raw, max_n=MAX_N,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
