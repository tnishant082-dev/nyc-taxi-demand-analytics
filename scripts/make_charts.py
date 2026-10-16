"""Build the four chart pages in screenshots/charts from the warehouse and sql/results.

These are matplotlib charts that mirror the Power BI report pages; they are
not Power BI screenshots.
"""
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "sql" / "results"
OUT = ROOT / "screenshots" / "charts"
AGG = ROOT / "data" / "processed"
BLUE, ORANGE, GREY, TEAL = "#1f5f99", "#e07b25", "#8a8886", "#2a9d8f"

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlesize": 11})


def r(name):
    return pd.read_csv(RES / f"{name}.csv")


def daily_and_heatmap():
    con = duckdb.connect(str(ROOT / "data" / "warehouse" / "nyc_taxi.duckdb"), read_only=True)
    daily = con.execute("""
        SELECT d.full_date, d.day_type, count(*) AS trips, round(sum(f.total_amount), 0) AS revenue
        FROM fact_trips f JOIN dim_date d USING (date_key) GROUP BY ALL ORDER BY 1""").df()
    heat = con.execute("""
        SELECT d.iso_weekday, d.weekday_name, f.hour_key,
               round(count(*) / count(DISTINCT f.date_key), 0) AS avg_trips
        FROM fact_trips f JOIN dim_date d USING (date_key) GROUP BY ALL ORDER BY 1, 3""").df()
    daily.to_csv(AGG / "daily_trips.csv", index=False)
    heat.to_csv(AGG / "weekday_hour_trips.csv", index=False)
    return daily, heat


def kpi(ax, label, value):
    ax.axis("off")
    ax.text(0.5, 0.62, value, ha="center", va="center", fontsize=20, weight="bold", color=BLUE)
    ax.text(0.5, 0.22, label, ha="center", va="center", fontsize=10, color=GREY)


def page(title, subtitle="NYC TLC yellow taxi trips, Jun-Aug 2025 (10.1M cleaned trips)"):
    fig = plt.figure(figsize=(16, 9), dpi=110)
    fig.text(0.02, 0.96, title, fontsize=18, weight="bold")
    fig.text(0.02, 0.93, subtitle, fontsize=10, color=GREY)
    return fig


def overview(daily):
    k = r("01_headline_kpis").iloc[0]
    m = r("02_month_trend")
    fig = page("1. Executive overview")
    gs = fig.add_gridspec(3, 4, top=0.88, hspace=0.45, wspace=0.3, height_ratios=[0.5, 1, 1])
    kpi(fig.add_subplot(gs[0, 0]), "cleaned trips", f"{k.trips/1e6:.2f}M")
    kpi(fig.add_subplot(gs[0, 1]), "gross revenue (total_amount)", f"${k.gross_revenue/1e6:.1f}M")
    kpi(fig.add_subplot(gs[0, 2]), "avg total per trip", f"${k.avg_total_per_trip:.2f}")
    kpi(fig.add_subplot(gs[0, 3]), "avg trips per day", f"{k.avg_trips_per_day:,.0f}")
    ax = fig.add_subplot(gs[1, :])
    c = np.where(daily.day_type == "Weekend", ORANGE, BLUE)
    ax.bar(pd.to_datetime(daily.full_date), daily.trips, color=c)
    ax.set_title("Trips per day (orange = weekend)")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v/1000:.0f}k")
    ax = fig.add_subplot(gs[2, :2])
    ax.bar(m.month_label, m.trips_per_day, color=BLUE)
    for i, v in enumerate(m.trips_per_day):
        ax.text(i, v, f"{v:,.0f}", ha="center", va="bottom")
    ax.set_title("Average trips per day by month")
    ax = fig.add_subplot(gs[2, 2:])
    ax.bar(m.month_label, m.revenue / 1e6, color=TEAL)
    for i, v in enumerate(m.revenue / 1e6):
        ax.text(i, v, f"${v:.1f}M", ha="center", va="bottom")
    ax.set_title("Revenue by month ($M)")
    fig.savefig(OUT / "01-executive-overview.png")
    plt.close(fig)


