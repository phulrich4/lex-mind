import streamlit as st

st.title("Finden Sie die perfekte juristische Vorlage")

query = st.text_input("Durchsuchen Sie über 1.000 professionelle juristische Vorlagen mit semantischer Suche. Schnell, präzise und intelligent?", placeholder="Suchen Sie nach juristischen Begriffen oder Abschnitten...")

st.markdown("# Ergebnisse")
st.markdown("---")
for i in range(3):
    with st.container():
        st.subheader(f"📄 Treffer {i + 1} – [KATEGORIE]")
        st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit... **Kapitalerhöhung** ...")
        st.button("📥 Vorlage herunterladen", key=f"download_{i}")
        st.markdown("---")

