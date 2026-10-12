def test_subject_crud_lifecycle(client, auth_headers_a):
    # 1. Create
    create_res = client.post(
        "/api/v1/subjects",
        headers=auth_headers_a,
        json={
            "name": "Neuroscience",
            "description": "Synapses, networks and cognition",
            "exam_date": "2026-12-15",
            "color": "#10B981"
        }
    )
    assert create_res.status_code == 201
    subject = create_res.json()
    subj_id = subject["id"]
    assert subject["name"] == "Neuroscience"
    assert subject["topic_count"] == 0

    # 2. Get by ID
    get_res = client.get(f"/api/v1/subjects/{subj_id}", headers=auth_headers_a)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Neuroscience"

    # 3. Update
    put_res = client.put(
        f"/api/v1/subjects/{subj_id}",
        headers=auth_headers_a,
        json={"name": "Advanced Neuroscience", "description": "Updated description"}
    )
    assert put_res.status_code == 200
    assert put_res.json()["name"] == "Advanced Neuroscience"
    assert put_res.json()["description"] == "Updated description"

    # 4. List and Search
    list_res = client.get("/api/v1/subjects?search=Neuroscience", headers=auth_headers_a)
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] >= 1
    assert any(s["id"] == subj_id for s in data["items"])

    # 5. Delete
    del_res = client.delete(f"/api/v1/subjects/{subj_id}", headers=auth_headers_a)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 6. Verify deleted
    verify_res = client.get(f"/api/v1/subjects/{subj_id}", headers=auth_headers_a)
    assert verify_res.status_code == 404


def test_topic_crud_and_ordering(client, auth_headers_a):
    # Setup subject
    subj_res = client.post(
        "/api/v1/subjects",
        headers=auth_headers_a,
        json={"name": "Computer Science"}
    )
    subj_id = subj_res.json()["id"]

    # 1. Create Topics with different difficulties
    t1 = client.post(
        f"/api/v1/subjects/{subj_id}/topics",
        headers=auth_headers_a,
        json={"name": "Arrays & Strings", "difficulty": "easy", "order_index": 0}
    )
    assert t1.status_code == 201
    assert t1.json()["mastery_score"] == 0.0

    t2 = client.post(
        f"/api/v1/subjects/{subj_id}/topics",
        headers=auth_headers_a,
        json={"name": "Dynamic Programming", "difficulty": "hard", "order_index": 1}
    )
    assert t2.status_code == 201

    topic_2_id = t2.json()["id"]

    # 2. List topics for subject
    list_res = client.get(f"/api/v1/subjects/{subj_id}/topics", headers=auth_headers_a)
    assert list_res.status_code == 200
    items = list_res.json()["items"]
    assert len(items) == 2
    assert items[0]["name"] == "Arrays & Strings"
    assert items[1]["name"] == "Dynamic Programming"

    # Verify subject topic_count is 2
    subj_check = client.get(f"/api/v1/subjects/{subj_id}", headers=auth_headers_a)
    assert subj_check.json()["topic_count"] == 2

    # 3. Update topic
    put_res = client.put(
        f"/api/v1/topics/{topic_2_id}",
        headers=auth_headers_a,
        json={"name": "DP & Memoization", "difficulty": "hard"}
    )
    assert put_res.status_code == 200
    assert put_res.json()["name"] == "DP & Memoization"

    # 4. Delete topic
    del_res = client.delete(f"/api/v1/topics/{topic_2_id}", headers=auth_headers_a)
    assert del_res.status_code == 200

    # Verify topic deleted
    verify_res = client.get(f"/api/v1/topics/{topic_2_id}", headers=auth_headers_a)
    assert verify_res.status_code == 404


def test_study_session_logging_and_summary(client, auth_headers_a):
    # Setup subject
    subj_res = client.post(
        "/api/v1/subjects",
        headers=auth_headers_a,
        json={"name": "Biochemistry"}
    )
    subj_id = subj_res.json()["id"]

    # 1. Log Pomodoro session
    s1 = client.post(
        "/api/v1/study-sessions",
        headers=auth_headers_a,
        json={
            "subject_id": subj_id,
            "duration_minutes": 25,
            "session_type": "pomodoro",
            "notes": "Focused on Krebs cycle"
        }
    )
    assert s1.status_code == 201
    s1_data = s1.json()
    assert s1_data["duration_minutes"] == 25
    assert s1_data["session_type"] == "pomodoro"
    assert s1_data["subject_name"] == "Biochemistry"

    # 2. Log Review session
    s2 = client.post(
        "/api/v1/study-sessions",
        headers=auth_headers_a,
        json={
            "subject_id": subj_id,
            "duration_minutes": 35,
            "session_type": "review",
            "notes": "Flashcards review"
        }
    )
    assert s2.status_code == 201

    # 3. List sessions
    list_res = client.get("/api/v1/study-sessions", headers=auth_headers_a)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 2

    # 4. Check summary
    summary_res = client.get("/api/v1/study-sessions/summary", headers=auth_headers_a)
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["total_sessions"] >= 2
    assert summary["total_minutes"] >= 60
    assert summary["by_type"]["pomodoro"] >= 25
    assert summary["by_type"]["review"] >= 35

    # 5. Delete session
    del_res = client.delete(f"/api/v1/study-sessions/{s1_data['id']}", headers=auth_headers_a)
    assert del_res.status_code == 200
