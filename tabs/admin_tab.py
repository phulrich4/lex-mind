# tabs/admin_tab.py
import streamlit as st
import pandas as pd

def render():
    st.header("Admin – Suchanfragen")

    if not st.session_state.search_queries:
        st.info("Noch keine Suchanfragen vorhanden.")
        return

    df = pd.DataFrame(st.session_state.search_queries)
    st.dataframe(df, use_container_width=True)

    # Optional: Export als CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Export als CSV", data=csv, file_name="search_queries.csv", mime="text/csv")
