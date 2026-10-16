"""Export the star schema for the Power BI project into data/powerbi.

Dimensions go out as CSV. The full fact table goes to fact_trips.parquet
(gitignored, ~10M rows) and a 200k-row random sample to
fact_trips_sample.parquet, which is committed so the report opens without
running the pipeline.
"""
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "powerbi"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(ROOT / "data" / "warehouse" / "nyc_taxi.duckdb"), read_only=True)
    for t in ["dim_zone", "dim_date", "dim_time", "dim_payment"]:
        con.execute(f"COPY {t} TO '{OUT}/{t}.csv' (HEADER)")
    cols = """trip_id, date_key, hour_key, pu_zone_id, do_zone_id, payment_type_id,
              trip_distance, duration_min, fare_amount, tip_amount, tolls_amount,
              airport_fee, cbd_congestion_fee, total_amount,
              CASE WHEN trip_distance < 1 THEN '1: <1 mi' WHEN trip_distance < 2 THEN '2: 1-2 mi'
                   WHEN trip_distance < 5 THEN '3: 2-5 mi' WHEN trip_distance < 10 THEN '4: 5-10 mi'
                   WHEN trip_distance < 20 THEN '5: 10-20 mi' ELSE '6: 20+ mi' END AS distance_band"""
    con.execute(f"COPY (SELECT {cols} FROM fact_trips) TO '{OUT}/fact_trips.parquet' (FORMAT parquet, COMPRESSION snappy)")
    con.execute(f"""COPY (SELECT {cols} FROM fact_trips USING SAMPLE reservoir(200000 ROWS) REPEATABLE (42) ORDER BY trip_id)
                    TO '{OUT}/fact_trips_sample.parquet' (FORMAT parquet, COMPRESSION snappy)""")
    print("exported to", OUT)


if __name__ == "__main__":
    main()
