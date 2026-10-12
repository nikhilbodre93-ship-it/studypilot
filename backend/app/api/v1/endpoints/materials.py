import os
import json
import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.topic import Topic
from app.models.material import Material
from app.api.v1.endpoints.auth import get_current_user
from app.services.ingestion import validate_file, process_material_ingestion

logger = logging.getLogger("studypilot.materials")
router = APIRouter()


def _run_background_ingest(material_id: int, topic_id: int, file_path: str, file_type: str):
    from app.database import SessionLocal
    try:
        summary = process_material_ingestion(material_id, topic_id, file_path, file_type)
        with SessionLocal() as db:
            mat = db.query(Material).filter(Material.id == material_id).first()
            if mat:
                mat.extracted_text = json.dumps({
                    "chunks": summary["chunks"],
                    "summary_text": summary["full_text"][:5000]
                })
                db.commit()
    except Exception as e:
        logger.error(f"Background ingestion failed for material {material_id}: {e}")


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_material(
    background_tasks: BackgroundTasks,
    topic_id: int = Form(...),
    title: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify topic exists and belongs to user
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic or topic.subject.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Topic not found or access denied")

    # Read bytes and validate
    file_bytes = await file.read()
    file_size = len(file_bytes)
    try:
        file_ext = validate_file(file.filename, file_size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save to disk
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    save_path = os.path.join(settings.STORAGE_DIR, unique_name)
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    material = Material(
        topic_id=topic_id,
        user_id=current_user.id,
        title=title or file.filename,
        file_name=file.filename,
        file_type=file_ext,
        file_size=file_size,
        storage_path=save_path,
        extracted_text=None
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    # Process ingestion synchronously for small files or trigger background
    try:
        summary = process_material_ingestion(material.id, topic_id, save_path, file_ext)
        material.extracted_text = json.dumps({
            "chunks": summary["chunks"],
            "summary_text": summary["full_text"][:5000]
        })
        db.commit()
        db.refresh(material)
    except Exception as e:
        logger.warning(f"Sync ingestion fallback to background: {e}")
        background_tasks.add_task(_run_background_ingest, material.id, topic_id, save_path, file_ext)

    return {
        "id": material.id,
        "topic_id": material.topic_id,
        "title": material.title,
        "file_name": material.file_name,
        "file_type": material.file_type,
        "file_size": material.file_size,
        "status": "completed" if material.extracted_text else "processing",
        "created_at": material.created_at.isoformat()
    }


@router.get("/topic/{topic_id}")
def list_materials_for_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic or topic.subject.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Topic not found or access denied")

    materials = db.query(Material).filter(
        Material.topic_id == topic_id,
        Material.user_id == current_user.id
    ).order_by(Material.created_at.desc()).all()

    return [
        {
            "id": m.id,
            "topic_id": m.topic_id,
            "title": m.title,
            "file_name": m.file_name,
            "file_type": m.file_type,
            "file_size": m.file_size,
            "status": "completed" if m.extracted_text else "processing",
            "created_at": m.created_at.isoformat()
        }
        for m in materials
    ]


@router.get("/{material_id}/status")
def get_material_status(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mat = db.query(Material).filter(
        Material.id == material_id,
        Material.user_id == current_user.id
    ).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material not found")

    is_done = bool(mat.extracted_text)
    chunk_count = 0
    if is_done:
        try:
            data = json.loads(mat.extracted_text)
            chunk_count = len(data.get("chunks", []))
        except Exception:
            chunk_count = 1

    return {
        "id": mat.id,
        "title": mat.title,
        "status": "completed" if is_done else "processing",
        "chunk_count": chunk_count,
        "file_size": mat.file_size
    }


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mat = db.query(Material).filter(
        Material.id == material_id,
        Material.user_id == current_user.id
    ).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material not found")

    if os.path.exists(mat.storage_path):
        try:
            os.remove(mat.storage_path)
        except Exception:
            pass

    db.delete(mat)
    db.commit()
    return None
