import pytest
from app.core.bkt import update_bkt, BKTConfig, record_topic_evidence
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.topic_mastery import TopicMastery


def test_bkt_correct_answer_increases_mastery():
    cfg = BKTConfig(p_init=0.20, p_learn=0.15, p_slip=0.10, p_guess=0.20)
    p0 = cfg.p_init

    p1 = update_bkt(p0, is_correct=True, config=cfg)
    assert p1 > p0, f"Mastery should increase on correct answer: {p1} > {p0}"
    assert p1 >= 0.50, f"Expected higher posterior after correct answer, got {p1}"


def test_bkt_incorrect_answer_decreases_mastery():
    cfg = BKTConfig(p_init=0.60, p_learn=0.15, p_slip=0.10, p_guess=0.20)
    p0 = 0.60

    p1 = update_bkt(p0, is_correct=False, config=cfg)
    assert p1 < p0, f"Mastery should decrease or drop on incorrect answer: {p1} < {p0}"


def test_bkt_consecutive_correct_approaches_ceiling():
    cfg = BKTConfig()
    p = 0.20
    for _ in range(6):
        p = update_bkt(p, is_correct=True, config=cfg)
    assert p >= 0.95, f"Repeated correct answers should lead to high mastery, got {p}"


def test_bkt_clamping_and_bounds():
    cfg = BKTConfig()
    p_high = update_bkt(0.999, is_correct=True, config=cfg)
    assert 0.01 <= p_high <= 0.99

    p_low = update_bkt(0.0001, is_correct=False, config=cfg)
    assert 0.01 <= p_low <= 0.99


def test_bkt_record_topic_evidence_in_db(db_session, user_a):
    subject = Subject(user_id=user_a.id, name="Biology")
    db_session.add(subject)
    db_session.commit()

    topic = Topic(subject_id=subject.id, name="Cell Division", difficulty="medium")
    db_session.add(topic)
    db_session.commit()

    # 1. Record correct answer
    m1 = record_topic_evidence(db_session, user_a.id, topic.id, is_correct=True)
    assert m1.observed_correct == 1
    assert m1.observed_total == 1
    assert m1.observed_accuracy == 1.0
    assert m1.p_mastery > 0.20
    assert m1.score == round(m1.p_mastery * 100.0, 1)

    # 2. Record incorrect answer
    m2 = record_topic_evidence(db_session, user_a.id, topic.id, is_correct=False)
    assert m2.observed_correct == 1
    assert m2.observed_total == 2
    assert m2.observed_accuracy == 0.5
    # Separate storage verified: score is BKT mastery estimate while accuracy is raw 50%
    assert m2.observed_accuracy == 0.5
    assert m2.score != 50.0  # BKT Bayesian estimate differs from naive percentage
