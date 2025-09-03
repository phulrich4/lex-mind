# utils/result_card.py

import streamlit as st
import re
import os
from sklearn.metrics.pairwise import cosine_similarity


# -------------------------------
# Semantisches Highlighting
# -------------------------------
def highlight_semantic_terms(text, query, embedding_model, threshold=0.7):
    STOPWORDS = {
        "ein", "eine", "einer", "der", "die", "das", "und", "oder", "für", "mit", "in",
        "auf", "von", "zu", "zur", "vom", "den", "des", "am", "im", "aus", "an", "dem",
        "ist", "es", "sind", "dass", "welche", "das", "dies", "diese", "dieser", "dieses",
        "etc", "sofern", "wenn", "wie", "auch"
    }

    words = list(set(re.findall(r'\b\w{4,}\b', text)))
    words_filtered = [w for w in words if w.lower() not in STOPWORDS]

    if not words_filtered:
        return text

    query_embedding = embedding_model.embed_query(query)
    word_embeddings = embedding_model.client.encode(words_filtered)

    similarities = cosine_similarity([query_embedding], word_embeddings)[0]

    for word, sim in zip(words_filtered, similarities):
        if sim >= threshold:
            pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
            text = pattern.sub(f"<mark>{word}</mark>", text)

    return text


# -------------------------------
# Result Card Rendering
# -------------------------------
def render_result_card(doc, idx, query, embedding_model=None):
    """
    Zeigt einen Suchtreffer im Karten-Design inkl. semantischem Highlighting,
    Dateiname, Kategorie, Jahr und Download-Option.
    """
    # Metadaten holen
    file_path = doc.metadata.get("path")  # vollständiger Pfad (falls vorhanden)
    file_name = doc.metadata.get("source", "Dokument")  # nur Dateiname
    page = doc.metadata.get("page", None)
    heading = doc.metadata.get("heading", None)
    category = doc.metadata.get("category", "–")
    year = doc.metadata.get("year", "–")

    # Titelzeile
    title_parts = [f"**{file_name}**"]
    if page:
        title_parts.append(f"(Seite {page})")
    if heading and heading != "–":
        title_parts.append(f"– {heading}")
    title = " ".join(title_parts)

    # Snippet bauen
    snippet = doc.page_content[:250] + ("…" if len(doc.page_content) > 250 else "")
    if embedding_model:
        snippet = highlight_semantic_terms(snippet, query, embedding_model)
    else:
        for term in query.split():
            snippet = re.sub(
                f"(?i){re.escape(term)}",
                r'<span style="background-color: yellow;">\g<0></span>',
                snippet
            )

    # Rendering
    with st.container():
        st.markdown("---")  # Trenner
        st.markdown(f"### {title}")

        # Badges
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown(
                f"<span style='background-color:#E5E7EB; padding:3px 8px; border-radius:8px;'>{category}</span>",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"<span style='background-color:#F87171; padding:3px 8px; border-radius:8px;'>PDF/DOCX</span>",
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                f"<span style='background-color:#BFDBFE; padding:3px 8px; border-radius:8px;'>{year}</span>",
                unsafe_allow_html=True
            )

        # Snippet anzeigen
        # st.markdown(f"<p style='color:#374151;'>{snippet}</p>", unsafe_allow_html=True)

        # HTML Snippet anzeigen über st.components
        from streamlit.components.v1 import html
        html(f"<div style='font-size: 16px; line-height: 1.4;'>{snippet}</div>", height=200)

        # Download-Button
        if file_path and os.path.exists(file_path):
            mime = "application/pdf" if file_name.endswith(".pdf") else \
                   "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"📥 {file_name} herunterladen",
                    data=f,
                    file_name=file_name,
                    mime=mime,
                    key=f"download-{idx}-{file_name}"
                )
