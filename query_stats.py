import os
from neo4j_adapter import Neo4jAdapter

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "testtest123") # Assuming testtest123 based on recent memory/code

adapter = Neo4jAdapter(URI, USER, PASSWORD)
try:
    adapter.connect()
    
    # Check node counts
    print("--- Node Statistics ---")
    query_counts = "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count"
    results = adapter.run_cypher(query_counts)
    if results:
        for record in results:
            print(f"{record['label']}: {record['count']}")
    else:
        print("Database is empty or no nodes found.")
        
    print("\n--- Recent Activity (Last 5 Nodes) ---")
    query_recent = "MATCH (n) RETURN labels(n)[0] AS label, properties(n) AS props ORDER BY id(n) DESC LIMIT 5"
    results = adapter.run_cypher(query_recent)
    if results:
        for record in results:
            print(f"[{record['label']}] {record['props']}")
    else:
        print("No recent activity.")
        
except Exception as e:
    print(f"Connection/Query Failed: {e}")
finally:
    adapter.close()
