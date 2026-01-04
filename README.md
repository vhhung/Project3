# TMDB Movies Analysis (Pandas) — Project 11

Analyze the `tmdb-movies.csv` dataset using **Python + pandas** and export results for **7 questions** into `output/q1.csv` … `output/q7.csv`.

---

## Project Structure

```
project3/
  .venv/                  # virtual environment (do NOT commit)
  data/
    tmdb-movies.csv
  output/                 # generated after running
  main.py
  requirements.txt
  .gitignore              # recommended
  README.md
```

---

## Requirements

- Python 3.9+ (3.10+ recommended)
- pandas (installed from `requirements.txt`)

Example `requirements.txt`:
```
pandas==2.3.3
```

---

## Setup (Virtual Environment)

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Run

Make sure the dataset is located at:

- `data/tmdb-movies.csv`

Then run:

```bash
python main.py
```

The script will create an `output/` folder and export:

- `output/q1.csv`
- `output/q2.csv`
- `output/q3.csv`
- `output/q4.csv`
- `output/q5.csv`
- `output/q6.csv`
- `output/q7.csv`

---

## Questions & Outputs

### Q1 — Sort movies by release date (descending)
**Output:** `output/q1.csv`  
Sort movies by `release_date` from newest to oldest (invalid/missing dates are removed).

### Q2 — Filter movies with average rating > 7.5
**Output:** `output/q2.csv`  
Filter rows where `vote_average > 7.5` and sort by rating (and `vote_count` if available).

### Q3 — Highest and lowest revenue movie
**Output:** `output/q3.csv`  
Return 2 rows:
- `highest_revenue`: movie with maximum `revenue`
- `lowest_revenue`: movie with minimum **positive** `revenue`

> Note: `revenue == 0` is excluded because it usually means unknown/missing in this dataset.

### Q4 — Total revenue of all movies
**Output:** `output/q4.csv`  
Sum `revenue` for all movies with `revenue > 0`.

### Q5 — Top 10 movies with highest profit
**Output:** `output/q5.csv`  
Compute:
```
profit = revenue - budget
```
Only movies with `revenue > 0` and `budget > 0` are included.

### Q6 — Director with most movies & Actor with most movies
**Output:** `output/q6.csv`  
- Director: based on the `director` column  
- Actor: based on the `cast` column (split by `|`)

### Q7 — Count movies by genre
**Output:** `output/q7.csv`  
Split `genres` by `|` and count the number of movies per genre.

---

## Important Data Cleaning Notes

- `release_date` is stored as `m/d/yy` (example: `12/15/74`).  
  The script parses it using the correct format and fixes “future year” issues (e.g., 2074 → 1974).
- Duplicates are removed.
- Text columns are trimmed (whitespace removed at both ends).
- `revenue == 0` is treated as “not meaningful for analysis” and excluded from Q3/Q4/Q5.

---

## Recommended `.gitignore`

Create a `.gitignore` file in the project root:

```
.venv/
__pycache__/
*.pyc
```

---

## Troubleshooting

### `No module named 'pandas'`
Your IDE is likely using the wrong interpreter. Activate `.venv` and install dependencies:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Release dates show years like 2074
That happens when parsing 2-digit years incorrectly. This project already fixes it by parsing with `"%m/%d/%y"` and correcting future years.
