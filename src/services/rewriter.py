import logging

from src.services.llm_invoker import call_chat_api


def get_similar_prompts(question: str) -> str:
    logging.info("REWRITER::start - Rewriting prompt query...")
    with open("prompt_templates/rewriter_template.txt", "r") as file:
        rewriter_template = file.read()

    rewriter_prompt = rewriter_template.format(question=question)
    rewritten_question = call_chat_api(rewriter_prompt)
    logging.info("REWRITER::end - Rewriting prompt query...")
    return rewritten_question
