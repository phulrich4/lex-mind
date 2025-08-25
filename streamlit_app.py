import streamlit as st
import os
from tabs import search_tab, documents_tab
from utils.document_loader import load_documents_from_folder
from utils.search import HybridRetriever
from langchain_community.vectorstores import InMemoryVectorStore
from langchain.embeddings import SentenceTransformerEmbeddings

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

    embedding_model = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

    vectorstore = InMemoryVectorStore.from_documents(docs, embedding=embedding_model)
    retriever = HybridRetriever(vectorstore, docs, embedding_model)
    return docs, vectorstore, retriever

if "docs" not in st.session_state or "vectorstore" not in st.session_state:
    st.session_state.docs, st.session_state.vectorstore, st.session_state.retriever = init_vectorstore()

# ---------------------------------------
# App UI
# ---------------------------------------
st.title("LexMind - KI-Assistent für Juristen")
st.write(
    "Durchsuchen Sie juristische Vorlagen mit KI. Intelligent, schnell und präzise."
)

tab_suche, tab_dokumente = st.tabs(["Suche", "Dokumente"])

with tab_suche:
    search_tab.render()

with tab_dokumente:
    documents_tab.render(st.session_state.docs)
