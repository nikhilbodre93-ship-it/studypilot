import io
import pytest
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.llm_log import LLMUsageLog
from app.models.topic_mastery import TopicMastery
from app.llm.mock import MockLLMProvider
from app.llm.base import LLMError
from prompts.v1.notes import GeneratedNotes
from prompts.v1.system import BASE_SYSTEM_INSTRUCTION


def test_mock_llm_provider_structured():
    """Verify MockLLMProvider returns valid structured Pydantic object."""
    import asyncio
    provider = MockLLMProvider()
    res = asyncio.run(provider.generate_structured(
        prompt="Generate notes on Cell structure",
        system_prompt=BASE_SYSTEM_INSTRUCTION,
        response_model=GeneratedNotes,
        user_id=1,
        feature_name="notes"
    ))
    assert isinstance(res, GeneratedNotes)
    assert len(res.sections) > 0
    assert "Membrane" in res.sections[0].heading


def test_material_upload_and_status(client, auth_headers_a, db_session):
    # Setup subject and topic
    res_subj = client.post("/api/v1/subjects/", json={"name": "Neuroscience"}, headers=auth_headers_a)
    assert res_subj.status_code == 201
    subj_id = res_subj.json()["id"]

    res_topic = client.post(f"/api/v1/subjects/{subj_id}/topics/", json={"name": "Action Potentials", "difficulty": "medium"}, headers=auth_headers_a)
    assert res_topic.status_code == 201
    topic_id = res_topic.json()["id"]

    # Upload text material
    sample_text = b"Neurons communicate via electrical action potentials. Depolarization is mediated by voltage-gated sodium channels."
    files = {"file": ("action_potential.txt", io.BytesIO(sample_text), "text/plain")}
    data = {"topic_id": str(topic_id), "title": "Action Potential Handout"}

    upload_res = client.post("/api/v1/materials/upload", data=data, files=files, headers=auth_headers_a)
    assert upload_res.status_code == 201
    mat_id = upload_res.json()["id"]
    assert upload_res.json()["status"] == "completed"

    # Check status endpoint
    status_res = client.get(f"/api/v1/materials/{mat_id}/status", headers=auth_headers_a)
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "completed"
    assert status_res.json()["chunk_count"] >= 1


def test_notes_generation_and_export(client, auth_headers_a):
    # Setup subject and topic
    res_subj = client.post("/api/v1/subjects/", json={"name": "Biochemistry"}, headers=auth_headers_a)
    subj_id = res_subj.json()["id"]
    res_topic = client.post(f"/api/v1/subjects/{subj_id}/topics/", json={"name": "Enzymes", "difficulty": "hard"}, headers=auth_headers_a)
    topic_id = res_topic.json()["id"]

    # Generate note
    gen_res = client.post("/api/v1/notes/generate", json={"topic_id": topic_id}, headers=auth_headers_a)
    assert gen_res.status_code == 201
    note_data = gen_res.json()
    assert note_data["topic_id"] == topic_id
    assert "Enzyme" in note_data["content_markdown"] or "Cellular" in note_data["content_markdown"]

    note_id = note_data["id"]

    # List notes
    list_res = client.get(f"/api/v1/notes/?topic_id={topic_id}", headers=auth_headers_a)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # Export markdown
    export_res = client.get(f"/api/v1/notes/{note_id}/export?format=md", headers=auth_headers_a)
    assert export_res.status_code == 200
    assert "text/markdown" in export_res.headers["content-type"]


def test_quiz_generation_submission_and_mastery(client, auth_headers_a):
    res_subj = client.post("/api/v1/subjects/", json={"name": "Genetics"}, headers=auth_headers_a)
    subj_id = res_subj.json()["id"]
    res_topic = client.post(f"/api/v1/subjects/{subj_id}/topics/", json={"name": "Mendelian Laws", "difficulty": "easy"}, headers=auth_headers_a)
    topic_id = res_topic.json()["id"]

    # Generate quiz
    gen_res = client.post("/api/v1/quizzes/generate", json={
        "topic_id": topic_id,
        "count": 3,
        "difficulty": "medium",
        "question_types": ["multiple_choice", "true_false", "short_answer"]
    }, headers=auth_headers_a)
    assert gen_res.status_code == 201
    quiz_data = gen_res.json()
    assert len(quiz_data["questions"]) >= 1

    quiz_id = quiz_data["id"]

    # Submit quiz answers
    answers = [{"question_id": q["id"], "selected_answer": "Mitochondria" if q["question_type"] == "multiple_choice" else "False"} for q in quiz_data["questions"]]
    sub_res = client.post(f"/api/v1/quizzes/{quiz_id}/submit", json={"answers": answers}, headers=auth_headers_a)
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert "score" in sub_data
    assert "results" in sub_data
    assert len(sub_data["results"]) == len(quiz_data["questions"])

    # Verify BKT topic mastery updated
    mastery_res = client.get(f"/api/v1/mastery/topic/{topic_id}", headers=auth_headers_a)
    assert mastery_res.status_code == 200
    assert mastery_res.json()["review_count"] >= 1


