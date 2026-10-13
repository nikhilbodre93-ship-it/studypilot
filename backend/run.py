import os
import subprocess
import sys
from pathlib import Path

# Add backend directory to sys.path so app can be imported regardless of CWD
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# 1. Run database migrations / initialize tables
try:
    print("Running Alembic database migrations...", flush=True)
    res = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(backend_dir),
        capture_output=True,
        text=True,
    )
    if res.returncode == 0:
        print("Database migrations applied successfully.", flush=True)
    else:
        print(f"Alembic notice: {res.stderr.strip() if res.stderr else 'fallback'}. Applying Base.metadata fallback...", flush=True)
        from app.database import engine, Base
        import app.models
        Base.metadata.create_all(bind=engine)
        print("Database tables initialized successfully.", flush=True)
except Exception as e:
    print(f"Database setup note: {e}. Ensuring tables exist...", flush=True)
    try:
        from app.database import engine, Base
        import app.models
        Base.metadata.create_all(bind=engine)
        print("Database tables verified.", flush=True)
    except Exception as inner_e:
        print(f"Table verification note: {inner_e}", flush=True)

# 2. Automatically ensure demo account and seed data exist
try:
    from app.seed import seed_database
    seed_database()
    print("Demo account & initial study data initialized successfully.", flush=True)
except Exception as seed_err:
    print(f"Seed note: {seed_err}", flush=True)

# 3. Determine target port safely (default to 8000 for local dev and Vite proxy compatibility)
raw_port = os.environ.get("PORT", "8000")
try:
    port = int(raw_port)
except ValueError:
    port = 8000

print(f"Starting StudyPilot API server on 0.0.0.0:{port} ...", flush=True)

# 4. Launch Uvicorn
import uvicorn
uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")

