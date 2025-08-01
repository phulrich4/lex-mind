import streamlit as st

# Streamlit-Konfiguration
st.set_page_config(page_title="LexMind", layout="wide")

# Seitenwahl im Sidebar-Menü
page = st.sidebar.selectbox("Navigation", ["🔍 Suche", "📚 Vorlagenübersicht"])

# --------------------------------------------
# 🔍 Suche – mit Platzhalter-Ergebnissen
# --------------------------------------------
if page == "🔍 Suche":
    st.title("🔍 Juristische Vorlage finden")

    # Suchfeld
    query = st.text_input("Was suchst du?", placeholder="z. B. Kapitalerhöhung, Abtretung, etc.")

    # Platzhalter für Trefferliste
    st.markdown("## Ergebnisse")
    st.markdown("---")
    for i in range(3):  # Drei Beispiel-Treffer
        with st.container():
            st.subheader(f"📄 Treffer {i + 1} – [KATEGORIE]")
            st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit... **Kapitalerhöhung** ...")
            st.button("📥 Vorlage herunterladen", key=f"download_{i}")
            st.markdown("---")

# --------------------------------------------
# 📚 Vorlagenübersicht – mit Filter & Liste
# --------------------------------------------
elif page == "📚 Vorlagenübersicht":
    st.title("📚 Übersicht aller Vorlagen")

    # Filter: Suchfeld + Kategorieauswahl
    col1, col2 = st.columns([2, 1])
    with col1:
        search_input = st.text_input("Vorlagen durchsuchen", placeholder="z. B. Arbeitsvertrag")
    with col2:
        category = st.selectbox("Kategorie", ["Alle", "Vertrag", "Urkunde", "Andere"])

    st.markdown("---")

    # Platzhalter-Vorlagenliste
    for i in range(6):  # Sechs Beispiel-Vorlagen
        with st.container():
            st.markdown(f"**📄 Vorlage {i + 1}** – Vertrag")
            st.write("Beispielinhalt der juristischen Vorlage…")
            st.button("📥 Herunterladen", key=f"lib_download_{i}")
            st.markdown("---")
