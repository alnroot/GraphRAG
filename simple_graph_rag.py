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
        nodes = self.find_relevant_nodes(question)
        if not nodes:
            return {"answer": "No encontré información relevante.", "context": None, "sources": []}
        # docs = self._get_related_documents(nodes)
        expanded = self._expand_context(nodes)
        return self._generate_response(question, nodes, expanded)
    
    
    def find_relevant_nodes(self, query):
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

        node_ids = [n["id"] for n in nodes if "id" in n]
        if not node_ids:
            return []

        query = """
            MATCH (n)-[r:HAS_ENTITY]->(e)
            WHERE elementId(n) IN $node_ids
            RETURN
            elementId(e)     AS id,
            COALESCE(e.text,
                    e.name,
                    e.id)       AS content,
            labels(e)         AS entity_labels,
            type(r)           AS relationship_type
            LIMIT $limit;
        """

        with self.driver.session() as session:
            result = session.run(query, node_ids=node_ids, limit=limit)

            expanded = []
            for record in result:
                expanded.append({
                    "id":                record["id"],
                    "content":           record["content"],
                    "labels":            record["entity_labels"],
                    "relationship_type": record["relationship_type"]
                })

            # Si no hay entidades, puedes devolver el texto original de los chunks
            if not expanded:
                expanded = [
                    {"id": n["id"], "content": n["text"], "labels": n.get("labels", []), "relationship_type": None}
                    for n in nodes[:limit]
                ]

            return expanded



    def _generate_response(self, question, nodes, expanded):
        """
        Construye un prompt que incluye:
        1. Los fragmentos de texto (chunks) más relevantes.
        2. La lista de entidades extraídas con sus etiquetas y tipo de relación.
        Y envía ese prompt al LLM para generar la respuesta.
        """
        # 1) Fragmentos relevantes
        chunk_lines = ["Fragmentos relevantes:"]
        for i, n in enumerate(nodes, start=1):
            text = n["text"].strip().replace("\n", " ")
            # recortamos a 200 caracteres para no saturar el prompt
            snippet = text[:200] + ("…" if len(text) > 200 else "")
            chunk_lines.append(f"{i}. {snippet}")

        # 2) Entidades extraídas
        entity_lines = ["Entidades extraídas:"]
        for e in expanded:
            name = e["content"]
            labs = ", ".join(e["labels"])
            rel  = e["relationship_type"]
            entity_lines.append(f"- “{name}” (etiquetas: {labs}, relación: {rel})")

        top = expanded[:5]

        # construyo las secciones
        frag = ["Fragmentos relevantes:"]
        for i,n in enumerate(nodes[:2],1):
            frag.append(f"{i}. {n['text'][:100]}…")

        ents = ["Entidades clave:"]
        for e in top:
            ents.append(f"- {e['content']} ({', '.join(e['labels'])}): {e.get('snippet','')}")

        rels = ["Relaciones:"]
        # aquí deberías recuperar los tipos y destinos reales
        for e in top:
            rels.append(f"• {e['content']} –{e['relationship_type']}→ …")

        prompt = "\n".join(["Contexto enriquecido:", *frag, "", *ents, "", *rels, "", f"Pregunta: {question}"])

        # 4) Llamada al LLM
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Utiliza el contexto proporcionado para responder de forma precisa y cita las entidades extraídas."},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )

        answer = response.choices[0].message.content

        # 5) Devolver estructura final
        return {
            "answer":  answer,
            "chunks":  nodes,
            "entities": expanded
        }
