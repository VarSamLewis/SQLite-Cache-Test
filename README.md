## SQLite Cache Test Report

### Overview
This test evaluates the use of SQLite as an in-memory cache for trip event data, using synthetic events generated in Python. The goal was to measure performance, data integrity, and resource usage under sustained write load.

### Methodology
- **Event Generation:** Synthetic trip events were created using the `generate_event()` function from `gen_data.py`, leveraging the Faker library for realistic data.
- **Cache Setup:** The cache was implemented in `sqlite.py` using an in-memory SQLite database. Performance-oriented PRAGMA settings were applied to maximize speed and minimize disk I/O.
- **Data Ingestion:** The `sqlite_main()` function handled table creation and event insertion. The main test loop in `run_test.py` repeatedly called this function to simulate continuous event ingestion.
- **Metrics Collection:** The test measured throughput, latency, data integrity (corrupt, duplicate, missing, and out-of-order records), and resource usage (memory and CPU). Results were printed after each run.

### Results
- **Performance:** The cache handled thousands of events per second with very low write latency:
	- Throughput: 1663.85 rows/second
	- Latency per Write: 0.2 milliseconds
- **Data Integrity:** No corrupt or duplicate records were observed. Out-of-order events were rare, and all generated events were accounted for.
	- Corrupt Records: 0
	- Duplicate trip_ids: 0
	- Out-of-Order Records: 64
	- Missing Records: 0
- **Resource Usage:** Memory and CPU usage were monitored and found to be reasonable for the test duration.
    - Memory Usage Delta: 226 MB
	- CPU Usage: 80.6% (single thread, single core)

### Diagram

```plaintext
+------------------+       +------------------+       +------------------+
|  Event Generator | ----> |   SQLite Cache   | ----> |   Postgresql DB  |
+------------------+       +------------------+       +------------------+
```

### Limitations in Test Methodology
- The test was conducted in a single-threaded environment, which does not reflect real-world concurrent access scenarios.
- Measurement is of the entire system, not just the cache.
- Python is slow, so the cache may be faster than reported.
- The out of order metric may be affected by system clock precision.
- The test was only ran for 60secs and may not reflect long-term performance or stability.
- Cache is cleared after each write to the DB, which may not reflect current caching strategies.

### Future Work
- **Multi-threaded Testing:** Future tests may introduce concurrent event generation and ingestion to evaluate thread safety and performance under parallel workloads.
- **Cloud Deployment:** Running the cache on cloud infrastructure will help assess scalability, network latency, and integration with distributed systems as well as allowing for more powerful hardware.
- **Extended Duration Tests:** Longer test runs will provide insights into stability, memory leaks, and performance degradation over time.

 
### Metrics Collected

- **Total Rows Written:** Number of events successfully inserted into the DB.
- **Throughput:** Events written per second.
- **Average Latency per Write:** Time taken for each insert operation.
- **Corrupt Records:** Count of records with missing or invalid fields.
- **Out-of-Order Records:** Number of events where timestamps are not in sequence.
- **Duplicate trip_ids:** Number of records with duplicate trip identifiers.
- **Missing Records:** Difference between generated and stored events.
- **Failed Writes:** Number of insert operations that did not succeed.
- **Constraint Violations:** Number of database constraint errors encountered.
- **Memory Usage Delta:** Change in memory consumption during the test.
- **CPU Usage:** Change in CPU utilization during the test.


### Dependencies
- Faker = 37.4.0
- psutil = 5.9.8
- sqlite3 = 3.45.1
- psycopg2 = 2.9.10

### Hardware
- **CPU:** 13th Gen Intel(R) Core(TM) i7-13700HX, 2100 Mhz, 16 Core(s), 24 Logical Processor(s)
- **Memory:** 16 GB DDR5 2400 MHz
