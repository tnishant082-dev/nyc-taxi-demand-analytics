-- airport pickups (JFK, LaGuardia, Newark) vs everything else
SELECT CASE WHEN z.is_airport = 1 THEN z.zone_name ELSE 'Non-airport' END AS pickup_group,
       count(*) AS trips,
       round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS pct_trips,
       round(avg(f.trip_distance), 2) AS avg_distance_mi,
       round(avg(f.duration_min), 1) AS avg_duration_min,
       round(avg(f.total_amount), 2) AS avg_total,
       round(100.0 * sum(f.total_amount) / sum(sum(f.total_amount)) OVER (), 2) AS pct_revenue
FROM fact_trips f JOIN dim_zone z ON z.zone_id = f.pu_zone_id
GROUP BY 1 ORDER BY trips DESC;
