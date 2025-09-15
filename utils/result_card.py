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
            text = pattern.sub(
                f"<span style='background-color:#FEF08A; border-radius:3px; padding:0 2px;'>{word}</span>",
                text
            )    

    return text


# -------------------------------
# Result Card Rendering
# -------------------------------
def render_result_card(doc, idx, query, embedding_model=None, score=None):
    file_path = doc.metadata.get("path")
    file_name = doc.metadata.get("source", "Dokument")
    category = doc.metadata.get("category", "–")

    # Dokumenttyp bestimmen
    doc_type = "PDF" if file_name.lower().endswith(".pdf") else "DOCX"

    # Titel
    title = f"### {file_name}"

    # Snippet
    snippet = doc.page_content[:300] + ("…" if len(doc.page_content) > 300 else "")
    if embedding_model:
        snippet = highlight_semantic_terms(snippet, query, embedding_model)
    else:
        for term in query.split():
            snippet = re.sub(
                f"(?i){re.escape(term)}",
                r'<span style="background-color: yellow;">\g<0></span>',
                snippet
            )

    with st.container():
        st.markdown(
            f"""
            <div style='border:1px solid #E5E7EB; border-radius:12px; padding:16px; margin-bottom:16px; background-color:white;'>
                {title}
                <p style="font-size:14px; color:#374151; margin-top:4px;">
                    Kategorie: <b>{category}</b> &nbsp; | &nbsp;
                    Score: <b>{score:.3f if score else "–"}</b> &nbsp; | &nbsp;
                    Typ: <b>{doc_type}</b>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        from streamlit.components.v1 import html
        html(f"""
            <div style='font-size:15px; line-height:1.5; 
                        padding:10px; background-color:#F9FAFB; 
                        border-radius:8px; margin:8px 0;'>
                {snippet}
            </div>
        """, height=180)

        # Download Button
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
