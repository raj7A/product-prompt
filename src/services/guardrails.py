import logging

from src.services.llm_invoker import call_guard_api


def prompt_check(prompt: str) -> None:
    logging.info("GUARDRAILS::start - Checking for unsafe content...")
    response = call_guard_api(prompt)
    if "unsafe" in response.get("message", {}).get("content", "").lower():
        logging.warning("GUARDRAILS::end - Ollama guardrails API detected unsafe content on prompt request")
        raise ValueError("Unsafe content detected by Ollama guardrails API.")
    logging.info("GUARDRAILS::end - Checking for unsafe content...")
