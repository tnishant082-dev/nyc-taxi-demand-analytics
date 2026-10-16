-- top 15 zone-to-zone routes
SELECT pz.zone_name AS pickup_zone, dz.zone_name AS dropoff_zone,
       count(*) AS trips,
       round(avg(f.trip_distance), 2) AS avg_distance_mi,
       round(avg(f.duration_min), 1) AS avg_duration_min,
       round(avg(f.total_amount), 2) AS avg_total
FROM fact_trips f
JOIN dim_zone pz ON pz.zone_id = f.pu_zone_id
JOIN dim_zone dz ON dz.zone_id = f.do_zone_id
WHERE f.pu_zone_id <> f.do_zone_id
GROUP BY ALL ORDER BY trips DESC LIMIT 15;
