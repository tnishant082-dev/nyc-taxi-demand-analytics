"""Build the DuckDB star schema from the cleaned trips (run from repo root)."""
import os
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    os.chdir(ROOT)
    (ROOT / "data" / "warehouse").mkdir(parents=True, exist_ok=True)
    con = duckdb.connect("data/warehouse/nyc_taxi.duckdb")
    con.execute((ROOT / "sql" / "schema.sql").read_text())
    for t in ["dim_zone", "dim_date", "dim_time", "dim_payment", "fact_trips"]:
        print(t, con.execute(f"SELECT count(*) FROM {t}").fetchone()[0])
    con.close()


if __name__ == "__main__":
    main()
