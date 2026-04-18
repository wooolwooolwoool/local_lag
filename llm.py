import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate(prompt, model="mistral"):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]