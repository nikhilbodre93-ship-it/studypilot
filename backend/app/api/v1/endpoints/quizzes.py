import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.topic import Topic
from app.models.quiz import Quiz, Question, QuizAttempt, AttemptAnswer
from app.api.v1.endpoints.auth import get_current_user
from app.llm.factory import get_llm_provider
from app.services.rag import retrieve_grounding_context
from app.services.quota import check_daily_quota
from app.core.bkt import record_topic_evidence
from prompts.v1.system import BASE_SYSTEM_INSTRUCTION
from prompts.v1.quiz import GeneratedQuiz, QUIZ_PROMPT_TEMPLATE
from prompts.v1.grading import SubmissionEvaluationResult, GRADING_PROMPT_TEMPLATE

logger = logging.getLogger("studypilot.quizzes")
router = APIRouter()


class QuizGenerateRequest(BaseModel):
    topic_id: int
    count: int = Field(default=5, ge=1, le=20)
    difficulty: str = Field(default="medium")
    question_types: List[str] = Field(default=["multiple_choice", "true_false", "short_answer"])


class AnswerSubmission(BaseModel):
    question_id: int
    selected_answer: str


class QuizSubmitRequest(BaseModel):
    answers: List[AnswerSubmission]


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    req: QuizGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_daily_quota(current_user.id, db)

    topic = db.query(Topic).filter(Topic.id == req.topic_id).first()
    if not topic or topic.subject.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Topic not found or unauthorized")

    context = retrieve_grounding_context(topic.id, query=f"{topic.name} quiz questions", db=db, top_k=4)

    prompt = QUIZ_PROMPT_TEMPLATE.format(
        topic_name=topic.name,
        count=req.count,
        difficulty=req.difficulty,
        question_types=", ".join(req.question_types),
        context=context
    )

    provider = get_llm_provider()
    try:
        gen_quiz: GeneratedQuiz = await provider.generate_structured(
            prompt=prompt,
            system_prompt=BASE_SYSTEM_INSTRUCTION,
            response_model=GeneratedQuiz,
            user_id=current_user.id,
            feature_name="quiz"
        )
    except Exception as e:
        logger.error(f"Quiz generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

    quiz = Quiz(
        topic_id=topic.id,
        user_id=current_user.id,
        title=gen_quiz.title,
        total_questions=len(gen_quiz.questions)
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    for idx, q_data in enumerate(gen_quiz.questions):
        question = Question(
            quiz_id=quiz.id,
            question_text=q_data.question_text,
            question_type=q_data.question_type,
            options_json=json.dumps(q_data.options) if q_data.options else None,
            correct_answer=q_data.correct_answer,
            explanation=q_data.explanation,
            order_index=idx
        )
        db.add(question)

    db.commit()

    return {
        "id": quiz.id,
        "topic_id": quiz.topic_id,
        "title": quiz.title,
        "total_questions": quiz.total_questions,
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "options": json.loads(q.options_json) if q.options_json else None,
                "order_index": q.order_index
            }
            for q in quiz.questions
        ]
    }


@router.get("/")
def list_quizzes(
    topic_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Quiz).filter(Quiz.user_id == current_user.id)
    if topic_id:
        q = q.filter(Quiz.topic_id == topic_id)
    quizzes = q.order_by(Quiz.created_at.desc()).all()

    return [
        {
            "id": qz.id,
            "topic_id": qz.topic_id,
            "topic_name": qz.topic.name if qz.topic else "",
            "subject_name": qz.topic.subject.name if qz.topic and qz.topic.subject else "",
            "title": qz.title,
            "total_questions": qz.total_questions,
            "created_at": qz.created_at.isoformat()
        }
        for qz in quizzes
    ]


@router.get("/{quiz_id}")
def get_quiz_details(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return {
        "id": quiz.id,
        "topic_id": quiz.topic_id,
        "topic_name": quiz.topic.name if quiz.topic else "",
        "subject_name": quiz.topic.subject.name if quiz.topic and quiz.topic.subject else "",
        "title": quiz.title,
        "total_questions": quiz.total_questions,
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "options": json.loads(q.options_json) if q.options_json else None,
                "order_index": q.order_index
            }
            for q in quiz.questions
        ]
    }


