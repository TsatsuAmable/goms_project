import sys
import os
from neo4j_adapter import Neo4jAdapter

def retrieve_lessons_by_context(keywords):
    try:
        URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        USER = os.getenv("NEO4J_USER", "neo4j")
        PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

        adapter = Neo4jAdapter(URI, USER, PASSWORD)
        adapter.connect()

        lessons = adapter.get_lessons_by_keywords(keywords)
        if lessons:
            print(f"Found {len(lessons)} lesson(s) matching context keywords {keywords}:\n")
            for record in lessons:
                print(f"- Lesson ID: {record['lesson_id']}")
                print(f"  Summary: {record['summary']}")
                print(f"  Solution: {record['solution']}")
                print(f"  Associated Error Context: {record['error_context']}")
                print(f"  Timestamp: {record['timestamp']}\n")
        else:
            print(f"No lessons found for context keywords: {keywords}")

    except Exception as e:
        print(f"Failed to retrieve lessons: {e}", file=sys.stderr)
    finally:
        if 'adapter' in locals() and adapter:
            adapter.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python goms_context_retriever.py <keyword1> [<keyword2> ...]")
        sys.exit(1)
        
    keywords = sys.argv[1:]
    retrieve_lessons_by_context(keywords)
