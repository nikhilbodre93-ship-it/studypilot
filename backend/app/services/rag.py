import json
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.models.material import Material
from app.services.vector_store import global_vector_store

logger = logging.getLogger("studypilot.rag")


def retrieve_grounding_context(
    topic_id: int,
    query: str,
    db: Optional[Session] = None,
    top_k: int = 4
) -> str:
    """
    Retrieve grounded study material chunks for a topic with citations.
    Enforces strict data encapsulation against prompt injection.
    """
    # 1. Try in-memory vector store first
    chunks = global_vector_store.search(topic_id, query, top_k=top_k)

    # 2. If memory store empty and db session provided, load from materials table
    if not chunks and db:
        materials = db.query(Material).filter(Material.topic_id == topic_id).all()
        for mat in materials:
            if mat.extracted_text:
                try:
                    data = json.loads(mat.extracted_text)
                    if isinstance(data, dict) and "chunks" in data:
                        global_vector_store.add_chunks(topic_id, data["chunks"])
                except Exception:
                    # Stored as plain text
                    global_vector_store.add_chunks(topic_id, [{
                        "chunk_id": f"mat_{mat.id}",
                        "page": 1,
                        "citation": f"{mat.title} (Page 1)",
                        "text": mat.extracted_text[:2000]
                    }])
        chunks = global_vector_store.search(topic_id, query, top_k=top_k)

    if not chunks:
        return (
            "NOTE: No specific study materials have been uploaded for this topic yet. "
            "Please use standard accredited academic curriculum knowledge, but state clearly: "
            "'The user has not uploaded custom study material for this topic.'"
        )

    # 3. Format chunks with citations, strictly bounded as data
    formatted_chunks = []
    for ch in chunks:
        citation = ch.get("citation", f"Page {ch.get('page', 1)}")
        text = ch.get("text", "").strip()
        # Escape any accidental injection delimiters
        safe_text = text.replace("</STUDY_MATERIAL_CONTEXT>", "[SAFE_DELIMITER]")
        formatted_chunks.append(f"[{citation}]\n{safe_text}")

    return "\n\n---\n\n".join(formatted_chunks)
