import streamlit as st
from tabs import search_tab, documents_tab

st.title("LexMind - KI-Assistent für Juristen")
st.write(
    "Durchsuchen Sie juristische Vorlagen mit KI. Intelligent, schnell und präzise."
)

tab_suche, tab_dokumente = st.tabs(["Suche", "Dokumente"])

with tab_suche:
    search_tab.render()

with tab_dokumente:
    documents_tab.render()
