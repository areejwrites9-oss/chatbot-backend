# RAG Chatbot Backend

This backend is the Python + FastAPI part of a beginner-friendly retrieval-augmented generation (RAG) chatbot. It loads Markdown documents, splits them into chunks, creates Gemini embeddings, stores them in Qdrant, retrieves relevant information for a user question, and sends that context to Groq for final answer generation.

## Part 1: Understand the project

### What is a backend?
A backend is the part of an application that runs on a server. It handles requests, reads files, calls APIs, stores data, and returns results to the frontend.

### What is an API?
An API (Application Programming Interface) is a set of endpoints that allow one program to talk to another. In this project, the React frontend sends questions to the FastAPI backend using HTTP requests.

### What is RAG?
RAG stands for Retrieval-Augmented Generation. Instead of asking a language model to answer only from its training memory, we first search a local knowledge base for the most relevant text and then pass that text to the model. This keeps answers grounded in your documents.

### Why do we need embeddings?
Embeddings are numerical representations of meaning. They convert text into vectors so a similarity search can find related information even when the exact words are different.

### What does Qdrant do?
Qdrant is a vector database. It stores vectors and metadata, and supports similarity search. In this project, it stores document chunks and their embeddings.

### What do Gemini and Groq do?
Gemini creates document and question embeddings. Groq generates the final answer from the context retrieved by the backend. Neither model reads Qdrant directly; the backend retrieves relevant text and sends it to Groq.

### What does ingestion mean?
Ingestion means preparing the knowledge base. The backend loads Markdown files, splits them into chunks, generates embeddings, and stores them in Qdrant.

### What does chunking mean?
Chunking means splitting long text into smaller pieces. This helps with retrieval because smaller chunks are easier to search and keep relevant context.

### What is the difference between ingestion and chatting?
- Ingestion prepares the knowledge base before the chatbot can answer questions.
- Chatting happens when a user asks a question and the backend finds relevant context, then generates an answer.

## Part 2: Prerequisites

Before you begin, make sure you have:

- Python 3.12 or a compatible version installed
- pip installed
- access to Google AI Studio for Gemini embeddings
- a GroqCloud account and API key for answer generation
- a Qdrant instance or Qdrant Cloud account

### Check Python and pip versions

Mac/Linux:

```bash
python3 --version
python3 -m pip --version
```

Windows PowerShell:

```powershell
python --version
python -m pip --version
```

If `python` is not recognized on Windows, try `py` instead:

```powershell
py --version
py -m pip --version
```

### Get API credentials
- Visit Google AI Studio to create a Gemini API key for embeddings.
- Create a GroqCloud API key at https://console.groq.com/keys for answer generation.
- Keep both keys in the backend `.env` file only.

### Get Qdrant credentials
- For local Qdrant: run a local instance and set `QDRANT_URL=http://localhost:6333`
- For Qdrant Cloud: create a cluster and copy the URL and API key

Never commit real secrets into the repository.

## Part 3: Create the main project and backend folder

From an empty directory, run:

```bash
mkdir chatbot
cd chatbot
mkdir backend
cd backend
```

What these commands do:
- `mkdir chatbot` creates the root project folder
- `cd chatbot` moves inside the project
- `mkdir backend` creates the backend folder
- `cd backend` moves into the backend folder

If the folder already exists, skip the creation step and just change into it:

```bash
cd chatbot/backend
```

## Part 4: Create the virtual environment

Create a virtual environment in the backend folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Verify that the environment is active:

```bash
which python
python -V
```

This isolates dependencies so each project has its own installed packages.

## Part 5: Install dependencies

Create `requirements.txt` with the package list shown in this project, then run:

```bash
python -m pip install -r requirements.txt
```

The key dependencies are:
- `fastapi` for the API server
- `uvicorn` to run the app
- `pydantic` for request validation
- `python-dotenv` for loading environment variables
- `google-genai` to create Gemini embeddings
- `groq` to generate answers
- `qdrant-client` to connect to Qdrant
- `pytest` for tests

## Part 6: Create the backend folders and files

Inside the backend folder, create these folders and files:

```bash
mkdir app data scripts tests
```

The purpose of each folder is:
- `app/` holds the main Python logic
- `data/` contains Markdown knowledge files
- `scripts/` contains terminal scripts
- `tests/` contains automated tests

The Python files are organized by responsibility:
- `app/main.py` starts the FastAPI app
- `app/config.py` loads environment variables
- `app/routes.py` defines API endpoints
- `app/schemas.py` defines request/response models
- `app/document_loader.py` loads Markdown files
- `app/chunking.py` splits text into chunks
- `app/embeddings.py` creates embeddings
- `app/qdrant_db.py` stores and searches vectors
- `app/ingest.py` builds the ingestion pipeline
- `app/retriever.py` searches Qdrant
- `app/prompt.py` stores the system prompt
- `app/generator.py` calls Groq to answer

