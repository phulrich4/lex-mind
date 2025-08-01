import streamlit as st

def render():
    st.title("🔍 Suche")
    query = st.text_input("Was suchst du?", placeholder="z. B. Kapitalerhöhung, Abtretung, etc.")
    st.markdown("## Ergebnisse")
    st.markdown("---")
    for i in range(3):
        st.subheader(f"📄 Treffer {i + 1}")
        st.write("Beispielinhalt für die Trefferanzeige…")
        st.button("📥 Herunterladen", key=f"download_{i}")
        st.markdown("---")
