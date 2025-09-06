import psycopg2
import os

# Step 1: Connect to the default 'postgres' database to create 'cache_test'
conn = psycopg2.connect(
    dbname="postgres",
    user='postgres',
    password=os.getenv("PGSQL_SU_PW"),
    host='localhost',
    port=5432
)
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute("SELECT 1 FROM pg_database WHERE datname='cache_test'")
    if not cur.fetchone():
        cur.execute("CREATE DATABASE cache_test;")
conn.close()

# Step 2: Connect to 'cache_test' and create the table
conn = psycopg2.connect(
    dbname="cache_test",
    user='postgres',
    password=os.getenv("PGSQL_SU_PW"),
    host='localhost',
    port=5432
)
with conn.cursor() as cur:
    cur.execute("""
        CREATE UNLOGGED TABLE IF NOT EXISTS trip_events_cache (
            trip_id TEXT NOT NULL,
            rider_id TEXT NOT NULL,
            driver_id TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            location_lat DOUBLE PRECISION NOT NULL,
            location_lon DOUBLE PRECISION NOT NULL,
            address TEXT NOT NULL,
            status TEXT CHECK (status IN ('in_progress', 'completed', 'cancelled')),
            checkpoint TEXT CHECK (checkpoint IN ('pickup', 'dropoff', 'cancelled'))
        );
    """)
conn.commit()
cur.close()
conn.close()
print("Tables created successfully.")