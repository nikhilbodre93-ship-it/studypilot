from datetime import datetime, date, timedelta, timezone
import json
import os

from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.topic_mastery import TopicMastery
from app.models.material import Material
from app.models.note import Note
from app.models.quiz import Quiz, Question, QuizAttempt, AttemptAnswer
from app.models.flashcard import Flashcard, CardReview
from app.models.question_paper import QuestionPaper
from app.models.roadmap import Roadmap
from app.models.tutor import TutorConversation, TutorMessage
from app.models.study_session import StudySession
from app.models.plan_session import PlanSession
from app.core.security import hash_password
from app.services.vector_store import global_vector_store


def populate_comprehensive_demo_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        users_to_seed = [
            {"email": "student.a@studypilot.io", "name": "Elena Rostova"},
            {"email": "demo@studypilot.io", "name": "Alex Chen"},
        ]

        now = datetime.now(timezone.utc)
        today = now.date()

        for u_info in users_to_seed:
            user = db.query(User).filter(User.email == u_info["email"]).first()
            if not user:
                user = User(
                    email=u_info["email"],
                    hashed_password=hash_password("StudyPilot2026!"),
                    full_name=u_info["name"],
                    is_active=True,
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"[Seed] Created user: {user.email}")
            else:
                print(f"[Seed] Found existing user: {user.email}")

            # 1. Subjects
            subjects_data = [
                {
                    "name": "Molecular & Cell Biology",
                    "description": "Cellular mechanics, membrane physiology, and molecular genetics.",
                    "exam_date": today + timedelta(days=12),
                    "color": "#2F5D46",
                    "topics": [
                        {
                            "name": "Cell Membrane Architecture",
                            "difficulty": "medium",
                            "mastery": 0.68,
                            "acc": 0.75,
                            "reviews": 4,
                        },
                        {
                            "name": "Active & Passive Transport",
                            "difficulty": "hard",
                            "mastery": 0.42,
                            "acc": 0.50,
                            "reviews": 3,
                        },
                        {
                            "name": "Mendelian Genetics",
                            "difficulty": "medium",
                            "mastery": 0.84,
                            "acc": 0.88,
                            "reviews": 6,
                        },
                    ],
                },
                {
                    "name": "Higher Mathematics",
                    "description": "Calculus, linear algebra, and mathematical statistics.",
                    "exam_date": today + timedelta(days=24),
                    "color": "#3B82F6",
                    "topics": [
                        {
                            "name": "Integral Calculus & Substitutions",
                            "difficulty": "hard",
                            "mastery": 0.35,
                            "acc": 0.40,
                            "reviews": 3,
                        },
                        {
                            "name": "Probability & Distributions",
                            "difficulty": "medium",
                            "mastery": 0.72,
                            "acc": 0.80,
                            "reviews": 5,
                        },
                    ],
                },
                {
                    "name": "Modern European History",
                    "description": "Geopolitical treaties, industrialization, and 20th-century conflicts.",
                    "exam_date": today + timedelta(days=38),
                    "color": "#818CF8",
                    "topics": [
                        {
                            "name": "The Treaty of Versailles (1919)",
                            "difficulty": "easy",
                            "mastery": 0.90,
                            "acc": 0.95,
                            "reviews": 7,
                        },
                    ],
                },
            ]

            created_topics = []

            for s_info in subjects_data:
                subj = db.query(Subject).filter(Subject.user_id == user.id, Subject.name == s_info["name"]).first()
                if not subj:
                    subj = Subject(
                        user_id=user.id,
                        name=s_info["name"],
                        description=s_info["description"],
                        exam_date=s_info["exam_date"],
                        color=s_info["color"],
                    )
                    db.add(subj)
                    db.commit()
                    db.refresh(subj)

                for t_info in s_info["topics"]:
                    top = db.query(Topic).filter(Topic.subject_id == subj.id, Topic.name == t_info["name"]).first()
                    if not top:
                        top = Topic(
                            subject_id=subj.id,
                            name=t_info["name"],
                            description=f"Detailed study guide for {t_info['name']}",
                            difficulty=t_info["difficulty"],
                        )
                        db.add(top)
                        db.commit()
                        db.refresh(top)

                        # Topic Mastery
                        mastery = TopicMastery(
                            user_id=user.id,
                            topic_id=top.id,
                            score=t_info["mastery"],
                            p_mastery=t_info["mastery"],
                            observed_accuracy=t_info["acc"],
                            observed_correct=int(t_info["reviews"] * t_info["acc"]),
                            observed_total=t_info["reviews"],
                            review_count=t_info["reviews"],
                            last_reviewed_at=now - timedelta(days=2),
                        )
                        db.add(mastery)
                        db.commit()

                    created_topics.append(top)

            primary_topic = created_topics[0]
            second_topic = created_topics[1]

            # 2. Seed Study Materials
            existing_mat = db.query(Material).filter(Material.user_id == user.id).first()
            if not existing_mat:
                os.makedirs("storage/materials", exist_ok=True)
                sample_file = "storage/materials/cell_membrane_lecture.txt"
                sample_content = (
                    "The cell membrane functions primarily as a selective permeable barrier based on the fluid mosaic model. "
                    "Lipid bilayers consist of amphipathic phospholipids with hydrophilic phosphate heads and hydrophobic hydrocarbon tails. "
                    "Integral proteins act as transport channels or pumps, such as the sodium-potassium ATPase pump."
                )
                with open(sample_file, "w", encoding="utf-8") as f:
                    f.write(sample_content)

                mat = Material(
                    topic_id=primary_topic.id,
                    user_id=user.id,
                    title="Cell Membrane Physiology Handout",
                    file_name="cell_membrane_lecture.txt",
                    file_type="txt",
                    file_size=len(sample_content),
                    storage_path=sample_file,
                    extracted_text=json.dumps({
                        "chunks": [
                            {"chunk_id": "chunk_0", "page": 1, "citation": "Page 1", "text": sample_content}
                        ],
                        "summary_text": sample_content
                    })
                )
                db.add(mat)
                db.commit()
                global_vector_store.add_chunks(primary_topic.id, [
                    {"chunk_id": "chunk_0", "page": 1, "citation": "Page 1", "text": sample_content}
                ])
                print(f"[Seed] Material created for topic '{primary_topic.name}'")

            # 3. Seed Study Notes
            existing_note = db.query(Note).filter(Note.user_id == user.id).first()
            if not existing_note:
                note1 = Note(
                    topic_id=primary_topic.id,
                    user_id=user.id,
                    title="Comprehensive Cell Membrane Notes",
                    content_markdown=(
                        "# Cell Membrane Architecture & Dynamic Transport\n\n"
                        "> The cell membrane operates via the **fluid mosaic model**, balancing structural fluidity and selective barrier functions.\n\n"
                        "## 1. Lipid Bilayer Thermodynamics\n"
                        "- Composed of amphipathic phospholipids organized spontaneously into bilayers.\n"
                        "- Cholesterol acts as a bidirectional fluidity buffer: preventing crystallization at low temperatures and restraining fluidity at high temperatures.\n\n"
                        "## 2. Active vs. Passive Kinetics\n"
                        "- **Passive diffusion**: Movement along concentration gradients with zero ATP required.\n"
                        "- **Active transport**: Uses ATP directly (primary) or indirect electrochemical gradients (secondary).\n\n"
                        "### High-Yield Takeaways\n"
                        "- Na+/K+ pump transports 3 Na+ out for every 2 K+ in.\n"
                        "- Phospholipids display lateral diffusion within the membrane plane.\n\n"
                        "### Grounded Citations\n"
                        "- Page 1, Section 1.2\n"
                        "- Page 2, Kinetics Overview"
                    ),
                    is_ai_generated=True,
                )
                db.add(note1)
                db.commit()
                print("[Seed] Seeded Study Note.")

            # 4. Seed Quizzes and Attempts
            existing_quiz = db.query(Quiz).filter(Quiz.user_id == user.id).first()
            if not existing_quiz:
                quiz = Quiz(
                    topic_id=primary_topic.id,
                    user_id=user.id,
                    title="Cell Biology Diagnostic Quiz",
                    total_questions=3,
                )
                db.add(quiz)
                db.commit()
                db.refresh(quiz)

                q1 = Question(
                    quiz_id=quiz.id,
                    question_text="Which organelle generates the majority of cellular ATP via oxidative phosphorylation?",
                    question_type="multiple_choice",
                    options_json=json.dumps(["Mitochondria", "Ribosome", "Golgi Apparatus", "Lysosome"]),
                    correct_answer="Mitochondria",
                    explanation="Mitochondria house the electron transport chain and ATP synthase complexes.",
                    order_index=0,
                )
                q2 = Question(
                    quiz_id=quiz.id,
                    question_text="Passive transport requires the hydrolysis of metabolic ATP.",
                    question_type="true_false",
                    options_json=json.dumps(["True", "False"]),
                    correct_answer="False",
                    explanation="Passive transport is driven entirely by concentration gradients.",
                    order_index=1,
                )
                q3 = Question(
                    quiz_id=quiz.id,
                    question_text="Define the physiological role of the sodium-potassium pump.",
                    question_type="short_answer",
                    options_json=None,
                    correct_answer="Pumps 3 Na+ ions out and 2 K+ ions in per ATP hydrolyzed to maintain resting potential.",
                    explanation="Maintains osmotic stability and cellular resting potential.",
                    order_index=2,
                )
                db.add_all([q1, q2, q3])
                db.commit()

                # Add a past attempt
                attempt = QuizAttempt(
                    quiz_id=quiz.id,
                    user_id=user.id,
                    score=2.0,
                    max_score=3.0,
                    completed_at=now - timedelta(days=1),
                )
                db.add(attempt)
                db.commit()
                print("[Seed] Seeded Quiz and past attempt.")

            # 5. Seed Flashcards
            existing_fc = db.query(Flashcard).filter(Flashcard.user_id == user.id).first()
            if not existing_fc:
                cards = [
                    Flashcard(
                        topic_id=primary_topic.id,
                        user_id=user.id,
                        front="What is the fluid mosaic model?",
                        back="A model describing cell membranes as two-dimensional fluids of lipid bilayers with embedded proteins.",
                        explanation="Proposed by Singer and Nicolson in 1972.",
                        difficulty="easy",
                        ease_factor=2.5,
                        interval_days=1,
                        repetitions=1,
                        due_date=now - timedelta(hours=2), # Due now!
                    ),
                    Flashcard(
                        topic_id=primary_topic.id,
                        user_id=user.id,
                        front="What is the stoichiometry of the Na+/K+ ATPase pump?",
                        back="3 Na+ ions pumped OUT of cell, 2 K+ ions pumped IN per ATP hydrolyzed.",
                        explanation="Electrogenic pump that maintains negative interior potential.",
                        difficulty="medium",
                        ease_factor=2.5,
                        interval_days=3,
                        repetitions=2,
                        due_date=now + timedelta(days=2),
                    ),
                    Flashcard(
                        topic_id=second_topic.id,
                        user_id=user.id,
                        front="Differentiate primary from secondary active transport.",
                        back="Primary uses ATP directly; secondary couples transport to ion gradients established by primary pumps.",
                        explanation="e.g. SGLT glucose transporter is secondary active transport.",
                        difficulty="hard",
                        ease_factor=2.4,
                        interval_days=1,
                        repetitions=1,
                        due_date=now - timedelta(hours=1), # Due now!
                    ),
                ]
                db.add_all(cards)
                db.commit()
                print("[Seed] Seeded Flashcards.")

            # 6. Seed Question Paper
            existing_qp = db.query(QuestionPaper).filter(QuestionPaper.user_id == user.id).first()
            if not existing_qp:
                qp = QuestionPaper(
                    subject_id=primary_topic.subject_id,
                    user_id=user.id,
                    title="Molecular Biology Term Examination",
                    exam_type="mock_exam",
                    duration_minutes=60,
                    total_marks=100,
                    content_json=json.dumps({
                        "title": "Molecular Biology Term Examination",
                        "subject_name": "Molecular & Cell Biology",
                        "total_marks": 100,
                        "duration_minutes": 60,
                        "instructions": [
                            "Section A contains 10 multiple-choice questions (20 marks).",
                            "Section B contains 4 structured short questions (30 marks).",
                            "Section C requires analytical essay responses (50 marks).",
                        ],
                        "sections": [
                            {
                                "name": "Section A: Objective Knowledge",
                                "description": "Foundational conceptual MCQs",
                                "section_code": "A",
                                "total_marks": 20,
                                "questions": [
                                    {
                                        "id": "Q1",
                                        "section": "A",
                                        "question_text": "Which phospholipid component faces inward toward the membrane core?",
                                        "marks": 2,
                                        "options": ["Hydrophobic fatty acid tails", "Hydrophilic phosphate heads", "Glycerol backbone", "Peripheral glycolipids"],
                                        "model_answer": "Hydrophobic fatty acid tails",
                                        "rubric": "2 marks for correct choice."
                                    }
                                ]
                            },
                            {
                                "name": "Section B: Conceptual Clarification",
                                "description": "Short explanatory questions",
                                "section_code": "B",
                                "total_marks": 30,
                                "questions": [
                                    {
                                        "id": "Q2",
                                        "section": "B",
                                        "question_text": "Explain how cholesterol modulates membrane fluidity across varying temperature ranges.",
                                        "marks": 5,
                                        "options": None,
                                        "model_answer": "Cholesterol functions as a bidirectional buffer: immobilizing lipid tails at high temperatures and preventing close packing at low temperatures.",
                                        "rubric": "3 marks for high temp stabilization, 2 marks for low temp anti-freezing effect."
                                    }
                                ]
                            },
                            {
                                "name": "Section C: Analytical Inquiry",
                                "description": "Long answer problem solving",
                                "section_code": "C",
                                "total_marks": 50,
                                "questions": [
                                    {
                                        "id": "Q3",
                                        "section": "C",
                                        "question_text": "Detail the mechanism of the Na+/K+ ATPase pump and its electrogenic significance in animal cells.",
                                        "marks": 10,
                                        "options": None,
                                        "model_answer": "Phosphorylation triggers conformational change releasing 3 Na+ externally; dephosphorylation returns conformation bringing 2 K+ inside.",
                                        "rubric": "5 marks for enzymatic steps, 5 marks for electrogenic resting potential maintenance."
                                    }
                                ]
                            }
                        ]
                    })
                )
                db.add(qp)
                db.commit()
                print("[Seed] Seeded Question Paper.")

            # 7. Seed Roadmap
            existing_rm = db.query(Roadmap).filter(Roadmap.user_id == user.id).first()
            if not existing_rm:
                rm = Roadmap(
                    subject_id=primary_topic.subject_id,
                    user_id=user.id,
                    title="Strategic Biology Exam Roadmap",
                    structure_json=json.dumps({
                        "title": "Strategic Biology Exam Roadmap",
                        "subject_name": "Molecular & Cell Biology",
                        "total_estimated_hours": 20,
                        "phases": [
                            {
                                "phase_number": 1,
                                "name": "Phase 1: Core Fundamentals & Membranes",
                                "timeframe": "Week 1",
                                "summary": "Establish strong mental models of lipid bilayers and transport energetics.",
                                "tasks": [
                                    {"id": "task-1", "title": "Read Cell Membrane Architecture Notes", "topic_name": "Cell Membrane Architecture", "task_type": "learn", "estimated_minutes": 25, "completed": True},
                                    {"id": "task-2", "title": "Take Diagnostic Quiz on Active Transport", "topic_name": "Active & Passive Transport", "task_type": "quiz", "estimated_minutes": 20, "completed": False},
                                    {"id": "task-3", "title": "Review Due Flashcards", "topic_name": "Cell Membrane Architecture", "task_type": "review", "estimated_minutes": 15, "completed": False},
                                ]
                            },
                            {
                                "phase_number": 2,
                                "name": "Phase 2: Molecular Genetics & Pedigrees",
                                "timeframe": "Week 2",
                                "summary": "Master monohybrid and dihybrid crosses and chromosome segregation.",
                                "tasks": [
                                    {"id": "task-4", "title": "Study Mendelian Inheritance Laws", "topic_name": "Mendelian Genetics", "task_type": "learn", "estimated_minutes": 35, "completed": False},
                                    {"id": "task-5", "title": "Complete Genetics Practice Set", "topic_name": "Mendelian Genetics", "task_type": "quiz", "estimated_minutes": 30, "completed": False},
                                ]
                            }
                        ]
                    })
                )
                db.add(rm)
                db.commit()
                print("[Seed] Seeded Roadmap.")

            # 8. Seed Tutor Conversation
            existing_tutor = db.query(TutorConversation).filter(TutorConversation.user_id == user.id).first()
            if not existing_tutor:
                conv = TutorConversation(
                    topic_id=primary_topic.id,
                    user_id=user.id,
                    title="Transport Mechanisms & ATPase Pump",
                )
                db.add(conv)
                db.commit()
                db.refresh(conv)

                m1 = TutorMessage(
                    conversation_id=conv.id,
                    sender="user",
                    content="Why is the sodium-potassium pump referred to as electrogenic?",
                )
                m2 = TutorMessage(
                    conversation_id=conv.id,
                    sender="assistant",
                    content=(
                        "Great question! The sodium-potassium pump is electrogenic because it produces a net movement of charge across the cell membrane.\n\n"
                        "Specifically, in every single cycle:\n"
                        "- It expels **3 positive Na+ ions** out of the cell.\n"
                        "- It imports only **2 positive K+ ions** into the cell.\n\n"
                        "This disparity yields a net loss of one positive charge (+1) from inside the cell per cycle, directly generating an electrical potential that makes the inside slightly more negative relative to the outside."
                    ),
                )
                db.add_all([m1, m2])
                db.commit()
                print("[Seed] Seeded Tutor Conversation.")

            # 9. Seed Study Sessions & Plan Sessions for Dashboard
            existing_sess = db.query(StudySession).filter(StudySession.user_id == user.id).first()
            if not existing_sess:
                # Log study sessions across past 7 days
                for days_ago in range(7, -1, -1):
                    mins = 25 if days_ago % 2 == 0 else 50
                    sess = StudySession(
                        user_id=user.id,
                        subject_id=primary_topic.subject_id,
                        topic_id=primary_topic.id,
                        duration_minutes=mins,
                        session_type="pomodoro" if days_ago % 2 == 0 else "review",
                        notes="Completed focused revision block.",
                        created_at=now - timedelta(days=days_ago),
                        completed_at=now - timedelta(days=days_ago) + timedelta(minutes=mins),
                    )
                    db.add(sess)

                # Today's plan sessions
                p1 = PlanSession(
                    user_id=user.id,
                    subject_id=primary_topic.subject_id,
                    topic_id=second_topic.id,
                    scheduled_date=today,
                    scheduled_order=1,
                    duration_minutes=25,
                    session_type="quiz",
                    status="pending",
                    reason="Low topic mastery (42%) and upcoming exam in 12 days.",
                )
                p2 = PlanSession(
                    user_id=user.id,
                    subject_id=primary_topic.subject_id,
                    topic_id=primary_topic.id,
                    scheduled_date=today,
                    scheduled_order=2,
                    duration_minutes=25,
                    session_type="review",
                    status="pending",
                    reason="2 flashcards due today for spaced repetition.",
                )
                db.add_all([p1, p2])
                db.commit()
                print("[Seed] Seeded Study Sessions and Plan Sessions.")

        print("[Seed] ALL COMPREHENSIVE DEMO DATA POPULATED SUCCESSFULLY!")
    finally:
        db.close()


if __name__ == "__main__":
    populate_comprehensive_demo_data()
