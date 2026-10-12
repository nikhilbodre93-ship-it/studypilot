from datetime import date, timedelta, datetime, timezone
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.topic_mastery import TopicMastery
from app.models.flashcard import Flashcard
from app.core.priority import calculate_topic_priority, compute_exam_multiplier, PriorityWeights
from app.core.scheduler import (
    build_daily_revision_queue,
    generate_plan_schedule,
    determine_session_type,
    compute_next_review_date,
)


def test_exam_multiplier_logic():
    today = date(2026, 10, 15)

    # Exam today
    mult, days, is_exam = compute_exam_multiplier(today, today)
    assert mult == 3.0
    assert days == 0
    assert is_exam is True

    # Exam in 3 days (within 7 days)
    mult, days, is_exam = compute_exam_multiplier(today + timedelta(days=3), today)
    assert mult > 1.5
    assert days == 3
    assert is_exam is True

    # Exam already passed
    mult, days, is_exam = compute_exam_multiplier(today - timedelta(days=5), today)
    assert mult == 0.4
    assert days == -5
    assert is_exam is False

    # No exam date
    mult, days, is_exam = compute_exam_multiplier(None, today)
    assert mult == 1.0
    assert days is None
    assert is_exam is False


def test_priority_breakdown_and_reason(db_session, user_a):
    today = date.today()
    subject = Subject(user_id=user_a.id, name="Physics", exam_date=today + timedelta(days=6))
    db_session.add(subject)
    db_session.commit()

    topic = Topic(subject_id=subject.id, name="Thermodynamics", difficulty="hard")
    db_session.add(topic)
    db_session.commit()

    mastery = TopicMastery(
        user_id=user_a.id,
        topic_id=topic.id,
        score=32.0,
        p_mastery=0.32,
        review_count=3,
        observed_correct=1,
        observed_total=3,
        observed_accuracy=0.33,
    )
    db_session.add(mastery)

    # Add 2 overdue flashcards
    now = datetime.now(timezone.utc)
    card1 = Flashcard(
        topic_id=topic.id,
        user_id=user_a.id,
        front="Q1",
        back="A1",
        due_date=now - timedelta(days=2),
    )
    card2 = Flashcard(
        topic_id=topic.id,
        user_id=user_a.id,
        front="Q2",
        back="A2",
        due_date=now - timedelta(days=1),
    )
    db_session.add_all([card1, card2])
    db_session.commit()

    breakdown = calculate_topic_priority(db_session, user_a.id, topic)

    assert breakdown.topic_id == topic.id
    assert breakdown.priority_score > 0
    assert breakdown.is_exam_mode is True
    assert breakdown.days_until_exam == 6
    assert breakdown.components["mastery"] == 0.68  # 1 - 0.32
    assert breakdown.components["overdue_cards"] == 0.4  # 2 / 5
    assert breakdown.components["difficulty"] == 1.0  # hard
    # Reason contains required details
    assert "Mastery 32.0% after 3 attempts" in breakdown.reason
    assert "2 cards overdue" in breakdown.reason
    assert "exam in 6 days" in breakdown.reason
    assert "Exam Mode active" in breakdown.reason


def test_scheduler_edge_case_no_data(db_session, user_b):
    # User B has no subjects or topics
    queue_resp = build_daily_revision_queue(db_session, user_b.id, available_minutes=60)
    assert queue_resp.sessions_count == 0
    assert queue_resp.queue == []
    assert queue_resp.total_scheduled_minutes == 0


def test_scheduler_edge_case_exam_today(db_session, user_a):
    today = date.today()
    subject = Subject(user_id=user_a.id, name="Urgent Math", exam_date=today)
    db_session.add(subject)
    db_session.commit()

    topic = Topic(subject_id=subject.id, name="Calculus", difficulty="hard")
    db_session.add(topic)
    db_session.commit()

    queue_resp = build_daily_revision_queue(db_session, user_a.id, available_minutes=30)
    assert queue_resp.is_exam_mode_active is True
    assert queue_resp.sessions_count >= 1
    first_session = queue_resp.queue[0]
    assert first_session.session_type == "rapid_review"  # Exam today triggers rapid review
    assert "exam TODAY" in first_session.reason


def test_scheduler_edge_case_exam_already_passed(db_session, user_a):
    today = date.today()
    past_subject = Subject(user_id=user_a.id, name="Past Subject", exam_date=today - timedelta(days=10))
    db_session.add(past_subject)
    db_session.commit()

    topic = Topic(subject_id=past_subject.id, name="Old Topic", difficulty="easy")
    db_session.add(topic)
    db_session.commit()

    queue_resp = build_daily_revision_queue(db_session, user_a.id, available_minutes=25)
    assert queue_resp.sessions_count >= 1
    # Does not crash, handles negative days gracefully
    assert "exam completed" in queue_resp.queue[0].reason


def test_scheduler_edge_case_very_small_time_window(db_session, user_a):
    subject = Subject(user_id=user_a.id, name="Quick Review Subject")
    db_session.add(subject)
    db_session.commit()

    topic = Topic(subject_id=subject.id, name="Micro Topic", difficulty="medium")
    db_session.add(topic)
    db_session.commit()

    # User only has 5 minutes
    queue_resp = build_daily_revision_queue(db_session, user_a.id, available_minutes=5)
    assert queue_resp.sessions_count == 1
    assert queue_resp.total_scheduled_minutes == 5
    assert queue_resp.queue[0].duration_minutes == 5
    assert "Quick burst session" in queue_resp.queue[0].reason


def test_scheduler_standard_packing_and_plan_generation(db_session, user_a):
    today = date.today()
    subject = Subject(user_id=user_a.id, name="Chemistry", exam_date=today + timedelta(days=10))
    db_session.add(subject)
    db_session.commit()

    t1 = Topic(subject_id=subject.id, name="Acids & Bases", difficulty="easy", order_index=0)
    t2 = Topic(subject_id=subject.id, name="Organic Reactions", difficulty="hard", order_index=1)
    db_session.add_all([t1, t2])
    db_session.commit()

    # 1. Test queue for 60 minutes
    queue_resp = build_daily_revision_queue(db_session, user_a.id, available_minutes=60)
    assert queue_resp.sessions_count >= 2
    assert queue_resp.total_scheduled_minutes <= 60

    # 2. Test day-by-day plan generation
    sessions = generate_plan_schedule(db_session, user_a.id, start_date=today, daily_minutes=50, days_horizon=3)
    assert len(sessions) >= 3
    assert all(s.user_id == user_a.id for s in sessions)
    assert all(s.status == "pending" for s in sessions)
    assert all(s.reason is not None for s in sessions)
