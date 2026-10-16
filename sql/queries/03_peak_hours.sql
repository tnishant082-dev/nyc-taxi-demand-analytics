-- trips by pickup hour, weekday vs weekend, as average trips per day
SELECT t.hour_key, t.hour_label, t.day_part, d.day_type,
       count(*) AS trips,
       round(count(*) / count(DISTINCT f.date_key), 0) AS avg_trips_per_day,
       round(avg(f.duration_min), 1) AS avg_duration_min,
       round(sum(f.trip_distance) / (sum(f.duration_min) / 60), 1) AS avg_speed_mph
FROM fact_trips f
JOIN dim_time t USING (hour_key)
JOIN dim_date d USING (date_key)
GROUP BY ALL ORDER BY d.day_type, t.hour_key;
