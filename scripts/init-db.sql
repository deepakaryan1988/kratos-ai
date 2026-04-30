-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tables
CREATE TABLE IF NOT EXISTS security_policies (
    id SERIAL PRIMARY KEY,
    finding TEXT,
    remediation TEXT,
    embedding VECTOR(768)
);