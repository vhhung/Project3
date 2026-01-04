import os
import pandas as pd

DATA_PATH = "data/tmdb-movies.csv"
FALLBACK_PATH = "/mnt/data/tmdb-movies.csv"
OUT_DIR = "output"


def ensure_outdir() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)


def resolve_data_path() -> str:
    if os.path.exists(DATA_PATH):
        return DATA_PATH
    if os.path.exists(FALLBACK_PATH):
        return FALLBACK_PATH
    raise FileNotFoundError(f"Cannot find data at '{DATA_PATH}'")


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean global:
    - drop duplicates
    - strip strings
    - keep NA properly (avoid turning NaN into 'nan')
    """
    df = df.copy().drop_duplicates()

    obj_cols = df.select_dtypes(include="object").columns
    for c in obj_cols:
        df.loc[:, c] = df[c].astype("string").str.strip()

    return df


def prepare_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fix datatypes:
    - parse release_date correctly (m/d/yy) and fix future-year issue
    - convert numeric cols
    - create profit
    """
    df = df.copy()

    # release_date in this dataset is like 12/15/74 (month/day/2-digit-year)
    if "release_date" in df.columns:
        dt = pd.to_datetime(df["release_date"], format="%m/%d/%y", errors="coerce")

        # Fix cases like 2074 -> 1974 (if dt year > current year)
        current_year = pd.Timestamp.today().year
        mask = dt.notna() & (dt.dt.year > current_year)
        dt.loc[mask] = dt.loc[mask] - pd.DateOffset(years=100)

        df["release_date"] = dt

    # numeric conversions
    num_cols = [
        "popularity", "budget", "revenue", "runtime",
        "vote_count", "vote_average", "budget_adj", "revenue_adj",
        "release_year",
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # profit (prefer raw revenue/budget)
    if "revenue" in df.columns and "budget" in df.columns:
        df["profit"] = df["revenue"] - df["budget"]
    elif "revenue_adj" in df.columns and "budget_adj" in df.columns:
        df["profit"] = df["revenue_adj"] - df["budget_adj"]

    return df


def explode_pipe(df: pd.DataFrame, col: str, new_col: str) -> pd.DataFrame:
    """
    Split pipe-separated values into rows: "A|B|C"
    """
    if col not in df.columns:
        raise ValueError(f"Missing column '{col}'")

    tmp = df.copy()
    tmp = tmp.dropna(subset=[col])

    tmp[new_col] = tmp[col].astype("string").str.split("|")
    tmp = tmp.explode(new_col)
    tmp[new_col] = tmp[new_col].astype("string").str.strip()
    tmp = tmp.dropna(subset=[new_col])

    return tmp



def q1_sort_by_release_date_desc(df: pd.DataFrame) -> pd.DataFrame:
    # drop rows where date is missing/invalid
    tmp = df.dropna(subset=["release_date"]).copy()
    return tmp.sort_values("release_date", ascending=False)


def q2_filter_vote_avg_gt_7_5(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.dropna(subset=["vote_average"]).copy()
    out = tmp[tmp["vote_average"] > 7.5].copy()
    sort_cols = [c for c in ["vote_average", "vote_count"] if c in out.columns]
    return out.sort_values(sort_cols, ascending=False)


def q3_highest_lowest_revenue(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.dropna(subset=["revenue"]).copy()
    tmp = tmp[tmp["revenue"] > 0]   # filter out revenue = 0

    if tmp.empty:
        return pd.DataFrame(columns=["type", "original_title", "revenue"])

    idx_max = tmp["revenue"].idxmax()
    idx_min = tmp["revenue"].idxmin()

    cols = [c for c in ["original_title", "revenue", "budget", "release_year", "release_date"] if c in tmp.columns]
    max_row = tmp.loc[[idx_max], cols].copy()
    max_row.insert(0, "type", "highest_revenue")

    min_row = tmp.loc[[idx_min], cols].copy()
    min_row.insert(0, "type", "lowest_revenue")

    return pd.concat([max_row, min_row], ignore_index=True)




def q4_total_revenue(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.dropna(subset=["revenue"]).copy()
    tmp = tmp[tmp["revenue"] > 0]   # filter out revenue = 0
    total = tmp["revenue"].sum()
    return pd.DataFrame([{"total_revenue": total}])




def q5_top10_profit(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.dropna(subset=["original_title", "revenue", "budget"]).copy()
    tmp = tmp[(tmp["revenue"] > 0) & (tmp["budget"] > 0)].copy()  # filter out revenue = 0 or budget = 0
    tmp["profit"] = tmp["revenue"] - tmp["budget"]

    cols = ["original_title", "release_year", "budget", "revenue", "profit"]
    cols = [c for c in cols if c in tmp.columns]
    return tmp.sort_values("profit", ascending=False).loc[:, cols].head(10)


def q6_top_director_and_actor(df: pd.DataFrame) -> pd.DataFrame:
    results = []

    # director: drop null directors
    if "director" in df.columns:
        dtmp = df.dropna(subset=["director"])
        if not dtmp.empty:
            vc = dtmp["director"].value_counts()
            if not vc.empty:
                results.append({"role": "director", "name": vc.index[0], "movie_count": int(vc.iloc[0])})

    # actor: explode cast, drop null cast
    if "cast" in df.columns:
        ctmp = df.dropna(subset=["cast"])
        if not ctmp.empty:
            tmp_cast = explode_pipe(ctmp, "cast", "actor")
            vc = tmp_cast["actor"].value_counts()
            if not vc.empty:
                results.append({"role": "actor", "name": vc.index[0], "movie_count": int(vc.iloc[0])})

    return pd.DataFrame(results, columns=["role", "name", "movie_count"])


def q7_count_movies_by_genre(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.dropna(subset=["genres"]).copy()
    g = explode_pipe(tmp, "genres", "genre")
    out = g.groupby("genre").size().reset_index(name="movie_count").sort_values("movie_count", ascending=False)
    return out


def save_q(out: pd.DataFrame, qnum: int) -> None:
    out.to_csv(os.path.join(OUT_DIR, f"q{qnum}.csv"), index=False)


def main() -> None:
    ensure_outdir()

    path = resolve_data_path()
    df = load_data(path)
    df = basic_clean(df)
    df = prepare_types(df)

    outs = [
        q1_sort_by_release_date_desc(df),
        q2_filter_vote_avg_gt_7_5(df),
        q3_highest_lowest_revenue(df),
        q4_total_revenue(df),
        q5_top10_profit(df),
        q6_top_director_and_actor(df),
        q7_count_movies_by_genre(df),
    ]

    for i, out in enumerate(outs, start=1):
        save_q(out, i)

    print("Done. Exported:")
    for i in range(1, 8):
        print(f"- {OUT_DIR}/q{i}.csv")


if __name__ == "__main__":
    main()
