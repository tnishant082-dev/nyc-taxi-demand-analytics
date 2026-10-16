-- month-over-month volume and revenue
SELECT d.month, d.month_label,
       count(*) AS trips,
       round(count(*) / count(DISTINCT f.date_key), 0) AS trips_per_day,
       round(sum(f.total_amount), 0) AS revenue,
       round(avg(f.total_amount), 2) AS avg_total,
       round(100.0 * (count(*) - lag(count(*)) OVER (ORDER BY d.month)) / lag(count(*)) OVER (ORDER BY d.month), 1) AS trips_mom_pct
FROM fact_trips f JOIN dim_date d USING (date_key)
GROUP BY 1, 2 ORDER BY 1;
