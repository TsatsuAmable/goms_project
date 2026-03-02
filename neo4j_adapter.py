import os
from neo4j import GraphDatabase

class Neo4jAdapter:
    def __init__(self, uri, user, password):
        self._uri = uri
        self._user = user
        self._password = password
        self._driver = None

    def connect(self):
        if not self._driver:
            try:
                self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))
                self._driver.verify_connectivity()
                print("Neo4j connection established.")
            except Exception as e:
                print(f"Failed to connect to Neo4j: {e}")
                print("Please ensure Neo4j is running and the credentials (URI, USER, PASSWORD) are correct.")
                raise

    def close(self):
        if self._driver:
            self._driver.close()
            print("Neo4j connection closed.")

    def _execute_query(self, query, parameters=None):
        self.connect() # Ensure connection is open
        with self._driver.session() as session:
            try:
                result = session.run(query, parameters)
                return [record for record in result]
            except Exception as e:
                print(f"Error executing query: {query}\nParameters: {parameters}\nError: {e}")
                raise

    def create_node(self, label, properties):
        props_str = ", ".join([f"{k}: ${k}" for k in properties])
        query = f"CREATE (n:{label} {{{props_str}}}) RETURN n"
        return self._execute_query(query, properties)

    def create_relationship(self, node1_label, node1_props, rel_type, node2_label, node2_props, rel_props=None):
        node1_match_str = "{" + ", ".join([f"{k}: ${k}_1" for k in node1_props]) + "}"
        node2_match_str = "{" + ", ".join([f"{k}: ${k}_2" for k in node2_props]) + "}"

        params = {f"{k}_1": v for k, v in node1_props.items()}
        params.update({f"{k}_2": v for k, v in node2_props.items()})

        rel_props_str = ""
        if rel_props:
            rel_props_str = " {" + ", ".join([f"{k}: ${k}_rel" for k in rel_props]) + "}"
            params.update({f"{k}_rel": v for k, v in rel_props.items()})

        query = (
            f"MATCH (a:{node1_label} {node1_match_str}), (b:{node2_label} {node2_match_str}) "
            f"MERGE (a)-[r:{rel_type}{rel_props_str}]->(b) RETURN r"
        )
        return self._execute_query(query, params)

    def update_node_properties(self, label, match_props, update_props):
        match_str = "{" + ", ".join([f"{k}: ${k}_match" for k in match_props]) + "}"
        set_str = ", ".join([f"n.{k} = ${k}_update" for k in update_props])

        params = {f"{k}_match": v for k, v in match_props.items()}
        params.update({f"{k}_update": v for k, v in update_props.items()})

        query = f"MATCH (n:{label} {match_str}) SET {set_str} RETURN n"
        return self._execute_query(query, params)

    def get_node(self, label, properties):
        props_str = "{" + ", ".join([f"{k}: ${k}" for k in properties]) + "}"
        query = f"MATCH (n:{label} {props_str}) RETURN n"
        return self._execute_query(query, properties)

    def run_cypher(self, cypher_query, parameters=None):
        return self._execute_query(cypher_query, parameters)

    def create_error(self, id, description, timestamp, context):
        query = (
            "MERGE (e:Error {id: $id}) "
            "ON CREATE SET e.description = $description, e.timestamp = $timestamp, e.context = $context "
            "ON MATCH SET e.description = $description, e.timestamp = $timestamp, e.context = $context "
            "RETURN e"
        )
        params = {"id": id, "description": description, "timestamp": timestamp, "context": context}
        return self._execute_query(query, params)

    def create_lesson(self, id, summary, solution, timestamp, error_id=None):
        query = (
            "MERGE (l:Lesson {id: $id}) "
            "ON CREATE SET l.summary = $summary, l.solution = $solution, l.timestamp = $timestamp "
            "ON MATCH SET l.summary = $summary, l.solution = $solution, l.timestamp = $timestamp "
            "RETURN l"
        )
        params = {"id": id, "summary": summary, "solution": solution, "timestamp": timestamp}
        lesson_node = self._execute_query(query, params)

        if error_id:
            # Create relationship if error_id is provided
            rel_query = (
                "MATCH (l:Lesson {id: $lesson_id}), (e:Error {id: $error_id}) "
                "MERGE (l)-[r:CAUSED_BY_ERROR]->(e) "
                "RETURN l, e, r"
            )
            rel_params = {"lesson_id": id, "error_id": error_id}
            self._execute_query(rel_query, rel_params)

        return lesson_node

    def get_lessons_for_error(self, error_id):
        query = (
            "MATCH (l:Lesson)-[:CAUSED_BY_ERROR]->(e:Error {id: $error_id}) "
            "RETURN l.id AS lesson_id, l.summary AS summary, l.solution AS solution, l.timestamp AS timestamp"
        )
        params = {"error_id": error_id}
        return self._execute_query(query, params)

    def get_lessons_by_keywords(self, keywords):
        # This query finds errors whose description or context contains any of the keywords
        # and then returns the associated lessons.
        # Uses `toLower` and `CONTAINS` for case-insensitive keyword search.
        
        conditions = []
        params = {}
        for i, keyword in enumerate(keywords):
            param_desc = f"keyword_desc_{i}"
            param_ctx = f"keyword_ctx_{i}"
            conditions.append(f"(toLower(e.description) CONTAINS toLower(${param_desc}) OR toLower(e.context) CONTAINS toLower(${param_ctx}))")
            params[param_desc] = keyword
            params[param_ctx] = keyword
            
        where_clause = "WHERE " + " OR ".join(conditions) if conditions else ""

        query = (
            "MATCH (l:Lesson)-[:CAUSED_BY_ERROR]->(e:Error) "
            f"{where_clause} "
            "RETURN l.id AS lesson_id, l.summary AS summary, l.solution AS solution, l.timestamp AS timestamp, "
            "e.description AS error_description, e.context AS error_context"
        )
        return self._execute_query(query, params)

