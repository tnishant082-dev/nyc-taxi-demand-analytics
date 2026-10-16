-- pickup borough to dropoff borough flows
SELECT pz.borough AS pickup_borough, dz.borough AS dropoff_borough,
       count(*) AS trips,
       round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS pct_trips,
       round(avg(f.total_amount), 2) AS avg_total
FROM fact_trips f
JOIN dim_zone pz ON pz.zone_id = f.pu_zone_id
JOIN dim_zone dz ON dz.zone_id = f.do_zone_id
GROUP BY ALL ORDER BY trips DESC LIMIT 15;
