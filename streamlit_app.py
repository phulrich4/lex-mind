# streamlit_app.py
import streamlit as st
import os
from tabs import search_tab, documents_tab, admin_tab
from utils.document_loader import load_documents_from_folder
from utils.search import InMemoryVectorStore, HybridRetriever
from sentence_transformers import SentenceTransformer

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(page_title="LexMind", layout="wide")

# ------------------------------
# Dokumentenpfad
# ------------------------------
DOCS_PATH = "docs/"

# ------------------------------
# Vectorstore & Retriever initialisieren
# ------------------------------
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

    # InMemoryVectorStore
    vectorstore = InMemoryVectorStore.from_documents(docs, embedding_model)

    # HybridRetriever
    retriever = HybridRetriever(vectorstore, docs, embedding_model)

    return docs, vectorstore, retriever

# ------------------------------
# Session State vorbereiten
# ------------------------------
if "docs" not in st.session_state:
    st.session_state.docs = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "retriever" not in st.session_state:
    st.session_state.retriever = None

# **Neu: search_queries initialisieren**
if "search_queries" not in st.session_state:
    st.session_state.search_queries = []

# Optional: Suchergebnisse (falls search_tab sie nutzt)
if "search_results" not in st.session_state:
    st.session_state.search_results = []
    
# Vectorstore & Retriever initialisieren, falls noch nicht vorhanden
if not st.session_state.retriever:
    st.session_state.docs, st.session_state.vectorstore, st.session_state.retriever = init_vectorstore()

# ------------------------------
# App UI
# ------------------------------
st.title("LexMind - KI-Assistent für Juristen")
st.write("Durchsuchen Sie juristische Vorlagen mit KI. Intelligent, schnell und präzise.")

tab_suche, tab_dokumente, tab_admin = st.tabs(["Suche", "Dokumente", "Admin"])

with tab_suche:
    if st.session_state.retriever:
        search_tab.render(st.session_state.docs, st.session_state.retriever)
    else:
        st.warning("Keine Dokumente verfügbar. Bitte Dokumente in 'docs/' ablegen.")

with tab_dokumente:
    documents_tab.render(st.session_state.docs)

with tab_admin:
    admin_tab.render()
