Mi Aventura con GraphRAG Knowledge Graph Builder 🚀

Por qué GraphRAG

No es solo memoria fotográfica: Con RAG normal es como buscar en un libro por palabras. Con GraphRAG es como entender que el asesino era el mayordomo porque tenía conexión con la víctima (navegas relaciones, no solo texto).
Es como tener un cerebro digital: Puedes "saltar" entre ideas relacionadas aunque no usen las mismas palabras.
Puedes ver por qué te responde algo: El grafo muestra todas las conexiones, así que sabes que no se está inventando cosas (al menos no tanto).

Mis batallas durante la implementación 💪
Lo que salió bien

Los problemas que me dieron dolores de cabeza 🤕

El drama de los embeddings: Intenté usar OpenAI para los embeddings, pero al no ser los mismos que los del builder original, me daba respuestas que no tenían nada que ver. Terminé usando sentence-transformers que, aunque más lento, al menos daba resultados consistentes.
Nodos fantasma: Muchos nodos venían con valores nulos o vacíos, y mi código se rompía de formas misteriosas.
La guerra contra los textos largos: Algunos fragmentos eran tan largos que el pobre LLM se quedaba sin tokens. Implementé un límite de 300 caracteres

Cómo lo haría mejor si tuviera más café y tiempo ☕

Refinamiento de relaciones: El GraphRAG actual está bien, pero podría refinar mucho más las relaciones entre entidades para aprovechar mejor la estructura del grafo. A veces siento que apenas estoy rascando la superficie.
Integraría LangChain y LangGraph: Estos frameworks abstraen mucha complejidad y tienen componentes pre-construidos que me habrían ahorrado escribir todo ese código para manejar el contexto y las consultas. ¡Sacarle el jugo al grafo con LangGraph sería épico!
Ajuste dinámico de embeddings: Cuando una búsqueda da resultados malos, sería genial poder ajustar automáticamente los parámetros de búsqueda o incluso cambiar el modelo de embeddings según el tipo de pregunta.
Memory multi-turno: Hacer que recuerde preguntas anteriores para poder tener una conversación natural, no solo preguntas aisladas.
Una interfaz que no parezca de los 90s: Una UI donde puedas ver el grafo, las conexiones, y cómo llegó a la respuesta. Sería como CSI pero para información.
Función "explícame como si tuviera 5 años": Botón para simplificar respuestas complejas y otro para profundizar si te interesa el tema.

PDF:
tesis_n6208_Klappenbach
Inteligencia_Lavandera_LeccMag_USPCEU_2024

Cómo ponerlo a funcionar en tu máquina
Lo que necesitas

Configuración rápida para DevMode **la rama DevMode**
**IMPORTANTE**

TENER DOCKER Y EJECUTAR CON LAS VARIABLES:

Crea un archivo .env con:

NEO4J_URI=neo4j+s://tu-instancia.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=xe5Y63flhQPBuBiwYebAis3FvrC_Tyt5peIZgy7DdGI
OPENAI_API_KEY=sk-tu-api-key-carísima
VECTOR_INDEX_NAME=vector

Construye la imagen:
docker-compose build

docker-compose up

estará en http://localhost:5000

por ultimo abrir el archivo index.html para visualizacion
veras algo asi:
![image](https://github.com/user-attachments/assets/bdeea60e-26d3-4fd9-b3b7-5c093c024c24)
![image](https://github.com/user-attachments/assets/92a3fc52-1232-4c27-a279-d9ef6895e19a)

