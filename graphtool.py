import os
import json
from typing import Any, Dict, List
from neo4j import GraphDatabase, exceptions as neo4j_exceptions
from langchain.tools import tool
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
load_dotenv

# /c:/gitprojects/ses22/local_agent.py
"""
Conectar a Neo4j en localhost:7474 y buscar relaciones.
Requisitos: pip install neo4j requests
"""


# Intentamos usar el driver oficial (Bolt). Si no está disponible o falla, usamos HTTP REST.
try:
    _HAS_BOLT = True
except Exception:
    GraphDatabase = None
    neo4j_exceptions = None
    _HAS_BOLT = False


DEFAULT_BOLT_URI = "bolt://localhost:7474"
DEFAULT_HTTP_URI = "http://localhost:7474"
DEFAULT_DB_HTTP_ENDPOINT = "/db/neo4j/tx/commit"  # endpoint estándar; en algunas versiones puede ser /db/data/transaction/commit

def search_with_bolt(user: str, password: str, cypher: str, params: Dict[str, Any] = None, limit: int = 25) -> List[Dict]:
    if not _HAS_BOLT:
        raise RuntimeError("neo4j driver no disponible. Instala 'neo4j' package para usar bolt.")
    uri = DEFAULT_BOLT_URI
    driver = GraphDatabase.driver(uri, auth=(user, password))
    results = []
    try:
        with driver.session() as session:
            q = f"{cypher} LIMIT $__limit" if "LIMIT" not in cypher.upper() else cypher
            merged_params = dict(params or {})
            merged_params["__limit"] = limit
            res = session.run(q, merged_params)
            for record in res:
                # record.data() devuelve un dict simple con claves del RETURN
                results.append(record.data())
    finally:
        driver.close()
    return results

def search_with_http(user: str, password: str, cypher: str, params: Dict[str, Any] = None, limit: int = 25) -> List[Dict]:
    url = DEFAULT_HTTP_URI + DEFAULT_DB_HTTP_ENDPOINT
    statement = cypher
    if "LIMIT" not in cypher.upper():
        statement = f"{cypher} LIMIT $__limit"
    payload = {
        "statements": [
            {
                "statement": statement,
                "parameters": dict(params or {}, **{"__limit": limit})
            }
        ]
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, auth=HTTPBasicAuth(user, password), headers=headers, data=json.dumps(payload))
    resp.raise_for_status()
    body = resp.json()
    results = []
    # respuesta: results -> series -> rows/columns
    for result in body.get("results", []):
        cols = result.get("columns", [])
        for row in result.get("data", []):
            # row["row"] es una lista de valores correspondientes a columns
            row_values = row.get("row", [])
            # convertir a dict columna:valor
            rec = {cols[i]: row_values[i] if i < len(row_values) else None for i in range(len(cols))}
            results.append(rec)
    return results

@tool
def search_relationships(cypher: str = "DRIVES", params: Dict[str, Any] = None, limit: int = 25) -> List[Dict]:
    """
    Buscar relaciones en Neo4j usando Cypher.
    Parámetros:
    - cypher: consulta Cypher o palabra clave ("LIVES_WITH", "DRIVES", "OWNS")
    - params: parámetros para la consulta Cypher
    - limit: número máximo de resultados a devolver
    Retorna una lista de diccionarios con los resultados.
    """
    cypher_LIVES = "MATCH p=()-[r:LIVES_WITH]->() RETURN p LIMIT 25" # LIVES_WITH
    cypher_DRIVES = "MATCH p=()-[r:DRIVES]->() RETURN p LIMIT 25" # DRIVES
    cypher_OWNS = "MATCH p=()-[r:OWNS]->() RETURN p LIMIT 25" # OWNS

    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    if cypher == "LIVES_WITH":
        cypher = cypher_LIVES
    elif cypher == "DRIVES":
        cypher = cypher_DRIVES
    elif cypher == "OWNS":
        cypher = cypher_OWNS
    else:
        raise ValueError("Cypher query no reconocida. Usa 'LIVES_WITH', 'DRIVES' o 'OWNS'.")
    
    # Intenta Bolt primero si está disponible, si falla usa HTTP
    if _HAS_BOLT:
        try:
            return search_with_bolt(user, password, cypher, params=params, limit=limit)
        except Exception as e:
            # si falla Bolt, intenta HTTP
            try:
                return search_with_http(user, password, cypher, params=params, limit=limit)
            except Exception:
                raise
    else:
        return search_with_http(user, password, cypher, params=params, limit=limit)

if __name__ == "__main__":
    # Configurar usuario/clave vía variables de entorno o cambiar aquí
    USER = os.getenv("NEO4J_USER", "neo4j")
    PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

    # Ejemplo: buscar relaciones
    cypher_query = "MATCH p=()-[r:LIVES_WITH]->() RETURN p LIMIT 25" # LIVES_WITH
    cypher_query = "MATCH p=()-[r:DRIVES]->() RETURN p LIMIT 25" # DRIVES
    cypher_query = "MATCH p=()-[r:OWNS]->() RETURN p LIMIT 25" # OWNS
    try:
        rows = search_relationships(USER, PASSWORD, cypher=cypher_query, limit=25)
        for i, r in enumerate(rows, 1):
            print(f"Result {i}: {r}")
    except Exception as ex:
        print("Error al consultar Neo4j:", str(ex))
        print("Si usas Bolt asegúrate de que Neo4j acepte conexiones bolt://localhost:7474 o ajusta los puertos.")