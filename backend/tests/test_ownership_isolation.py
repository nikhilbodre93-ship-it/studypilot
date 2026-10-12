def test_subject_ownership_isolation(client, auth_headers_a, auth_headers_b):
    # User A creates a subject
    create_res = client.post(
        "/api/v1/subjects",
        headers=auth_headers_a,
        json={"name": "User A Private Physics", "description": "Mechanics", "exam_date": "2026-12-01"}
    )
    assert create_res.status_code == 201
    subj_a_id = create_res.json()["id"]

    # User B lists subjects -> should NOT contain User A's subject
    list_b_res = client.get("/api/v1/subjects", headers=auth_headers_b)
    assert list_b_res.status_code == 200
    b_items = list_b_res.json()["items"]
    assert all(item["id"] != subj_a_id for item in b_items)

    # User B tries to get User A's subject directly -> 404
    get_res = client.get(f"/api/v1/subjects/{subj_a_id}", headers=auth_headers_b)
    assert get_res.status_code == 404
    assert get_res.json()["error"]["code"] == "NOT_FOUND"

    # User B tries to update User A's subject -> 404
    put_res = client.put(f"/api/v1/subjects/{subj_a_id}", headers=auth_headers_b, json={"name": "Hacked"})
    assert put_res.status_code == 404

    # User B tries to delete User A's subject -> 404
    del_res = client.delete(f"/api/v1/subjects/{subj_a_id}", headers=auth_headers_b)
    assert del_res.status_code == 404

    # Verify subject still exists for User A
    verify_res = client.get(f"/api/v1/subjects/{subj_a_id}", headers=auth_headers_a)
    assert verify_res.status_code == 200
    assert verify_res.json()["name"] == "User A Private Physics"


def test_topic_ownership_isolation(client, auth_headers_a, auth_headers_b):
    # User A creates a subject and a topic
    subj_res = client.post(
        "/api/v1/subjects",
        headers=auth_headers_a,
        json={"name": "Chemistry", "exam_date": "2026-11-20"}
    )
    subj_a_id = subj_res.json()["id"]

    topic_res = client.post(
        f"/api/v1/subjects/{subj_a_id}/topics",
        headers=auth_headers_a,
        json={"name": "Thermodynamics", "difficulty": "hard", "order_index": 0}
    )
    assert topic_res.status_code == 201
    topic_a_id = topic_res.json()["id"]

    # User B tries to create topic under User A's subject -> 404
    b_add_topic = client.post(
        f"/api/v1/subjects/{subj_a_id}/topics",
        headers=auth_headers_b,
        json={"name": "Unauthorized Topic", "difficulty": "easy"}
    )
    assert b_add_topic.status_code == 404

    # User B tries to list topics of User A's subject -> 404
    b_list = client.get(f"/api/v1/subjects/{subj_a_id}/topics", headers=auth_headers_b)
    assert b_list.status_code == 404

    # User B tries to view topic directly -> 404
    b_get = client.get(f"/api/v1/topics/{topic_a_id}", headers=auth_headers_b)
    assert b_get.status_code == 404

    # User B tries to update topic -> 404
    b_put = client.put(f"/api/v1/topics/{topic_a_id}", headers=auth_headers_b, json={"name": "Changed"})
    assert b_put.status_code == 404

    # User B tries to delete topic -> 404
    b_del = client.delete(f"/api/v1/topics/{topic_a_id}", headers=auth_headers_b)
    assert b_del.status_code == 404


def test_study_session_ownership_isolation(client, auth_headers_a, auth_headers_b):
    # User A creates a subject
    subj_res = client.post(
        "/api/v1/subjects",
        headers=auth_headers_a,
        json={"name": "History"}
    )
    subj_a_id = subj_res.json()["id"]

    # User B tries to log a study session under User A's subject -> 404
    session_res = client.post(
        "/api/v1/study-sessions",
        headers=auth_headers_b,
        json={"subject_id": subj_a_id, "duration_minutes": 25, "session_type": "pomodoro"}
    )
    assert session_res.status_code == 404
