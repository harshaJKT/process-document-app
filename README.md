# Process Document App

This application processes uploaded documents, chunks their content, generates keywords and summaries using Ollama, and provides a retrieval API for question answering.

---

## Features
- Upload PDF documents
- Chunk content and store in PostgreSQL
- Generate keywords and summaries for each chunk using Ollama LLM
- Retrieve answers to user questions based on document content and user role

---

## Prerequisites
- Python 3.10+
- PostgreSQL
- Ollama (local LLM server)
- [Optional] DBeaver or any SQL client for DB management

---

## Setup Instructions

### 1. Clone the repository
```
git clone <your-repo-url>
cd process-document-app
```

### 2. Create and activate a virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Configure PostgreSQL
- Create a database (e.g., `process_documents`)
- Run the SQL script in `script_db` to create tables:
  - `document_data`
  - `user_role_map`

### 5. Configure Ollama
- [Download and install Ollama](https://ollama.com/download)
- Start the Ollama server:
  ```
  ollama serve
  ```
- Pull your desired model (e.g., llama3.2:1b):
  ```
  ollama pull llama3.2:1b
  ```

### 6. Configure environment variables (if needed)
- Edit `config.py` to set your database connection and upload directory.

### 7. Start the FastAPI server
```
uvicorn app.main:app --reload
```

---

## Usage

### Upload a Document
- Send a POST request to `/upload` with a PDF file and a `role` field.
- The file will be saved and processed in the background.


### Retrieve an Answer
- Send a GET request to `/retrieve?role=<role>&question=<your question>`

#### Example using browser or Postman
```
http://localhost:8000/retrieve?role=admin&question=What%20is%20IoT%3F
```

#### Example using Python (requests):
```python
import requests
url = "http://localhost:8000/retrieve"
params = {"role": "admin", "question": "What is IoT?"}
response = requests.get(url, params=params)
print(response.json())
```

- The API will return a JSON answer based on the document content and extracted keywords.

### User Role Management
- Use `/user-role` endpoints to manage user roles.

---

## Notes
- Ensure Ollama and PostgreSQL are running before starting the FastAPI app.
- The app uses background processing for document chunking and LLM calls.
- For large documents, only relevant chunks are used for answering questions.

---

## Troubleshooting
- If you get a 404 on `/retrieve`, make sure the router is included in `main.py`.
- If Ollama is not responding, check that the server is running and the model is pulled.
- For database errors, verify your schema matches the models.


