import streamlit as st

st.title("🔍 Juristische Vorlage finden")

query = st.text_input("Was suchst du?", placeholder="z. B. Kapitalerhöhung, Abtretung, etc.")

st.markdown("## Ergebnisse")
st.markdown("---")
for i in range(3):
    with st.container():
        st.subheader(f"📄 Treffer {i + 1} – [KATEGORIE]")
        st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit... **Kapitalerhöhung** ...")
        st.button("📥 Vorlage herunterladen", key=f"download_{i}")
        st.markdown("---")

