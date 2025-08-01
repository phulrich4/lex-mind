import streamlit as st

st.set_page_config(page_title="LexMind", layout="wide")

# Initiale Seitenwahl in session_state, falls noch nicht gesetzt
if "page" not in st.session_state:
    st.session_state.page = "Suche"  # Default-Seite

# Sidebar mit fixen Buttons für Navigation
with st.sidebar:
    st.markdown("## Navigation")
    if st.button("🔍 Suche"):
        st.session_state.page = "Suche"
    if st.button("📚 Vorlagenübersicht"):
        st.session_state.page = "Vorlagenübersicht"

# Seiteninhalt je nach ausgewählter Seite
if st.session_state.page == "Suche":
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

elif st.session_state.page == "Vorlagenübersicht":
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
