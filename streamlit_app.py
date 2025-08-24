import streamlit as st
import os
from tabs import search_tab, documents_tab
from utils.document_loader import load_documents_from_folder

# Fix: Wide Mode dauerhaft aktivieren
st.set_page_config(page_title="LexMind", layout="wide")
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


