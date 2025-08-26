import streamlit as st
import os
from tabs import search_tab, documents_tab
from utils.document_loader import load_documents_from_folder
from utils.search import HybridRetriever, InMemoryVectorStore
from sentence_transformers import SentenceTransformer

# Page Config
st.set_page_config(page_title="LexMind", layout="wide")

# Pfad zu Dokumenten
DOCS_PATH = "docs/"

# ---------------------------------------
# Vectorstore & Retriever initialisieren
# ---------------------------------------
@st.cache_resource
def init_vectorstore():
    if not os.path.exists(DOCS_PATH):
        st.warning(f"Dokumentenordner '{DOCS_PATH}' nicht gefunden.")
        return [], None, None

    docs = load_documents_from_folder(DOCS_PATH)
    if not docs:
        return [], None, None

    # Embedding-Modell
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # InMemoryVectorStore initialisieren
    vectorstore = InMemoryVectorStore.from_documents(docs, embedding_model)
    
    # HybridRetriever
    retriever = HybridRetriever(vectorstore, docs, embedding_model)
    
    return docs, vectorstore, retriever


# ---------------------------------------
# App UI
# ---------------------------------------
st.title("LexMind - KI-Assistent für Juristen")
st.write("Durchsuchen Sie juristische Vorlagen mit KI. Intelligent, schnell und präzise.")

tab_suche, tab_dokumente = st.tabs(["Suche", "Dokumente"])

with tab_suche:
    search_tab.render(st.session_state.docs, st.session_state.retriever)

with tab_dokumente:
    documents_tab.render(st.session_state.docs)
