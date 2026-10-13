import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.routes import router as api_router
from app.core.config import settings
from app.database.database import Base, engine, SessionLocal
from app.database.seed import seed_database
from app.models import Bloom, Question, Subject, Unit, User  # noqa: F401


if os.environ.get("AI_PROVIDER", "gemini").lower() in {
    "v17_2",
    "v17.2",
    "flan_t5_v17_2",
}:
    from app.services.ai.v17_2_inference_adapter import V17_2InferenceAdapter

    v17_2_adapter = V17_2InferenceAdapter()
    if not v17_2_adapter.is_available():
        raise RuntimeError("V17.2 checkpoint integrity verification failed; refusing to start")

app = FastAPI(
    title="Automated Question Paper Generator API",
    description="Backend API for the AI-powered question paper generation system.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    import logging
    logging.getLogger("uvicorn.error").exception("Unhandled server exception: %s", exc)
    origin = request.headers.get("origin")
    headers = {}
    if origin and (origin in settings.BACKEND_CORS_ORIGINS or "*" in settings.BACKEND_CORS_ORIGINS):
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    elif settings.BACKEND_CORS_ORIGINS:
        headers["Access-Control-Allow-Origin"] = settings.BACKEND_CORS_ORIGINS[0]
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
        headers=headers,
    )

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
def create_tables():
    """Create database tables, ensure schema migrations, and seed sample data on startup."""
    try:
        from sqlalchemy import text
        Base.metadata.create_all(bind=engine)
        
        # Check and add optional columns if not present (MySQL/SQLite migration safety)
        with engine.connect() as conn:
            # Questions columns
            for col, col_def in [
                ("question_type", "VARCHAR(50) DEFAULT 'Short Answer'"),
                ("answer", "TEXT"),
                ("explanation", "TEXT"),
                ("source", "VARCHAR(200) DEFAULT 'Question Bank'"),
                ("source_type", "VARCHAR(50) DEFAULT 'teacher'"),
                ("is_ai_generated", "BOOLEAN DEFAULT 0"),
                ("approved", "BOOLEAN DEFAULT 1"),
                ("status", "VARCHAR(50) DEFAULT 'approved'"),
                ("active", "BOOLEAN DEFAULT 1"),
                ("numerical_data", "TEXT NULL"),
                ("application_context", "TEXT NULL"),
                ("board_id", "INT NULL"),
                ("academic_year_id", "INT NULL"),
                ("class_id", "INT NULL"),
                ("topic_id", "INT NULL"),
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE questions ADD COLUMN {col} {col_def}"))
                    conn.commit()
                except Exception:
                    pass

            # Subjects columns
            for col, col_def in [
                ("board_id", "INT NULL"),
                ("academic_year_id", "INT NULL"),
                ("class_id", "INT NULL"),
                ("stream_id", "INT NULL"),
                ("subject_code", "VARCHAR(50) NULL"),
                ("subject_type", "VARCHAR(50) DEFAULT 'core'"),
                ("source_url", "VARCHAR(255) NULL"),
                ("active", "BOOLEAN DEFAULT 1"),
                ("last_synced_at", "DATETIME NULL"),
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE subjects ADD COLUMN {col} {col_def}"))
                    conn.commit()
                except Exception:
                    pass

            # Units columns
            for col, col_def in [
                ("unit_number", "INT NULL"),
                ("description", "TEXT NULL"),
                ("source_url", "VARCHAR(255) NULL"),
                ("active", "BOOLEAN DEFAULT 1"),
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE units ADD COLUMN {col} {col_def}"))
                    conn.commit()
                except Exception:
                    pass

            # Boards columns
            for col, col_def in [
                ("active", "BOOLEAN DEFAULT 1"),
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE boards ADD COLUMN {col} {col_def}"))
                    conn.commit()
                except Exception:
                    pass

            # Academic Classes columns
            for col, col_def in [
                ("active", "BOOLEAN DEFAULT 1"),
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE academic_classes ADD COLUMN {col} {col_def}"))
                    conn.commit()
                except Exception:
                    pass

            # Topics columns
            for col, col_def in [
                ("active", "BOOLEAN DEFAULT 1"),
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE topics ADD COLUMN {col} {col_def}"))
                    conn.commit()
                except Exception:
                    pass



        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()
    except Exception as exc:
        print(f"Database initialization error: {exc}")





@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}
