import streamlit as st
import os
from tabs import search_tab, documents_tab
from utils.document_loader import load_documents_from_folder

# Page Config
# Fix: Wide Mode dauerhaft aktivieren
st.set_page_config(page_title="LexMind", layout="wide")

# Index + Docs nur einmal laden
DOCS_PATH = "data/"

@st.cache_resource
def init_vectorstore():
    """Lädt Dokumente und erstellt/holt den Vectorstore (nur 1x pro Session)."""
    docs = load_documents_from_folder(DOCS_PATH)
    vectorstore = load_or_create_vectorstore(docs)
    return docs, vectorstore

if "docs" not in st.session_state or "vectorstore" not in st.session_state:
    st.session_state.docs, st.session_state.vectorstore = init_vectorstore()
    st.session_state.retriever = HybridRetriever(st.session_state.vectorstore)

st.title("LexMind - KI-Assistent für Juristen")
st.write(
    "Durchsuchen Sie juristische Vorlagen mit KI. Intelligent, schnell und präzise."
)

tab_suche, tab_dokumente = st.tabs(["Suche", "Dokumente"])

# Dokumente aus dem "docs" folder in die App laden
docs = load_documents_from_folder("docs/")
if not docs:
    st.error("Keine Dokumente im Ordner `docs/` gefunden.")
    st.stop()

with tab_suche:
    search_tab.render()

with tab_dokumente:
    documents_tab.render(docs)


