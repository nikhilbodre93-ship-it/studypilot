from datetime import date, timedelta
from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.topic_mastery import TopicMastery
from app.core.security import hash_password


def seed_database():
    """Seed sample data for local development."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Create or get demo user
        demo_email = "demo@studypilot.io"
        user = db.query(User).filter(User.email == demo_email).first()
        if not user:
            user = User(
                email=demo_email,
                hashed_password=hash_password("StudyPilot2026!"),
                full_name="Alex Chen",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"[Seed] Created demo user: {user.email}")
        else:
            print(f"[Seed] Found existing demo user: {user.email}")

        # 2. Sample subjects data definition
        today = date.today()
        sample_subjects = [
            {
                "name": "Biology",
                "description": "Cellular biology, genetic processes, and inheritance systems.",
                "exam_date": today + timedelta(days=45),
                "color": "#2F5D46",
                "topics": [
                    {
                        "name": "Cell structure",
                        "description": "Prokaryotic vs eukaryotic cells, organelle functions, and membrane dynamics.",
                        "difficulty": "medium",
                        "order_index": 0,
                    },
                    {
                        "name": "Genetics & inheritance",
                        "description": "Mendelian genetics, DNA replication, gene expression, and pedigree charts.",
                        "difficulty": "hard",
                        "order_index": 1,
                    },
                ],
            },
            {
                "name": "Math",
                "description": "Higher mathematics focusing on integral calculus and applied probability.",
                "exam_date": today + timedelta(days=30),
                "color": "#3B82F6",
                "topics": [
                    {
                        "name": "Calculus: integration",
                        "description": "Definite/indefinite integrals, substitution, integration by parts, and area under curves.",
                        "difficulty": "hard",
                        "order_index": 0,
                    },
                    {
                        "name": "Statistics",
                        "description": "Probability distributions, hypothesis testing, confidence intervals, and regression.",
                        "difficulty": "medium",
                        "order_index": 1,
                    },
                ],
            },
            {
                "name": "Computer Engineering",
                "description": "Core computer science fundamentals: hardware-software interface and algorithms.",
                "exam_date": today + timedelta(days=60),
                "color": "#6366F1",
                "topics": [
                    {
                        "name": "Data structures",
                        "description": "Arrays, linked lists, trees, graphs, heaps, hash tables, and asymptotic complexity.",
                        "difficulty": "medium",
                        "order_index": 0,
                    },
                    {
                        "name": "Computer architecture",
                        "description": "Instruction set architecture (ISA), pipelining, cache memory hierarchy, and ALU design.",
                        "difficulty": "hard",
                        "order_index": 1,
                    },
                    {
                        "name": "Operating systems",
                        "description": "Process management, virtual memory, concurrency, deadlocks, and filesystem structures.",
                        "difficulty": "hard",
                        "order_index": 2,
                    },
                ],
            },
        ]

        # 3. Insert subjects and topics
        for subj_data in sample_subjects:
            existing_subj = (
                db.query(Subject)
                .filter(Subject.user_id == user.id, Subject.name == subj_data["name"])
                .first()
            )
            if not existing_subj:
                subj = Subject(
                    user_id=user.id,
                    name=subj_data["name"],
                    description=subj_data["description"],
                    exam_date=subj_data["exam_date"],
                    color=subj_data["color"],
                )
                db.add(subj)
                db.commit()
                db.refresh(subj)
                print(f"[Seed] Created subject: {subj.name}")
            else:
                subj = existing_subj
                print(f"[Seed] Found existing subject: {subj.name}")

            for top_data in subj_data["topics"]:
                existing_topic = (
                    db.query(Topic)
                    .filter(Topic.subject_id == subj.id, Topic.name == top_data["name"])
                    .first()
                )
                if not existing_topic:
                    topic = Topic(
                        subject_id=subj.id,
                        name=top_data["name"],
                        description=top_data["description"],
                        difficulty=top_data["difficulty"],
                        order_index=top_data["order_index"],
                    )
                    db.add(topic)
                    db.commit()
                    db.refresh(topic)

                    mastery = TopicMastery(
                        user_id=user.id,
                        topic_id=topic.id,
                        score=0.0,
                        stability=1.0,
                        retrievability=1.0,
                    )
                    db.add(mastery)
                    db.commit()
                    print(f"  |-- Created topic: {topic.name} ({topic.difficulty})")
                else:
                    print(f"  |-- Found existing topic: {existing_topic.name}")

        print("[Seed] Seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
