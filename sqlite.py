import sqlite3
from gen_data import generate_event

def setup_conn():
    conn = sqlite3.connect(':memory:')
    
    return conn

def setup_cursor(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=DELETE;")  # disables WAL
    cur.execute("PRAGMA synchronous=OFF;")      # don’t wait for disk flush
    cur.execute("PRAGMA journal_mode=OFF;")     # no journaling
    cur.execute("PRAGMA temp_store=MEMORY;")    # keep temp tables in RAM
    cur.execute("PRAGMA cache_size=-64000;")    # ~64MB in-memory cache
    return cur

def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trip_events_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER,
            rider_id INTEGER,
            driver_id INTEGER,
            timestamp TEXT,
            location_lat REAL,
            location_lon REAL,
            address TEXT,
            status TEXT,
            checkpoint TEXT
        )
    """)
    

def insert_trip_events(conn, cur, events):
    for event in events:
        loc = event["location"]
        cur.execute("""
            INSERT INTO trip_events_cache (
                trip_id, rider_id, driver_id, timestamp,
                location_lat, location_lon, address, status, checkpoint
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    conn.commit()


def clear_table(cur):
    cur.execute("DELETE FROM trip_events_cache")

def sqlite_main():
    conn = setup_conn()
    cur = setup_cursor(conn)
    create_table(cur)
    clear_table(cur)
    event = generate_event()
    insert_trip_events(conn, cur, [event])
    cur.close()
    conn.close()
    return event