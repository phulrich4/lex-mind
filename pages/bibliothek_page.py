import streamlit as st

def render():
    st.title("📚 Bibliothek")
    st.write("Hier findest du alle juristischen Vorlagen.")
    st.markdown("---")
    for i in range(6):
        st.markdown(f"**📄 Vorlage {i + 1}** – Vertrag")
        st.write("Beispielinhalt der Vorlage …")
        st.button("📥 Herunterladen", key=f"lib_{i}")
        st.markdown("---")
