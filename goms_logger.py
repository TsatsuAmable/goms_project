import os
import sys
import uuid
from datetime import datetime
from neo4j_adapter import Neo4jAdapter

def log_error_to_goms(command, output, error_message, context):
    try:
        URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        USER = os.getenv("NEO4J_USER", "neo4j")
        PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

        adapter = Neo4jAdapter(URI, USER, PASSWORD)
        adapter.connect()

        error_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        full_description = f"Command: {command}\nOutput: {output}\nError: {error_message}"

        error_node = adapter.create_error(
            id=error_id,
            description=full_description,
            timestamp=timestamp,
            context=context
        )
        print(f"Error logged to GOMS with ID: {error_id}")
        return error_id

    except Exception as e:
        print(f"Failed to log error to GOMS: {e}", file=sys.stderr)
        return None
    finally:
        if adapter:
            adapter.close()

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python goms_logger.py <command> <output> <error_message> <context>")
        sys.exit(1)

    command = sys.argv[1]
    output = sys.argv[2]
    error_message = sys.argv[3]
    context = sys.argv[4]

    log_error_to_goms(command, output, error_message, context)
