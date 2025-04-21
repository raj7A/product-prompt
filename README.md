# GenAI prompting application

    A RAG based GenAI prompting application that runs completely on local developer machine, and can be used for demo/learning purpose.

## Overview

![prompt_flow.png](docs/prompt_flow.png)

## Technology Stack

- **Python**: The programming language used for the script.
- **ollama**: A local LLM server that runs on your machine.
- **docker**: A containerization platform used to run Qdrant.
- **Qdrant**: A vector database used for storing and retrieving embeddings.

## Installation and Setup

Follow these steps to set up and run the script:

### 1. Install & Run ollama

```shell
  brew install ollama
  ollama serve &
  ollama pull all-minilm
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

### 5. Run the Script
```bash  
  cd src/api/
  python product_chat.py
```

### 6. Deactivating the Virtual Environment
```bash
deactivate
```

## Sample output:

[product_chat.log](logs/product_chat.log)

![logs.png](docs/logs.png)

## References

https://martinfowler.com/articles/gen-ai-patterns