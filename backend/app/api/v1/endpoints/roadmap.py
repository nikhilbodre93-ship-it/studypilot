import json
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.roadmap import Roadmap
from app.models.topic_mastery import TopicMastery
from app.api.v1.endpoints.auth import get_current_user
from app.llm.factory import get_llm_provider
from app.services.rag import retrieve_grounding_context
from app.services.quota import check_daily_quota
from prompts.v1.system import BASE_SYSTEM_INSTRUCTION
from prompts.v1.roadmap import GeneratedRoadmap, ROADMAP_PROMPT_TEMPLATE

logger = logging.getLogger("studypilot.roadmap")
router = APIRouter()


class RoadmapGenerateRequest(BaseModel):
    subject_id: int


class TaskToggleRequest(BaseModel):
    task_id: str
    completed: bool


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_or_regenerate_roadmap(
    req: RoadmapGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_daily_quota(current_user.id, db)

    subject = db.query(Subject).filter(Subject.id == req.subject_id, Subject.user_id == current_user.id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Gather mastery profile
    topics = db.query(Topic).filter(Topic.subject_id == subject.id).all()
    topics_summary_list = []
    mastery_profile_list = []
    for t in topics:
        topics_summary_list.append(f"- {t.name} (Difficulty: {t.difficulty})")
        m = db.query(TopicMastery).filter(TopicMastery.topic_id == t.id, TopicMastery.user_id == current_user.id).first()
        score = round(m.score * 100, 1) if m else 0.0
        mastery_profile_list.append(f"- {t.name}: {score}% mastery")

    combined_context_parts = []
    for t in topics[:3]:
        c = retrieve_grounding_context(t.id, query=t.name, db=db, top_k=2)
        combined_context_parts.append(f"### {t.name}\n{c}")
    context = "\n\n".join(combined_context_parts) if combined_context_parts else "Standard syllabus curriculum."

    prompt = ROADMAP_PROMPT_TEMPLATE.format(
        subject_name=subject.name,
        exam_date=subject.exam_date.isoformat() if subject.exam_date else "Not set",
        topics_summary="\n".join(topics_summary_list) if topics_summary_list else "None",
        mastery_profile="\n".join(mastery_profile_list) if mastery_profile_list else "All topics fresh (0% mastery)",
        context=context
    )

    provider = get_llm_provider()
    try:
        gen_roadmap: GeneratedRoadmap = await provider.generate_structured(
            prompt=prompt,
            system_prompt=BASE_SYSTEM_INSTRUCTION,
            response_model=GeneratedRoadmap,
            user_id=current_user.id,
            feature_name="roadmap"
        )
    except Exception as e:
        logger.error(f"Roadmap generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate roadmap: {str(e)}")

    existing = db.query(Roadmap).filter(Roadmap.subject_id == subject.id, Roadmap.user_id == current_user.id).first()
    if existing:
        existing.title = gen_roadmap.title
        existing.structure_json = gen_roadmap.model_dump_json()
        db.commit()
        db.refresh(existing)
        target_roadmap = existing
    else:
        new_roadmap = Roadmap(
            subject_id=subject.id,
            user_id=current_user.id,
            title=gen_roadmap.title,
            structure_json=gen_roadmap.model_dump_json()
        )
        db.add(new_roadmap)
        db.commit()
        db.refresh(new_roadmap)
        target_roadmap = new_roadmap

    return {
        "id": target_roadmap.id,
        "subject_id": target_roadmap.subject_id,
        "title": target_roadmap.title,
        "roadmap": gen_roadmap.model_dump()
    }


@router.get("/subject/{subject_id}")
def get_roadmap_by_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    roadmap = db.query(Roadmap).filter(Roadmap.subject_id == subject_id, Roadmap.user_id == current_user.id).first()
    if not roadmap:
        return {"roadmap": None}

    content = {}
    try:
        content = json.loads(roadmap.structure_json)
    except Exception:
        pass

    return {
        "id": roadmap.id,
        "subject_id": roadmap.subject_id,
        "title": roadmap.title,
        "roadmap": content,
        "created_at": roadmap.created_at.isoformat(),
        "updated_at": roadmap.updated_at.isoformat()
    }


@router.post("/subject/{subject_id}/toggle-task")
def toggle_roadmap_task(
    subject_id: int,
    req: TaskToggleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    roadmap = db.query(Roadmap).filter(Roadmap.subject_id == subject_id, Roadmap.user_id == current_user.id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    data = json.loads(roadmap.structure_json)
    found = False
    for phase in data.get("phases", []):
        for task in phase.get("tasks", []):
            if task.get("id") == req.task_id:
                task["completed"] = req.completed
                found = True
                break
        if found:
            break

    if not found:
        raise HTTPException(status_code=404, detail="Task ID not found in roadmap")

    roadmap.structure_json = json.dumps(data)
    db.commit()

    return {"status": "ok", "task_id": req.task_id, "completed": req.completed}
