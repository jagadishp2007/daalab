"""
Travelling Salesman Problem (TSP) solvers.

- reduce_matrix(): row/column reduction of a cost matrix (used as the
  lower-bound step of branch & bound).
- tsp_branch_and_bound(): exact solver using best-first branch & bound
  with matrix reduction (uses heapq as a priority queue).
- tsp_brute_force(): exact solver by trying every permutation — used to
  verify the branch & bound result on small inputs.

Kept separate from the web/CLI layers so both can reuse it.
"""

from itertools import permutations
import heapq

INF = float('inf')


def _copy_matrix(mat):
    return [row[:] for row in mat]


def reduce_matrix(mat):
    """
    Row-reduce then column-reduce a cost matrix.

    Returns (reduced_matrix, total_reduction_cost). The reduction cost is
    a valid lower bound contribution: every row and column has at least
    one zero afterward (ignoring rows/columns that are all INF).
    """
    m = _copy_matrix(mat)
    n = len(m)
    cost = 0

    # Row reduction
    for i in range(n):
        finite = [x for x in m[i] if x != INF]
        if not finite:
            continue
        row_min = min(finite)
        if row_min and row_min != INF:
            cost += row_min
            m[i] = [x - row_min if x != INF else INF for x in m[i]]

    # Column reduction
    for j in range(n):
        col_vals = [m[i][j] for i in range(n) if m[i][j] != INF]
        if not col_vals:
            continue
        col_min = min(col_vals)
        if col_min and col_min != INF:
            cost += col_min
            for i in range(n):
                if m[i][j] != INF:
                    m[i][j] -= col_min

    return m, cost


class _Node:
    """A partial tour in the branch & bound search tree."""
    __slots__ = ("matrix", "path", "bound", "level", "vertex")

    def __init__(self, matrix, path, bound, level, vertex):
        self.matrix = matrix
        self.path = path
        self.bound = bound
        self.level = level
        self.vertex = vertex


def tsp_branch_and_bound(cost, n):
    """
    Exact TSP solver: best-first branch & bound using matrix reduction
    for the lower bound at each node.

    Args:
        cost: n x n cost matrix, cost[i][j] = distance/cost from i to j.
              Diagonal entries must be INF.
        n: number of cities.

    Returns:
        (path, total_cost) where path is a list of city indices starting
        and ending at city 0, e.g. [0, 2, 1, 3, 0].
    """
    if n == 1:
        return [0, 0], 0

    reduced0, base_cost = reduce_matrix(cost)
    root = _Node(reduced0, [0], base_cost, 0, 0)

    heap = []
    counter = 0  # tie-breaker so heap never compares _Node objects directly
    heapq.heappush(heap, (root.bound, counter, root))

    while heap:
        _, _, node = heapq.heappop(heap)

        if node.level == n - 1:
            return node.path + [0], node.bound

        i = node.vertex
        for j in range(n):
            if node.matrix[i][j] == INF or j in node.path:
                continue

            child_matrix = _copy_matrix(node.matrix)
            for k in range(n):
                child_matrix[i][k] = INF   # leaving i is done
                child_matrix[k][j] = INF   # arriving at j is done
            child_matrix[j][0] = INF       # block premature return to start

            edge_cost = node.matrix[i][j]
            reduced_child, reduction_cost = reduce_matrix(child_matrix)
            child_bound = node.bound + edge_cost + reduction_cost

            counter += 1
            child = _Node(reduced_child, node.path + [j], child_bound, node.level + 1, j)
            heapq.heappush(heap, (child_bound, counter, child))

    return None, INF


def tsp_brute_force(cost, n):
    """Try every permutation — exact, but O(n!). Used to verify B&B on small n."""
    cities = list(range(1, n))
    best_cost = INF
    best_path = None
    for perm in permutations(cities):
        path = [0] + list(perm) + [0]
        c = sum(cost[path[i]][path[i + 1]] for i in range(n))
        if c < best_cost:
            best_cost = c
            best_path = path
    return best_path, best_cost


def format_matrix(cost, cities):
    """Return the cost matrix as a printable text table."""
    header = f'{"":>6}' + ' '.join(f'{c:>6}' for c in cities)
    lines = [header]
    for i, row in enumerate(cost):
        r = ['INF' if x == INF else str(x) for x in row]
        lines.append(f'{cities[i]:>6}' + ' '.join(f'{v:>6}' for v in r))
    return '\n'.join(lines)
