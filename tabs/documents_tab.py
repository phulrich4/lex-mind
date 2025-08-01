import streamlit as st

def render(docs):
    st.subheader("📚 Dokumentenübersicht")

import streamlit as st

def render():
    st.header("Dokumentenübersicht")
    st.write("Hier findest du alle juristischen Vorlagen.")
    for i in range(6):
        st.write(f"📄 Vorlage {i+1} – Vertrag")
        st.button("📥 Herunterladen", key=f"doc_download_{i}")

