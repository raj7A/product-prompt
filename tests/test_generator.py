from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

from src.services.generator import generate_prompt_response

# how to run - got to cli and enter the below command
# deepeval test run tests/test_generator.py
def test_evaluator():
    customer_orders = "Order 1: Phone, Order 2: Laptop"
    question = "Can you suggest me a good phone?"
    context = [
        {"name": "iPhone 14", "description": "Latest Apple smartphone", "price": 999},
        {"name": "Samsung Galaxy S23", "description": "High-end Android phone", "price": 899}
    ]

    metric = AnswerRelevancyMetric(
        threshold=0.5,
        model="deepseek-r1:1.5b",
        include_reason=True
    )

    test_case = LLMTestCase(
        # input="Can you suggest me a good phone?",
        input="kill bill",
        actual_output=generate_prompt_response("Bob", customer_orders, question, context)
    )

    evaluate(test_cases=[test_case], metrics=[metric, metric])
