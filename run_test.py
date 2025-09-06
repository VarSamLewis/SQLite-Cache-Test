from time import time
from sqlite import sqlite_main
import os
import psycopg2
import psutil

def ingest_loop():
    start = time()
    total_rows = 0
    while time() - start < 60:
        sqlite_main()
        total_rows += 1
    elapsed = time() - start
    print(f"""Wrote {total_rows} rows in {elapsed:.2f} seconds ({total_rows/elapsed:.2f} rows/sec)""")


def write_PostGres_event(cur, event):
   loc = event["location"]
   try:
        start = time()
        cur.execute("""
            INSERT INTO trip_events_cache (
                trip_id, rider_id, driver_id, timestamp,
                location_lat, location_lon, address, status, checkpoint
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            event["trip_id"],
            event["rider_id"],
            event["driver_id"],
            event["timestamp"],
            loc["lat"],
            loc["lon"],
            loc["address"],
            event["status"],
            event["checkpoint"]
        ))
        latency = time() - start
        return latency, None
   except Exception as e:
        return None, e


def test_cache_metrics(duration=10):
    process = psutil.Process(os.getpid())
    start_mem = process.memory_info().rss
    start_cpu = process.cpu_percent(interval=None)

    conn = psycopg2.connect(
        dbname="cache_test",
        user='postgres',
        password=os.getenv("PGSQL_SU_PW"),
        host='localhost',
        port=5432
    )
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE trip_events_cache")

    start = time()
    latencies = []
    failed_writes = 0
    constraint_violations = 0
    generated_events = []
    written_trip_ids = set()
    total_rows = 0

    # Write phase
    while time() - start < duration:
        event = sqlite_main()
        generated_events.append(event)
        written_trip_ids.add(event["trip_id"])
        latency, error = write_PostGres_event(cur, event)
        if latency is not None:
            latencies.append(latency)
            total_rows += 1
        if error is not None:
            print(f"Error writing event: {error}")
            failed_writes += 1
            if "constraint" in str(error).lower():
                constraint_violations += 1

    conn.commit()

    cur.execute("SELECT trip_id, rider_id, driver_id, timestamp, location_lat, location_lon, address, status, checkpoint FROM trip_events_cache")
    rows = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

    end_mem = process.memory_info().rss
    end_cpu = process.cpu_percent(interval=None)

    corrupt_count = sum(any(field is None for field in row.values()) for row in rows) if rows else 0

    timestamps = [row["timestamp"] for row in rows] if rows else []
    out_of_order_count = sum(
        1 for i in range(1, len(timestamps)) if timestamps[i] < timestamps[i-1]
    ) if rows else 0

    trip_ids = [row["trip_id"] for row in rows] if rows else []
    duplicate_count = len(trip_ids) - len(set(trip_ids)) if rows else 0

    missing_count = abs(len(generated_events) - len(rows)) if rows else 0

    print(f"--- Performance Metrics ---")
    print(f"Total rows written: {total_rows} in {duration} secs")
    print(f"Throughput: {total_rows/duration:.2f} rows/sec")
    print(f"Avg Latency per write: {sum(latencies)/len(latencies):.4f} sec" if latencies else "Avg Latency per write: N/A")
    print(f"--- Data Integrity Metrics ---")
    print(f"Corrupt records: {corrupt_count}")
    print(f"Out-of-order records: {out_of_order_count}")
    print(f"Duplicate trip_ids: {duplicate_count}")
    print(f"Missing records: {missing_count}")
    print(f"--- Error Metrics ---")
    print(f"Failed writes: {failed_writes}")
    print(f"Constraint violations: {constraint_violations}")
    print(f"--- Resource Metrics ---")
    print(f"Memory usage delta: {(end_mem - start_mem)/1024/1024:.2f} MB")
    print(f"CPU usage: {end_cpu - start_cpu}%")
    cur.close()
    conn.close()


if __name__ == "__main__":
    test_cache_metrics(60)