import os
import re
from neo4j_adapter import Neo4jAdapter

class GraphRAGRetriever:
    def __init__(self, uri, user, password):
        self.adapter = Neo4jAdapter(uri, user, password)

    def extract_keywords(self, query):
        """Very basic keyword extraction for v1. Removes stop words."""
        stopwords = {"what", "is", "the", "status", "of", "my", "how", "do", "i", "can", "you", "tell", "me", "about", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by"}
        words = re.findall(r'\b\w+\b', query.lower())
        return [w for w in words if w not in stopwords and len(w) > 2]

    def retrieve_context(self, query, depth=1):
        """
        Retrieves graph context based on a natural language query.
        Returns a formatted string representing the local graph topology.
        """
        keywords = self.extract_keywords(query)
        if not keywords:
            return "No significant keywords extracted from query."

        self.adapter.connect()
        try:
            context_data = []
            
            # Step 1: Find matching nodes across common labels
            match_conditions = " OR ".join([f"toLower(n.name) CONTAINS '{kw}' OR toLower(n.description) CONTAINS '{kw}'" for kw in keywords])
            
            cypher_query = f"""
            MATCH (n)
            WHERE {match_conditions}
            OPTIONAL MATCH (n)-[r]-(m)
            RETURN labels(n)[0] AS label_n, n.name AS name_n, properties(n) AS props_n, 
                   type(r) AS rel_type, 
                   labels(m)[0] AS label_m, m.name AS name_m, properties(m) AS props_m
            LIMIT 50
            """
            
            results = self.adapter.run_cypher(cypher_query)
            
            if not results:
                return f"No graph context found for keywords: {keywords}"

            # Step 2: Format the results into a readable topology string
            topology = {}
            for record in results:
                node_id = f"[{record['label_n']}] {record['name_n'] or 'Unnamed'}"
                if node_id not in topology:
                    # Simplify properties string
                    props = {k: v for k, v in record['props_n'].items() if k not in ['name', 'description']}
                    desc = record['props_n'].get('description', '')
                    topology[node_id] = {"props": props, "desc": desc, "relations": set()}
                
                if record['rel_type'] and record['label_m']:
                    rel_target = f"[{record['label_m']}] {record['name_m'] or 'Unnamed'}"
                    topology[node_id]["relations"].add(f"-({record['rel_type']})-> {rel_target}")

            # Build output string
            output = f"Graph Context for query: '{query}' (Keywords: {keywords})\n\n"
            for node, data in topology.items():
                output += f"{node}\n"
                if data['desc']:
                    # Truncate long descriptions
                    desc = data['desc'][:100] + "..." if len(data['desc']) > 100 else data['desc']
                    output += f"  Desc: {desc}\n"
                if data['props']:
                    output += f"  Props: {data['props']}\n"
                for rel in data['relations']:
                    output += f"  {rel}\n"
                output += "\n"

            return output
            
        except Exception as e:
            return f"Error retrieving GraphRAG context: {e}"
        finally:
            self.adapter.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        USER = os.getenv("NEO4J_USER", "neo4j")
        PASSWORD = os.getenv("NEO4J_PASSWORD", "testtest123")
        
        rag = GraphRAGRetriever(URI, USER, PASSWORD)
        print(rag.retrieve_context(query))
    else:
        print("Usage: python graph_rag.py <natural language query>")