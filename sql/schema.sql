-- star schema for the cleaned yellow taxi trips (DuckDB)
-- grain of fact_trips: one completed, cleaned trip

CREATE OR REPLACE TABLE dim_zone AS
SELECT
    CAST(LocationID AS INTEGER)               AS zone_id,
    Borough                                   AS borough,
    Zone                                      AS zone_name,
    service_zone,
    CASE WHEN LocationID IN (1, 132, 138) THEN 1 ELSE 0 END AS is_airport
FROM read_csv_auto('data/raw/taxi_zone_lookup.csv');

CREATE OR REPLACE TABLE dim_date AS
SELECT
    CAST(strftime(d, '%Y%m%d') AS INTEGER)    AS date_key,
    CAST(d AS DATE)                           AS full_date,
    year(d)                                   AS year,
    month(d)                                  AS month,
    strftime(d, '%b %Y')                      AS month_label,
    day(d)                                    AS day_of_month,
    isodow(d)                                 AS iso_weekday,
    strftime(d, '%a')                         AS weekday_name,
    CASE WHEN isodow(d) IN (6, 7) THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    CASE WHEN CAST(d AS DATE) IN (DATE '2025-06-19', DATE '2025-07-04') THEN 1 ELSE 0 END AS is_us_holiday
FROM range(TIMESTAMP '2025-06-01', TIMESTAMP '2025-09-01', INTERVAL 1 DAY) r(d);

CREATE OR REPLACE TABLE dim_time AS
SELECT
    h                                         AS hour_key,
    lpad(CAST(h AS VARCHAR), 2, '0') || ':00' AS hour_label,
    CASE
        WHEN h BETWEEN 6 AND 9  THEN 'AM peak (6-10)'
        WHEN h BETWEEN 10 AND 15 THEN 'Midday (10-16)'
        WHEN h BETWEEN 16 AND 19 THEN 'PM peak (16-20)'
        WHEN h BETWEEN 20 AND 23 THEN 'Evening (20-24)'
        ELSE 'Overnight (0-6)'
    END                                       AS day_part
FROM range(0, 24) r(h);

CREATE OR REPLACE TABLE dim_payment AS
SELECT * FROM (VALUES
    (0, 'Flex fare / not recorded'),
    (1, 'Credit card'),
    (2, 'Cash'),
    (3, 'No charge'),
    (4, 'Dispute'),
    (5, 'Unknown'),
    (6, 'Voided trip')
) v(payment_type_id, payment_type);

CREATE OR REPLACE TABLE fact_trips AS
SELECT
    row_number() OVER ()                              AS trip_id,
    CAST(strftime(pickup_ts, '%Y%m%d') AS INTEGER)    AS date_key,
    hour(pickup_ts)                                   AS hour_key,
    pu_zone_id,
    do_zone_id,
    CAST(payment_type AS INTEGER)                     AS payment_type_id,
    vendor_id,
    CAST(ratecode_id AS INTEGER)                      AS ratecode_id,
    passenger_count,
    trip_distance,
    round(duration_min, 2)                            AS duration_min,
    fare_amount,
    tip_amount,
    tolls_amount,
    coalesce(airport_fee, 0)                          AS airport_fee,
    coalesce(cbd_congestion_fee, 0)                   AS cbd_congestion_fee,
    total_amount
FROM read_parquet('data/processed/trips_clean.parquet');
