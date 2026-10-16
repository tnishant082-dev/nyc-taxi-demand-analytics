-- weekday vs weekend averages per day
SELECT d.day_type,
       count(DISTINCT f.date_key) AS days,
       round(count(*) / count(DISTINCT f.date_key), 0) AS trips_per_day,
       round(sum(f.total_amount) / count(DISTINCT f.date_key), 0) AS revenue_per_day,
       round(avg(f.trip_distance), 2) AS avg_distance_mi,
       round(avg(f.total_amount), 2) AS avg_total,
       round(sum(f.trip_distance) / (sum(f.duration_min) / 60), 1) AS avg_speed_mph
FROM fact_trips f JOIN dim_date d USING (date_key)
GROUP BY 1 ORDER BY 1;
