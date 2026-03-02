import os
from neo4j_adapter import Neo4jAdapter

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

adapter = Neo4jAdapter(URI, USER, PASSWORD)
try:
    adapter.connect()
    print("Neo4j connection established for test.")
    
    query = "MATCH (l:Lesson)-[:CAUSED_BY_ERROR]->(e:Error) WHERE toLower(e.description) CONTAINS toLower('not found') RETURN l.id AS lesson_id, l.summary AS summary"
    print(f"Executing Cypher: {query}")
    results = adapter.run_cypher(query)
    
    if results:
        for record in results:
            print(f"  Lesson ID: {record['lesson_id']}, Summary: {record['summary']}")
    else:
        print("  No lessons found for 'not found' via direct Cypher test.")
        
except Exception as e:
    print(f"An error occurred during direct Cypher test: {e}")
finally:
    adapter.close()
    print("Neo4j connection closed for test.")
