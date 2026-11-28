from langchain_ollama import ChatOllama

rag_generation_llm = ChatOllama(
            model="qwen3:8b",
            temperature=0,
            num_ctx=4096,
        )