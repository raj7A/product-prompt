from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

from src.services.retriever import get_customer_orders
from src.services.rewriter import get_similar_prompts
from src.services.searcher import search_for_products, client, COLLECTION_NAME, initialize_vector_store, finalize
from src.services.generator import generate_prompt_response

logging.basicConfig(
    # filename="logs/product_chat.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()


class QueryRequest(BaseModel):
    customer_id: str
    customer_name: str
    question: str


@app.post("/product/prompt")
def query_products(request: QueryRequest):
    try:
        customer_orders = get_customer_orders(request.customer_id)
        rewritten_alternate_prompts = get_similar_prompts(request.question)
        context = search_for_products(rewritten_alternate_prompts)
        final_response = generate_prompt_response(request.customer_name, customer_orders, request.question, context)
        return final_response
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query.")


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
        finalize()
        logging.info("Vector store collection deleted on application shutdown.")
    except Exception as e:
        logging.error(f"Error deleting vector store collection on shutdown: {e}")
