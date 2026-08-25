"""
Command-line Quicksort comparison — takes array size (and optionally a
custom array) as user input, then compares deterministic vs randomized
quicksort across Random / Sorted / Reverse / Nearly Sorted inputs.

Run with:
    python quicksort_cli.py
"""

from quicksort import (
    deterministic_quicksort, randomized_quicksort,
    run_sort_safe, make_test_cases,
)

MAX_N = 20000  # local runs have no request timeout, but keep this sane


def get_n_from_user():
    while True:
        raw = input(f"Enter array size N (1-{MAX_N}): ").strip()
        if not raw.isdigit():
            print("Please enter a positive whole number.")
            continue
        n = int(raw)
        if n < 1 or n > MAX_N:
            print(f"Please choose a number between 1 and {MAX_N}.")
            continue
        return n


def get_custom_array():
    raw = input("Optional: enter a custom array (comma-separated ints), or press Enter to skip: ").strip()
    if not raw:
        return None
    try:
        return [int(x) for x in raw.replace(",", " ").split()]
    except ValueError:
        print("Could not parse that as integers — skipping custom array.")
        return None


def run_case(name, arr):
    d_comps, d_time = run_sort_safe(deterministic_quicksort, arr[:])
    r_comps, r_time = run_sort_safe(randomized_quicksort, arr[:])
    print(f'{name:<16} {d_comps:>12} {d_time:>14.2f} {r_comps:>12} {r_time:>14.2f}')


def main():
    n = get_n_from_user()
    custom = get_custom_array()

    test_cases = make_test_cases(n)
    if custom:
        test_cases["Custom"] = custom

    header = f'{"Input Type":<16} {"DQS Comps":>12} {"DQS Time(ms)":>14} {"RQS Comps":>12} {"RQS Time(ms)":>14}'
    print(header)
    print('-' * len(header))
    for case, arr in test_cases.items():
        run_case(case, arr)


if __name__ == "__main__":
    main()
