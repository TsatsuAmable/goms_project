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
        # existing code
        pass

    def log_task_event(self, task_name, task_description, agent_name, event_type, status, details=None):
        timestamp = datetime.datetime.now().isoformat()
        
        agent_props = {"name": agent_name, "type": "GSV", "status": "active"}
        self._ensure_node_exists("Agent", agent_props, "name")

        task_props = {"name": task_name, "description": task_description, "status": status, "last_updated": timestamp}
        if event_type == 'task_start':
            self.adapter.run_cypher(
                "MERGE (t:Task {name: $name}) "
                "ON CREATE SET t += $props "
                "ON MATCH SET t.status = $status, t.last_updated = $last_updated "
                "RETURN t",
                {"name": task_name, "props": task_props, "status": status, "last_updated": timestamp}
            )
        else:
            self.adapter.update_node_properties("Task", {"name": task_name}, {"status": status, "last_updated": timestamp})

        event_node_name = f"Task {event_type.replace('_', ' ').capitalize()} for '{task_name}'"
        event_node_props = {
            "name": event_node_name,
            "type": event_type,
            "timestamp": timestamp,
            "description": f"Agent {agent_name} {event_type.replace('_', ' ')} for task '{task_name}'. Status: {status}.",
            "details": str(details) if details else ""
        }
        self.adapter.create_node("Event", event_node_props)

        self.adapter.create_relationship(
            "Agent", {"name": agent_name},
            "PERFORMS",
            "Task", {"name": task_name}
        )
        self.adapter.create_relationship(
            "Task", {"name": task_name},
            "GENERATED_EVENT",
            "Event", {"timestamp": timestamp, "name": event_node_name}
        )
        self.adapter.create_relationship(
            "Agent", {"name": agent_name},
            "CAUSED",
            "Event", {"timestamp": timestamp, "name": event_node_name}
        )

    # --- Phase 1: New Capabilities ---

    def log_subagent_state(self, agent_id, parent_task, status, model="unknown", purpose=""):
        """Logs the spawning or state change of a sub-agent."""
        timestamp = datetime.datetime.now().isoformat()
        
        # Ensure SubAgent node exists
        subagent_props = {"id": agent_id, "model": model, "purpose": purpose, "status": status, "last_updated": timestamp}
        self._ensure_node_exists("SubAgent", subagent_props, "id")
        
        # Update status if already exists
        self.adapter.update_node_properties("SubAgent", {"id": agent_id}, {"status": status, "last_updated": timestamp})

        if parent_task:
            # Link SubAgent working on Task
            self.adapter.create_relationship(
                "SubAgent", {"id": agent_id},
                "WORKING_ON",
                "Task", {"name": parent_task}
            )
            # Link main agent spawning subagent (assuming Aineko is the parent)
            self.adapter.create_relationship(
                "Agent", {"name": "Aineko"},
                "SPAWNED",
                "SubAgent", {"id": agent_id}
            )

    def log_process_state(self, process_id, parent_task, command, status):
        """Logs a background process (like an exec command)."""
        timestamp = datetime.datetime.now().isoformat()
        
        process_props = {"id": process_id, "command": command, "status": status, "last_updated": timestamp}
        self._ensure_node_exists("Process", process_props, "id")
        self.adapter.update_node_properties("Process", {"id": process_id}, {"status": status, "last_updated": timestamp})

        if parent_task:
            self.adapter.create_relationship(
                "Process", {"id": process_id},
                "WORKING_ON",
                "Task", {"name": parent_task}
            )

    def link_subtask(self, parent_task_name, subtask_name, order_index=None):
        """Builds procedural memory by linking a subtask to a parent task."""
        rel_props = {}
        if order_index is not None:
            rel_props["order"] = order_index
            
        self._ensure_node_exists("Task", {"name": parent_task_name}, "name")
        self._ensure_node_exists("Task", {"name": subtask_name}, "name")

        self.adapter.create_relationship(
            "Task", {"name": parent_task_name},
            "HAS_SUBTASK",
            "Task", {"name": subtask_name},
            rel_props
        )

    def pre_flight_check(self, command):
        """Queries the graph for past errors associated with a command pattern."""
        # Simple implementation: looks for commands that contain the first word of the command
        base_tool = command.split(" ")[0] if " " in command else command
        query = (
            "MATCH (e:Error) "
            "WHERE toLower(e.description) CONTAINS toLower($tool) "
            "OPTIONAL MATCH (l:Lesson)-[:CAUSED_BY_ERROR]->(e) "
            "RETURN e.description AS error, e.context AS context, l.summary AS lesson_summary, l.solution AS lesson_solution"
        )
        results = self.adapter.run_cypher(query, {"tool": base_tool})
        return results

    def add_dependency(self, task_name, dependency_type, dependency_name):
        """Links a task to a required tool, skill, or object."""
        # dependency_type should be Tool, Skill, Object
        # Relationship will be REQUIRES_TOOL, REQUIRES_SKILL, REQUIRES_OBJECT
        rel_type = f"REQUIRES_{dependency_type.upper()}"
        
        self._ensure_node_exists(dependency_type, {"name": dependency_name}, "name")
        self.adapter.create_relationship(
            "Task", {"name": task_name},
            rel_type,
            dependency_type, {"name": dependency_name}
        )

    def plan_task(self, task_name):
        """Generates a dependency checklist for a task."""
        query = (
            "MATCH (t:Task {name: $task_name})-[r]->(d) "
            "WHERE type(r) STARTS WITH 'REQUIRES_' "
            "RETURN type(r) AS rel_type, labels(d)[0] AS dep_type, d.name AS dep_name"
        )
        results = self.adapter.run_cypher(query, {"task_name": task_name})
        
        # Also check for subtasks
        subtask_query = (
            "MATCH (t:Task {name: $task_name})-[:HAS_SUBTASK]->(sub:Task) "
            "RETURN sub.name AS subtask_name "
            "ORDER BY sub.order" # Order by relationship property if it exists, fallback gracefully if not in cypher
        )
        subtask_results = self.adapter.run_cypher(subtask_query, {"task_name": task_name})

        return {"dependencies": results, "subtasks": subtask_results}

