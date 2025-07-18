import logging
import requests

OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODEL_NAME = "all-minilm"
OLLAMA_GUARD_URL = "http://localhost:11434/api/chat"
GUARD_MODEL_NAME = "llama-guard3:1b"
CONVERSATIONAL_OLLAMA_URL = "http://localhost:11434/api/generate"
CONVERSATIONAL_MODEL_NAME = "llama3.2"


def call_embedder(prompt: str) -> str:
    logging.info("Calling Ollama embedder API...")
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={"model": EMBED_MODEL_NAME, "input": prompt}
    )
    response.raise_for_status()
    logging.info("Ollama embedder API called successfully.")
    return response.json()["embeddings"]


def call_chat_api(prompt: str) -> str:
    logging.info("Calling Ollama chat API...")
    response = requests.post(
        CONVERSATIONAL_OLLAMA_URL,
        json={"model": CONVERSATIONAL_MODEL_NAME, "prompt": prompt, "stream": False}
    )
    response.raise_for_status()
    logging.info("Ollama chat API called successfully.")
    return response.json()["response"]


def call_guard_api(prompt: str) -> str:
    logging.info("Calling Ollama guardrails API...")
    response = requests.post(
        OLLAMA_GUARD_URL,
        json={"model": GUARD_MODEL_NAME, "messages": [{"role": "user", "content": prompt}]
        , "stream": False}
    )
    response.raise_for_status()
    logging.info("Ollama guardrails API called successfully.")
    return response.json()
