-- share of trips paying the manhattan cbd congestion relief fee, by pickup borough
SELECT z.borough,
       count(*) AS trips,
       round(100.0 * avg(CASE WHEN f.cbd_congestion_fee > 0 THEN 1 ELSE 0 END), 1) AS pct_paying_cbd_fee,
       round(sum(f.cbd_congestion_fee), 0) AS cbd_fee_collected
FROM fact_trips f JOIN dim_zone z ON z.zone_id = f.pu_zone_id
GROUP BY 1 ORDER BY trips DESC;
