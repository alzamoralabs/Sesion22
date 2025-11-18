from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from graphtool import search_with_bolt, search_with_http, search_relationships
import os

load_dotenv()
NEO4J_URL = os.getenv("NEO4J_URL", "bolt://localhost:7687")
query = "DRIVES"  # Opciones: "LIVES_WITH", "DRIVES", "OWNS"

prompt_template="eres un asistente experto en relaciones entre personas y vehiculos" \
"Usa las herramientas disponibles para responder a las consultas sobre relaciones entre personas y " \
"vehículos que se encuentran en una base de datos Neo4j." \
"Responde de manera concisa y precisa." \
"las relaciones disponibles son:" \
"LIVES_WITH: cuando se desea saber la relacion de quienes viven juntos" \
"DRIVES: cuando se desea saber quien maneja un vehiculo" \
"OWNS: cuando se desea saber quien es el propietario de un vehiculo." \
"Utiliza la herramienta 'search_relationships' para buscar en la base de datos Neo4j." \
"El usuario y la clave de Neo4j son proporcionados automáticamente." \

model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,
    max_tokens=1000,
    timeout=30
)

agent = create_agent(model, tools=[search_relationships], system_prompt=prompt_template)

if __name__ == "__main__":
    prompt = "¿Quién conduce el vehículo de marca Volvo?"
    response = agent.invoke({"input": prompt})
    print("Respuesta del agente:")
    print(str(response))