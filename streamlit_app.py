import streamlit as st
from tabs import search_tab, documents_tab

st.title("LexMind - KI-Assistent für Juristen")
st.write(
    "Durchsuchen Sie über 1.000 professionelle juristische Vorlagen mit semantischer Suche. Intelligent, schnell und präzise."
)

tab_suche, tab_dokumente = st.tabs(["Suche", "Dokumente"])

with tab_suche:
    suche.render()

with tab_dokumente:
    dokumente.render()
