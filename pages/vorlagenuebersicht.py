import streamlit as st

def render():
    st.title("📚 Übersicht aller Vorlagen")

    col1, col2 = st.columns([2, 1])
    with col1:
        search_input = st.text_input("Vorlagen durchsuchen", placeholder="z. B. Arbeitsvertrag")
    with col2:
        category = st.selectbox("Kategorie", ["Alle", "Vertrag", "Urkunde", "Andere"])

    st.markdown("---")

    for i in range(6):
        with st.container():
            st.markdown(f"**📄 Vorlage {i + 1}** – Vertrag")
            st.write("Beispielinhalt der juristischen Vorlage…")
            st.button("📥 Herunterladen", key=f"lib_download_{i}")
            st.markdown("---")
