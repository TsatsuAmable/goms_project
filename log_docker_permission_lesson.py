import os
import uuid
from datetime import datetime
from neo4j_adapter import Neo4jAdapter

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

adapter = Neo4jAdapter(URI, USER, PASSWORD)
try:
    adapter.connect()
    
    error_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # Log the Docker build stalling error
    error_description = "Docker build/pull stalled due to insufficient OS-level permissions for Node.js."
    error_context = "Attempting to build Docker testbed image."
    adapter.create_error(error_id, error_description, timestamp, error_context)
    print(f"Logged Error ID: {error_id}")
    
    # Log the lesson learned
    lesson_id = str(uuid.uuid4())
    lesson_summary = "Ensure Node.js has sufficient OS-level permissions to prevent Docker build/pull stalls."
    lesson_solution = "Grant Node.js necessary OS-level permissions (e.g., file system access, network access as required by Docker Desktop)."
    adapter.create_lesson(lesson_id, lesson_summary, lesson_solution, timestamp, error_id=error_id)
    print(f"Logged Lesson ID: {lesson_id} linked to Error ID: {error_id}")
    
except Exception as e:
    print(f"Failed to log Docker permission lesson to GOMS: {e}")
finally:
    adapter.close()
