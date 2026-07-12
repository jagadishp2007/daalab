"""
CS5303 - DAA Lab | Ex. No. 3
Implementation of Kruskal's and Prim's Algorithms for Minimum Spanning Tree

REST API + frontend wrapper around both MST algorithms.
Deployable on Render as a Web Service.
"""

import heapq
import time

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


# ----------------------------
# Union-Find for Kruskal
# ----------------------------

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


def kruskal(n, edges):
    """edges: list of (weight, u, v)"""
    edges = sorted(edges)  # O(E log E)
    uf = UnionFind(n)
    mst = []
    cost = 0
    for w, u, v in edges:
        if uf.union(u, v):
            mst.append((u, v, w))
            cost += w
        if len(mst) == n - 1:
            break
    return mst, cost


def prim(n, adj, start=0):
    """adj: adjacency list {u: [(v, w), ...]}"""
    INF = float('inf')
    key = [INF] * n
    parent = [-1] * n
    inMST = [False] * n
    key[start] = 0
    pq = [(0, start)]
    mst = []
    cost = 0
    while pq:
        w, u = heapq.heappop(pq)
        if inMST[u]:
            continue
        inMST[u] = True
        if parent[u] != -1:
            mst.append((parent[u], u, w))
            cost += w
        for v, wt in adj.get(u, []):
            if not inMST[v] and wt < key[v]:
                key[v] = wt
                parent[v] = u
                heapq.heappush(pq, (wt, v))
    return mst, cost


DEFAULT_N = 7
DEFAULT_EDGES = [
    (7, 0, 1), (5, 0, 3), (8, 1, 2), (9, 1, 3),
    (7, 1, 4), (5, 2, 4), (15, 3, 4), (6, 3, 5),
    (8, 4, 5), (9, 4, 6), (11, 5, 6),
]


def build_adj(n, edges):
    adj = {}
    for w, u, v in edges:
        adj.setdefault(u, []).append((v, w))
        adj.setdefault(v, []).append((u, w))
    return adj


def run_both(n, edges, start=0):
    result = {}

    t0 = time.perf_counter()
    k_mst, k_cost = kruskal(n, edges[:])
    k_time = (time.perf_counter() - t0) * 1000
    result["kruskal"] = {
        "mst": [{"u": u, "v": v, "weight": w} for u, v, w in k_mst],
        "cost": k_cost,
        "time_ms": round(k_time, 4),
    }

    adj = build_adj(n, edges)
    t0 = time.perf_counter()
    p_mst, p_cost = prim(n, adj, start)
    p_time = (time.perf_counter() - t0) * 1000
    result["prim"] = {
        "mst": [{"u": u, "v": v, "weight": w} for u, v, w in p_mst],
        "cost": p_cost,
        "time_ms": round(p_time, 4),
    }

    return result


# ----------------------------
# Routes
# ----------------------------

@app.get("/")
def ui():
    return render_template("index.html")


@app.get("/api")
def index():
    return jsonify({
        "service": "Minimum Spanning Tree API (Kruskal + Prim)",
        "endpoints": {
            "GET /": "interactive frontend",
            "GET /api": "this help message",
            "GET /health": "health check",
            "POST /mst": (
                "body: {\"n\": int, \"edges\": [[w,u,v], ...], \"start\": int (optional)} "
                "-> Kruskal & Prim MSTs, costs, and timing"
            ),
        },
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/mst")
def mst():
    data = request.get_json(silent=True) or {}
    n = data.get("n")
    raw_edges = data.get("edges")
    start = data.get("start", 0)

    if not isinstance(n, int) or n <= 0:
        return jsonify({"error": "'n' must be a positive integer (number of nodes)."}), 400
    if not isinstance(raw_edges, list) or not raw_edges:
        return jsonify({"error": "'edges' must be a non-empty list of [weight, u, v]."}), 400
    if not isinstance(start, int) or not (0 <= start < n):
        return jsonify({"error": "'start' must be a valid node index."}), 400

    edges = []
    for e in raw_edges:
        if not (isinstance(e, list) and len(e) == 3):
            return jsonify({"error": "Each edge must be [weight, u, v]."}), 400
        w, u, v = e
        if not all(isinstance(x, (int, float)) for x in (w, u, v)):
            return jsonify({"error": "Edge values must be numeric."}), 400
        u, v = int(u), int(v)
        if not (0 <= u < n and 0 <= v < n):
            return jsonify({"error": f"Edge endpoints must be in range [0, {n-1}]."}), 400
        edges.append((w, u, v))

    results = run_both(n, edges, start)
    connected = len(results["kruskal"]["mst"]) == n - 1

    return jsonify({
        "n": n,
        "edges": [{"u": u, "v": v, "weight": w} for w, u, v in edges],
        "start": start,
        "connected": connected,
        "results": results,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
