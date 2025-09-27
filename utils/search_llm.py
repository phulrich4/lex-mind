# utils/search_llm.py
from gpt4all import GPT4All

# Modell laden (Mini-Version, CPU-tauglich)
# Streamlit Cloud: Modell wird beim Start geladen
model_path = "ggml-gpt4all-j-v1.3-groovy.bin"  # Mini/CPU Version
llm = GPT4All(model_path, verbose=False)

def run_llm_search(query: str) -> str:
    """
    LLM-gestützte Suche mit GPT4All Mini
    """
    prompt = f"""
    Du bist ein juristischer Assistent.
    Beantworte die folgende Frage präzise und sachlich:

    Frage: {query}
    """
    response = llm.generate(prompt)
    return response

