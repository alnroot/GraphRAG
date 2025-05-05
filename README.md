Mientras que un sistema RAG tradicional busca coincidencias de palabras clave, GraphRAG permite comprender y navegar las relaciones entre entidades, proporcionando respuestas más contextuales y explicables.

Permite identificar conexiones entre entidades, como entender que "el asesino era el mayordomo" debido a su relación con la víctima.

Facilita saltar entre ideas relacionadas, incluso si no comparten las mismas palabras.

El grafo muestra todas las conexiones, ayudando a verificar la veracidad de las respuestas.

✅
PDFs: tesis_n6208_Klappenbach e Inteligencia_Lavandera_LeccMag_USPCEU_2024, extrayendo información relevante de estos 2 papers que hablan de IA (tecnologia) y neurociencia de la dopamina para identificar relaciones..

Se implementó una interfaz que permite visualizar las conexiones entre entidades, facilitando la comprensión de las respuestas generadas.

🧩 Desafíos
Inicialmente se utilizaron embeddings de OpenAI, pero al no coincidir con los del builder original "graphRAG builder neo4j", las respuestas eran incoherentes. Se optó por sentence-transformers, que, aunque más lentos, ofrecieron resultados consistentes y eran los mismos generados por la interfaz de neo4j publica..

Se encontraron nodos con valores nulos o vacíos, lo que causaba errores en el código. Se implementaron validaciones para manejar estos casos y asegurar la estabilidad del sistema.

☕ Mejoras futuras
Mejorar la precisión en la identificación de relaciones entre entidades para aprovechar al máximo la estructura del grafo.

Integración con LangChain y LangGraph: Estos frameworks ofrecen componentes preconstruidos que podrían simplificar la gestión del contexto y las consultas, además de permitir flujos de trabajo más complejos y dinámicos.

Ajuste dinámico de embeddings: Implementar mecanismos que ajusten automáticamente los parámetros de búsqueda o cambien el modelo de embeddings según el tipo de pregunta.

Memoria de múltiples turnos: Permitir que el sistema recuerde interacciones anteriores para mantener conversaciones más naturales y coherentes.

Función de simplificación: Añadir un botón que simplifique las respuestas complejas y otro que permita profundizar en el tema según el interés del usuario.

🛠️ Configuración rápida para DevMode y probarlo localmente

**Importante: Actualmente, el backend utiliza sentence-transformers para los embeddings, lo que requiere una cantidad significativa de memoria para ejecutarse localmente.
**
Requisitos
Tener Docker instalado.

Pasos
Clonar la rama DevMode del repositorio.

Crear un archivo .env con las siguientes variables:

.env

NEO4J_URI=neo4j+s://33e44caf.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=xe5Y63flhQPBuBiwYebAis3FvrC_Tyt5peIZgy7DdGI
OPENAI_API_KEY=sk-tu-api-key
VECTOR_INDEX_NAME=vector
Construir la imagen de Docker:

.bash:
docker-compose build
Iniciar los servicios:

bash
Copiar
Editar
docker-compose up
Acceder a la aplicación en http://localhost:5000.

Abrir el archivo index.html para visualizar el grafo y las conexiones.


![image](https://github.com/user-attachments/assets/5ab0ee76-4871-46b8-9ce3-6469d8d2c42d)

![image](https://github.com/user-attachments/assets/1c55fa4d-ee3d-42e2-8840-1b4bfed47930)

