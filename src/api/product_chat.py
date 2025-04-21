import json
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.services.generator import generate_prompt_response
from src.services.guardrails import prompt_check
from src.services.rewriter import get_similar_prompts
from src.services.retriever import search_for_products, initialize_vector_store, finalize

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
        prompt_check(request.question)
        customer_orders = get_customer_orders(request.customer_id)
        rewritten_alternate_prompts = get_similar_prompts(request.question)
        context = search_for_products(rewritten_alternate_prompts)
        final_response = generate_prompt_response(request.customer_name, customer_orders, request.question, context)
        prompt_check(final_response)
        return final_response
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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

def get_customer_orders(customer_id: str):
    logging.info("start - Reading customer orders...")
    with open("data/customer_orders.json", "r") as file:
        customer_orders = json.load(file)
    logging.info("end - Reading customer orders...")
    return customer_orders
