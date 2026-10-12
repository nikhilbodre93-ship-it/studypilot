from datetime import date, timedelta
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.flashcard import Flashcard
from app.models.study_session import StudySession


def test_mastery_record_quiz_and_card_endpoints(client, auth_headers_a, db_session, user_a):
    subject = Subject(user_id=user_a.id, name="Computer Systems")
    db_session.add(subject)
    db_session.commit()

    topic = Topic(subject_id=subject.id, name="Cache Memory", difficulty="hard")
    db_session.add(topic)
    db_session.commit()

    card = Flashcard(
        topic_id=topic.id,
        user_id=user_a.id,
        front="What is L1 Cache?",
        back="Fastest on-chip memory directly adjacent to CPU core.",
    )
    db_session.add(card)
    db_session.commit()

    # 1. Record Quiz Answer (Correct)
    quiz_res = client.post(
        "/api/v1/mastery/record",
        headers=auth_headers_a,
        json={
            "topic_id": topic.id,
            "event_type": "quiz_answer",
            "is_correct": True,
        }
    )
    assert quiz_res.status_code == 200
    q_data = quiz_res.json()
    assert q_data["new_mastery_score"] > 20.0
    assert q_data["observed_correct"] == 1
    assert q_data["observed_total"] == 1
    assert q_data["observed_accuracy"] == 1.0

    # 2. Record Flashcard Rating (4)
    card_res = client.post(
        "/api/v1/mastery/record",
        headers=auth_headers_a,
        json={
            "topic_id": topic.id,
            "event_type": "card_rating",
            "rating": 4,
            "flashcard_id": card.id,
            "review_duration_ms": 3200,
        }
    )
    assert card_res.status_code == 200
    c_data = card_res.json()
    assert c_data["observed_total"] == 2
    assert c_data["card_id"] == card.id
    assert c_data["card_repetitions"] == 1
    assert c_data["card_interval_days"] == 1
    assert c_data["card_due_date"] is not None


def test_revision_queue_and_explain_endpoints(client, auth_headers_a, db_session, user_a):
    subject = Subject(user_id=user_a.id, name="Biology", exam_date=date.today() + timedelta(days=5))
    db_session.add(subject)
    db_session.commit()

    topic = Topic(subject_id=subject.id, name="Genetics", difficulty="hard")
    db_session.add(topic)
    db_session.commit()

    # 1. Revision Queue
    queue_res = client.get("/api/v1/revision/queue?minutes=60", headers=auth_headers_a)
    assert queue_res.status_code == 200
    q_data = queue_res.json()
    assert q_data["available_minutes"] == 60
    assert q_data["sessions_count"] >= 1
    assert q_data["is_exam_mode_active"] is True

    # 2. Explain Topic Priority
    explain_res = client.get(f"/api/v1/revision/explain/{topic.id}", headers=auth_headers_a)
    assert explain_res.status_code == 200
    ex_data = explain_res.json()
    assert ex_data["topic_id"] == topic.id
    assert ex_data["priority_score"] > 0
    assert "components" in ex_data
    assert "reason" in ex_data
    assert "Genetics" in ex_data["topic_name"]


def test_plan_generate_schedule_and_patch(client, auth_headers_a, db_session, user_a):
    subject = Subject(user_id=user_a.id, name="Linear Algebra", exam_date=date.today() + timedelta(days=7))
    db_session.add(subject)
    db_session.commit()

    topic = Topic(subject_id=subject.id, name="Eigenvalues", difficulty="medium")
    db_session.add(topic)
    db_session.commit()

    # 1. Generate Plan
    gen_res = client.post(
        "/api/v1/plan/generate",
        headers=auth_headers_a,
        json={"daily_minutes": 50, "days_horizon": 5}
    )
    assert gen_res.status_code == 200
    g_data = gen_res.json()
    assert g_data["total_sessions_created"] >= 1

    # 2. View Schedule
    sched_res = client.get("/api/v1/plan/schedule", headers=auth_headers_a)
    assert sched_res.status_code == 200
    sessions = sched_res.json()
    assert len(sessions) >= 1
    session_id = sessions[0]["id"]
    assert sessions[0]["status"] == "pending"

    # 3. Patch Session Status (Mark Completed)
    patch_res = client.patch(
        f"/api/v1/plan/sessions/{session_id}",
        headers=auth_headers_a,
        json={"status": "completed"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "completed"


def test_analytics_endpoints(client, auth_headers_a, db_session, user_a):
    today = date.today()
    subject = Subject(user_id=user_a.id, name="Psychology", exam_date=today + timedelta(days=12), color="#818CF8")
    db_session.add(subject)
    db_session.commit()

    topic = Topic(subject_id=subject.id, name="Cognitive Bias", difficulty="easy")
    db_session.add(topic)
    db_session.commit()

    # Add a study session
    study = StudySession(
        user_id=user_a.id,
        subject_id=subject.id,
        topic_id=topic.id,
        duration_minutes=35,
        session_type="review"
    )
    db_session.add(study)
    db_session.commit()

    # 1. Summary
    sum_res = client.get("/api/v1/analytics/summary", headers=auth_headers_a)
    assert sum_res.status_code == 200
    s_data = sum_res.json()
    assert s_data["total_subjects"] >= 1
    assert s_data["total_study_minutes"] >= 35
    assert len(s_data["upcoming_exams"]) >= 1
    assert s_data["upcoming_exams"][0]["subject_name"] == "Psychology"

    # 2. Mastery breakdown
    mast_res = client.get("/api/v1/analytics/mastery", headers=auth_headers_a)
    assert mast_res.status_code == 200
    m_data = mast_res.json()
    assert len(m_data["subjects"]) >= 1
    assert any(s["subject_name"] == "Psychology" for s in m_data["subjects"])

    # 3. Study Time By Day
    time_res = client.get("/api/v1/analytics/study-time-by-day?days=7", headers=auth_headers_a)
    assert time_res.status_code == 200
    t_data = time_res.json()
    assert len(t_data["days"]) == 7
    assert t_data["total_period_minutes"] >= 35
