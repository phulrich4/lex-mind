import streamlit as st
from pages import suche_page, bibliothek_page

st.set_page_config(page_title="LexMind", layout="wide")

# Sidebar Navigation
st.sidebar.title("⚖️ LexMind")
page = st.sidebar.radio("Navigation", ["Suche", "Bibliothek"])

# Hauptbereich – Inhalt pro Seite
if page == "Suche":
    suche_page.render()
elif page == "Bibliothek":
    bibliothek_page.render()
