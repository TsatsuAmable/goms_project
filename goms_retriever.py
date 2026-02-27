import sys
import os
from neo4j_adapter import Neo4jAdapter

def retrieve_lessons(error_id):
    try:
        URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        USER = os.getenv("NEO4J_USER", "neo4j")
        PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

        adapter = Neo4jAdapter(URI, USER, PASSWORD)
        adapter.connect()

        lessons = adapter.get_lessons_for_error(error_id)
        if lessons:
            print(f"Found {len(lessons)} lesson(s) for error '{error_id}':\n")
            for record in lessons:
                print(f"- Lesson ID: {record['lesson_id']}")
                print(f"  Summary: {record['summary']}")
                print(f"  Solution: {record['solution']}")
                print(f"  Timestamp: {record['timestamp']}\n")
        else:
            print(f"No lessons found for error ID: {error_id}")

    except Exception as e:
        print(f"Failed to retrieve lessons: {e}", file=sys.stderr)
    finally:
        if 'adapter' in locals() and adapter:
            adapter.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python goms_retriever.py <error_id>")
        sys.exit(1)
        
    error_id = sys.argv[1]
    retrieve_lessons(error_id)
