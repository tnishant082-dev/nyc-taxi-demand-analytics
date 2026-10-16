-- headline KPIs for the whole window
SELECT
    count(*)                                         AS trips,
    round(sum(total_amount), 0)                      AS gross_revenue,
    round(avg(total_amount), 2)                      AS avg_total_per_trip,
    round(avg(fare_amount), 2)                       AS avg_fare,
    round(avg(trip_distance), 2)                     AS avg_distance_mi,
    round(median(trip_distance), 2)                  AS median_distance_mi,
    round(avg(duration_min), 1)                      AS avg_duration_min,
    round(sum(fare_amount) / sum(trip_distance), 2)  AS fare_per_mile,
    round(count(*) / count(DISTINCT date_key), 0)    AS avg_trips_per_day
FROM fact_trips;
