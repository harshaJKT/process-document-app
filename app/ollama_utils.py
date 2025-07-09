import requests

OLLAMA_MODEL = "llama3.2:1b"
OLLAMA_URL = "http://localhost:11434/api/generate"

def summarize_text(text: str) -> str:
    prompt = f"Summarize the following text in one sentence:\n{text}"
    try:
        print(f"[OLLAMA] Sending summary prompt: {prompt[:60]}...")
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        })
        print(f"[OLLAMA] Status: {response.status_code}, Response: {response.text}")
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        print(f"Ollama summarization failed: {e}")
        return ""
    
def generate_keywords(text: str) -> str:
    prompt = f"Extract 5 keywords from the following text, comma separated. Only return the keywords, nothing else:\n{text}"
    try:
        print(f"[OLLAMA] Sending keyword prompt: {prompt[:60]}...")
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        })
        print(f"[OLLAMA] Status: {response.status_code}, Response: {response.text}")
        response.raise_for_status()
        keywords = response.json()["response"].strip()

        if ":" in keywords:
            keywords = keywords.split(":", 1)[-1].strip()
        return keywords
    except Exception as e:
        print(f"Ollama keyword extraction failed: {e}")
        return ""

