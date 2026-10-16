# DAX measures

All measures live in the `_Measures` table of `NycTaxiDemand.SemanticModel`.

| Measure | Folder | DAX | Notes |
|---|---|---|---|
| Trips | Volume | `COUNTROWS ( fact_trips )` | Cleaned trips |
| Revenue | Revenue | `SUM ( fact_trips[total_amount] )` | Sum of total_amount charged to riders |
| Fare Revenue | Revenue | `SUM ( fact_trips[fare_amount] )` | Metered fare only |
| Avg Total per Trip | Revenue | `DIVIDE ( [Revenue], [Trips] )` |  |
| Avg Fare | Revenue | `DIVIDE ( [Fare Revenue], [Trips] )` |  |
| Total Miles | Volume | `SUM ( fact_trips[trip_distance] )` |  |
| Avg Distance (mi) | Volume | `DIVIDE ( [Total Miles], [Trips] )` |  |
| Avg Duration (min) | Volume | `AVERAGE ( fact_trips[duration_min] )` |  |
| Revenue per Mile | Revenue | `DIVIDE ( [Revenue], [Total Miles] )` |  |
| Avg Speed (mph) | Volume | `DIVIDE ( [Total Miles], SUM ( fact_trips[duration_min] ) / 60 )` |  |
| Days | Volume | `DISTINCTCOUNT ( fact_trips[date_key] )` | Days with at least one trip in context |
| Trips per Day | Volume | `DIVIDE ( [Trips], [Days] )` |  |
| Revenue per Day | Revenue | `DIVIDE ( [Revenue], [Days] )` |  |
| Tips | Tips | `SUM ( fact_trips[tip_amount] )` |  |
| Tip % of Fare | Tips | `DIVIDE ( [Tips], [Fare Revenue] )` | Recorded tips only; cash tips are not captured |
| Card Tip % of Fare | Tips | `CALCULATE ( [Tip % of Fare], dim_payment[payment_type_id] = 1 )` |  |
| Tipped Trip % | Tips | `DIVIDE ( CALCULATE ( [Trips], fact_trips[tip_amount] > 0 ), [Trips] )` |  |
| Airport Pickups | Airports | `CALCULATE ( [Trips], dim_zone[is_airport] = 1 )` | Pickups at JFK, LaGuardia or Newark |
| Airport Pickup % | Airports | `DIVIDE ( [Airport Pickups], [Trips] )` |  |
| Airport Revenue % | Airports | `DIVIDE ( CALCULATE ( [Revenue], dim_zone[is_airport] = 1 ), [Revenue] )` |  |
| Dropoff Trips | Volume | `CALCULATE ( [Trips], USERELATIONSHIP ( fact_trips[do_zone_id], dim_zone[zone_id] ) )` | Trips counted by dropoff zone |
| Weekend Trips per Day | Volume | `CALCULATE ( [Trips per Day], dim_date[day_type] = "Weekend" )` |  |
| Weekday Trips per Day | Volume | `CALCULATE ( [Trips per Day], dim_date[day_type] = "Weekday" )` |  |
| CBD Fee Trip % | Revenue | `DIVIDE ( CALCULATE ( [Trips], fact_trips[cbd_congestion_fee] > 0 ), [Trips] )` | Share of trips charged the Manhattan congestion relief zone fee |
| Trips per Day MoM % | Volume | `VAR cur = [Trips per Day] VAR m = MAX ( dim_date[month] ) VAR prev = CALCULATE ( [Trips per Day], REMOVEFILTERS ( dim_date ), dim_date[month] = m - 1 ) RETURN IF ( NOT ISBLANK ( prev ), DIVIDE ( cur - prev, prev ) )` | Change in trips per day vs previous month |
