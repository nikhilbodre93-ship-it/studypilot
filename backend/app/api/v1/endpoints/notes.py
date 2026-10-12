import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.topic import Topic
from app.models.note import Note
from app.api.v1.endpoints.auth import get_current_user
from app.llm.factory import get_llm_provider
from app.services.rag import retrieve_grounding_context
from app.services.quota import check_daily_quota
from prompts.v1.system import BASE_SYSTEM_INSTRUCTION
from prompts.v1.notes import GeneratedNotes, NOTES_PROMPT_TEMPLATE

logger = logging.getLogger("studypilot.notes")
router = APIRouter()


class NoteCreate(BaseModel):
    topic_id: int
    title: str
    content_markdown: str


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content_markdown: Optional[str] = None


class NoteGenerateRequest(BaseModel):
    topic_id: int
    academic_level: str = "Undergraduate / High School"
    custom_instructions: Optional[str] = None


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_note(
    req: NoteGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Quota check
    check_daily_quota(current_user.id, db)

    # Validate topic ownership
    topic = db.query(Topic).filter(Topic.id == req.topic_id).first()
    if not topic or topic.subject.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Topic not found or unauthorized")

    # Retrieve grounded context with citations
    context = retrieve_grounding_context(topic.id, query=topic.name, db=db, top_k=4)

    prompt = NOTES_PROMPT_TEMPLATE.format(
        topic_name=topic.name,
        level=req.academic_level,
        context=context
    )
    if req.custom_instructions:
        prompt += f"\nAdditional Student Instructions: {req.custom_instructions}"

    provider = get_llm_provider()
    try:
        gen_notes: GeneratedNotes = await provider.generate_structured(
            prompt=prompt,
            system_prompt=BASE_SYSTEM_INSTRUCTION,
            response_model=GeneratedNotes,
            user_id=current_user.id,
            feature_name="notes"
        )
    except Exception as e:
        logger.error(f"Note generation error: {e}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

    # Assemble structured markdown
    sections_md = []
    for s in gen_notes.sections:
        takeaways = "\n".join(f"- {t}" for t in s.key_takeaways)
        sections_md.append(f"## {s.heading}\n\n{s.content_markdown}\n\n**High-Yield Takeaways:**\n{takeaways}")

    citation_block = ""
    if gen_notes.citations:
        citation_block = "\n\n### Grounded Citations\n" + "\n".join(f"- {c}" for c in gen_notes.citations)

    warning_block = ""
    if gen_notes.not_in_context_warning:
        warning_block = f"\n\n> ⚠️ **Context Notice:** {gen_notes.not_in_context_warning}\n"

    full_markdown = (
        f"# {gen_notes.title}\n\n"
        f"> {gen_notes.summary}\n\n"
        f"{warning_block}"
        + "\n\n".join(sections_md)
        + citation_block
    )

    note = Note(
        topic_id=topic.id,
        user_id=current_user.id,
        title=gen_notes.title,
        content_markdown=full_markdown,
        is_ai_generated=True
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    return {
        "id": note.id,
        "topic_id": note.topic_id,
        "title": note.title,
        "content_markdown": note.content_markdown,
        "is_ai_generated": note.is_ai_generated,
        "created_at": note.created_at.isoformat(),
        "citations": gen_notes.citations
    }


@router.get("/")
def list_notes(
    topic_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Note).filter(Note.user_id == current_user.id)
    if topic_id:
        q = q.filter(Note.topic_id == topic_id)
    if search:
        q = q.filter(Note.title.ilike(f"%{search}%"))

    notes = q.order_by(Note.created_at.desc()).all()
    return [
        {
            "id": n.id,
            "topic_id": n.topic_id,
            "topic_name": n.topic.name if n.topic else "",
            "subject_name": n.topic.subject.name if n.topic and n.topic.subject else "",
            "title": n.title,
            "content_markdown": n.content_markdown,
            "is_ai_generated": n.is_ai_generated,
            "created_at": n.created_at.isoformat(),
            "updated_at": n.updated_at.isoformat()
        }
        for n in notes
    ]


@router.get("/{note_id}")
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {
        "id": note.id,
        "topic_id": note.topic_id,
        "topic_name": note.topic.name if note.topic else "",
        "title": note.title,
        "content_markdown": note.content_markdown,
        "is_ai_generated": note.is_ai_generated,
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat()
    }


@router.put("/{note_id}")
def update_note(
    note_id: int,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.content_markdown is not None:
        note.content_markdown = payload.content_markdown
    db.commit()
    db.refresh(note)
    return {
        "id": note.id,
        "topic_id": note.topic_id,
        "title": note.title,
        "content_markdown": note.content_markdown,
        "updated_at": note.updated_at.isoformat()
    }


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return None


@router.get("/{note_id}/export")
def export_note(
    note_id: int,
    format: str = Query("md", pattern="^(md|html|txt)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    safe_title = "".join(c for c in note.title if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")

    if format == "md":
        return Response(
            content=note.content_markdown,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{safe_title}.md"'}
        )
    elif format == "txt":
        return Response(
            content=note.content_markdown,
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="{safe_title}.txt"'}
        )
    else:  # html printable view
        html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{note.title}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 40px auto; line-height: 1.6; color: #1f2937; padding: 0 20px; }}
h1, h2, h3 {{ color: #2F5D46; }}
pre {{ background: #f3f4f6; padding: 12px; border-radius: 8px; }}
blockquote {{ border-left: 4px solid #2F5D46; padding-left: 16px; color: #4b5563; }}
</style>
</head>
<body>
<pre style="white-space: pre-wrap; font-family: inherit;">{note.content_markdown}</pre>
</body>
</html>"""
        return Response(
            content=html_content,
            media_type="text/html",
            headers={"Content-Disposition": f'inline; filename="{safe_title}.html"'}
        )
