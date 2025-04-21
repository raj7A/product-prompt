import logging

from typing import List

from src.services.llm_invoker import call_embedder


def get_embedding(text: str) -> List[float]:
    logging.info("EMBEDDER::start - Generating embedding for the text...")
    embedding = call_embedder(text)

    if isinstance(embedding[0], list):
        embedding = embedding[0]
    logging.info("EMBEDDER::end - Generating embedding for the text...")
    return embedding
