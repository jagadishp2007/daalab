"""
Quicksort comparison: deterministic (last-element pivot) vs randomized pivot.

- partition() / deterministic_quicksort() / randomized_quicksort() mirror the
  original algorithm exactly, but take a `counter` list instead of a global,
  so multiple runs (e.g. concurrent web requests) never share state.
- run_sort_safe() executes a sort inside a worker thread with a larger native
  stack. Deterministic quicksort on already-sorted or reverse-sorted input
  recurses to a depth equal to n (its worst case) — for large n that risks
  a segfault or crash on the default stack, especially under a web server.
  Running it in a thread with a bigger stack makes that safe.
"""

import random
import sys
import threading
import time


def partition(arr, low, high, counter):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        counter[0] += 1
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def deterministic_quicksort(arr, low, high, counter):
    if low < high:
        pi = partition(arr, low, high, counter)
        deterministic_quicksort(arr, low, pi - 1, counter)
        deterministic_quicksort(arr, pi + 1, high, counter)


def randomized_quicksort(arr, low, high, counter, rng=None):
    rng = rng or random
    if low < high:
        rand_idx = rng.randint(low, high)
        arr[rand_idx], arr[high] = arr[high], arr[rand_idx]
        pi = partition(arr, low, high, counter)
        randomized_quicksort(arr, low, pi - 1, counter, rng)
        randomized_quicksort(arr, pi + 1, high, counter, rng)


def run_sort_safe(sort_fn, arr, stack_size_bytes=64 * 1024 * 1024, recursion_limit=20000):
    """
    Run sort_fn(arr, 0, len(arr)-1, counter) inside a worker thread with a
    larger native stack, so deep recursion (worst case: depth == len(arr))
    can't crash the process. Returns (comparisons, elapsed_ms).
    Raises RuntimeError if the sort itself raised an exception.
    """
    counter = [0]
    outcome = {}

    def worker():
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(recursion_limit, len(arr) + 1000))
        try:
            start = time.perf_counter()
            sort_fn(arr, 0, len(arr) - 1, counter)
            outcome["elapsed_ms"] = (time.perf_counter() - start) * 1000
        except Exception as e:  # noqa: BLE001 - surface any sort failure to caller
            outcome["error"] = repr(e)
        finally:
            sys.setrecursionlimit(old_limit)

    old_stack_size = threading.stack_size()
    try:
        threading.stack_size(stack_size_bytes)
        t = threading.Thread(target=worker)
        t.start()
        t.join()
    finally:
        try:
            threading.stack_size(old_stack_size)
        except (ValueError, RuntimeError):
            pass  # some platforms don't allow resetting; safe to ignore

    if "error" in outcome:
        raise RuntimeError(outcome["error"])
    return counter[0], outcome["elapsed_ms"]


def make_test_cases(n, seed=None):
    """Build the standard Random / Sorted / Reverse / Nearly Sorted inputs."""
    rng = random.Random(seed)
    nearly_sorted = list(range(n))
    for _ in range(max(1, n // 20)):
        i, j = rng.randint(0, n - 1), rng.randint(0, n - 1)
        nearly_sorted[i], nearly_sorted[j] = nearly_sorted[j], nearly_sorted[i]

    return {
        "Random": [rng.randint(1, 100000) for _ in range(n)],
        "Sorted": list(range(n)),
        "Reverse": list(range(n, 0, -1)),
        "Nearly Sorted": nearly_sorted,
    }
