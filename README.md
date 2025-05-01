GraphRAG permite comprender y navegar las relaciones entre entidades, proporcionando respuestas más contextuales y explicables.

Permite identificar conexiones entre entidades, como entender que "el asesino era el mayordomo" debido a su relación con la víctima.
Facilita saltar entre ideas relacionadas, incluso si no comparten las mismas palabras.
Ademas el grafo muestra todas las conexiones, ayudando a verificar la veracidad de las respuestas.

✅
Integración de PDFs: documentos como tesis_n6208_Klappenbach e Inteligencia_Lavandera_LeccMag_USPCEU_2024
Se implementó una interfaz que permite visualizar las conexiones entre entidades, facilitando la comprensión de las respuestas generadas.

🧩 Desafíos enfrentados
1. Embeddings inconsistentes
Intenté usar OpenAI para los embeddings, pero al no ser los mismos que los del builder original, me daba respuestas que no tenían nada que ver. Terminé usando sentence-transformers que, aunque más lento, al menos daba resultados consistentes.
Nodos fantasma: Muchos nodos venían con valores nulos o vacíos, y mi código se rompía de formas misteriosas.

☕ Mejoras futuras
Refinamiento de relaciones: Mejorar la precisión en la identificación de relaciones entre entidades para aprovechar al máximo la estructura del grafo..

Integración con LangChain y LangGraph: Estos frameworks ofrecen componentes preconstruidos que podrían simplificar la gestión del contexto y las consultas, además de permitir flujos de trabajo más complejos y dinámicos.

Ajuste dinámico de embeddings: Implementar mecanismos que ajusten automáticamente los parámetros de búsqueda o cambien el modelo de embeddings según el tipo de pregunta ademas de usar los mas actualizados..

Memoria dinamica: Permitir que el sistema recuerde interacciones anteriores para mantener conversaciones más naturales y coherentes.

Función de simplificación: Añadir un botón que simplifique las respuestas complejas y otro que permita profundizar en el tema según el interés del usuario.

🛠️ Configuración rápida para DevMode
Importante: Actualmente, el backend utiliza sentence-transformers para los embeddings, lo que requiere una cantidad significativa de memoria para ejecutarse en instancias gratuitas.., entonces localmente es la solucion en esta instancia.

Requisitos
Tener Docker instalado.

Pasos
Clonar la rama DevMode del repositorio.

Crear un archivo .env con las siguientes variables:

env
Copiar
Editar
NEO4J_URI=neo4j+s://tu-instancia.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=xe5Y63flhQPBuBiwYebAis3FvrC_Tyt5peIZgy7DdGI
OPENAI_API_KEY=sk-tu-api-key
VECTOR_INDEX_NAME=vector
Construir la imagen de Docker:

bash
Copiar
Editar
docker-compose build
Iniciar los servicios:

bash
Copiar
Editar
docker-compose up
Acceder a la aplicación en http://localhost:5000.

Abrir el archivo index.html para visualizar el grafo y las conexiones.


![image](https://github.com/user-attachments/assets/bdeea60e-26d3-4fd9-b3b7-5c093c024c24)
![image](https://github.com/user-attachments/assets/92a3fc52-1232-4c27-a279-d9ef6895e19a)

