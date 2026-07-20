# Min-Max Lab — Divide & Conquer (CS5303 Ex. No. 5)

Flask app implementing the Divide & Conquer min-max algorithm and comparing
it against the naive linear scan, with a REST API and an interactive
frontend.

## Routes

| Method | Path         | Description                                                              |
|--------|--------------|---------------------------------------------------------------------------|
| GET    | `/`          | Interactive frontend — enter or randomize an array, compare D&C vs naive vs the 3n/2−2 formula |
| GET    | `/api`       | JSON info about available endpoints                                      |
| GET    | `/health`    | Health check                                                              |
| POST   | `/minmax`    | Body: `{"array": [numbers]}` → min, max, D&C comparisons, naive comparisons, timing |
| GET    | `/benchmark` | Query param: `sizes` (comma-separated, default `10,100,1000,10000`) → comparison table on random arrays |

### Example

```bash
curl -X POST https://<your-app>.onrender.com/minmax \
  -H "Content-Type: application/json" \
  -d '{"array": [3, 1, 7, 4, 9, 2, 8, 5, 6, 0]}'

curl "https://<your-app>.onrender.com/benchmark?sizes=10,100,1000"
```

## Deploying on Render (same pattern as Labs 2-4)

1. Copy this `lab5` folder into your existing `daalab` repo, alongside `lab2`, `lab3`, `lab4`.
2. Commit and push:
   ```bash
   git add lab5
   git commit -m "Add Lab 5 - Min-Max Divide and Conquer API"
   git push
   ```
3. In the Render Dashboard: **New → Web Service** → select your `daalab` repo.
4. Set:
   - **Root Directory**: `lab5`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free
5. Click **Deploy web service**.

You'll get a separate URL for this lab, e.g. `https://minmax-api.onrender.com`.

## Running locally

```bash
pip install -r requirements.txt
python app.py          # dev server on http://localhost:5000
# or, production-style:
gunicorn app:app
```
