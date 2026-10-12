import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.core.security import hash_password, create_access_token

# In-memory SQLite for high-speed isolated test execution
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clear_vector_store():
    from app.services.vector_store import global_vector_store
    global_vector_store._stores.clear()
    yield
    global_vector_store._stores.clear()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def user_a(db_session: Session) -> User:
    user = User(
        email="student.a@studypilot.io",
        hashed_password=hash_password("Password123!"),
        full_name="Student Alpha",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_b(db_session: Session) -> User:
    user = User(
        email="student.b@studypilot.io",
        hashed_password=hash_password("Password123!"),
        full_name="Student Beta",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def token_a(user_a: User) -> str:
    return create_access_token(subject=str(user_a.id), extra_claims={"email": user_a.email})


@pytest.fixture
def token_b(user_b: User) -> str:
    return create_access_token(subject=str(user_b.id), extra_claims={"email": user_b.email})


@pytest.fixture
def auth_headers_a(token_a: str) -> dict:
    return {"Authorization": f"Bearer {token_a}"}


@pytest.fixture
def auth_headers_b(token_b: str) -> dict:
    return {"Authorization": f"Bearer {token_b}"}
