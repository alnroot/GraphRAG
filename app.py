from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from simple_graph_rag import GraphRAGChatbot

# Load environment variables
load_dotenv()
# import debugpy
# debugpy.listen(("0.0.0.0", 5678))
# # debugpy.wait_for_client()
print("⏳ Debugger is ready to attach")
app = Flask(__name__)

chatbot = GraphRAGChatbot()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

@app.route('/graph/info', methods=['GET'])
def graph_info():
    """Endpoint to get basic info about the graph."""
    try:
        info = chatbot.get_graph_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/ask', methods=['POST'])
def ask_question():
    """Endpoint to ask questions using GraphRAG."""
    data = request.json
    if not data or 'question' not in data:
        return jsonify({"error": "No question provided"}), 400
    
    question = data['question']
    try:
        response = chatbot.ask(question)
        return jsonify({"answer": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/graph/summary', methods=['GET'])
def graph_summary():
    """Endpoint to get a summary of the knowledge graph."""
    try:
        with chatbot.driver.session() as session:
            # Count nodes by label
            node_count_query = """
            MATCH (n)
            RETURN labels(n) AS label, count(n) AS count
            """
            node_counts = session.run(node_count_query)
            
            # Count relationships by type
            rel_count_query = """
            MATCH ()-[r]->()
            RETURN type(r) AS type, count(r) AS count
            """
            rel_counts = session.run(rel_count_query)
            
            summary = {
                "nodes": {record["label"][0] if record["label"] else "Unlabeled": record["count"] 
                         for record in node_counts},
                "relationships": {record["type"]: record["count"] for record in rel_counts}
            }
            
            return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.teardown_appcontext
def close_db_connection(error):
    """Close Neo4j connection when application context ends."""
    chatbot.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)