"""
CS5303 - DAA Lab | Ex. No. 4
Implementation of Dijkstra's Algorithm for Single-Source Shortest Path

REST API + frontend wrapper around Dijkstra's algorithm.
Deployable on Render as a Web Service.
"""

import heapq
import time

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


# ----------------------------
# Dijkstra's Algorithm
# ----------------------------

def dijkstra(graph, source):
    """
    Dijkstra's Algorithm using Min-Heap
    Time: O((V + E) log V), Space: O(V)
    graph: dict {u: [(v, weight), ...]}, 0-indexed
    """
    n = len(graph)
    dist = [float('inf')] * n
    prev = [None] * n
    dist[source] = 0
    pq = [(0, source)]  # (distance, vertex)
    visited = set()
    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                heapq.heappush(pq, (dist[v], v))
    return dist, prev


def reconstruct_path(prev, source, target):
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    if path and path[0] == source:
        return path
    return []


DEFAULT_GRAPH = {
    0: [(1, 4), (2, 1)],
    1: [(3, 1)],
    2: [(1, 2), (3, 5)],
    3: [(4, 3)],
    4: [(5, 2)],
    5: [],
}
DEFAULT_SOURCE = 0


# ----------------------------
# Routes
# ----------------------------

@app.get("/")
def ui():
    return render_template("index.html")


@app.get("/api")
def index():
    return jsonify({
        "service": "Dijkstra's Shortest Path API",
        "endpoints": {
            "GET /": "interactive frontend",
            "GET /api": "this help message",
            "GET /health": "health check",
            "POST /dijkstra": (
                "body: {\"graph\": {\"0\": [[v,w], ...], ...}, \"source\": int} "
                "-> distances, predecessor tree, and reconstructed paths for every vertex"
            ),
        },
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/dijkstra")
def run_dijkstra():
    data = request.get_json(silent=True) or {}
    raw_graph = data.get("graph")
    source = data.get("source")

    if not isinstance(raw_graph, dict) or not raw_graph:
        return jsonify({"error": "'graph' must be a non-empty object mapping vertex -> [[v, w], ...]."}), 400

    # Normalize keys to ints, validate vertex count is contiguous 0..n-1
    try:
        node_ids = sorted(int(k) for k in raw_graph.keys())
    except (TypeError, ValueError):
        return jsonify({"error": "Graph keys must be integer vertex ids."}), 400

    n = len(node_ids)
    if node_ids != list(range(n)):
        return jsonify({"error": f"Vertices must be numbered contiguously from 0 to {n-1}."}), 400

    graph = {i: [] for i in range(n)}
    for k, adj in raw_graph.items():
        u = int(k)
        if not isinstance(adj, list):
            return jsonify({"error": f"Adjacency list for vertex {u} must be a list."}), 400
        for edge in adj:
            if not (isinstance(edge, list) and len(edge) == 2):
                return jsonify({"error": f"Each edge from vertex {u} must be [v, weight]."}), 400
            v, w = edge
            v = int(v)
            if not (0 <= v < n):
                return jsonify({"error": f"Edge target {v} from vertex {u} is out of range."}), 400
            if not isinstance(w, (int, float)) or w < 0:
                return jsonify({"error": f"Edge weight from {u} to {v} must be a non-negative number."}), 400
            graph[u].append((v, w))

    if not isinstance(source, int) or not (0 <= source < n):
        return jsonify({"error": f"'source' must be an integer in range [0, {n-1}]."}), 400

    t0 = time.perf_counter()
    dist, prev = dijkstra(graph, source)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    vertices = []
    for v in range(n):
        path = reconstruct_path(prev, source, v)
        vertices.append({
            "vertex": v,
            "distance": None if dist[v] == float('inf') else dist[v],
            "reachable": dist[v] != float('inf'),
            "path": path,
        })

    return jsonify({
        "n": n,
        "source": source,
        "edges": [{"u": u, "v": v, "weight": w} for u, adj in graph.items() for v, w in adj],
        "vertices": vertices,
        "time_ms": round(elapsed_ms, 4),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
