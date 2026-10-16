"""Run every query in sql/queries against the warehouse and save results to sql/results."""
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    con = duckdb.connect(str(ROOT / "data" / "warehouse" / "nyc_taxi.duckdb"), read_only=True)
    out = ROOT / "sql" / "results"
    out.mkdir(parents=True, exist_ok=True)
    for q in sorted((ROOT / "sql" / "queries").glob("*.sql")):
        df = con.execute(q.read_text()).df()
        df.to_csv(out / f"{q.stem}.csv", index=False)
        print(f"\n== {q.stem} ({len(df)} rows)")
        print(df.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
