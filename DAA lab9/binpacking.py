"""
Bin Packing heuristics.

- first_fit(): place each item in the first bin that has room, else open a new bin.
- first_fit_decreasing(): sort items largest-first, then apply First Fit.
- best_fit_decreasing(): sort items largest-first, then place each item in the
  bin that will have the LEAST leftover space after it's added (tightest fit).
- lower_bound(): a simple lower bound on the number of bins any packing needs
  (ceil(total size / capacity)) — no valid packing can use fewer bins than this.

Kept separate from the CLI/web layers so both can reuse it.
"""

import math


def first_fit(items, capacity=1.0):
    """Return bin_contents: a list of bins, each a list of the items placed in it."""
    bins = []          # remaining free space per bin
    bin_contents = []
    for item in items:
        placed = False
        for i, space in enumerate(bins):
            if space >= item:
                bins[i] -= item
                bin_contents[i].append(item)
                placed = True
                break
        if not placed:
            bins.append(capacity - item)
            bin_contents.append([item])
    return bin_contents


def first_fit_decreasing(items, capacity=1.0):
    return first_fit(sorted(items, reverse=True), capacity)


def best_fit_decreasing(items, capacity=1.0):
    sorted_items = sorted(items, reverse=True)
    bins = []
    bin_contents = []
    for item in sorted_items:
        best_idx = -1
        best_space = float('inf')
        for i, space in enumerate(bins):
            if space >= item and space - item < best_space:
                best_space = space - item
                best_idx = i
        if best_idx >= 0:
            bins[best_idx] -= item
            bin_contents[best_idx].append(item)
        else:
            bins.append(capacity - item)
            bin_contents.append([item])
    return bin_contents


def lower_bound(items, capacity=1.0):
    """Ceiling(total size / capacity) — no packing can use fewer bins than this."""
    return math.ceil(sum(items) / capacity)


def validate_items(items, capacity):
    """Raise ValueError with a clear message if any item can never fit."""
    too_big = [x for x in items if x > capacity]
    if too_big:
        raise ValueError(
            f"Item(s) {too_big} exceed the bin capacity ({capacity}) and can never be placed."
        )


def summarize(bins, capacity=1.0):
    """Return per-bin used space / free space, for display."""
    rows = []
    for i, contents in enumerate(bins, 1):
        used = sum(contents)
        rows.append({
            "index": i,
            "contents": [round(x, 3) for x in contents],
            "used": round(used, 3),
            "free": round(capacity - used, 3),
            "fill_pct": round((used / capacity) * 100, 1) if capacity else 0,
        })
    return rows
