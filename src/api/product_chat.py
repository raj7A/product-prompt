import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List
import warnings
import logging
import json
from fastapi import FastAPI, HTTPException
from typing import List
import logging
from pydantic import BaseModel

warnings.filterwarnings("ignore", category=DeprecationWarning, message="`search` method is deprecated and will be removed in the future. Use `query_points` instead.")

logging.basicConfig(
    # filename="../../logs/product_chat.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")

OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODEL_NAME = "all-minilm"
OLLAMA_URL = "http://localhost:11434/api/generate"
COVERSATIONAL_MODEL_NAME = "llama3.2"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "product"

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

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

def load_data(file_path: str):
    with open(file_path, "r") as file:
        return json.load(file)

def serialize_product(product):
    """Convert product into a flat string for embedding."""
    return f"Product {product['name']} (ID: {product['id']}) with description: {product['description']} and price: ${product['price']}"

def get_embedding(text: str) -> List[float]:
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={"model": EMBED_MODEL_NAME, "input": text}
    )
    response.raise_for_status()
    embedding = response.json()["embeddings"]

    if isinstance(embedding[0], list):
        embedding = embedding[0]

    return embedding

def receive_request(customerId: str, customer_name: str, question: str):
    """
    Receives the request with the customer name and question.
    """
    logging.info(f"Received request from customer '{customer_name}' with question: '{question}'")
    return customerId, customer_name, question

def get_similar_prompts(question: str) -> str:
    logging.info("REWRITER::start - Rewriting prompt query...")
    with open("prompt_templates/rewriter_template.txt", "r") as file:
        rewriter_template = file.read()

    rewriter_prompt = rewriter_template.format(question=question)
    rewritten_question = call_ollama_api(rewriter_prompt)
    logging.info("REWRITER::end - Rewriting prompt query...")
    return rewritten_question

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

def call_ollama_api(prompt: str):
    """
    Calls the Ollama API with the provided prompt.
    """
    logging.info("Calling Ollama API...")
    response = requests.post(
        OLLAMA_URL,
        json={"model": COVERSATIONAL_MODEL_NAME, "prompt": prompt, "stream": False}
    )
    response.raise_for_status()
    logging.info("Ollama API called successfully.")
    return response.json()["response"]

def generate_prompt_response(customer_name: str, customer_orders: str, question: str, context: List[dict]) -> str:
    logging.info("GENERATOR::start - Generating response prompt for the customer query...")

    if context:
        formatted_context = "\n".join(
            [f"- {product['name']}: {product['description']} (Price: ${product['price']})" for product in context]
        )
    else:
        formatted_context = "No relevant products found."

    with open("prompt_templates/chat_template.txt", "r") as file:
        prompt_template = file.read()

    prompt = prompt_template.format(
        customerName=customer_name,
        customerOrders=customer_orders,
        question=question,
        context=formatted_context
    )

    prompt_response = call_ollama_api(prompt)
    logging.info("GENERATOR::end - Generating response prompt for the customer query...")
    return prompt_response

def get_customer_orders(customer_id: str) :
    logging.info("RETRIEVER::start - Retrieving customer orders...")
    customer_orders = load_data("data/customer_orders.json")
    logging.info("RETRIEVER::end - Retrieving customer orders...")
    return customer_orders

def main():
    initialize_vector_store()

    customer_id, customer_name, prompt_request = receive_request(1, "Bob", "Can you suggest me a good phone?")

    customer_orders = get_customer_orders(customer_id)

    rewritten_alternate_prompts = get_similar_prompts(prompt_request)

    context = search_for_products(rewritten_alternate_prompts)

    final_response = generate_prompt_response(customer_name, customer_orders, prompt_request, context)

    logging.info("*********************************************************************")
    logging.info(final_response)
    logging.info("*********************************************************************")

# if __name__ == "__main__":
#     main()

app = FastAPI()

class QueryRequest(BaseModel):
    customer_id: str
    customer_name: str
    question: str

@app.on_event("startup")
def on_startup():
    try:
        initialize_vector_store()
        logging.info("Vector store initialized on application startup.")
    except Exception as e:
        logging.error(f"Error initializing vector store on startup: {e}")

@app.on_event("shutdown")
def on_startup():
    try:
        client.delete_collection(COLLECTION_NAME)
        logging.info("Vector store collection deleted on application shutdown.")
    except Exception as e:
        logging.error(f"Error deleting vector store collection on shutdown: {e}")

@app.post("/product/prompt")
def query_products(request: QueryRequest):
    try:
        customer_orders = get_customer_orders(request.customer_id)
        rewritten_alternate_prompts = get_similar_prompts(request.question)
        context = search_for_products(rewritten_alternate_prompts)
        final_response = generate_prompt_response(request.customer_name, customer_orders, request.question, context)
        return {"response": final_response}
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query.")

@app.get("/health")
def health_check():
    return {"status": "OK"}