def demand(heat):
    fig = page("2. Demand by time")
    gs = fig.add_gridspec(2, 2, top=0.88, hspace=0.4, wspace=0.25)
    ax = fig.add_subplot(gs[0, :])
    piv = heat.pivot(index="weekday_name", columns="hour_key", values="avg_trips")
    piv = piv.loc[["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]]
    im = ax.imshow(piv.values, aspect="auto", cmap="Blues")
    ax.set_yticks(range(7), piv.index)
    ax.set_xticks(range(24), [f"{h:02d}" for h in range(24)])
    ax.set_title("Average trips per hour by weekday and pickup hour")
    fig.colorbar(im, ax=ax, fraction=0.02)
    ph = r("03_peak_hours")
    ax = fig.add_subplot(gs[1, 0])
    for dt, col in [("Weekday", BLUE), ("Weekend", ORANGE)]:
        s = ph[ph.day_type == dt]
        ax.plot(s.hour_key, s.avg_trips_per_day, color=col, marker="o", ms=3, label=dt)
    ax.legend(frameon=False)
    ax.set_title("Average trips per day by hour")
    ax.set_xlabel("pickup hour")
    ax = fig.add_subplot(gs[1, 1])
    for dt, col in [("Weekday", BLUE), ("Weekend", ORANGE)]:
        s = ph[ph.day_type == dt]
        ax.plot(s.hour_key, s.avg_speed_mph, color=col, marker="o", ms=3, label=dt)
    ax.legend(frameon=False)
    ax.set_title("Average trip speed by hour (mph)")
    ax.set_xlabel("pickup hour")
    fig.savefig(OUT / "02-demand-by-time.png")
    plt.close(fig)


def zones():
    fig = page("3. Zones and airports")
    gs = fig.add_gridspec(2, 2, top=0.88, left=0.13, hspace=0.4, wspace=0.45)
    z = r("04_top_pickup_zones").iloc[::-1]
    ax = fig.add_subplot(gs[:, 0])
    ax.barh(z.zone_name, z.trips / 1000, color=[ORANGE if "Airport" in n else BLUE for n in z.zone_name])
    ax.set_title("Top 15 pickup zones (thousand trips)")
    a = r("06_airport_trips")
    ax = fig.add_subplot(gs[0, 1])
    a = a[a.trips > 1000]
    x = np.arange(len(a))
    ax.bar(x - 0.2, a.pct_trips, 0.4, color=BLUE, label="% of trips")
    ax.bar(x + 0.2, a.pct_revenue, 0.4, color=ORANGE, label="% of revenue")
    ax.set_xticks(x, a.pickup_group)
    ax.legend(frameon=False)
    ax.set_title("Airport pickups: share of trips vs revenue")
    b = r("05_borough_flows").head(8).iloc[::-1]
    ax = fig.add_subplot(gs[1, 1])
    ax.barh(b.pickup_borough + " -> " + b.dropoff_borough, b.pct_trips, color=TEAL)
    ax.set_title("Top borough flows (% of trips)")
    fig.savefig(OUT / "03-zones-and-airports.png")
    plt.close(fig)


def revenue():
    fig = page("4. Revenue and tips")
    gs = fig.add_gridspec(2, 2, top=0.88, hspace=0.45, wspace=0.3)
    t = r("07_tip_by_payment")
    t = t[t.trips > 1000]
    ax = fig.add_subplot(gs[0, 0])
    ax.bar(t.payment_type, t.tip_pct_of_fare, color=BLUE)
    for i, v in enumerate(t.tip_pct_of_fare):
        ax.text(i, v, f"{v}%", ha="center", va="bottom")
    ax.set_title("Recorded tip as % of fare by payment type")
    ax.tick_params(axis="x", labelsize=8)
    ax = fig.add_subplot(gs[0, 1])
    h = r("08_card_tip_by_hour")
    ax.plot(h.hour_key, h.tip_pct_of_fare, color=ORANGE, marker="o", ms=3)
    ax.set_title("Credit-card tip % of fare by pickup hour")
    ax.set_xlabel("pickup hour")
    d = r("09_revenue_per_mile_by_distance")
    lab = d.distance_band.str[3:]
    ax = fig.add_subplot(gs[1, 0])
    ax.bar(lab, d.revenue_per_mile, color=TEAL)
    for i, v in enumerate(d.revenue_per_mile):
        ax.text(i, v, f"${v:.2f}", ha="center", va="bottom")
    ax.set_title("Revenue per mile by trip length")
    ax = fig.add_subplot(gs[1, 1])
    ax.bar(lab, d.pct_trips, color=BLUE)
    ax.set_title("Share of trips by trip length (%)")
    fig.savefig(OUT / "04-revenue-and-tips.png")
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    daily, heat = daily_and_heatmap()
    overview(daily)
    demand(heat)
    zones()
    revenue()
    print("charts saved to", OUT)


if __name__ == "__main__":
    main()
