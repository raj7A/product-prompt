# GenAI prompting application

Read this [blog](https://medium.com/@r_7/e1d165962656) once for more context,

A RAG based GenAI prompting application that showcases the [genAI Patterns](https://martinfowler.com/articles/gen-ai-patterns). 

This application is capable of answering customer queries (like suggest me a good phone) based on the product catalog and customer purchase history.

This setup runs completely on local developer machine, and to be used for poc/learning purpose.

## Overview

### Architecture
![arch.png](docs/arch.png)

### Prompt flow

![prompt_flow.png](docs/prompt_flow.png)

## Technology Stack

- **Python**: The programming language used for the script.
- **Ollama**: A local LLM server that runs on your machine.
- **Docker**: A containerization platform used to run Qdrant.
- **Qdrant**: A vector database used for storing and retrieving embeddings.

## Installation and Setup

Follow these steps to set up and run the script:

### 1. Install & Run ollama

```shell
  brew install ollama
  ollama serve &
  ollama pull llama3.2:latest
  ollama pull all-minilm
  ollama pull llama-guard3:1b
```

### 2. Install & Run Qdrant
```shell
  brew install docker
  docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

### 3. Create and Activate a Virtual Environment
```bash
  python3 -m venv venv
  source venv/bin/activate
```

### 4. Install Dependencies
```bash
  pip install -r requirements.txt
```

### 5. Run
1. Start the app
```bash  
  uvicorn src.api.product_chat:app --host 0.0.0.0 --port 8000
```
2. Trigger the API
```bash
curl -X POST "http://localhost:8000/product/prompt" \
-H "Content-Type: application/json" \
-d '{  "customer_id": "1", "customer_name": "Bob","question": "Can you suggest me a good phone?"}'
```

### 6. Deactivating the Virtual Environment
```bash
deactivate
```

## Sample output

### 1. Prompt response - safe request
![output.png](docs/output.png)

### 2. Prompt response - unsafe request

![guardrails.png](docs/guardrails.png)

### 3. Prompt logs

[product_chat.log](logs/product_chat.log)

![logs.png](docs/logs.png)

## Disclaimer
This application is to be used for learning purposes only, specifically to explore how a genAI application would look like, and to help understand these patterns better.
Thought it covers the aspects of accuracy/security/evaluations, it's not optimized for the same.
There are lots of tools/frameworks (refer the AI Stack image below) available in the market for each of the aspects covered in the application, with more tools comes the more power to the app. 
Explore them for production use cases.

![AI-Stack.png](docs/AI-Stack.png)

## References

https://martinfowler.com/articles/gen-ai-patterns