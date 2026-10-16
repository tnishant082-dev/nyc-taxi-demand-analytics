-- average trips per day by weekday
SELECT d.iso_weekday, d.weekday_name,
       count(DISTINCT f.date_key) AS days,
       round(count(*) / count(DISTINCT f.date_key), 0) AS trips_per_day,
       round(sum(f.total_amount) / count(DISTINCT f.date_key), 0) AS revenue_per_day
FROM fact_trips f JOIN dim_date d USING (date_key)
GROUP BY 1, 2 ORDER BY 1;
