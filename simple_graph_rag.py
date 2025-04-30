import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from openai import OpenAI
from sentence_transformers import SentenceTransformer



VECTOR_INDEX_NAME = os.getenv("VECTOR_INDEX_NAME", "vector")

# Neo4j connection details
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://33e44caf.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


load_dotenv()


_SYSTEM_PROMPT = (
    "Eres un asistente especializado que responde preguntas basándose únicamente en el contexto extraído del grafo Neo4j.. de lo contrario no responder"
)
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not set. Some features may not work.")
client = OpenAI(api_key=OPENAI_API_KEY)

load_dotenv()
class GraphRAGChatbot:
    """Implementación de un chatbot con GraphRAG."""

    def __init__(self):
        print(f"Conectando a Neo4j en {NEO4J_URI}")
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self._test_connection()

    def _test_connection(self):
        with self.driver.session() as session:
            msg = session.run("RETURN '✅ Conectado a Neo4j' AS message").single()["message"]
            print(msg)

    def close(self):
        self.driver.close()

    def get_graph_info(self):
        with self.driver.session() as session:
            node_count = session.run("MATCH (n) RETURN count(n) AS count").single()["count"]
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()["count"]
            labels = session.run(
                "CALL db.labels() YIELD label RETURN collect(label) AS labels"
            ).single()["labels"]
            rel_types = session.run(
                "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) AS types"
            ).single()["types"]
            
            top_entities = []
            for rec in session.run(
                "MATCH (n) WHERE NOT n:Chunk AND NOT n:Document"
                " RETURN labels(n) AS label, count(n) AS count"
                " ORDER BY count DESC LIMIT 10"
            ):
                top_entities.append({"label": rec["label"], "count": rec["count"]})

            return {
                "nodeCount": node_count,
                "relationshipCount": rel_count,
                "labels": labels,
                "relationshipTypes": rel_types,
                "topEntityCounts": top_entities
            }

    def ask(self, question):
        print(f"\nPregunta: {question}")
        nodes = self._find_relevant_nodes(question)
        if not nodes:
            return {"answer": "No encontré información relevante.", "context": None, "sources": []}
        expanded = self._expand_context(nodes)
        return self._generate_response(question, nodes, expanded)
    
    
    def _find_relevant_nodes(self, query):
        # client = OpenAI(api_key=OPENAI_API_KEY)
        # response = client.embeddings.create(
        #     input=query,
        #     model="text-embedding-3-small",
        #     dimensions=384
        # )
        # query_embedding = response.data[0].embedding
        query_embedding = self.model.encode(query).tolist()

        with self.driver.session() as session:
            # Usar el índice vectorial existente llamado "vector"
            result = session.run("""
                CALL db.index.vector.queryNodes("vector", 20, $query_vector)
                YIELD node, score
                RETURN 
                    node.text as text, 
                    score,
                    elementId(node) as id,
                    labels(node) as labels
                ORDER BY score DESC
            """, {
                "query_vector": query_embedding
            })
            
            chunks = [
                {
                    "text": record["text"], 
                    "score": record["score"],
                    "id": record["id"],
                    "labels": record["labels"]
                } 
                for record in result
            ]
        
        return chunks


            
    def _expand_context(self, nodes, limit=10):
        if not nodes:
            return []

        # 1) IDs de los chunks iniciales
        node_ids = [n["id"] for n in nodes if "id" in n]
        if not node_ids:
            return []

        # 2) Consulta que devuelve nodos + relación al origen
        query = """
        UNWIND $node_ids AS nid
        MATCH (c)-[r:PART_OF|NEXT_CHUNK|HAS_ENTITY|SIMILAR]->(m)
        WHERE elementId(c)=nid
        RETURN DISTINCT
        elementId(m)             AS id,
        coalesce(m.text, m.name) AS content,
        type(r)                  AS relationship
        LIMIT $limit
        """

        # 3) Ejecutar y formatear resultado
        with self.driver.session() as session:
            result = session.run(query, node_ids=node_ids, limit=limit)
            expanded = [
                {"id": r["id"], "content": r["content"], "relationship": r["relationship"]}
                for r in result
            ]

        # 4) Fallback a los chunks si no hay vecinos
        if not expanded:
            expanded = [{"id": n["id"], "content": n["text"], "relationship": None}
                        for n in nodes[:limit]]

        return expanded

    def _generate_response(self, question, nodes, expanded):
        """
        Genera respuesta completa basada en nodos relevantes y sus conexiones en el grafo.
        Preserva todos los nodos y limita los textos a 300 caracteres solo si son más extensos.
        """
        # Fragmentos relevantes
        fragments = ["# Fragmentos relevantes:"]
        for i, node in enumerate(nodes, 1):
            text = node.get("text", "").strip().replace("\n", " ")
            # Solo truncar si es extremadamente largo
            if len(text) > 300:
                text = text[:300] + "..."
            fragments.append(f"{i}. {text}")
        
        # Entidades y relaciones
        entities = ["# Entidades detectadas:"]
        relations = ["# Relaciones:"]
        
        for e in expanded:
            content = e.get("content")
            rel_type = e.get("relationship")            
            if content:
                if len(str(content)) > 300:
                    content = str(content)[:300] + "..."
                    
                if rel_type == "HAS_ENTITY":
                    entities.append(f"- {content}")
                
                relations.append(f"- {rel_type}: {content}")
        
        prompt_sections = [
            "\n".join(fragments),
            "\n".join(entities),
            "\n".join(relations),
            f"\n# Pregunta: {question}"
        ]
        
        prompt = "\n\n".join(prompt_sections)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Responde basándote solo en el contexto proporcionado del grafo de conocimiento. Cita la información relevante."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )
        
        return {
            "answer": response.choices[0].message.content,
            "chunks": nodes,
            "entities": expanded
        }
