-- credit-card tip rate by hour of day
SELECT f.hour_key,
       count(*) AS card_trips,
       round(100.0 * sum(f.tip_amount) / sum(f.fare_amount), 1) AS tip_pct_of_fare,
       round(avg(f.tip_amount), 2) AS avg_tip
FROM fact_trips f
WHERE f.payment_type_id = 1
GROUP BY 1 ORDER BY 1;
