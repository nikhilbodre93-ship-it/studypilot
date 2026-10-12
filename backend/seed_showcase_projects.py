import json
from datetime import datetime, date, timedelta, timezone
from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.topic_mastery import TopicMastery
from app.models.note import Note
from app.models.quiz import Quiz, Question, QuizAttempt, AttemptAnswer
from app.models.flashcard import Flashcard, CardReview
from app.models.question_paper import QuestionPaper
from app.models.roadmap import Roadmap
from app.models.study_session import StudySession
from app.models.plan_session import PlanSession


def seed_two_showcase_projects():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    now = datetime.now(timezone.utc)
    today = now.date()

    # The 2 showcase projects / subjects
    PROJECTS = [
        {
            "name": "Database Management Systems (DBMS)",
            "description": "Enterprise database engineering, relational algebra, ACID transactions, B+ tree indexing, and distributed concurrency control.",
            "exam_date": today + timedelta(days=18),
            "color": "#1E3A8A", # Deep Indigo / Navy
            "topics": [
                {
                    "name": "Relational Model & SQL Schema Architecture",
                    "difficulty": "medium",
                    "mastery": 0.78,
                    "acc": 0.82,
                    "reviews": 5,
                    "note_title": "Comprehensive Guide: Relational Schema & Integrity Constraints",
                    "note_content": """# Relational Model & SQL Schema Architecture

## 1. Core Definition & Foundations
The relational model structures data into mathematical relations (tables) with tuples (rows) and attributes (columns). Introduced by E.F. Codd, it establishes independence between physical storage and logical representations.

### Essential Integrity Constraints:
- **Domain Constraint**: Attribute values must strictly belong to the defined atomic data type domain.
- **Entity Integrity**: The Primary Key uniquely identifies each tuple and cannot accept NULL values.
- **Referential Integrity**: A Foreign Key in a referencing relation must either match an existing Primary Key in the referenced relation or be explicitly NULL.

```sql
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE employees (
    emp_id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    dept_id INT REFERENCES departments(dept_id) ON DELETE CASCADE,
    salary NUMERIC(10, 2) CHECK (salary > 0)
);
```

## 2. Relational Algebra Operations
- **Selection (σ)**: Filters horizontal subsets of tuples matching a predicate: $\\sigma_{salary > 50000}(employees)$.
- **Projection (π)**: Extracts vertical subsets of specified attributes: $\\pi_{full\\_name, salary}(employees)$.
- **Natural Join (⋈)**: Combines relations on matching common attributes, projecting out duplicate join keys.

## 3. High-Yield Exam Takeaways
1. Entity integrity strictly enforces non-null primary keys.
2. Referential integrity prevents orphan rows via `ON DELETE CASCADE` or `ON DELETE SET NULL`.
3. Relational algebra forms the underlying declarative blueprint that query optimizers rewrite into efficient physical execution trees.
"""
                },
                {
                    "name": "Transaction Management & ACID Properties",
                    "difficulty": "hard",
                    "mastery": 0.52,
                    "acc": 0.58,
                    "reviews": 4,
                    "note_title": "Mastery Notes: Transaction Processing & ACID Guarantees",
                    "note_content": """# Transaction Management & ACID Properties

## 1. Definition of a Database Transaction
A transaction is a logical unit of database processing that includes one or more database access operations (read, write, commit, abort). It transitions the database between valid states.

## 2. The ACID Criteria Explained
- **Atomicity (All-or-Nothing)**: Either all operations in the transaction execute successfully, or the entire transaction is rolled back. Enforced via Write-Ahead Logging (WAL) and Undo logs.
- **Consistency (State Validity)**: Execution of a transaction in isolation preserves all database integrity constraints and business rules.
- **Isolation (Concurrent Independence)**: Intermediate states of concurrently executing transactions remain invisible to each other.
- **Durability (Persistence)**: Once a transaction issues `COMMIT`, its updates survive hardware crashes, power outages, and system restarts.

```
+-------------------------------------------------------------+
|                      ACID CRITERIA                          |
+-------------------+-----------------------------------------+
| Atomicity         | WAL / Undo Logging (All or Nothing)     |
| Consistency       | Schema Constraints & Serializability    |
| Isolation         | 2PL, Lock Managers & MVCC               |
| Durability        | Redo Logging & Non-Volatile Disk Flush  |
+-------------------+-----------------------------------------+
```

## 3. Isolation Levels & Concurrency Anomalies
1. **Read Uncommitted**: Suffers from Dirty Reads (reading uncommitted data).
2. **Read Committed**: Solves Dirty Reads; suffers from Non-Repeatable Reads.
3. **Repeatable Read**: Solves Non-Repeatable Reads; may suffer from Phantom Reads.
4. **Serializable**: Full serial execution equivalence; eliminates all anomalies.
"""
                },
                {
                    "name": "Relational Normalization (1NF, 2NF, 3NF, BCNF)",
                    "difficulty": "hard",
                    "mastery": 0.44,
                    "acc": 0.50,
                    "reviews": 3,
                    "note_title": "Exam Breakdown: Functional Dependencies & Normal Forms",
                    "note_content": """# Relational Normalization (1NF to BCNF)

## 1. Motivation for Normalization
Decomposing relations prevents data redundancy, update anomalies, insertion anomalies, and deletion anomalies while ensuring lossless join decomposition and dependency preservation.

## 2. Step-by-Step Normal Forms
- **First Normal Form (1NF)**: Every attribute contains only atomic (indivisible) values; no repeating groups or arrays.
- **Second Normal Form (2NF)**: Must be in 1NF, and every non-prime attribute is fully functionally dependent on the primary key (eliminates partial key dependencies).
- **Third Normal Form (3NF)**: Must be in 2NF, and no non-prime attribute is transitively dependent on any candidate key (if $X \\rightarrow Y$, then $X$ is a superkey OR $Y$ is a prime attribute).
- **Boyce-Codd Normal Form (BCNF)**: Strictly requires that for every non-trivial functional dependency $X \\rightarrow Y$, the determinant $X$ must be a superkey.

## 3. Key Comparison: 3NF vs BCNF
BCNF is strictly stronger than 3NF. While 3NF guarantees both lossless join and dependency preservation, certain relations cannot be decomposed into BCNF without sacrificing dependency preservation.
"""
                },
                {
                    "name": "Indexing, B+ Trees & Query Optimization",
                    "difficulty": "hard",
                    "mastery": 0.60,
                    "acc": 0.65,
                    "reviews": 4,
                    "note_title": "Architecture: B+ Tree Storage & Query Planner Execution",
                    "note_content": """# Indexing, B+ Trees & Query Optimization

## 1. Why B+ Trees for Disk Storage?
Unlike standard binary search trees or B-trees, B+ trees store all actual record pointers strictly in the leaf nodes, while internal nodes store only routing keys. Leaf nodes are linked via bidirectional pointers for extremely fast range scans ($O(\\log_B N)$ height with high fan-out).

## 2. Clustered vs Non-Clustered Indexes
- **Clustered Index**: Determines the physical ordering of data pages on disk. There can only be ONE clustered index per table (typically the Primary Key).
- **Non-Clustered (Secondary) Index**: A separate auxiliary B+ tree containing indexed keys pointing to the clustered index key or RID.
"""
                },
                {
                    "name": "Concurrency Control & Recovery Protocols",
                    "difficulty": "medium",
                    "mastery": 0.70,
                    "acc": 0.75,
                    "reviews": 5,
                    "note_title": "Mechanics: Two-Phase Locking, Deadlocks & ARIES Recovery",
                    "note_content": """# Concurrency Control & Recovery Protocols

## 1. Two-Phase Locking (2PL)
- **Growing Phase**: Transaction may acquire locks (Shared or Exclusive) but cannot release any lock.
- **Shrinking Phase**: Transaction releases locks but cannot acquire new locks.
- **Strict 2PL**: Holds all exclusive locks until transaction commit/abort, guaranteeing strict serializability and preventing cascading rollbacks.

## 2. ARIES Recovery Algorithm
1. **Analysis Phase**: Identifies dirty pages in buffer pool and active transactions at time of crash.
2. **Redo Phase**: Repeats history from the oldest unwritten log record forward.
3. **Undo Phase**: Rolls back operations of all transactions that were active (uncommitted) at crash time.
"""
                }
            ],
            "flashcards": [
                {
                    "front": "What does the 'I' in ACID stand for, and what mechanism enforces it?",
                    "back": "Isolation. It guarantees that concurrently executing transactions do not interfere with each other, enforced via Two-Phase Locking (2PL) or Multi-Version Concurrency Control (MVCC).",
                    "explanation": "Isolation prevents dirty reads, non-repeatable reads, and phantom reads.",
                    "difficulty": "medium"
                },
                {
                    "front": "What is the difference between 3NF and BCNF?",
                    "back": "In 3NF, for any X -> Y, X must be a superkey OR Y must be a prime attribute. In BCNF, X must ALWAYS be a superkey with no exceptions.",
                    "explanation": "BCNF is strictly stronger than 3NF and eliminates all functional redundancy.",
                    "difficulty": "hard"
                },
                {
                    "front": "Why are B+ Trees preferred over B-Trees for database indexing?",
                    "back": "B+ Trees store all data records strictly at the leaf level and link leaves sequentially, maximizing node fan-out and dramatically speeding up range scans.",
                    "explanation": "Higher fan-out reduces the tree height, minimizing expensive disk I/O operations.",
                    "difficulty": "hard"
                },
                {
                    "front": "What is the primary difference between a Clustered and Non-Clustered Index?",
                    "back": "A Clustered index physically sorts the data rows on disk (only 1 per table). A Non-Clustered index is an auxiliary structure containing pointers to data rows.",
                    "explanation": "Clustered indexes provide the fastest range queries on the primary key.",
                    "difficulty": "medium"
                },
                {
                    "front": "What is Strict Two-Phase Locking (Strict 2PL)?",
                    "back": "A concurrency control protocol where a transaction holds all its exclusive locks until it commits or aborts.",
                    "explanation": "Prevents cascading rollbacks and guarantees serializable transaction schedules.",
                    "difficulty": "medium"
                },
                {
                    "front": "What are the three phases of the ARIES database crash recovery algorithm?",
                    "back": "1. Analysis Phase (identifies active transactions)\n2. Redo Phase (repeats history to restore state)\n3. Undo Phase (rolls back uncommitted transactions).",
                    "explanation": "Standard Write-Ahead Logging recovery paradigm used in relational engines.",
                    "difficulty": "hard"
                }
            ],
            "quiz_title": "Mastery Assessment: Database Systems & Transaction Architecture",
            "quiz_questions": [
                {
                    "text": "Which ACID property ensures that committed transactions survive subsequent hardware power failures?",
                    "type": "multiple_choice",
                    "options": ["Atomicity", "Consistency", "Isolation", "Durability"],
                    "correct": "Durability",
                    "explanation": "Durability guarantees persistence of committed updates via non-volatile storage and WAL redo logs."
                },
                {
                    "text": "A relation is in BCNF if for every non-trivial functional dependency X -> Y, X is a:",
                    "type": "multiple_choice",
                    "options": ["Prime Attribute", "Superkey", "Composite Key", "Foreign Key"],
                    "correct": "Superkey",
                    "explanation": "BCNF strictly requires the determinant X to be a superkey for every functional dependency."
                },
                {
                    "text": "True or False: A table can have multiple clustered indexes if they cover different columns.",
                    "type": "true_false",
                    "options": ["True", "False"],
                    "correct": "False",
                    "explanation": "A table can have only ONE clustered index because data rows can only be physically sorted on disk in one order."
                },
                {
                    "text": "What type of transaction anomaly occurs when a transaction reads data modified by an uncommitted transaction?",
                    "type": "multiple_choice",
                    "options": ["Dirty Read", "Non-Repeatable Read", "Phantom Read", "Write Skew"],
                    "correct": "Dirty Read",
                    "explanation": "Dirty reads occur at the Read Uncommitted isolation level when uncommitted writes are observed."
                },
                {
                    "text": "Which phase of Strict 2PL allows releasing exclusive locks?",
                    "type": "multiple_choice",
                    "options": ["Growing Phase", "Shrinking Phase", "Only at Commit/Abort", "Analysis Phase"],
                    "correct": "Only at Commit/Abort",
                    "explanation": "Strict 2PL holds exclusive locks until transaction commit or abort to prevent cascading aborts."
                }
            ]
        },
        {
            "name": "Full-Stack Web Development & Cloud Systems",
            "description": "Modern frontend architectures, RESTful backend APIs, JWT authentication, Docker containerization, and cloud deployment pipelines.",
            "exam_date": today + timedelta(days=28),
            "color": "#0D9488", # Deep Teal
            "topics": [
                {
                    "name": "Client-Server Architecture & RESTful API Design",
                    "difficulty": "medium",
                    "mastery": 0.85,
                    "acc": 0.90,
                    "reviews": 6,
                    "note_title": "Foundations: HTTP Protocol & REST Architectural Constraints",
                    "note_content": """# Client-Server Architecture & RESTful API Design

## 1. Core Principles of REST
Representational State Transfer (REST) is an architectural style for distributed hypermedia systems formalized by Roy Fielding:
1. **Client-Server Separation**: UI concerns are decoupled from data storage concerns.
2. **Statelessness**: Every request contains all context needed; the server stores no client session context.
3. **Cacheability**: Responses explicitly declare themselves cacheable or non-cacheable (`Cache-Control`, `ETag`).
4. **Uniform Interface**: Resource identification via URIs (`/api/v1/users/12`), resource manipulation through representations, self-descriptive messages, and HATEOAS.

## 2. HTTP Methods & Idempotency
- `GET`: Safe and idempotent. Retrieves resource representation without side effects.
- `POST`: Non-idempotent. Creates subordinate resources or executes commands.
- `PUT`: Idempotent. Replaces target resource state entirely.
- `PATCH`: Non-idempotent in theory. Applies partial delta modifications to a resource.
- `DELETE`: Idempotent. Removes target resource representation.
"""
                },
                {
                    "name": "Authentication, JWT & Security Primitives",
                    "difficulty": "hard",
                    "mastery": 0.55,
                    "acc": 0.60,
                    "reviews": 4,
                    "note_title": "Security: JSON Web Tokens, OAuth2 & Web Threat Mitigation",
                    "note_content": """# Authentication, JWT & Security Primitives

## 1. JSON Web Token (JWT) Anatomy
A JWT consists of three base64url-encoded parts separated by periods:
1. **Header**: Cryptographic algorithm and token type (`{"alg": "HS256", "typ": "JWT"}`).
2. **Payload**: Registered and custom claims (`sub`, `exp`, `iat`, `role`).
3. **Signature**: Computed over Header + Payload using a secret key: `HMACSHA256(base64Url(header) + "." + base64Url(payload), secret)`.

## 2. Essential Web Security Defenses
- **Cross-Origin Resource Sharing (CORS)**: Browser security mechanism restricting resource sharing across origins.
- **Cross-Site Scripting (XSS)**: Mitigated via Content Security Policy (CSP), HTML escaping, and storing tokens in `HttpOnly; Secure; SameSite=Strict` cookies.
- **Cross-Site Request Forgery (CSRF)**: Mitigated using anti-CSRF synchronizer tokens and strict SameSite cookies.
"""
                },
                {
                    "name": "State Management & Asynchronous Data Fetching",
                    "difficulty": "medium",
                    "mastery": 0.72,
                    "acc": 0.78,
                    "reviews": 5,
                    "note_title": "Frontend Engineering: React Virtual DOM, Hooks & React Query",
                    "note_content": """# State Management & Asynchronous Data Fetching

## 1. React Virtual DOM & Reconciliation
React maintains a lightweight virtual representation of the UI tree. When state changes occur:
1. React executes render functions to produce a new Virtual DOM tree.
2. The Fiber reconciliation engine diffs the old and new trees ($O(N)$ heuristic diffing).
3. Batched mutation commits apply minimal patches directly to the real browser DOM.

## 2. Server State vs Client State
- **Client State**: Ephemeral UI state (modals open, active tabs, form inputs).
- **Server State**: Remote data owned by the backend (user profiles, database lists). Managed via tools like TanStack React Query for caching, background revalidation, deduplication, and optimistic updates.
"""
                },
                {
                    "name": "Containerization, Docker & Cloud Deployment",
                    "difficulty": "hard",
                    "mastery": 0.48,
                    "acc": 0.52,
                    "reviews": 3,
                    "note_title": "DevOps & Cloud: Docker OCI Images, Multi-Stage Builds & CI/CD",
                    "note_content": """# Containerization, Docker & Cloud Deployment

## 1. Containers vs Virtual Machines
- **Virtual Machines**: Hypervisor runs full guest operating systems on virtualized hardware (high memory overhead).
- **Docker Containers**: Share the host OS kernel and isolate processes using Linux namespaces (PID, NET, MNT) and cgroups (CPU, RAM limits).

## 2. Production Multi-Stage Dockerfile Pattern
```dockerfile
# Stage 1: Build Frontend Assets
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Minimal Production Web Server
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```
"""
                },
                {
                    "name": "Microservices & Distributed System Design",
                    "difficulty": "hard",
                    "mastery": 0.62,
                    "acc": 0.68,
                    "reviews": 4,
                    "note_title": "Architecture: Event-Driven Microservices & CAP Theorem",
                    "note_content": """# Microservices & Distributed System Design

## 1. Monolith vs Microservices Trade-offs
- Monoliths offer simple local debugging, unified deployment, and zero network latency between modules.
- Microservices provide independent service scalability, autonomous team deployments, and polyglot technology stacks, at the cost of distributed data management complexity.

## 2. Distributed Patterns
- **API Gateway**: Unified entry point handling SSL termination, rate limiting, and authentication.
- **Saga Pattern**: Coordinates distributed transactions across services using compensating transactions.
- **Message Queues (Kafka/RabbitMQ)**: Decouples service execution via asynchronous event streaming.
"""
                }
            ],
            "flashcards": [
                {
                    "front": "What does it mean for an HTTP method to be 'idempotent'?",
                    "back": "Making multiple identical requests produces the exact same server state as making a single request (e.g. GET, PUT, DELETE).",
                    "explanation": "POST is non-idempotent because repeated calls create multiple resources.",
                    "difficulty": "medium"
                },
                {
                    "front": "What are the three components of a JSON Web Token (JWT)?",
                    "back": "1. Header (algorithm and type)\n2. Payload (claims and data)\n3. Signature (HMAC or RSA verification hash).",
                    "explanation": "The signature guarantees token integrity and detects tampering.",
                    "difficulty": "easy"
                },
                {
                    "front": "How do Docker containers differ from Virtual Machines?",
                    "back": "Containers share the host OS kernel and isolate processes via namespaces and cgroups, whereas VMs virtualize physical hardware and run full guest OS kernels.",
                    "explanation": "Containers start in milliseconds and consume vastly less RAM.",
                    "difficulty": "medium"
                },
                {
                    "front": "What is the CAP Theorem in distributed systems?",
                    "back": "A distributed system can guarantee at most two of: Consistency, Availability, and Partition Tolerance simultaneously.",
                    "explanation": "Because network partitions (P) are inevitable in real networks, systems must choose between Consistency (CP) or Availability (AP).",
                    "difficulty": "hard"
                },
                {
                    "front": "What is the difference between Server State and Client State in React?",
                    "back": "Server state is asynchronous, remotely owned data cached locally (React Query). Client state is synchronous, purely local UI interaction state (useState).",
                    "explanation": "Decoupling server state handles caching, background refetching, and deduping automatically.",
                    "difficulty": "medium"
                },
                {
                    "front": "How does storing JWTs in HttpOnly cookies protect against XSS attacks?",
                    "back": "HttpOnly cookies cannot be accessed or read by JavaScript (via document.cookie), preventing malicious injected scripts from stealing the authentication token.",
                    "explanation": "Standard defense-in-depth practice for browser web applications.",
                    "difficulty": "hard"
                }
            ],
            "quiz_title": "Mastery Assessment: Full-Stack Architecture & Cloud Systems",
            "quiz_questions": [
                {
                    "text": "Which HTTP method is designed to be idempotent and completely replace the target resource?",
                    "type": "multiple_choice",
                    "options": ["POST", "PUT", "PATCH", "CONNECT"],
                    "correct": "PUT",
                    "explanation": "PUT is idempotent and replaces the representation of the resource in its entirety."
                },
                {
                    "text": "True or False: A JWT payload is encrypted by default and its contents cannot be read by anyone without the secret key.",
                    "type": "true_false",
                    "options": ["True", "False"],
                    "correct": "False",
                    "explanation": "A standard JWT payload is merely Base64URL-encoded (not encrypted); anyone can decode and inspect its claims. The signature only verifies authenticity."
                },
                {
                    "text": "Which Linux kernel feature enables Docker to isolate process trees and network interfaces?",
                    "type": "multiple_choice",
                    "options": ["Namespaces", "Control Groups (cgroups)", "Hypervisor Ring 0", "Swap Partitioning"],
                    "correct": "Namespaces",
                    "explanation": "Namespaces isolate process IDs, network interfaces, and mount points; cgroups govern resource quotas (CPU/RAM)."
                },
                {
                    "text": "In the CAP theorem, what does Partition Tolerance (P) guarantee?",
                    "type": "multiple_choice",
                    "options": [
                        "The system continues to operate despite network packet loss or communication delays between nodes",
                        "All reads return the most recent write immediately",
                        "Every non-failing node returns a successful response without exception",
                        "The database automatically shards data into equal partitions"
                    ],
                    "correct": "The system continues to operate despite network packet loss or communication delays between nodes",
                    "explanation": "Partition tolerance means the distributed system functions even when messages between nodes are dropped."
                },
                {
                    "text": "What is the purpose of multi-stage Docker builds?",
                    "type": "multiple_choice",
                    "options": [
                        "To compile assets in a heavy build stage and copy only finished artifacts into a minimal, secure production image",
                        "To run multiple containers on the same port",
                        "To bypass Linux security namespaces",
                        "To automatically push images to Docker Hub during build"
                    ],
                    "correct": "To compile assets in a heavy build stage and copy only finished artifacts into a minimal, secure production image",
                    "explanation": "Multi-stage builds dramatically reduce Docker image size (e.g. from 1GB to 25MB) and eliminate compiler vulnerabilities in production."
                }
            ]
        }
    ]

    # Target users
    users = db.query(User).all()
    print(f"Found {len(users)} users in database to populate with showcase projects.")

    for user in users:
        print(f"\nProcessing user: {user.email} (ID: {user.id})")

        for p_data in PROJECTS:
            # Check or create Subject
            subject = db.query(Subject).filter(
                Subject.user_id == user.id,
                Subject.name == p_data["name"]
            ).first()

            if not subject:
                subject = Subject(
                    user_id=user.id,
                    name=p_data["name"],
                    description=p_data["description"],
                    exam_date=p_data["exam_date"],
                    color=p_data["color"]
                )
                db.add(subject)
                db.commit()
                db.refresh(subject)
                print(f"  [+] Created Subject: '{subject.name}' (ID: {subject.id})")
            else:
                subject.description = p_data["description"]
                subject.exam_date = p_data["exam_date"]
                subject.color = p_data["color"]
                db.commit()
                print(f"  [*] Updated existing Subject: '{subject.name}' (ID: {subject.id})")

            # Seed Topics
            created_topic_objs = []
            for idx, t_info in enumerate(p_data["topics"]):
                topic = db.query(Topic).filter(
                    Topic.subject_id == subject.id,
                    Topic.name == t_info["name"]
                ).first()

                if not topic:
                    topic = Topic(
                        subject_id=subject.id,
                        name=t_info["name"],
                        difficulty=t_info["difficulty"],
                        order_index=idx
                    )
                    db.add(topic)
                    db.commit()
                    db.refresh(topic)
                    print(f"    [+] Created Topic: '{topic.name}' (ID: {topic.id})")
                created_topic_objs.append(topic)

                # Seed Topic Mastery (BKT)
                mastery = db.query(TopicMastery).filter(
                    TopicMastery.user_id == user.id,
                    TopicMastery.topic_id == topic.id
                ).first()
                if not mastery:
                    mastery = TopicMastery(
                        user_id=user.id,
                        topic_id=topic.id,
                        score=t_info["mastery"] * 100.0,
                        p_mastery=t_info["mastery"],
                        observed_accuracy=t_info["acc"],
                        observed_total=t_info["reviews"],
                        observed_correct=max(1, int(t_info["reviews"] * t_info["acc"])),
                        review_count=t_info["reviews"],
                        last_reviewed_at=now - timedelta(days=idx),
                        next_review_due=now + timedelta(days=idx + 1)
                    )
                    db.add(mastery)
                else:
                    mastery.score = t_info["mastery"] * 100.0
                    mastery.p_mastery = t_info["mastery"]
                    mastery.observed_accuracy = t_info["acc"]
                    mastery.review_count = t_info["reviews"]
                db.commit()

                # Seed High-Yield Study Note
                existing_note = db.query(Note).filter(
                    Note.user_id == user.id,
                    Note.topic_id == topic.id
                ).first()
                if not existing_note:
                    note = Note(
                        user_id=user.id,
                        topic_id=topic.id,
                        title=t_info["note_title"],
                        content_markdown=t_info["note_content"],
                        is_ai_generated=True
                    )
                    db.add(note)
                    db.commit()
                    print(f"    [+] Created Note for topic '{topic.name}'")

            primary_topic = created_topic_objs[0]

            # Seed Flashcards
            existing_cards_count = db.query(Flashcard).filter(
                Flashcard.user_id == user.id,
                Flashcard.topic_id.in_([t.id for t in created_topic_objs])
            ).count()

            if existing_cards_count == 0:
                for c_idx, fc in enumerate(p_data["flashcards"]):
                    card_topic = created_topic_objs[c_idx % len(created_topic_objs)]
                    flashcard = Flashcard(
                        user_id=user.id,
                        topic_id=card_topic.id,
                        front=fc["front"],
                        back=fc["back"],
                        explanation=fc["explanation"],
                        difficulty=fc["difficulty"],
                        interval_days=max(1, c_idx * 2),
                        ease_factor=2.5,
                        repetitions=c_idx,
                        due_date=today + timedelta(days=c_idx - 1)
                    )
                    db.add(flashcard)
                db.commit()
                print(f"  [+] Seeded {len(p_data['flashcards'])} Flashcards for '{subject.name}'")

            # Seed Quiz
            existing_quiz = db.query(Quiz).filter(
                Quiz.user_id == user.id,
                Quiz.topic_id == primary_topic.id
            ).first()

            if not existing_quiz:
                quiz = Quiz(
                    user_id=user.id,
                    topic_id=primary_topic.id,
                    title=p_data["quiz_title"],
                    total_questions=len(p_data["quiz_questions"])
                )
                db.add(quiz)
                db.commit()
                db.refresh(quiz)

                for q_idx, q_data in enumerate(p_data["quiz_questions"]):
                    q_obj = Question(
                        quiz_id=quiz.id,
                        question_text=q_data["text"],
                        question_type=q_data["type"],
                        options_json=json.dumps(q_data["options"]) if q_data["options"] else None,
                        correct_answer=q_data["correct"],
                        explanation=q_data["explanation"],
                        order_index=q_idx
                    )
                    db.add(q_obj)
                db.commit()
                print(f"  [+] Seeded Practice Quiz with {len(p_data['quiz_questions'])} questions for '{subject.name}'")

            # Seed Question Paper
            existing_paper = db.query(QuestionPaper).filter(
                QuestionPaper.user_id == user.id,
                QuestionPaper.subject_id == subject.id
            ).first()

            if not existing_paper:
                sections_data = [
                    {
                        "name": "Section A: Conceptual & Multiple Choice",
                        "section_code": "A",
                        "total_marks": 20,
                        "questions": [
                            {
                                "id": "Q1",
                                "section": "A",
                                "question_text": f"Define the core architecture of {p_data['name']} and identify its primary integrity constraints.",
                                "marks": 5,
                                "options": None,
                                "model_answer": f"A comprehensive definition establishing the formal criteria, constraints, and operating guarantees of {p_data['name']}.",
                                "rubric": "3 marks for accurate theoretical definition, 2 marks for stating both integrity constraints."
                            }
                        ]
                    },
                    {
                        "name": "Section B: Analytical Mechanics & Proofs",
                        "section_code": "B",
                        "total_marks": 30,
                        "questions": [
                            {
                                "id": "Q2",
                                "section": "B",
                                "question_text": f"Differentiate the primary tradeoffs between performance and consistency in {p_data['name']}.",
                                "marks": 10,
                                "options": None,
                                "model_answer": "Clear analytical breakdown detailing how increasing consistency constraints impacts throughput and latency.",
                                "rubric": "5 marks for theoretical comparison, 5 marks for practical implementation examples."
                            }
                        ]
                    },
                    {
                        "name": "Section C: Advanced System Design & Synthesis",
                        "section_code": "C",
                        "total_marks": 50,
                        "questions": [
                            {
                                "id": "Q3",
                                "section": "C",
                                "question_text": f"Design an end-to-end production pipeline utilizing {p_data['name']}. Detail error recovery, fault tolerance, and scaling strategies.",
                                "marks": 20,
                                "options": None,
                                "model_answer": "In-depth architecture specification including schema layout, caching, logging, failover mechanisms, and performance profiling.",
                                "rubric": "8 marks for architecture layout, 6 marks for fault recovery, 6 marks for scaling strategy."
                            }
                        ]
                    }
                ]
                paper_content = {
                    "instructions": [
                        "Answer all questions in Section A.",
                        "Section B requires clear technical justifications.",
                        "Section C requires modular architectural specifications and diagrams."
                    ],
                    "sections": sections_data
                }
                paper = QuestionPaper(
                    user_id=user.id,
                    subject_id=subject.id,
                    title=f"Term Examination: {p_data['name']}",
                    duration_minutes=90,
                    total_marks=100,
                    content_json=json.dumps(paper_content)
                )
                db.add(paper)
                db.commit()
                print(f"  [+] Seeded Question Paper for '{subject.name}'")

            # Seed Learning Roadmap
            existing_roadmap = db.query(Roadmap).filter(
                Roadmap.user_id == user.id,
                Roadmap.subject_id == subject.id
            ).first()

            if not existing_roadmap:
                phases_data = [
                    {
                        "phase_number": 1,
                        "name": f"Phase 1: Foundations & Core Architecture",
                        "timeframe": "Week 1",
                        "summary": f"Master fundamental principles, definitions, and operational criteria for {p_data['name']}.",
                        "tasks": [
                            {
                                "id": "task-1",
                                "title": f"Review study notes on {p_data['topics'][0]['name']}",
                                "topic_name": p_data['topics'][0]['name'],
                                "task_type": "learn",
                                "estimated_minutes": 35,
                                "completed": True
                            },
                            {
                                "id": "task-2",
                                "title": f"Complete diagnostic quiz on foundational concepts",
                                "topic_name": p_data['topics'][0]['name'],
                                "task_type": "quiz",
                                "estimated_minutes": 20,
                                "completed": True
                            }
                        ]
                    },
                    {
                        "phase_number": 2,
                        "name": f"Phase 2: In-Depth Mechanisms & Protocols",
                        "timeframe": "Week 2",
                        "summary": f"Dive deep into {p_data['topics'][1]['name']} and advanced operational workflows.",
                        "tasks": [
                            {
                                "id": "task-3",
                                "title": f"Study notes & examples for {p_data['topics'][1]['name']}",
                                "topic_name": p_data['topics'][1]['name'],
                                "task_type": "learn",
                                "estimated_minutes": 45,
                                "completed": False
                            },
                            {
                                "id": "task-4",
                                "title": "Spaced flashcard session on high-yield exam traps",
                                "topic_name": p_data['topics'][1]['name'],
                                "task_type": "review",
                                "estimated_minutes": 25,
                                "completed": False
                            }
                        ]
                    },
                    {
                        "phase_number": 3,
                        "name": "Phase 3: Rigorous Exam Simulation & Problem Solving",
                        "timeframe": "Week 3",
                        "summary": "Take full-length timed mock question papers and target remaining knowledge gaps.",
                        "tasks": [
                            {
                                "id": "task-5",
                                "title": f"Complete 90-minute timed mock exam for {p_data['name']}",
                                "topic_name": p_data['topics'][2]['name'],
                                "task_type": "quiz",
                                "estimated_minutes": 90,
                                "completed": False
                            }
                        ]
                    }
                ]
                roadmap_structure = {
                    "title": f"Strategic Mastery Roadmap: {p_data['name']}",
                    "subject_name": p_data["name"],
                    "total_estimated_hours": 24,
                    "phases": phases_data
                }
                roadmap = Roadmap(
                    user_id=user.id,
                    subject_id=subject.id,
                    title=f"Strategic Mastery Roadmap: {p_data['name']}",
                    structure_json=json.dumps(roadmap_structure)
                )
                db.add(roadmap)
                db.commit()
                print(f"  [+] Seeded Learning Roadmap for '{subject.name}'")

            # Seed Study Sessions for Activity Graph
            existing_sessions = db.query(StudySession).filter(
                StudySession.user_id == user.id,
                StudySession.subject_id == subject.id
            ).count()

            if existing_sessions < 3:
                for day_offset in [1, 3, 5]:
                    session = StudySession(
                        user_id=user.id,
                        subject_id=subject.id,
                        topic_id=primary_topic.id,
                        duration_minutes=45 + day_offset * 5,
                        session_type="pomodoro",
                        notes=f"Deep revision session on {p_data['name']} - reviewed key mechanisms and flashcards.",
                        completed_at=now - timedelta(days=day_offset),
                        created_at=now - timedelta(days=day_offset)
                    )
                    db.add(session)
                db.commit()
                print(f"  [+] Seeded recent study sessions for activity analytics")

    print("\n[SUCCESS] Both showcase projects, topics, notes, flashcards, quizzes, roadmaps, and papers successfully seeded!")
    db.close()


if __name__ == "__main__":
    seed_two_showcase_projects()