# Example Usage (for testing purposes, not part of the module itself)
if __name__ == "__main__":
    # These should ideally come from environment variables or a config file
    # For testing, ensure these are set in your environment or replace with actual values
    URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    USER = os.getenv("NEO4J_USER", "neo4j")
    PASSWORD = os.getenv("NEO4J_PASSWORD", "password") # Use a strong password in production

    adapter = Neo4jAdapter(URI, USER, PASSWORD)
    try:
        adapter.connect()

        # --- Existing Examples (kept for general functionality demonstration) ---
        print("Creating Agent Aineko...")
        agent_node = adapter.create_node("Agent", {"name": "Aineko", "type": "GSV", "status": "idle"})
        print(f"Agent created: {agent_node}")

        print("\nCreating Location Bay 3...")
        location_node = adapter.create_node("Location", {"name": "Bay 3", "type": "physical", "coordinates": "X:10,Y:20,Z:0"})
        print(f"Location created: {location_node}")

        # --- New MVGOMS Error/Lesson Examples ---
        # 1. Create an Error node
        print("\nCreating an Error node: ModuleNotFoundError on 2026-02-26...")
        error_id_1 = "module_not_found_20260226"
        error_description_1 = "ModuleNotFoundError when importing neo4j driver during GOMS setup."
        error_timestamp_1 = "2026-02-26T10:00:00Z"
        error_context_1 = "Attempting to initialize GOMS project, Python environment."
        error_node_1 = adapter.create_error(error_id_1, error_description_1, error_timestamp_1, error_context_1)
        print(f"Error created: {error_node_1}")

        # 2. Create a Lesson node linked to the Error
        print("\nCreating a Lesson node linked to the Error...")
        lesson_id_1 = "venv_install_neo4j"
        lesson_summary_1 = "Use Python virtual environment and pip install neo4j."
        lesson_solution_1 = "python3 -m venv .venv && source .venv/bin/activate && pip install neo4j"
        lesson_timestamp_1 = "2026-02-26T11:30:00Z"
        lesson_node_1 = adapter.create_lesson(lesson_id_1, lesson_summary_1, lesson_solution_1, lesson_timestamp_1, error_id=error_id_1)
        print(f"Lesson created: {lesson_node_1}")

        # 3. Create another Error node (e.g., password length)
        print("\nCreating another Error node: Neo4j password length issue...")
        error_id_2 = "neo4j_password_length_20260227"
        error_description_2 = "Neo4j container exited due to password not meeting minimum length requirement (8 characters)."
        error_timestamp_2 = "2026-02-27T09:00:00Z"
        error_context_2 = "Docker deployment of Neo4j for GOMS."
        error_node_2 = adapter.create_error(error_id_2, error_description_2, error_timestamp_2, error_context_2)
        print(f"Error created: {error_node_2}")

        # 4. Create another Lesson node linked to the new Error
        print("\nCreating a Lesson node linked to the new Error...")
        lesson_id_2 = "stronger_neo4j_password"
        lesson_summary_2 = "Use a password of at least 8 characters for Neo4j deployment."
        lesson_solution_2 = "docker run ... -e NEO4J_AUTH=neo4j/testtest123 ..."
        lesson_timestamp_2 = "2026-02-27T10:00:00Z"
        lesson_node_2 = adapter.create_lesson(lesson_id_2, lesson_summary_2, lesson_solution_2, lesson_timestamp_2, error_id=error_id_2)
        print(f"Lesson created: {lesson_node_2}")

        # --- New MVGOMS Query Examples ---
        # 5. Get lessons for a specific error
        print(f"\nGetting lessons for Error ID: {error_id_1}...")
        lessons_for_error_1 = adapter.get_lessons_for_error(error_id_1)
        if lessons_for_error_1:
            for record in lessons_for_error_1:
                print(f"  Lesson ID: {record['lesson_id']}, Summary: {record['summary']}")
        else:
            print(f"  No lessons found for error ID: {error_id_1}")

        print(f"\nGetting lessons for Error ID: {error_id_2}...")
        lessons_for_error_2 = adapter.get_lessons_for_error(error_id_2)
        if lessons_for_error_2:
            for record in lessons_for_error_2:
                print(f"  Lesson ID: {record['lesson_id']}, Summary: {record['summary']}")
        else:
            print(f"  No lessons found for error ID: {error_id_2}")
            
        # --- New MVGOMS Contextual Query Examples ---
        # 6. Get lessons by keywords
        print("\nGetting lessons by keywords 'not found'...")
        lessons_by_keywords_1 = adapter.get_lessons_by_keywords(["not found"])
        if lessons_by_keywords_1:
            for record in lessons_by_keywords_1:
                print(f"  Lesson ID: {record['lesson_id']}, Summary: {record['summary']}")
                print(f"  Error Description: {record['error_description']}")
                print(f"  Error Context: {record['error_context']}")
        else:
            print("  No lessons found for keywords 'not found'.")

        print("\nGetting lessons by keywords 'password' and 'docker'...")
        lessons_by_keywords_2 = adapter.get_lessons_by_keywords(["password", "docker"])
        if lessons_by_keywords_2:
            for record in lessons_by_keywords_2:
                print(f"  Lesson ID: {record['lesson_id']}, Summary: {record['summary']}")
                print(f"  Error Description: {record['error_description']}")
                print(f"  Error Context: {record['error_context']}")
        else:
            print("  No lessons found for keywords 'password' and 'docker'.")


    except Exception as e:
        print(f"An error occurred during example usage: {e}")
    finally:
        adapter.close()
