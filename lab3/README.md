# MST Lab — Kruskal & Prim (CS5303 Ex. No. 3)

Flask app implementing Kruskal's and Prim's Minimum Spanning Tree algorithms,
with a REST API and an interactive graph visualization frontend.

## Routes

| Method | Path      | Description                                                        |
|--------|-----------|----------------------------------------------------------------------|
| GET    | `/`       | Interactive frontend — edit the graph, run both algorithms, see the MST drawn on the graph |
| GET    | `/api`    | JSON info about available endpoints                                  |
| GET    | `/health` | Health check                                                        |
| POST   | `/mst`    | Body: `{"n": int, "edges": [[weight,u,v], ...], "start": int (optional)}` → Kruskal & Prim MSTs, costs, timing |

### Example

```bash
curl -X POST https://<your-app>.onrender.com/mst \
  -H "Content-Type: application/json" \
  -d '{
    "n": 7,
    "edges": [[7,0,1],[5,0,3],[8,1,2],[9,1,3],[7,1,4],[5,2,4],[15,3,4],[6,3,5],[8,4,5],[9,4,6],[11,5,6]],
    "start": 0
  }'
```

## Deploying on Render (same pattern as Lab 2)

1. Copy this `lab3` folder into your existing `daalab` repo, alongside `lab2`.
2. Commit and push:
   ```bash
   git add lab3
   git commit -m "Add Lab 3 - Kruskal & Prim MST API"
   git push
   ```
3. In the Render Dashboard: **New → Web Service** → select your `daalab` repo.
4. Set:
   - **Root Directory**: `lab3`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free
5. Click **Deploy web service**.

You'll get a separate URL for this lab, e.g. `https://mst-api.onrender.com`.

## Running locally

```bash
pip install -r requirements.txt
python app.py          # dev server on http://localhost:5000
# or, production-style:
gunicorn app:app
```
