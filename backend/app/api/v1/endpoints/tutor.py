import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.tutor import TutorConversation, TutorMessage
from app.api.v1.endpoints.auth import get_current_user
from app.llm.factory import get_llm_provider
from app.services.rag import retrieve_grounding_context
from app.services.quota import check_daily_quota
from prompts.v1.system import BASE_SYSTEM_INSTRUCTION
from prompts.v1.quiz import GeneratedQuiz, QUIZ_PROMPT_TEMPLATE

logger = logging.getLogger("studypilot.tutor")
router = APIRouter()

TUTOR_SYSTEM_INSTRUCTION = """You are StudyPilot AI, an elite, patient, and highly knowledgeable academic tutor and pedagogical coach.
Your primary mission is to help the student deeply understand concepts, master their syllabus, solve problems, and excel in exams.

TEACHING & PEDAGOGICAL GUIDELINES:
1. Always give direct, accurate, and structured answers to the student's question.
2. Structure your explanations clearly:
   - Start with a clear, concise definition or direct answer.
   - Break down complex mechanisms, processes, or proofs into clear numbered steps or phases.
   - Use vivid real-world analogies, intuitive metaphors, and concrete examples.
   - Highlight key formulas, definitions, and common student misconceptions or exam traps.
   - End with a thought-provoking follow-up question or memory tip to verify understanding.
3. GROUNDING POLICY:
   - When study materials are provided in <STUDY_MATERIAL_CONTEXT>, prioritize them and cite relevant chapters, sections, or pages.
   - If the student's question is broader than the uploaded materials or if no custom materials have been uploaded, ALWAYS answer thoroughly and accurately using your comprehensive academic knowledge, while relating it back to the subject. Never refuse to explain a concept or claim you cannot answer.
4. Format your response cleanly using GitHub-flavored Markdown (clear section headings, bold key terms, clean bullet points, code blocks where applicable).
"""


class ChatMessageRequest(BaseModel):
    topic_id: Optional[int] = None
    message: str
    mode: str = Field(default="standard")  # standard | eli5 | deeper
    conversation_id: Optional[int] = None


class CheckUnderstandingRequest(BaseModel):
    topic_id: Optional[int] = None
    concept: Optional[str] = None


