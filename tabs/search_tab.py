import streamlit as st

def render():
    query = st.text_input("", placeholder= "z. B. Kapitalerhöhung, Abtretung, etc.")
    st.markdown("")
    for i in range(3):
        st.write(f"📄 Treffer {i+1} – Beispielinhalt ...")
        st.button("📥 Vorlage herunterladen", key=f"download_{i}")

