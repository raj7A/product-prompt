import json
import logging
import warnings
from typing import List

from src.services.embedder import get_embedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "product"

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

warnings.filterwarnings("ignore", category=DeprecationWarning,
                        message="`search` method is deprecated and will be removed in the future. Use `query_points` instead.")


def search_for_products(query_text: str, top_k=3) -> List[dict]:
    logging.info("SEARCHER::start - Searching for similar products from vector store")
    query_vector = get_embedding(query_text)

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        score_threshold=0.1,
    )

    if results is None or len(results) == 0:
        logging.warning("No results found.")
        return []

    payloads = [result.payload for result in results]
    logging.info("SEARCHER::end - Searching for similar products from vector store")
    return payloads


def initialize_vector_store():
    logging.info("LOADER::start - Initializing vector store...")

    client.delete_collection(COLLECTION_NAME)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    logging.info("Vector store collection created.")

    points = []
    for idx, product in enumerate(load_data("data/products.json")):
        text = serialize_product(product)
        vector = get_embedding(text)
        points.append(PointStruct(
            id=idx,
            vector=vector,
            payload={
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "price": product["price"]
            }
        ))

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    logging.info("LOADER::end - Initializing vector store...")

def finalize():
    logging.info("LOADER::start - Deleting vector store collection...")
    client.delete_collection(COLLECTION_NAME)
    logging.info("LOADER::end - Deleting vector store collection...")

def load_data(file_path: str):
    with open(file_path, "r") as file:
        return json.load(file)


def serialize_product(product):
    """Convert product into a flat string for embedding."""
    return f"Product {product['name']} (ID: {product['id']}) with description: {product['description']} and price: ${product['price']}"
