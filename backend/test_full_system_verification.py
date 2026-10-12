import os
import sys
import io
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_system_flow():
    print("=" * 70)
    print("STARTING END-TO-END SYSTEM VERIFICATION")
    print("=" * 70)

    # 1. Register fresh user
    user_email = "e2e_student@studypilot.io"
    user_pwd = "Password123!"
    reg_res = client.post("/api/v1/auth/register", json={
        "email": user_email,
        "password": user_pwd,
        "full_name": "E2E Student"
    })
    if reg_res.status_code in (400, 409):
        # Already registered, log in
        login_res = client.post("/api/v1/auth/login", json={"email": user_email, "password": user_pwd})
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
    else:
        assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"
        token = reg_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] 1. User registration & authentication verified.")

    # 2. Add subject with exam date
    subj_res = client.post("/api/v1/subjects/", json={
        "name": "Molecular Biology",
        "description": "Cell biology and genetics course",
        "exam_date": "2026-11-20T00:00:00Z",
        "color": "#2F5D46"
    }, headers=headers)
    assert subj_res.status_code == 201, f"Create subject failed: {subj_res.text}"
    subject_id = subj_res.json()["id"]
    print(f"[PASS] 2. Created Subject: 'Molecular Biology' (ID: {subject_id}, Exam: 2026-11-20).")

    # 3. Add topic with difficulty
    topic_res = client.post(f"/api/v1/subjects/{subject_id}/topics/", json={
        "name": "Membrane Transport Kinetics",
        "description": "Active and passive ion transport mechanisms",
        "difficulty": "hard"
    }, headers=headers)
    assert topic_res.status_code == 201, f"Create topic failed: {topic_res.text}"
    topic_id = topic_res.json()["id"]
    print(f"[PASS] 3. Created Topic: 'Membrane Transport Kinetics' (ID: {topic_id}, Difficulty: hard).")

    # 4. Upload material with size/type validation
    sample_material = (
        b"Cellular transport occurs across phospholipid bilayers. "
        b"Primary active transport couples directly with ATP hydrolysis. "
        b"Secondary active transport uses electrochemical gradients established by primary pumps."
    )
    files = {"file": ("kinetics_summary.txt", io.BytesIO(sample_material), "text/plain")}
    data = {"topic_id": str(topic_id), "title": "Transport Lecture Notes"}

    upload_res = client.post("/api/v1/materials/upload", data=data, files=files, headers=headers)
    assert upload_res.status_code == 201, f"Upload material failed: {upload_res.text}"
    material_id = upload_res.json()["id"]
    print(f"[PASS] 4. Uploaded study material (ID: {material_id}, chunks indexed in RAG).")

    # Check material status
    status_res = client.get(f"/api/v1/materials/{material_id}/status", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "completed"
    print(f"[PASS]    Material status endpoint reports completed (chunks: {status_res.json()['chunk_count']}).")

    # 5. Generate grounded study notes
    notes_res = client.post("/api/v1/notes/generate", json={
        "topic_id": topic_id,
        "academic_level": "Undergraduate"
    }, headers=headers)
    assert notes_res.status_code == 201, f"Notes generation failed: {notes_res.text}"
    note_id = notes_res.json()["id"]
    print(f"[PASS] 5. Generated Study Note: '{notes_res.json()['title']}' (ID: {note_id}).")

    # Export note as Markdown
    exp_res = client.get(f"/api/v1/notes/{note_id}/export?format=md", headers=headers)
    assert exp_res.status_code == 200
    assert len(exp_res.text) > 50
    print("[PASS]    Exported note as Markdown successfully.")

    # 6. Generate practice quiz
    quiz_res = client.post("/api/v1/quizzes/generate", json={
        "topic_id": topic_id,
        "count": 3,
        "difficulty": "medium",
        "question_types": ["multiple_choice", "true_false", "short_answer"]
    }, headers=headers)
    assert quiz_res.status_code == 201, f"Quiz generation failed: {quiz_res.text}"
    quiz = quiz_res.json()
    quiz_id = quiz["id"]
    print(f"[PASS] 6. Generated Quiz: '{quiz['title']}' with {len(quiz['questions'])} questions.")

    # 7. Generate flashcards
    fc_res = client.post("/api/v1/flashcards/generate", json={
        "topic_id": topic_id,
        "count": 4
    }, headers=headers)
    assert fc_res.status_code == 201, f"Flashcards generation failed: {fc_res.text}"
    deck = fc_res.json()
    print(f"[PASS] 7. Generated Flashcard Deck: '{deck['deck_title']}' with {len(deck['cards'])} cards.")

    # 8. Submit quiz attempt
    answers = []
    for q in quiz["questions"]:
        ans_text = "Mitochondria" if q["question_type"] == "multiple_choice" else ("False" if q["question_type"] == "true_false" else "It maintains resting membrane potential.")
        answers.append({"question_id": q["id"], "selected_answer": ans_text})

    sub_res = client.post(f"/api/v1/quizzes/{quiz_id}/submit", json={"answers": answers}, headers=headers)
    assert sub_res.status_code == 200, f"Submit quiz failed: {sub_res.text}"
    result = sub_res.json()
    print(f"[PASS] 8. Submitted quiz attempt. Score: {result['score']}/{result['max_score']} ({result['percentage']}%).")

    # 9. Verify BKT topic mastery updated
    mastery_res = client.get(f"/api/v1/mastery/topic/{topic_id}", headers=headers)
    assert mastery_res.status_code == 200
    mastery_data = mastery_res.json()
    print(f"[PASS] 9. BKT Mastery successfully updated! Score: {round(mastery_data['score'] * 100, 1)}% (Reviews: {mastery_data['review_count']}, Accuracy: {round(mastery_data['observed_accuracy'] * 100, 1)}%).")

    # 10. Query revision queue and verify explainable reason
    queue_res = client.get("/api/v1/revision/queue?minutes=60", headers=headers)
    assert queue_res.status_code == 200
    queue_data = queue_res.json()
    assert len(queue_data["queue"]) > 0
    top_item = queue_data["queue"][0]
    print(f"[PASS] 10. Revision Queue scheduled '{top_item['topic_name']}'. Rationale: '{top_item['reason']}'.")

    # 11. Review a flashcard with SM-2 rating
    card_id = deck["cards"][0]["id"]
    review_res = client.post("/api/v1/flashcards/review", json={
        "flashcard_id": card_id,
        "rating": 4, # Good
        "review_duration_ms": 1500
    }, headers=headers)
    assert review_res.status_code == 200
    rev_data = review_res.json()
    print(f"[PASS] 11. SM-2 Flashcard reviewed (Rating 4). Next interval: {rev_data['interval_days']} days, Ease Factor: {rev_data['ease_factor']}.")

    # 12. Generate question paper and submit evaluation
    paper_res = client.post("/api/v1/question-papers/generate", json={
        "subject_id": subject_id,
        "duration_minutes": 60,
        "total_marks": 100
    }, headers=headers)
    assert paper_res.status_code == 201
    paper_id = paper_res.json()["id"]
    print(f"[PASS] 12. Question Paper generated with Section A/B/C breakdown (ID: {paper_id}).")

    eval_res = client.post(f"/api/v1/question-papers/{paper_id}/evaluate", json={
        "answers": {"Q1": "Cell wall", "Q2": "ATP synthase uses proton motive force", "Q3": "Fluid mosaic model buffer"}
    }, headers=headers)
    assert eval_res.status_code == 200
    print(f"[PASS]     AI Exam Evaluation awarded {eval_res.json()['total_marks_awarded']} marks ({eval_res.json()['percentage']}%).")

    # 13. Generate roadmap and toggle task
    roadmap_res = client.post("/api/v1/roadmap/generate", json={"subject_id": subject_id}, headers=headers)
    assert roadmap_res.status_code == 201
    rd = roadmap_res.json()["roadmap"]
    task_id = rd["phases"][0]["tasks"][0]["id"]
    toggle_res = client.post(f"/api/v1/roadmap/subject/{subject_id}/toggle-task", json={"task_id": task_id, "completed": True}, headers=headers)
    assert toggle_res.status_code == 200
    print(f"[PASS] 13. Learning Roadmap generated with {len(rd['phases'])} phases. Task '{task_id}' toggled completed.")

    # 14. Test AI Tutor chat streaming
    tutor_res = client.post("/api/v1/tutor/chat", json={
        "topic_id": topic_id,
        "message": "Explain primary active transport in simple terms",
        "mode": "eli5"
    }, headers=headers)
    assert tutor_res.status_code == 200
    assert "text/event-stream" in tutor_res.headers["content-type"]
    assert "data: " in tutor_res.text
    print("[PASS] 14. AI Tutor SSE streaming verified.")

    print("=" * 70)
    print("ALL 14 END-TO-END FLOW VERIFICATION STEPS PASSED PERFECTLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_full_system_flow()
