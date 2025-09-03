import streamlit as st
import pandas as pd

def render():
    st.header("Admin – Suchqueries")

    if not st.session_state.search_queries:
        st.info("Noch keine Suchanfragen vorhanden.")
        return

    df = pd.DataFrame(st.session_state.search_queries)
    st.dataframe(df, use_container_width=True)
