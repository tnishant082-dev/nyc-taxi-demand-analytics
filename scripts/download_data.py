"""Download NYC TLC yellow taxi trip records and the taxi zone lookup.

Files come from the official TLC trip record page:
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
"""
import sys
import urllib.request
from pathlib import Path

BASE = "https://d37ci6vzurychx.cloudfront.net"
MONTHS = ["2025-06", "2025-07", "2025-08"]
RAW = Path(__file__).resolve().parents[1] / "data" / "raw"


def fetch(url: str, dest: Path) -> None:
    if dest.exists():
        print(f"skip {dest.name} (already there)")
        return
    print(f"downloading {url}")
    urllib.request.urlretrieve(url, dest)


def main(months=MONTHS) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for m in months:
        name = f"yellow_tripdata_{m}.parquet"
        fetch(f"{BASE}/trip-data/{name}", RAW / name)
    fetch(f"{BASE}/misc/taxi_zone_lookup.csv", RAW / "taxi_zone_lookup.csv")


if __name__ == "__main__":
    main(sys.argv[1:] or MONTHS)
