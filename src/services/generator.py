import logging
from typing import List

from src.services.llm_invoker import call_chat_api


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

    prompt_response = call_chat_api(prompt)
    logging.info("GENERATOR::end - Generating response prompt for the customer query...")
    return prompt_response