## Part 7: Configure environment variables

Create a copy of `.env.example`:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Fill in the variables:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GROQ_API_KEY=your_groq_api_key_here
GROQ_GENERATION_MODEL=openai/gpt-oss-20b
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION_NAME=chatbot_knowledge
FRONTEND_ORIGIN=http://localhost:5173
CHUNK_SIZE=500
CHUNK_OVERLAP=80
```

Make sure `.env` is ignored by Git using `.gitignore`.

## Part 8: Understand each Python file

The backend follows this execution order:

1. `config.py` loads environment variables
2. `document_loader.py` reads Markdown files
3. `chunking.py` splits text into chunks
4. `embeddings.py` converts text into vectors
5. `qdrant_db.py` stores and searches vectors
6. `ingest.py` runs the ingestion pipeline
7. `retriever.py` searches Qdrant for relevant chunks
8. `generator.py` calls Groq with the retrieved context
9. `routes.py` exposes the API
10. `main.py` starts FastAPI

### `config.py`
Purpose: read environment variables and validate required settings.
Input: `.env` values.
Processing: `load_dotenv()` loads variables and the app validates required keys.
Output: configuration settings used by the rest of the app.
Next: all modules that need API keys or database settings.

### `document_loader.py`
Purpose: read Markdown knowledge files.
Input: the `data/` directory.
Processing: finds all `.md` files and reads them as text.
Output: a list of documents with file names and content.
Next: `chunking.py`.

### `chunking.py`
Purpose: split long text into smaller overlapping pieces.
Input: document text.
Processing: slice text into chunks while preserving some overlap.
Output: a list of chunk strings.
Next: `embeddings.py`.

### `embeddings.py`
Purpose: convert text into vectors.
Input: document chunk text or a user question.
Processing: call the Gemini embedding model.
Output: a list of floating-point numbers representing semantic meaning.
Next: `qdrant_db.py` during ingestion and `retriever.py` during chat.

### `qdrant_db.py`
Purpose: connect to Qdrant and store/search vectors.
Input: embedding vectors and metadata.
Processing: create a collection if it does not exist, store vectors, and run similarity search.
Output: matching chunks with source names and scores.
Next: `ingest.py` and `retriever.py`.

### `ingest.py`
Purpose: execute the ingestion pipeline.
Input: Markdown files from `data/`.
Processing: load, chunk, embed, and upsert documents.
Output: counts for documents, chunks, and stored vectors.
Next: `scripts/ingest_documents.py` or an API route.

### `retriever.py`
Purpose: search the knowledge base for relevant content.
Input: a user question.
Processing: embed the question and search Qdrant.
Output: retrieved context and source metadata.
Next: `generator.py`.

### `prompt.py`
Purpose: keep the system prompt separate and easy to edit.
Input: a prompt string.
Processing: instruct Groq to use retrieved context and avoid hallucinations.
Output: a reusable system prompt.
Next: `generator.py`.

### `generator.py`
Purpose: produce the final answer with Groq.
Input: the user question and the retrieved context.
Processing: send a prompt to Groq with the system instructions.
Output: a final answer string.
Next: `routes.py`.

### `routes.py`
Purpose: define HTTP endpoints.
Input: `POST /chat` requests and `POST /ingest` requests.
Processing: call retrieval, generation, and ingestion logic.
Output: JSON responses with answers and sources.
Next: `main.py`.

### `main.py`
Purpose: create the FastAPI app and register routes.
Input: the app configuration and router.
Processing: initialize FastAPI, enable CORS, and include API routes.
Output: a running backend service.
Next: Uvicorn starts the app.

## Part 9: Add knowledge to Markdown files

The project includes a sample file at `backend/data/kashaf_info.md`.

You can open it and replace the sample content with your own notes:

```bash
nano data/kashaf_info.md
```

Or on Windows:

```powershell
notepad data\kashaf_info.md
```

You can also add more Markdown files in the same folder. The loader automatically finds files ending with `.md`.

## Part 10: Run document ingestion

From the backend folder, run:

```bash
python -m scripts.ingest_documents
```

You should see output similar to:

```text
Ingestion complete.
Documents processed: 1
Chunks processed: 8
Vectors stored: 8
```

This step does the following:
- reads Markdown files
- splits them into chunks
- creates embeddings
- stores vectors in Qdrant

If you change the Markdown content, you should ingest again so the vector database reflects the latest content.

### Troubleshooting ingestion

- Missing file: make sure `data/` exists and contains `.md` files
- Invalid embedding API key: check `GEMINI_API_KEY`
- Invalid answer-generation API key: check `GROQ_API_KEY`
- Qdrant connection error: confirm `QDRANT_URL` and `QDRANT_API_KEY`
- Embedding failure: verify the model name is supported by the Gemini API
- Empty file: the loader raises a clear error if the Markdown file is blank

## Part 11: Start the FastAPI backend

From the backend directory, run:

```bash
uvicorn app.main:app --reload
```

This command does the following:
- `uvicorn` starts the ASGI server
- `app.main:app` points to the app object in `app/main.py`
- `--reload` reloads the server when files change

Open the API docs in your browser:

```text
http://127.0.0.1:8000/docs
```

### Health check example

Request:

```bash
curl http://127.0.0.1:8000/health
```

Example response:

```json
{"status":"ok","service":"rag-chatbot-backend"}
```

## Part 12: Test the RAG chatbot

### Check backend health
Use the health endpoint or the FastAPI docs.

### Run ingestion
Use:

```bash
python -m scripts.ingest_documents
```

### Chat request example
Open the Swagger UI at `/docs` or send a request with curl:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```

