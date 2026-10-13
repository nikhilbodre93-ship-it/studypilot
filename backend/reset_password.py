"""CLI tool to reset any user's password in StudyPilot."""
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def reset_password(email: str, new_password: str):
    email = email.lower().strip()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Error: User with email '{email}' not found.")
            print("Existing users:")
            for u in db.query(User).all():
                print(f" - {u.email} ({u.full_name})")
            return False

        user.hashed_password = hash_password(new_password)
        db.add(user)
        db.commit()
        print(f"SUCCESS: Password for '{email}' has been reset to '{new_password}'.")
        return True
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python reset_password.py <email> <new_password>")
        print("Example: python reset_password.py demo@studypilot.io StudyPilot2026!")
        sys.exit(1)

    email_arg = sys.argv[1]
    pass_arg = sys.argv[2]
    success = reset_password(email_arg, pass_arg)
    sys.exit(0 if success else 1)
