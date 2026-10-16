"""Clean raw yellow taxi trips and log how many rows each rule removes.

Writes data/processed/trips_clean.parquet (gitignored) and
data/processed/cleaning_log.csv (committed).
"""
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

# each rule is applied in order; the log records rows dropped by that rule
RULES = [
    ("pickup inside study window (Jun-Aug 2025)",
     "tpep_pickup_datetime >= TIMESTAMP '2025-06-01' AND tpep_pickup_datetime < TIMESTAMP '2025-09-01'"),
    ("valid pickup/dropoff zone (1-263)",
     "PULocationID BETWEEN 1 AND 263 AND DOLocationID BETWEEN 1 AND 263"),
    ("duration between 1 and 180 min",
     "date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime) BETWEEN 60 AND 10800"),
    ("distance between 0.1 and 100 miles",
     "trip_distance BETWEEN 0.1 AND 100"),
    ("fare between $3 and $500 (meter drop is $3)",
     "fare_amount BETWEEN 3 AND 500"),
    ("non-negative tip/tolls/extras, total >= fare",
     "tip_amount >= 0 AND tolls_amount >= 0 AND extra >= 0 AND total_amount >= fare_amount"),
    ("average speed under 70 mph",
     "trip_distance / (date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime) / 3600.0) < 70"),
    ("passenger count missing or 1-6",
     "passenger_count IS NULL OR passenger_count BETWEEN 1 AND 6"),
    ("rate code missing or a valid TLC code",
     "RatecodeID IS NULL OR RatecodeID IN (1, 2, 3, 4, 5, 6)"),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"CREATE TABLE t AS SELECT * FROM read_parquet('{RAW}/yellow_tripdata_2025-*.parquet')")
    log = []
    start = con.execute("SELECT count(*) FROM t").fetchone()[0]
    log.append(("raw rows (3 monthly files)", start, 0))
    for name, cond in RULES:
        before = con.execute("SELECT count(*) FROM t").fetchone()[0]
        con.execute(f"DELETE FROM t WHERE NOT ({cond}) OR ({cond}) IS NULL")
        after = con.execute("SELECT count(*) FROM t").fetchone()[0]
        log.append((name, after, before - after))
        print(f"{name:<50} kept {after:>10,}  dropped {before - after:>9,}")
    con.execute(f"""
        COPY (
          SELECT
            VendorID AS vendor_id,
            tpep_pickup_datetime AS pickup_ts,
            tpep_dropoff_datetime AS dropoff_ts,
            passenger_count, trip_distance, RatecodeID AS ratecode_id,
            PULocationID AS pu_zone_id, DOLocationID AS do_zone_id,
            payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount,
            improvement_surcharge, congestion_surcharge, Airport_fee AS airport_fee,
            cbd_congestion_fee, total_amount,
            date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime) / 60.0 AS duration_min
          FROM t
        ) TO '{OUT}/trips_clean.parquet' (FORMAT parquet, COMPRESSION zstd)
    """)
    import pandas as pd
    df = pd.DataFrame(log, columns=["step", "rows_remaining", "rows_dropped"])
    df["pct_of_raw_remaining"] = (df.rows_remaining / start * 100).round(2)
    df.to_csv(OUT / "cleaning_log.csv", index=False)
    print(f"\nraw {start:,} -> clean {df.rows_remaining.iloc[-1]:,}")


if __name__ == "__main__":
    main()
