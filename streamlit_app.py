import streamlit as st
from tabs import search_tab, documents_tab

st.title("LexMind - KI-Assistent für Juristen")
st.write(
    "Let's start building! Hier entsteht grossartiges."
)

tab_suche, tab_dokumente = st.tabs(["Suche", "Dokumente"])

with tab_suche:
    suche.render()

with tab_dokumente:
    dokumente.render()
