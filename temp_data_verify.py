import os
from neo4j_adapter import Neo4jAdapter

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

adapter = Neo4jAdapter(URI, USER, PASSWORD)
try:
    adapter.connect()
    print("Neo4j connection established for data verification.")
    
    query = "MATCH (e:Error) RETURN e.id AS id, e.description AS description, e.context AS context"
    print(f"Executing Cypher: {query}")
    results = adapter.run_cypher(query)
    
    if results:
        for record in results:
            print(f"  ID: {record['id']}")
            print(f"  Description: {record['description']}")
            print(f"  Context: {record['context']}\n")
    else:
        print("  No Error nodes found in the database.")
            
except Exception as e:
    print(f"An error occurred during data verification: {e}")
finally:
    adapter.close()
    print("Neo4j connection closed for data verification.")
