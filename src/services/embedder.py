import logging

from typing import List

from src.services.llm_invoker import call_embedder


def get_embedding(text: str) -> List[float]:
    logging.info("Calling Ollama embedder API...")
    embedding = call_embedder(text)

    if isinstance(embedding[0], list):
        embedding = embedding[0]
    logging.info("Calling Ollama embedder API...")
    return embedding