@router.post("/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: int,
    submission: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions_by_id = {q.id: q for q in quiz.questions}
    submitted_dict = {a.question_id: a.selected_answer.strip() for a in submission.answers}

    total_score = 0.0
    max_score = float(len(quiz.questions))
    results = []

    # Identify short answer questions needing AI grading
    short_answers_to_grade = []
    for q in quiz.questions:
        user_ans = submitted_dict.get(q.id, "")
        if q.question_type == "short_answer" and user_ans:
            short_answers_to_grade.append({
                "question_id": str(q.id),
                "question_text": q.question_text,
                "correct_answer": q.correct_answer,
                "student_answer": user_ans,
                "max_marks": 1.0
            })

    # Call AI grading for short answers if present
    ai_evaluations: Dict[str, Any] = {}
    if short_answers_to_grade:
        try:
            provider = get_llm_provider()
            prompt = GRADING_PROMPT_TEMPLATE.format(submissions_json=json.dumps(short_answers_to_grade))
            eval_result: SubmissionEvaluationResult = await provider.generate_structured(
                prompt=prompt,
                system_prompt=BASE_SYSTEM_INSTRUCTION,
                response_model=SubmissionEvaluationResult,
                user_id=current_user.id,
                feature_name="grading"
            )
            for q_eval in eval_result.question_evaluations:
                ai_evaluations[q_eval.question_id] = q_eval
        except Exception as e:
            logger.warning(f"AI grading fallback to exact match: {e}")

    # Evaluate each question
    attempt = QuizAttempt(
        quiz_id=quiz.id,
        user_id=current_user.id,
        score=0.0,
        max_score=max_score,
        completed_at=datetime.now(timezone.utc)
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    for q in quiz.questions:
        user_ans = submitted_dict.get(q.id, "")
        is_correct = False
        feedback = q.explanation or ""

        if q.question_type in ("multiple_choice", "true_false"):
            is_correct = (user_ans.lower() == q.correct_answer.lower())
        elif q.question_type == "short_answer":
            if str(q.id) in ai_evaluations:
                ev = ai_evaluations[str(q.id)]
                is_correct = ev.is_correct
                feedback = ev.feedback
            else:
                is_correct = (user_ans.lower() == q.correct_answer.lower())

        if is_correct:
            total_score += 1.0

        ans_record = AttemptAnswer(
            attempt_id=attempt.id,
            question_id=q.id,
            selected_answer=user_ans,
            is_correct=is_correct
        )
        db.add(ans_record)

        # Update topic mastery via Bayesian Knowledge Tracing!
        record_topic_evidence(
            db=db,
            user_id=current_user.id,
            topic_id=quiz.topic_id,
            is_correct=is_correct
        )

        results.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "selected_answer": user_ans,
            "correct_answer": q.correct_answer,
            "is_correct": is_correct,
            "explanation": feedback
        })

    attempt.score = total_score
    db.commit()

    return {
        "attempt_id": attempt.id,
        "score": total_score,
        "max_score": max_score,
        "percentage": round((total_score / max_score) * 100, 1) if max_score > 0 else 0,
        "completed_at": attempt.completed_at.isoformat(),
        "results": results
    }


@router.get("/history/all")
def get_recent_attempts(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id
    ).order_by(QuizAttempt.created_at.desc()).limit(limit).all()

    return [
        {
            "id": a.id,
            "quiz_id": a.quiz_id,
            "quiz_title": a.quiz.title if a.quiz else "",
            "topic_name": a.quiz.topic.name if a.quiz and a.quiz.topic else "",
            "score": a.score,
            "max_score": a.max_score,
            "percentage": round((a.score / a.max_score) * 100, 1) if a.max_score > 0 else 0,
            "created_at": a.created_at.isoformat()
        }
        for a in attempts
    ]
