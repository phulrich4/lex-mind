import streamlit as st
from pages import suche, vorlagenueberischt

st.set_page_config(page_title="LexMind", layout="wide")

# Initiale Seitenwahl in session_state, falls noch nicht gesetzt
if "page" not in st.session_state:
    st.session_state.page = "Suche"  # Default-Seite

# Sidebar mit fixen Buttons für Navigation
with st.sidebar:
    st.markdown("## ⚖️LexMind")
    if st.button("🔍 Suche"):
        st.session_state.page = "Suche"
    if st.button("📚 Vorlagenübersicht"):
        st.session_state.page = "Vorlagenübersicht"

# Sidebar Navigation (schlicht mit Radio)
page = st.sidebar.button("Navigation", ["Suche", "Vorlagenübersicht"])

# Inhalt je nach Seite
if page == "Suche":
    suche_page.render()
elif page == "Vorlagenübersicht":
    vorlagen_page.render()

