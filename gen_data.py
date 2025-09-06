from faker import Faker
from datetime import datetime, timedelta
import uuid, random

fake = Faker()

def generate_event():
    location = {
        "lat": float(round(fake.latitude(), 6)),
        "lon": float(round(fake.longitude(), 6)),
        "address": fake.address().replace("\n", ", ")
    }

    status = random.choices(
        ["completed", "cancelled",],
        weights=[0.85, 0.15],
        k=1
    )[0]

    drivers = [f"driver-{i}" for i in range(2500)]
    trip_id = str(uuid.uuid4())
    rider_id = f"rider-{random.randint(1000, 9999)}"
    driver_id = random.choice(drivers)
    checkpoint = random.choice(["pickup", "dropoff", "cancelled"])

    return {
        "trip_id": trip_id,
        "rider_id": rider_id,
        "driver_id": driver_id,
        "timestamp": datetime.utcnow().isoformat(),
        "location": location,
        "status": status,
        "checkpoint": checkpoint
    }

if __name__ == "__main__":
    generate_event()
