"""
Command-line TSP solver — takes the number of cities and the cost matrix
as user input, then solves with branch & bound (and verifies with brute
force for small n).

Run with:
    python tsp_cli.py
"""

import string
from tsp import tsp_branch_and_bound, tsp_brute_force, format_matrix, INF

BRUTE_FORCE_LIMIT = 9  # n! blows up fast; skip verification above this


def get_n_from_user():
    while True:
        raw = input("Enter number of cities (2-10): ").strip()
        if not raw.isdigit():
            print("Please enter a positive whole number.")
            continue
        n = int(raw)
        if n < 2 or n > 10:
            print("Please choose a number between 2 and 10.")
            continue
        return n


def get_matrix_from_user(n, cities):
    print(f"\nEnter the cost for each pair of cities ({', '.join(cities)}).")
    print("Costs must be symmetric or asymmetric, whole numbers, > 0.")
    print("The diagonal (a city to itself) is fixed at INF automatically.\n")

    cost = [[INF] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if cost[i][j] != INF:
                continue  # already filled in (if we ever offer symmetric mode)
            while True:
                raw = input(f"  Cost {cities[i]} -> {cities[j]}: ").strip()
                if raw.isdigit() and int(raw) > 0:
                    cost[i][j] = int(raw)
                    break
                print("  Please enter a positive whole number.")
    return cost


def main():
    n = get_n_from_user()
    cities = list(string.ascii_uppercase[:n])
    cost = get_matrix_from_user(n, cities)

    print("\nCost matrix:")
    print(format_matrix(cost, cities))

    print("\nSolving with Branch & Bound...")
    bb_path, bb_cost = tsp_branch_and_bound(cost, n)
    print(f"\nOptimal Tour: {' -> '.join(cities[i] for i in bb_path)}")
    print(f"Minimum Cost: {bb_cost}")

    print("\nPath verification:")
    for i in range(n):
        u, v = bb_path[i], bb_path[i + 1]
        print(f"  {cities[u]} -> {cities[v]}: cost = {cost[u][v]}")

    if n <= BRUTE_FORCE_LIMIT:
        bf_path, bf_cost = tsp_brute_force(cost, n)
        match = "MATCH" if bf_cost == bb_cost else "MISMATCH"
        print(f"\nBrute-force verification: cost = {bf_cost} ({match})")
    else:
        print(f"\n(Skipping brute-force verification: n={n} is too large for {n}! permutations.)")


if __name__ == "__main__":
    main()
