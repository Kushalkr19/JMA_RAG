# JMA_RAG
JMA Knowledge Base Prototype (PostgreSQL, pgvector, Llama 3.2)
=============================================================

This folder contains a **complete implementation** of the
JMA RAG prototype using PostgreSQL, the `pgvector` extension for
semantic search, the Llama 3.2 Instruct model from Hugging Face for
language generation, and `python‑docx` for document assembly. 

Requirements
------------

To run this project you will need:

* A running PostgreSQL server (version 13 or higher is recommended).
* The [`pgvector` extension](https://github.com/pgvector/pgvector)
  installed in your PostgreSQL cluster.  On Ubuntu you can install it
  with:

  ```bash
  sudo apt-get install postgresql-13 pgvector-postgresql-13
  ```

  Then enable it in your database using:

  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  ```

* A Python environment with the following packages:

  - `psycopg2-binary` for connecting to PostgreSQL.
  - `pgvector` (Python client) for working with vector types.
  - `sentence-transformers` for computing text embeddings (e.g. using
    `all-MiniLM-L6-v2`).
  - `transformers` and `accelerate` for loading and running
    `meta-llama/Llama-3.2-3B-Instruct` (or another Llama 3.2 model).
  - `python-docx` for generating Word documents.

You can install these dependencies via pip:

```bash
pip install psycopg2-binary pgvector sentence-transformers transformers accelerate python-docx
```

Note: Accessing the Llama 3.2 models on Hugging Face requires
agreement to Meta’s community license and acceptance of terms on
HuggingFace.  Once you have access, you can download the model using
the `transformers` library.  Expect that these models are large and
require significant memory.

Database Setup
--------------

1. Create a new PostgreSQL database (e.g. `jma_knowledge_base`).
2. Enable the `pgvector` extension:

   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Run the `schema.sql` script in this directory to create the
   required tables and insert sample data.  For example:

   ```bash
   psql -d jma_knowledge_base -f schema.sql
   ```

Running the Prototype
---------------------

Set the following environment variables before running the script:

```bash
export PGHOST=localhost
export PGPORT=5432
export PGUSER=your_username
export PGPASSWORD=your_password
export PGDATABASE=jma_knowledge_base
```

Then run the main script:

```bash
python main.py
```

The script will:

1. Create the database schema if it does not exist.
2. Populate sample clients, stakeholders and knowledge entries.
3. Compute embeddings for the unstructured text using
   `sentence-transformers/all-MiniLM-L6-v2` and store them in the
   `embedding` column of the `knowledge_entries` table.
4. Retrieve relevant documents using semantic search with pgvector.
5. Construct a prompt and call `meta-llama/Llama-3.2-3B-Instruct` to
   generate a polished executive summary and recommendations.
6. Assemble the resulting text into a Word document using
   `python-docx` and save it to the `deliverables/` directory.
7. Store a record of the approved deliverable back into the database.

Files
-----

* `schema.sql` – Defines the PostgreSQL schema and inserts sample
  data.  It also creates a `vector` column on `knowledge_entries` for
  storing embeddings.
* `main.py` – Contains the end‑to‑end workflow described above.
* `requirements.txt` – Lists Python packages required to run the
  project.

Limitations
-----------

This implementation is **not executed** in this environment, and some
minor adjustments may be required to run it successfully in your own
setup (e.g. adjusting vector dimensions to match the embedding model
you choose).  Ensure your machine has sufficient memory to load
Llama 3.2 and that the database has the `pgvector` extension enabled.
