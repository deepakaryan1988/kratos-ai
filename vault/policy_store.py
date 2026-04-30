import psycopg2
from pgvector.psycopg2 import register_vector
import os
import requests

EMBEDDING_MODEL = "text-embedding-nomic-embed-text-v1.5"

def get_embedding(text: str):
    response = requests.post(
        f"{os.getenv('LOCAL_LLM_URL', 'http://localhost:1234/v1')}/embeddings",
        json={"model": EMBEDDING_MODEL, "input": text}
    )
    return response.json()['data'][0]['embedding']

def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "kratos_vault"),
        user=os.getenv("POSTGRES_USER", "dev_user"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

def store_policy(finding: str, remediation: str, embedding=None):
    conn = get_connection()
    register_vector(conn)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO security_policies (finding, remediation, embedding) VALUES (%s, %s, %s)",
        (finding, remediation, embedding)
    )
    conn.commit()
    cur.close()
    conn.close()

def find_similar(findings: list, limit: int = 5):
    """Find similar past findings using vector similarity."""
    embeddings = [get_embedding(f) for f in findings]
    # Average embeddings for multi-finding search
    avg_embedding = [sum(x[i] for x in embeddings) / len(embeddings) for i in range(len(embeddings[0]))]

    conn = get_connection()
    register_vector(conn)
    cur = conn.cursor()
    cur.execute(
        "SELECT finding, remediation FROM security_policies ORDER BY embedding <=> %s LIMIT %s",
        (avg_embedding, limit)
    )
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results