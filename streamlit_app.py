import streamlit as st
import os
from tabs import search_tab, documents_tab
from utils.document_loader import load_documents_from_folder
from utils.search import load_or_create_vectorstore, HybridRetriever
from langchain.embeddings import SentenceTransformerEmbeddings

# Page Config
st.set_page_config(page_title="LexMind", layout="wide")

# Pfad zu Dokumenten
DOCS_PATH = "docs/"

# Indexierung + Docs nur einmal pro Session laden
@st.cache_resource
def init_vectorstore():
    """Lädt Dokumente und erstellt den Vectorstore nur 1x pro Session."""
    if not os.path.exists(DOCS_PATH):
        st.warning(f"Dokumentenordner '{DOCS_PATH}' nicht gefunden.")
        return [], None
    docs = load_documents_from_folder(DOCS_PATH)
    vectorstore = load_or_create_vectorstore(docs)
    return docs, vectorstore

# Initialisieren der Docs und Vectorstore in Session State
if "docs" not in st.session_state or "vectorstore" not in st.session_state:
    st.session_state.docs, st.session_state.vectorstore = init_vectorstore()
    if st.session_state.vectorstore is not None:
        # Embedding-Modell erstellen
        embedding_model = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
        # HybridRetriever korrekt initialisieren
        st.session_state.retriever = HybridRetriever(
            faiss_index=st.session_state.vectorstore,
            texts=st.session_state.docs,
            embedding_model=embedding_model
        )
    else:
        st.session_state.retriever = None

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