@router.post("/chat")
async def tutor_chat_stream(
    req: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_daily_quota(current_user.id, db)

    topic = None
    if req.topic_id:
        candidate = db.query(Topic).filter(Topic.id == req.topic_id).first()
        if candidate and candidate.subject and candidate.subject.user_id == current_user.id:
            topic = candidate

    if not topic:
        # Fallback to any user topic
        first_subject = db.query(Subject).filter(Subject.user_id == current_user.id).first()
        if first_subject:
            topic = db.query(Topic).filter(Topic.subject_id == first_subject.id).first()

    if not topic:
        # Create default General Studies workspace so tutor works out-of-the-box
        default_sub = Subject(
            user_id=current_user.id,
            name="General Studies",
            description="General coaching and Socratic tutoring workspace",
            color="#2F5D46"
        )
        db.add(default_sub)
        db.commit()
        db.refresh(default_sub)

        topic = Topic(
            subject_id=default_sub.id,
            name="General Concepts",
            description="Core topics and questions",
            difficulty="medium"
        )
        db.add(topic)
        db.commit()
        db.refresh(topic)

    # Locate or create conversation
    if req.conversation_id:
        conv = db.query(TutorConversation).filter(
            TutorConversation.id == req.conversation_id,
            TutorConversation.user_id == current_user.id
        ).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = TutorConversation(
            topic_id=topic.id,
            user_id=current_user.id,
            title=f"Tutoring: {topic.name} ({req.message[:30]}...)"
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # Save user message
    user_msg = TutorMessage(
        conversation_id=conv.id,
        sender="user",
        content=req.message
    )
    db.add(user_msg)
    db.commit()

    # Ground in topic material
    context = retrieve_grounding_context(topic.id, query=req.message, db=db, top_k=3)

    mode_instruction = ""
    if req.mode == "eli5":
        mode_instruction = "\nTUTORING MODE: Explain Like I'm 5 (ELI5). Use clear, intuitive metaphors, vivid real-world analogies, and simple everyday language without being condescending."
    elif req.mode == "deeper":
        mode_instruction = "\nTUTORING MODE: Deep Dive. Provide rigorous academic detail, underlying chemical/mathematical/physical principles, formal derivations or formulas, nuances, and common exam traps."

    subject_name = topic.subject.name if topic.subject else "General"
    system_prompt = (
        f"{TUTOR_SYSTEM_INSTRUCTION}\n"
        f"Subject: '{subject_name}' | Topic: '{topic.name}'.\n"
        f"{mode_instruction}\n"
        f"<STUDY_MATERIAL_CONTEXT>\n{context}\n</STUDY_MATERIAL_CONTEXT>"
    )

    # Fetch past messages in conversation for multi-turn conversational context
    history_records = db.query(TutorMessage).filter(
        TutorMessage.conversation_id == conv.id,
        TutorMessage.id != user_msg.id
    ).order_by(TutorMessage.created_at.asc()).all()[-10:]
    history = [{"role": m.sender, "content": m.content} for m in history_records]

    provider = get_llm_provider()

    async def sse_event_generator():
        yield f"data: {json.dumps({'type': 'conv_id', 'conversation_id': conv.id})}\n\n"
        collected_chunks = []
        try:
            async for token in provider.generate_stream(
                system_prompt=system_prompt,
                prompt=req.message,
                user_id=current_user.id,
                feature_name="tutor",
                history=history
            ):
                collected_chunks.append(token)
                yield f"data: {json.dumps({'type': 'token', 'text': token})}\n\n"

            # Save full assistant message
            full_response = "".join(collected_chunks)
            from app.database import SessionLocal
            with SessionLocal() as inner_db:
                asst_msg = TutorMessage(
                    conversation_id=conv.id,
                    sender="assistant",
                    content=full_response
                )
                inner_db.add(asst_msg)
                inner_db.commit()

            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(sse_event_generator(), media_type="text/event-stream")


@router.get("/conversations")
def list_conversations(
    topic_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(TutorConversation).filter(TutorConversation.user_id == current_user.id)
    if topic_id:
        q = q.filter(TutorConversation.topic_id == topic_id)
    convs = q.order_by(TutorConversation.updated_at.desc()).all()

    return [
        {
            "id": c.id,
            "topic_id": c.topic_id,
            "topic_name": c.topic.name if c.topic else "",
            "title": c.title,
            "message_count": len(c.messages),
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat()
        }
        for c in convs
    ]


@router.get("/conversations/{conversation_id}")
def get_conversation_history(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(TutorConversation).filter(
        TutorConversation.id == conversation_id,
        TutorConversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "id": conv.id,
        "topic_id": conv.topic_id,
        "title": conv.title,
        "messages": [
            {
                "id": m.id,
                "sender": m.sender,
                "content": m.content,
                "created_at": m.created_at.isoformat()
            }
            for m in conv.messages
        ]
    }


@router.post("/check-understanding")
async def check_understanding_mini_quiz(
    req: CheckUnderstandingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    topic = None
    if req.topic_id:
        candidate = db.query(Topic).filter(Topic.id == req.topic_id).first()
        if candidate and candidate.subject and candidate.subject.user_id == current_user.id:
            topic = candidate

    if not topic:
        first_subject = db.query(Subject).filter(Subject.user_id == current_user.id).first()
        if first_subject:
            topic = db.query(Topic).filter(Topic.subject_id == first_subject.id).first()

    if not topic:
        raise HTTPException(status_code=400, detail="Please create or select a topic first to run an understanding check.")

    query_str = req.concept or topic.name
    context = retrieve_grounding_context(topic.id, query=query_str, db=db, top_k=2)

    target_concept = f"{topic.name} ({req.concept})" if req.concept else topic.name
    prompt = QUIZ_PROMPT_TEMPLATE.format(
        topic_name=target_concept,
        count=1,
        difficulty="medium",
        question_types="multiple_choice",
        context=context
    )

    provider = get_llm_provider()
    try:
        gen_quiz: GeneratedQuiz = await provider.generate_structured(
            prompt=prompt,
            system_prompt=BASE_SYSTEM_INSTRUCTION,
            response_model=GeneratedQuiz,
            user_id=current_user.id,
            feature_name="tutor"
        )
    except Exception as e:
        logger.error(f"Check understanding error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate check: {str(e)}")

    q_item = gen_quiz.questions[0] if gen_quiz.questions else None
    if not q_item:
        raise HTTPException(status_code=500, detail="No question generated")

    return {
        "question_text": q_item.question_text,
        "options": q_item.options,
        "correct_answer": q_item.correct_answer,
        "explanation": q_item.explanation,
        "citation": q_item.citation
    }
