from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    subjects,
    topics,
    study_sessions,
    plan,
    revision,
    mastery,
    analytics,
    materials,
    notes,
    quizzes,
    flashcards,
    question_papers,
    roadmap,
    tutor,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["Subjects"])
api_router.include_router(topics.router, tags=["Topics"])
api_router.include_router(study_sessions.router, prefix="/study-sessions", tags=["Study Sessions"])
api_router.include_router(plan.router, prefix="/plan", tags=["Revision Plan"])
api_router.include_router(revision.router, prefix="/revision", tags=["Revision Queue & Priority"])
api_router.include_router(mastery.router, prefix="/mastery", tags=["Mastery & BKT"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(materials.router, prefix="/materials", tags=["Materials & Ingestion"])
api_router.include_router(notes.router, prefix="/notes", tags=["Study Notes"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["Practice Quizzes"])
api_router.include_router(flashcards.router, prefix="/flashcards", tags=["Flashcards & Spaced Repetition"])
api_router.include_router(question_papers.router, prefix="/question-papers", tags=["Exam Question Papers"])
api_router.include_router(roadmap.router, prefix="/roadmap", tags=["Learning Roadmap"])
api_router.include_router(tutor.router, prefix="/tutor", tags=["AI Tutor"])

