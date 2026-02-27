import datetime
import os
from neo4j_adapter import Neo4jAdapter
from perception_simulator import generate_observation_event # For simulated input

class MemoryManager:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password, neo4j_adapter_instance=None):
        if neo4j_adapter_instance:
            self.adapter = neo4j_adapter_instance
        else:
            self.adapter = Neo4jAdapter(neo4j_uri, neo4j_user, neo4j_password)
            self.adapter.connect() # Establish connection on initialization

    def close(self):
        self.adapter.close()

    def _ensure_node_exists(self, label, properties, unique_property_key):
        """
        Ensures a node with given label and unique_property_key exists.
        If not, creates it. Returns the node properties for relationship creation.
        """
        query = (
            f"MERGE (n:{label} {{{unique_property_key}: ${unique_property_key}}}) "
            f"ON CREATE SET n += $properties "
            f"RETURN n"
        )
        params = {unique_property_key: properties[unique_property_key], "properties": properties}
        result = self.adapter.run_cypher(query, params)
        return result[0]["n"]._properties if result else None

    def process_perception_event(self, event):
        """
        Processes a simulated perception event and updates the Neo4j graph.
        Example event structure:
        {
            "event_type": "observation",
            "timestamp": "2024-03-01T10:00:00.000000",
            "details": {
                "agent_name": "Aineko",
                "observed_object": "energy cell",
                "object_type": "device",
                "object_state": "available",
                "location": "cargo bay 1"
            }
        }
        """
        print(f"Processing perception event: {event['event_type']} at {event['timestamp']}")
        details = event["details"]

        agent_name = details["agent_name"]
        observed_object = details["observed_object"]
        object_type = details["object_type"]
        object_state = details["object_state"]
        location_name = details["location"]
        event_timestamp = event["timestamp"]

        # Ensure Agent node exists
        agent_props = {"name": agent_name, "type": "GSV", "status": "active"}
        self._ensure_node_exists("Agent", agent_props, "name")

        # Ensure Location node exists
        location_props = {"name": location_name, "type": "physical"}
        self._ensure_node_exists("Location", location_props, "name")

        # Ensure Object node exists and update its state
        object_props = {"name": observed_object, "type": object_type, "state": object_state}
        existing_object = self.adapter.get_node("Object", {"name": observed_object})
        if not existing_object:
            self._ensure_node_exists("Object", object_props, "name")
        else:
            self.adapter.update_node_properties("Object", {"name": observed_object}, {"state": object_state})


        # Create (or update) Agent LOCATED_AT Location relationship
        self.adapter.create_relationship(
            "Agent", {"name": agent_name},
            "LOCATED_AT",
            "Location", {"name": location_name},
            {"timestamp": event_timestamp} # Relationship property
        )

        # Create (or update) Object LOCATED_AT Location relationship
        self.adapter.create_relationship(
            "Object", {"name": observed_object},
            "LOCATED_AT",
            "Location", {"name": location_name},
            {"timestamp": event_timestamp} # Relationship property
        )

        # Create an Event node for the observation
        event_node_props = {
            "name": f"Observation of {observed_object} at {location_name}",
            "type": "observation",
            "timestamp": event_timestamp,
            "description": f"Agent {agent_name} observed {observed_object} ({object_type}, state: {object_state}) at {location_name}."
        }
        event_node = self.adapter.create_node("Event", event_node_props)

        # Link Agent to Event (OBSERVED)
        self.adapter.create_relationship(
            "Agent", {"name": agent_name},
            "OBSERVED",
            "Event", {"timestamp": event_timestamp, "name": event_node_props["name"]} # Using timestamp and name for unique identification of the event
        )
        print(f"Graph updated for perception event: {observed_object} at {location_name}")

    def log_task_event(self, task_name, task_description, agent_name, event_type, status, details=None):
        """
        Logs a task event (initiation, progress update, completion, failure) to the Neo4j graph.
        `event_type` can be 'task_start', 'task_progress', 'task_completed', 'task_failed'.
        `status` reflects the current state of the Task node (e.g., 'pending', 'in_progress', 'completed', 'failed').
        """
        timestamp = datetime.datetime.now().isoformat()
        print(f"Logging task event: {event_type} for '{task_name}' by {agent_name} at {timestamp}")

        # Ensure Agent node exists
        agent_props = {"name": agent_name, "type": "GSV", "status": "active"}
        self._ensure_node_exists("Agent", agent_props, "name")

        # Ensure Task node exists and update its properties
        task_props = {"name": task_name, "description": task_description, "status": status, "last_updated": timestamp}
        if event_type == 'task_start':
            # For a new task, add initial properties if not present
            self.adapter.run_cypher(
                "MERGE (t:Task {name: $name}) "
                "ON CREATE SET t += $props "
                "ON MATCH SET t.status = $status, t.last_updated = $last_updated "
                "RETURN t",
                {"name": task_name, "props": task_props, "status": status, "last_updated": timestamp}
            )
        else:
            self.adapter.update_node_properties("Task", {"name": task_name}, {"status": status, "last_updated": timestamp})

        # Create an Event node for this task update
        event_node_name = f"Task {event_type.replace('_', ' ').capitalize()} for '{task_name}'"
        event_node_props = {
            "name": event_node_name,
            "type": event_type,
            "timestamp": timestamp,
            "description": f"Agent {agent_name} {event_type.replace('_', ' ')} for task '{task_name}'. Status: {status}.",
            "details": str(details) if details else ""
        }
        event_node = self.adapter.create_node("Event", event_node_props)

        # Link Agent to Task (PERFORMS) - MERGE to avoid duplicates
        self.adapter.create_relationship(
            "Agent", {"name": agent_name},
            "PERFORMS",
            "Task", {"name": task_name}
        )

        # Link Task to Event (GENERATED_EVENT)
        self.adapter.create_relationship(
            "Task", {"name": task_name},
            "GENERATED_EVENT",
            "Event", {"timestamp": timestamp, "name": event_node_name}
        )

        # Link Agent to Event (CAUSED)
        self.adapter.create_relationship(
            "Agent", {"name": agent_name},
            "CAUSED",
            "Event", {"timestamp": timestamp, "name": event_node_name}
        )
        print(f"Task graph updated for event '{event_type}'. Task '{task_name}' status: {status}")


# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Ensure Neo4j is running and accessible
    URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    USER = os.getenv("NEO4J_USER", "neo4j")
    PASSWORD = os.getenv("NEO4J_PASSWORD", "newtestpassword") # Use a strong password in production

    manager = MemoryManager(URI, USER, PASSWORD)

    try:
        # --- Simulated Perception Input ---
        print("\n--- Processing Simulated Perception Events ---")
        for _ in range(2):
            perception_event = generate_observation_event()
            manager.process_perception_event(perception_event)
            print("-" * 30)

        # --- Task Execution Logging ---
        print("\n--- Logging Task Execution Events ---")
        agent_name = "Aineko"
        task1_name = "Scan Sector 7"
        task1_desc = "Perform a detailed scan of stellar sector 7 for anomalies."

        # Task Start
        manager.log_task_event(task1_name, task1_desc, agent_name, "task_start", "in_progress", {"priority": "high"})

        # Task Progress Update
        manager.log_task_event(task1_name, task1_desc, agent_name, "task_progress", "in_progress", {"progress": "30%", "subtask": "Initial sweep completed"})

        # Another Task Start (different task)
        task2_name = "Refuel at Station Alpha"
        task2_desc = "Navigate to Station Alpha and refuel."
        manager.log_task_event(task2_name, task2_desc, agent_name, "task_start", "pending", {"priority": "medium"})

        # Task Completion
        manager.log_task_event(task1_name, task1_desc, agent_name, "task_completed", "completed", {"result": "No anomalies found", "duration": "2 hours"})

        # Task Failure
        manager.log_task_event(task2_name, task2_desc, agent_name, "task_failed", "failed", {"reason": "Navigation error, unable to dock."})

    except Exception as e:
        print(f"An error occurred during example usage: {e}")
    finally:
        print("\nClosing MemoryManager...")
        manager.close()
