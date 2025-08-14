-- Schema definition for JMA RAG prototype using PostgreSQL and pgvector.

-- Enable the pgvector extension.  This must be executed once per
-- database before creating the tables.  If you have already enabled
-- the extension you can comment out the following line.
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop tables if they already exist (useful for development).
DROP TABLE IF EXISTS knowledge_entries;
DROP TABLE IF EXISTS stakeholders;
DROP TABLE IF EXISTS clients;

-- Clients table: stores organisations.
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Stakeholders table: associates named individuals with a client.
CREATE TABLE stakeholders (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    tone VARCHAR(50) NOT NULL,
    priority1 VARCHAR(255),
    priority2 VARCHAR(255),
    priority3 VARCHAR(255)
);

-- Knowledge entries table: stores unstructured text associated with a
-- client and optionally a stakeholder.  The `embedding` column uses
-- pgvector to store a high‑dimensional representation of the entry.
CREATE TABLE knowledge_entries (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    stakeholder_id INTEGER REFERENCES stakeholders(id) ON DELETE SET NULL,
    type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sample data.  Two clients with one stakeholder each and several
-- knowledge entries.  The embeddings will be computed and updated
-- by the Python script.
INSERT INTO clients (name) VALUES
  ('Acme Corp'),
  ('Globex Inc');

INSERT INTO stakeholders (client_id, name, role, tone, priority1, priority2, priority3) VALUES
  (1, 'John Smith', 'Chief Information Officer', 'direct', 'timeline efficiency', 'cost reduction', 'vendor selection'),
  (2, 'Mary Johnson', 'Chief Financial Officer', 'collaborative', 'budget control', 'risk mitigation', 'cross-team communication');

INSERT INTO knowledge_entries (client_id, stakeholder_id, type, content) VALUES
  (1, 1, 'meeting', 'The project timeline is a major concern for Acme Corp. We need to reduce delays by streamlining vendor selection and improving team coordination. The CIO emphasised the importance of cost reduction while maintaining quality.'),
  (2, 2, 'email', 'Our budget control has improved, but we need to mitigate risks and ensure cross-team communication remains strong for Globex Inc. Mary wants to keep stakeholders aligned.'),
  (1, NULL, 'meeting', 'In a joint meeting stakeholders expressed anxiety about timeline and budget overruns. Cost reduction is key; we should analyse production costs and look for savings without sacrificing quality.');