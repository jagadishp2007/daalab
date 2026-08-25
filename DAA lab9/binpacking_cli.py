"""
Command-line Bin Packing solver — takes bin capacity and item sizes as
user input, then compares First Fit, First Fit Decreasing, and Best Fit
Decreasing.

Run with:
    python binpacking_cli.py
"""

from binpacking import (
    first_fit, first_fit_decreasing, best_fit_decreasing,
    lower_bound, validate_items, summarize,
)


def get_capacity_from_user():
    while True:
        raw = input("Enter bin capacity (e.g. 1.0): ").strip()
        try:
            capacity = float(raw)
            if capacity <= 0:
                print("Capacity must be greater than 0.")
                continue
            return capacity
        except ValueError:
            print("Please enter a number.")


def get_items_from_user(capacity):
    print("Enter item sizes separated by commas or spaces (e.g. 0.5, 0.7, 0.3, 0.9).")
    while True:
        raw = input("Items: ").strip()
        raw = raw.replace(",", " ")
        parts = [p for p in raw.split() if p]
        if not parts:
            print("Please enter at least one item.")
            continue
        try:
            items = [float(p) for p in parts]
        except ValueError:
            print("Please enter numbers only.")
            continue
        if any(x <= 0 for x in items):
            print("All item sizes must be greater than 0.")
            continue
        try:
            validate_items(items, capacity)
        except ValueError as e:
            print(str(e))
            continue
        return items


def display_bins(label, bins, capacity):
    print(f'\n{label}: {len(bins)} bins')
    for row in summarize(bins, capacity):
        bar = '#' * int(row["fill_pct"] / 5)  # 20-char bar for 100%
        print(f'  Bin {row["index"]}: {row["contents"]} | Used: {row["used"]:.2f} '
              f'[{bar:<20}]')


def main():
    capacity = get_capacity_from_user()
    items = get_items_from_user(capacity)

    lb = lower_bound(items, capacity)
    print(f'\nItems: {items}')
    print(f'Capacity: {capacity}')
    print(f'Sum of items: {sum(items):.3f}')
    print(f'Lower bound on bins: {lb}')

    ff_bins = first_fit(items, capacity)
    ffd_bins = first_fit_decreasing(items, capacity)
    bfd_bins = best_fit_decreasing(items, capacity)

    display_bins('First Fit (FF)', ff_bins, capacity)
    display_bins('First Fit Decreasing (FFD)', ffd_bins, capacity)
    display_bins('Best Fit Decreasing (BFD)', bfd_bins, capacity)

    print(f'\nSummary: Lower Bound={lb}, FF={len(ff_bins)}, '
          f'FFD={len(ffd_bins)}, BFD={len(bfd_bins)}')


if __name__ == "__main__":
    main()
