import sys
import httpx
import json
from datetime import date, timedelta

requests = httpx

BASE_URL = "http://127.0.0.1:8000"

def test_full_live_flow():
    print("--- 1. Health Check ---")
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("Health check OK:", r.json())

    print("\n--- 2. Register New User ---")
    email = f"student_{int(date.today().strftime('%Y%m%d%H%M%S'))}@studypilot.io"
    password = "SecureStudyPass2026!"
    reg_payload = {
        "email": email,
        "password": password,
        "full_name": "Satyam Sharma"
    }
    r = requests.post(f"{BASE_URL}/api/v1/auth/register", json=reg_payload)
    assert r.status_code == 201, f"Register failed: {r.text}"
    token_data = r.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Registered successfully, token received.")

    print("\n--- 3. Add Subject & Topics ---")
    exam_date = (date.today() + timedelta(days=21)).isoformat()
    subj_payload = {
        "name": "Molecular Biology",
        "exam_date": exam_date,
        "color": "#2F5D46"
    }
    r = requests.post(f"{BASE_URL}/api/v1/subjects", json=subj_payload, headers=headers)
    assert r.status_code == 201, f"Subject creation failed: {r.text}"
    subject = r.json()
    subj_id = subject["id"]
    print(f"Created Subject: {subject['name']} (ID: {subj_id})")

    # Add Topics
    topics = [
        {"name": "Replication & Transcription", "difficulty": "medium", "order_index": 0},
        {"name": "CRISPR & Gene Editing", "difficulty": "hard", "order_index": 1}
    ]
    created_topics = []
    for t in topics:
        r = requests.post(f"{BASE_URL}/api/v1/subjects/{subj_id}/topics", json=t, headers=headers)
        assert r.status_code == 201, f"Topic creation failed: {r.text}"
        created_topics.append(r.json())
        print(f"  |-- Created Topic: {t['name']} ({t['difficulty']})")

    print("\n--- 4. Generate Revision Plan ---")
    plan_payload = {
        "daily_minutes": 50,
        "days_horizon": 14
    }
    r = requests.post(f"{BASE_URL}/api/v1/plan/generate", json=plan_payload, headers=headers)
    assert r.status_code == 200, f"Plan generation failed: {r.text}"
    plan_result = r.json()
    print(f"Plan generated: {plan_result['total_sessions_created']} sessions created.")

    print("\n--- 5. Verify Dashboard & Schedule ---")
    r = requests.get(f"{BASE_URL}/api/v1/plan/schedule", headers=headers)
    assert r.status_code == 200
    schedule = r.json()
    assert len(schedule) > 0, "Schedule is empty"
    first_session = schedule[0]
    print(f"First planned session: {first_session['topic_name']} ({first_session['duration_minutes']} min, status: {first_session['status']})")

    print("\n--- 6. Complete a Session ---")
    r = requests.patch(
        f"{BASE_URL}/api/v1/plan/sessions/{first_session['id']}",
        json={"status": "completed"},
        headers=headers
    )
    assert r.status_code == 200
    updated_session = r.json()
    assert updated_session["status"] == "completed"
    print(f"Session {updated_session['id']} marked as COMPLETED.")

    print("\n--- 7. Run Focus Timer / Log Study Session ---")
    timer_payload = {
        "subject_id": subj_id,
        "topic_id": created_topics[0]["id"],
        "duration_minutes": 25,
        "session_type": "pomodoro",
        "notes": "Studied Replication & Transcription for 25 minutes"
    }
    r = requests.post(f"{BASE_URL}/api/v1/study-sessions", json=timer_payload, headers=headers)
    assert r.status_code == 201
    study_session = r.json()
    print(f"Logged Focus Timer Session: {study_session['duration_minutes']} min ({study_session['session_type']})")

    print("\n--- 8. Verify Dashboard Analytics Updated ---")
    r = requests.get(f"{BASE_URL}/api/v1/analytics/summary", headers=headers)
    assert r.status_code == 200
    analytics = r.json()
    print("Updated Analytics Summary:")
    print(f"  Total Subjects: {analytics['total_subjects']}")
    print(f"  Total Topics: {analytics['total_topics']}")
    print(f"  Total Study Minutes: {analytics['total_study_minutes']}")
    print(f"  Total Study Sessions: {analytics['total_study_sessions']}")
    print(f"  Upcoming Exams: {len(analytics['upcoming_exams'])}")
    assert analytics["total_study_minutes"] >= 25
    assert analytics["total_study_sessions"] >= 1
    assert len(analytics["upcoming_exams"]) >= 1

    print("\n--- 9. Verify Frontend Serves HTML ---")
    r_fe = requests.get("http://localhost:5173")
    assert r_fe.status_code == 200
    assert "studypilot." in r_fe.text
    print("Frontend Vite Server running and serving index.html successfully!")

    print("\nALL FLOW CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_full_live_flow()
