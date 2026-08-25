import os

from flask import Flask, render_template, request

from binpacking import (
    first_fit, first_fit_decreasing, best_fit_decreasing,
    lower_bound, validate_items, summarize,
)

app = Flask(__name__)

DEFAULT_CAPACITY = "1.0"
DEFAULT_ITEMS = "0.5, 0.7, 0.3, 0.9, 0.2, 0.6, 0.8, 0.4, 0.1, 0.5"
MAX_ITEMS = 200  # keep the page and the O(n^2) heuristics fast


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    capacity_raw = DEFAULT_CAPACITY
    items_raw = DEFAULT_ITEMS

    if request.method == "POST":
        capacity_raw = request.form.get("capacity", "").strip()
        items_raw = request.form.get("items", "").strip()

        try:
            capacity = float(capacity_raw)
            if capacity <= 0:
                raise ValueError("Capacity must be greater than 0.")

            parts = [p for p in items_raw.replace(",", " ").split() if p]
            if not parts:
                raise ValueError("Please enter at least one item size.")
            if len(parts) > MAX_ITEMS:
                raise ValueError(f"Please enter at most {MAX_ITEMS} items.")

            items = [float(p) for p in parts]
            if any(x <= 0 for x in items):
                raise ValueError("All item sizes must be greater than 0.")

            validate_items(items, capacity)

            lb = lower_bound(items, capacity)
            ff_bins = first_fit(items, capacity)
            ffd_bins = first_fit_decreasing(items, capacity)
            bfd_bins = best_fit_decreasing(items, capacity)

            result = {
                "capacity": capacity,
                "items": items,
                "total": round(sum(items), 3),
                "lower_bound": lb,
                "algorithms": [
                    {"label": "First Fit (FF)", "count": len(ff_bins),
                     "bins": summarize(ff_bins, capacity)},
                    {"label": "First Fit Decreasing (FFD)", "count": len(ffd_bins),
                     "bins": summarize(ffd_bins, capacity)},
                    {"label": "Best Fit Decreasing (BFD)", "count": len(bfd_bins),
                     "bins": summarize(bfd_bins, capacity)},
                ],
            }
        except ValueError as e:
            error = str(e)

    return render_template(
        "index.html",
        result=result, error=error,
        capacity_raw=capacity_raw, items_raw=items_raw,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
