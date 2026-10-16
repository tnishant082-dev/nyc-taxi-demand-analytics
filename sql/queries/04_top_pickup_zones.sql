-- top 15 pickup zones by trips with revenue share
SELECT z.zone_name, z.borough,
       count(*) AS trips,
       round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS pct_trips,
       round(sum(f.total_amount), 0) AS revenue,
       round(avg(f.total_amount), 2) AS avg_total
FROM fact_trips f JOIN dim_zone z ON z.zone_id = f.pu_zone_id
GROUP BY ALL ORDER BY trips DESC LIMIT 15;