def test_flashcards_generate_and_review(client, auth_headers_a):
    res_subj = client.post("/api/v1/subjects/", json={"name": "Physics"}, headers=auth_headers_a)
    subj_id = res_subj.json()["id"]
    res_topic = client.post(f"/api/v1/subjects/{subj_id}/topics/", json={"name": "Thermodynamics", "difficulty": "hard"}, headers=auth_headers_a)
    topic_id = res_topic.json()["id"]

    # Generate deck
    gen_res = client.post("/api/v1/flashcards/generate", json={"topic_id": topic_id, "count": 3}, headers=auth_headers_a)
    assert gen_res.status_code == 201
    deck_data = gen_res.json()
    assert len(deck_data["cards"]) >= 1

    card_id = deck_data["cards"][0]["id"]

    # Review card with rating 4 (Good)
    rev_res = client.post("/api/v1/flashcards/review", json={"flashcard_id": card_id, "rating": 4, "review_duration_ms": 1200}, headers=auth_headers_a)
    assert rev_res.status_code == 200
    rev_data = rev_res.json()
    assert rev_data["repetitions"] == 1
    assert rev_data["interval_days"] >= 1
    assert rev_data["is_correct"] is True


def test_question_paper_generation_and_evaluation(client, auth_headers_a):
    res_subj = client.post("/api/v1/subjects/", json={"name": "Calculus"}, headers=auth_headers_a)
    subj_id = res_subj.json()["id"]
    client.post(f"/api/v1/subjects/{subj_id}/topics/", json={"name": "Derivatives", "difficulty": "medium"}, headers=auth_headers_a)

    # Generate Question Paper
    gen_res = client.post("/api/v1/question-papers/generate", json={
        "subject_id": subj_id,
        "duration_minutes": 60,
        "total_marks": 100
    }, headers=auth_headers_a)
    assert gen_res.status_code == 201
    paper_data = gen_res.json()
    assert paper_data["total_marks"] == 100
    paper_id = paper_data["id"]

    # Evaluate attempt
    eval_res = client.post(f"/api/v1/question-papers/{paper_id}/evaluate", json={
        "answers": {
            "Q1": "Cell wall",
            "Q2": "ATP synthase uses proton gradient for phosphorylation",
            "Q3": "Fluid mosaic model describes membrane lipids and proteins"
        }
    }, headers=auth_headers_a)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert eval_data["total_marks_awarded"] > 0
    assert eval_data["percentage"] > 0


def test_roadmap_generation_and_toggle(client, auth_headers_a):
    res_subj = client.post("/api/v1/subjects/", json={"name": "Organic Chemistry"}, headers=auth_headers_a)
    subj_id = res_subj.json()["id"]
    client.post(f"/api/v1/subjects/{subj_id}/topics/", json={"name": "Alkanes", "difficulty": "easy"}, headers=auth_headers_a)

    gen_res = client.post("/api/v1/roadmap/generate", json={"subject_id": subj_id}, headers=auth_headers_a)
    assert gen_res.status_code == 201
    rd_data = gen_res.json()
    assert len(rd_data["roadmap"]["phases"]) >= 1

    first_task = rd_data["roadmap"]["phases"][0]["tasks"][0]
    task_id = first_task["id"]

    # Toggle task completed
    toggle_res = client.post(f"/api/v1/roadmap/subject/{subj_id}/toggle-task", json={"task_id": task_id, "completed": True}, headers=auth_headers_a)
    assert toggle_res.status_code == 200
    assert toggle_res.json()["completed"] is True


def test_tutor_chat_and_check_understanding(client, auth_headers_a):
    res_subj = client.post("/api/v1/subjects/", json={"name": "Ecology"}, headers=auth_headers_a)
    subj_id = res_subj.json()["id"]
    res_topic = client.post(f"/api/v1/subjects/{subj_id}/topics/", json={"name": "Biomes", "difficulty": "medium"}, headers=auth_headers_a)
    topic_id = res_topic.json()["id"]

    # Check understanding mini quiz
    cu_res = client.post("/api/v1/tutor/check-understanding", json={"topic_id": topic_id, "concept": "Tundra"}, headers=auth_headers_a)
    assert cu_res.status_code == 200
    cu_data = cu_res.json()
    assert "question_text" in cu_data
    assert "correct_answer" in cu_data

    # Test streaming chat endpoint
    chat_res = client.post("/api/v1/tutor/chat", json={"topic_id": topic_id, "message": "Explain how permafrost affects soil", "mode": "eli5"}, headers=auth_headers_a)
    assert chat_res.status_code == 200
    assert "text/event-stream" in chat_res.headers["content-type"]
    assert "data: " in chat_res.text
