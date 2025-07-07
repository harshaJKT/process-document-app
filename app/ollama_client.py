import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"  # Use your model name

def ask_ollama(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt
    }
    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    response.raise_for_status()
    result = ""
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8")
            import json
            obj = json.loads(data)
            if "response" in obj:
                result += obj["response"]
    print(result+"\n")
    return result