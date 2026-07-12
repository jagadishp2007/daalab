# Shortest Path Lab — Dijkstra (CS5303 Ex. No. 4)

Flask app implementing Dijkstra's single-source shortest path algorithm
(min-heap based), with a REST API and an interactive directed-graph
visualization frontend.

## Routes

| Method | Path        | Description                                                        |
|--------|-------------|----------------------------------------------------------------------|
| GET    | `/`         | Interactive frontend — edit the graph, run Dijkstra, click any vertex to trace its shortest path |
| GET    | `/api`      | JSON info about available endpoints                                  |
| GET    | `/health`   | Health check                                                        |
| POST   | `/dijkstra` | Body: `{"graph": {"0": [[v,w], ...], ...}, "source": int}` → distances, predecessor tree, and reconstructed paths for every vertex |

### Example

```bash
curl -X POST https://<your-app>.onrender.com/dijkstra \
  -H "Content-Type: application/json" \
  -d '{
    "graph": {
      "0": [[1,4],[2,1]],
      "1": [[3,1]],
      "2": [[1,2],[3,5]],
      "3": [[4,3]],
      "4": [[5,2]],
      "5": []
    },
    "source": 0
  }'
```

## Deploying on Render (same pattern as Lab 2 / Lab 3)

1. Copy this `lab4` folder into your existing `daalab` repo, alongside `lab2` and `lab3`.
2. Commit and push:
   ```bash
   git add lab4
   git commit -m "Add Lab 4 - Dijkstra shortest path API"
   git push
   ```
3. In the Render Dashboard: **New → Web Service** → select your `daalab` repo.
4. Set:
   - **Root Directory**: `lab4`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free
5. Click **Deploy web service**.

You'll get a separate URL for this lab, e.g. `https://dijkstra-api.onrender.com`.

## Running locally

```bash
pip install -r requirements.txt
python app.py          # dev server on http://localhost:5000
# or, production-style:
gunicorn app:app
```