Example response:

```json
{
  "answer": "RAG stands for Retrieval-Augmented Generation. It combines a search step with a generation step so the model can answer using relevant knowledge from a local dataset.",
  "sources": [
    {"source": "kashaf_info.md", "score": 0.85}
  ]
}
```

### When no relevant context is found
The backend returns a clear answer explaining that the knowledge base did not include enough information.

## Part 13: Common errors

### Python or pip not found
Install Python and ensure it is added to `PATH`.

### Virtual environment not activated
Run the activation command again before installing dependencies.

### Missing environment variables
Check your `.env` file and confirm the keys are written correctly.

### Gemini embedding authentication or quota errors
Verify `GEMINI_API_KEY` and check your Gemini usage limits.

### Groq authentication, quota, or model errors
Verify `GROQ_API_KEY`, your GroqCloud usage limits, and that `GROQ_GENERATION_MODEL` is currently available to your account.

### Unsupported model names
Make sure `GEMINI_EMBEDDING_MODEL` is supported by Gemini and `GROQ_GENERATION_MODEL` is available through GroqCloud.

### Embedding dimension mismatch
The Qdrant collection vector size must match the embedding model dimension.

### Qdrant connection failure
Check whether Qdrant is running locally or whether the Cloud URL and API key are correct.

### Empty or missing Markdown files
Ensure the `data/` folder contains valid `.md` files.

### No relevant search results
The query may not match the stored knowledge. Try different wording or add more information to the Markdown files.

### CORS errors
Confirm the frontend origin matches `FRONTEND_ORIGIN` in `.env`.

### Port 8000 already in use
Use a different port or stop the other process using the port.

### Import errors
Make sure you are running from the backend folder and your virtual environment is active.

## Part 14: Beginner exercises

1. Change the information in `data/kashaf_info.md`.
2. Add a second Markdown file to the `data/` folder.
3. Change the chunk size and overlap in `.env`.
4. Change the number of retrieved chunks in `routes.py` or `retriever.py`.
5. Edit the system prompt in `app/prompt.py`.
6. Ask questions the knowledge base can and cannot answer.

These exercises show how the different parts of a RAG pipeline affect the final output.

## Summary

This backend is intentionally simple and clear so students can understand each stage of the pipeline without unnecessary complexity. The main educational flow is:

- load Markdown files
- split into chunks
- embed each chunk
- store vectors in Qdrant
- embed the user question
- search for relevant text
- send retrieved context to Groq
- return the answer and source metadata


## config.py
The config.py file is the backend’s central place for settings

##  document_loader.py
The document_loader.py file reads the knowledge-base Markdown files from backend/data/.

## embeddings.py
In this project, embeddings.py uses Gemini to:

Convert document chunks into vectors during ingestion.

Convert each user’s question into a vector during chat.

## ingest.py
ingest.py runs the document-preparation workflow: it loads Markdown files, splits them into chunks, creates an embedding for each chunk, and sends those chunks and vectors to Qdrant for storage. Run ingestion after adding or changing knowledge files.

## qdrant_db.py
qdrant_db.py to store it in Qdrant.

## retriever.py
retriever.py handles the search step during a chat. It takes the user’s question, turns it into an embedding, asks qdrant_db.py to find the most similar stored chunks, and returns the matching text with its source information.

## generator.py
generator.py creates the chatbot’s final answer. It receives the user’s question and the relevant text retrieved from Qdrant, then sends both—along with the system instructions—to Groq.


