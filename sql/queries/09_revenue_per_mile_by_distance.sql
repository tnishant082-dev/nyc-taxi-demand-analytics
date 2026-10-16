-- revenue per mile and per minute by trip length band
SELECT CASE
         WHEN trip_distance < 1 THEN '1: <1 mi'
         WHEN trip_distance < 2 THEN '2: 1-2 mi'
         WHEN trip_distance < 5 THEN '3: 2-5 mi'
         WHEN trip_distance < 10 THEN '4: 5-10 mi'
         WHEN trip_distance < 20 THEN '5: 10-20 mi'
         ELSE '6: 20+ mi' END AS distance_band,
       count(*) AS trips,
       round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS pct_trips,
       round(avg(total_amount), 2) AS avg_total,
       round(sum(total_amount) / sum(trip_distance), 2) AS revenue_per_mile,
       round(sum(total_amount) / sum(duration_min), 2) AS revenue_per_minute
FROM fact_trips
GROUP BY 1 ORDER BY 1;
