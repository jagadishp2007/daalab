"""
CS5303 - DAA Lab | Ex. No. 2
Comparative Analysis of Naive, Rabin-Karp, and KMP Algorithms for String Matching

REST API wrapper around the three string-matching algorithms.
Deployable on Render as a Web Service.
"""

import random
import string
import time

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


# ----------------------------
# Algorithms
# ----------------------------

def naive_search(text, pattern):
    n, m = len(text), len(pattern)
    matches, comparisons = [], 0
    for i in range(n - m + 1):
        j = 0
        while j < m:
            comparisons += 1
            if text[i + j] != pattern[j]:
                break
            j += 1
        if j == m:
            matches.append(i)
    return matches, comparisons


def compute_lps(pattern):
    m = len(pattern)
    lps = [0] * m
    length, i = 0, 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1
    return lps


def kmp_search(text, pattern):
    n, m = len(text), len(pattern)
    lps = compute_lps(pattern)
    matches, comparisons = [], 0
    i = j = 0
    while i < n:
        comparisons += 1
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == m:
            matches.append(i - j)
            j = lps[j - 1]
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return matches, comparisons


def rabin_karp(text, pattern, q=101):
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return [], 0
    d = 256
    h = pow(d, m - 1, q)
    p_hash = t_hash = 0
    matches, comparisons = [], 0
    for i in range(m):
        p_hash = (d * p_hash + ord(pattern[i])) % q
        t_hash = (d * t_hash + ord(text[i])) % q
    for s in range(n - m + 1):
        if p_hash == t_hash:
            for k in range(m):
                comparisons += 1
                if text[s + k] != pattern[k]:
                    break
            else:
                matches.append(s)
        if s < n - m:
            t_hash = (d * (t_hash - ord(text[s]) * h) + ord(text[s + m])) % q
            if t_hash < 0:
                t_hash += q
    return matches, comparisons


ALGORITHMS = {
    "naive": naive_search,
    "kmp": kmp_search,
    "rabin_karp": rabin_karp,
}


def run_all(text, pattern):
    result = {}
    for name, fn in ALGORITHMS.items():
        start = time.perf_counter()
        matches, comparisons = fn(text, pattern)
        elapsed_ms = (time.perf_counter() - start) * 1000
        result[name] = {
            "matches": matches,
            "comparisons": comparisons,
            "time_ms": round(elapsed_ms, 4),
        }
    return result


# ----------------------------
# Routes
# ----------------------------

@app.get("/")
def index():
    return jsonify({
        "service": "String Matching Algorithms API",
        "endpoints": {
            "GET /": "this help message",
            "GET /ui": "interactive frontend (try it in a browser)",
            "GET /health": "health check",
            "POST /search": "body: {\"text\": str, \"pattern\": str} -> matches/comparisons for all 3 algorithms",
            "GET /benchmark": "optional query params: length (int, default 10000), patterns (comma-separated, default AB,ABCD,ABCDAB,ABCDABCD)",
        },
    })


@app.get("/ui")
def ui():
    return render_template("ui.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/search")
def search():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    pattern = data.get("pattern")

    if not isinstance(text, str) or not isinstance(pattern, str):
        return jsonify({"error": "Both 'text' and 'pattern' are required and must be strings."}), 400
    if len(pattern) == 0:
        return jsonify({"error": "'pattern' must be non-empty."}), 400
    if len(pattern) > len(text):
        return jsonify({"error": "'pattern' cannot be longer than 'text'."}), 400

    return jsonify({
        "text": text,
        "pattern": pattern,
        "results": run_all(text, pattern),
    })


@app.get("/benchmark")
def benchmark():
    try:
        length = int(request.args.get("length", 10000))
    except ValueError:
        return jsonify({"error": "'length' must be an integer."}), 400
    length = max(1, min(length, 200000))  # guard against abuse

    patterns_param = request.args.get("patterns", "AB,ABCD,ABCDAB,ABCDABCD")
    patterns = [p for p in patterns_param.split(",") if p]

    text_large = "".join(random.choices("ABCD", k=length))

    table = []
    for p in patterns:
        if len(p) > length:
            continue
        row = {"pattern": p}
        results = run_all(text_large, p)
        for algo, r in results.items():
            row[algo] = {"comparisons": r["comparisons"], "time_ms": r["time_ms"]}
        table.append(row)

    return jsonify({
        "text_length": length,
        "alphabet": "ABCD",
        "patterns": patterns,
        "benchmark": table,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)