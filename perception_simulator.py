import random
import time
from datetime import datetime

def generate_observation_event():
    """Generates a mock observation event."""
    objects = ["energy cell", "tool kit", "repair arm", "data chip", "sensor array"]
    locations = ["cargo bay 1", "engine room", "med bay", "bridge", "crew quarters"]
    object_type = ["device", "component", "supply", "data", "tool"]
    object_state = ["available", "in_use", "damaged", "unknown"]

    observed_object = random.choice(objects)
    observed_location = random.choice(locations)
    observed_object_type = random.choice(object_type)
    observed_object_state = random.choice(object_state)

    event_type = "observation"
    timestamp = datetime.now().isoformat()

    event = {
        "event_type": event_type,
        "timestamp": timestamp,
        "details": {
            "agent_name": "Aineko",
            "observed_object": observed_object,
            "object_type": observed_object_type,
            "object_state": observed_object_state,
            "location": observed_location,
        }
    }
    return event

if __name__ == "__main__":
    print("Generating 5 mock observation events:")
    for _ in range(5):
        event = generate_observation_event()
        print(f"- {event}")
        time.sleep(0.5)
