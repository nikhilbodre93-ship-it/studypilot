import json
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.question_paper import QuestionPaper
from app.api.v1.endpoints.auth import get_current_user
from app.llm.factory import get_llm_provider
from app.services.rag import retrieve_grounding_context
from app.services.quota import check_daily_quota
from prompts.v1.system import BASE_SYSTEM_INSTRUCTION
from prompts.v1.question_paper import GeneratedQuestionPaper, QUESTION_PAPER_PROMPT_TEMPLATE
from prompts.v1.grading import SubmissionEvaluationResult, GRADING_PROMPT_TEMPLATE

logger = logging.getLogger("studypilot.question_papers")
router = APIRouter()


class PaperGenerateRequest(BaseModel):
    subject_id: int
    duration_minutes: int = Field(default=60, ge=15, le=180)
    total_marks: int = Field(default=100, ge=20, le=200)
    exam_type: str = Field(default="mock_exam")


class PaperAttemptSubmission(BaseModel):
    answers: Dict[str, str] = Field(description="Map of question_id -> student answer text")


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_question_paper(
    req: PaperGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_daily_quota(current_user.id, db)

    subject = db.query(Subject).filter(Subject.id == req.subject_id, Subject.user_id == current_user.id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    topics_list = [t.name for t in subject.topics]
    combined_context_parts = []
    for t in subject.topics[:4]:
        c = retrieve_grounding_context(t.id, query=t.name, db=db, top_k=2)
        combined_context_parts.append(f"### Topic: {t.name}\n{c}")

    combined_context = "\n\n".join(combined_context_parts) if combined_context_parts else "Standard syllabus curriculum."

    prompt = QUESTION_PAPER_PROMPT_TEMPLATE.format(
        subject_name=subject.name,
        topics_list=", ".join(topics_list) if topics_list else "All subject core concepts",
        total_marks=req.total_marks,
        duration_minutes=req.duration_minutes,
        context=combined_context
    )

    provider = get_llm_provider()
    try:
        gen_paper: GeneratedQuestionPaper = await provider.generate_structured(
            prompt=prompt,
            system_prompt=BASE_SYSTEM_INSTRUCTION,
            response_model=GeneratedQuestionPaper,
            user_id=current_user.id,
            feature_name="exam"
        )
    except Exception as e:
        logger.error(f"Question paper generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate exam paper: {str(e)}")

    paper = QuestionPaper(
        subject_id=subject.id,
        user_id=current_user.id,
        title=gen_paper.title,
        exam_type=req.exam_type,
        duration_minutes=req.duration_minutes,
        total_marks=req.total_marks,
        content_json=gen_paper.model_dump_json()
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)

    return {
        "id": paper.id,
        "subject_id": paper.subject_id,
        "title": paper.title,
        "exam_type": paper.exam_type,
        "duration_minutes": paper.duration_minutes,
        "total_marks": paper.total_marks,
        "content": gen_paper.model_dump()
    }


@router.get("/")
def list_question_papers(
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(QuestionPaper).filter(QuestionPaper.user_id == current_user.id)
    if subject_id:
        q = q.filter(QuestionPaper.subject_id == subject_id)
    papers = q.order_by(QuestionPaper.created_at.desc()).all()

    return [
        {
            "id": p.id,
            "subject_id": p.subject_id,
            "subject_name": p.subject.name if p.subject else "",
            "title": p.title,
            "exam_type": p.exam_type,
            "duration_minutes": p.duration_minutes,
            "total_marks": p.total_marks,
            "created_at": p.created_at.isoformat()
        }
        for p in papers
    ]


@router.get("/{paper_id}")
def get_question_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    paper = db.query(QuestionPaper).filter(
        QuestionPaper.id == paper_id,
        QuestionPaper.user_id == current_user.id
    ).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Question paper not found")

    content = {}
    try:
        content = json.loads(paper.content_json)
    except Exception:
        pass

    return {
        "id": paper.id,
        "subject_id": paper.subject_id,
        "subject_name": paper.subject.name if paper.subject else "",
        "title": paper.title,
        "exam_type": paper.exam_type,
        "duration_minutes": paper.duration_minutes,
        "total_marks": paper.total_marks,
        "content": content,
        "created_at": paper.created_at.isoformat()
    }


@router.post("/{paper_id}/evaluate")
async def evaluate_paper_attempt(
    paper_id: int,
    submission: PaperAttemptSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    paper = db.query(QuestionPaper).filter(
        QuestionPaper.id == paper_id,
        QuestionPaper.user_id == current_user.id
    ).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Question paper not found")

    paper_data = json.loads(paper.content_json)
    # Collect all questions across sections
    all_questions = []
    for sec in paper_data.get("sections", []):
        for q in sec.get("questions", []):
            qid = q.get("id")
            student_ans = submission.answers.get(qid, "")
            all_questions.append({
                "question_id": qid,
                "question_text": q.get("question_text"),
                "marks": q.get("marks", 5),
                "model_answer": q.get("model_answer", ""),
                "rubric": q.get("rubric", ""),
                "student_answer": student_ans
            })

    provider = get_llm_provider()
    prompt = GRADING_PROMPT_TEMPLATE.format(submissions_json=json.dumps(all_questions))

    try:
        eval_result: SubmissionEvaluationResult = await provider.generate_structured(
            prompt=prompt,
            system_prompt=BASE_SYSTEM_INSTRUCTION,
            response_model=SubmissionEvaluationResult,
            user_id=current_user.id,
            feature_name="grading"
        )
    except Exception as e:
        logger.error(f"Paper evaluation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate exam: {str(e)}")

    return {
        "paper_id": paper.id,
        "title": paper.title,
        "total_marks_awarded": eval_result.total_marks_awarded,
        "total_max_marks": eval_result.total_max_marks,
        "percentage": eval_result.percentage,
        "summary_feedback": eval_result.summary_feedback,
        "question_evaluations": [ev.model_dump() for ev in eval_result.question_evaluations]
    }


@router.get("/{paper_id}/export/pdf")
def export_question_paper_pdf(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    paper = db.query(QuestionPaper).filter(
        QuestionPaper.id == paper_id,
        QuestionPaper.user_id == current_user.id
    ).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Question paper not found")

    data = json.loads(paper.content_json)

    sections_html = ""
    for sec in data.get("sections", []):
        q_html = ""
        for q in sec.get("questions", []):
            opts_html = ""
            if q.get("options"):
                opts_html = "<ol type='A'>" + "".join(f"<li>{opt}</li>" for opt in q["options"]) + "</ol>"
            q_html += f"""
            <div style="margin-bottom: 18px;">
                <p><strong>{q.get('id', 'Q')}.</strong> {q.get('question_text')} <span style="float:right; font-weight:bold;">[{q.get('marks')} Marks]</span></p>
                {opts_html}
            </div>
            """
        sections_html += f"""
        <div style="margin-top: 24px; border-bottom: 2px solid #2F5D46; padding-bottom: 12px;">
            <h3 style="color: #2F5D46;">{sec.get('name')}</h3>
            <p style="color: #666; font-style: italic;">{sec.get('description')} (Total Marks: {sec.get('total_marks')})</p>
            {q_html}
        </div>
        """

    instructions_html = "".join(f"<li>{ins}</li>" for ins in data.get("instructions", []))

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{paper.title}</title>
<style>
body {{ font-family: "Times New Roman", Times, serif; max-width: 850px; margin: 40px auto; padding: 0 20px; line-height: 1.5; color: #111; }}
.header {{ text-align: center; border-bottom: 3px double #2F5D46; padding-bottom: 16px; }}
.instructions {{ background: #fdfdfd; border: 1px solid #ccc; padding: 12px; margin: 20px 0; border-radius: 4px; }}
</style>
</head>
<body>
<div class="header">
    <h1 style="margin-bottom: 4px; color: #2F5D46;">{paper.title}</h1>
    <p><strong>Time Allowed:</strong> {paper.duration_minutes} Minutes &nbsp;|&nbsp; <strong>Maximum Marks:</strong> {paper.total_marks}</p>
</div>
<div class="instructions">
    <strong>Instructions to Candidates:</strong>
    <ol>{instructions_html}</ol>
</div>
{sections_html}
</body>
</html>"""

    return Response(
        content=html,
        media_type="text/html",
        headers={"Content-Disposition": f'inline; filename="{paper.title.replace(" ", "_")}.html"'}
    )
