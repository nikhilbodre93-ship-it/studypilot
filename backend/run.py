import os
import subprocess
import sys

# 1. Run database migrations / initialize tables
try:
    print("Running Alembic database migrations...", flush=True)
    res = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
    if res.returncode == 0:
        print("Database migrations applied successfully.", flush=True)
    else:
        print(f"Alembic notice: {res.stderr}. Applying Base.metadata fallback...", flush=True)
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

# 2. Determine target port safely
raw_port = os.environ.get("PORT", "10000")
try:
    port = int(raw_port)
except ValueError:
    port = 10000

print(f"Starting StudyPilot API server on 0.0.0.0:{port} ...", flush=True)

# 3. Launch Uvicorn
import uvicorn
uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
