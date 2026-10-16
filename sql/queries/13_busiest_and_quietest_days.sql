-- five busiest and five quietest days
(SELECT 'busiest' AS rank_group, d.full_date, d.weekday_name, count(*) AS trips
 FROM fact_trips f JOIN dim_date d USING (date_key) GROUP BY ALL ORDER BY trips DESC LIMIT 5)
UNION ALL
(SELECT 'quietest', d.full_date, d.weekday_name, count(*) AS trips
 FROM fact_trips f JOIN dim_date d USING (date_key) GROUP BY ALL ORDER BY trips ASC LIMIT 5);
