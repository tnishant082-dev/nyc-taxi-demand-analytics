-- tip behaviour by payment type (cash tips are not recorded by the meter)
SELECT p.payment_type,
       count(*) AS trips,
       round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS pct_trips,
       round(avg(f.tip_amount), 2) AS avg_tip,
       round(100.0 * sum(f.tip_amount) / sum(f.fare_amount), 1) AS tip_pct_of_fare,
       round(100.0 * avg(CASE WHEN f.tip_amount > 0 THEN 1 ELSE 0 END), 1) AS pct_trips_tipped
FROM fact_trips f JOIN dim_payment p USING (payment_type_id)
GROUP BY 1 ORDER BY trips DESC;
