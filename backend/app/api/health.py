from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.schemas.base import HealthResponse, ReadinessResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse, summary="Liveness check endpoint")
def health_check():
    return HealthResponse(status="ok")

@router.get("/ready", response_model=ReadinessResponse, summary="Readiness check endpoint")
def readiness_check(db: Session = Depends(get_db)):
    db_healthy = False
    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception as e:
        db_healthy = False
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity check failed: {str(e)}"
        )
        
    return ReadinessResponse(
        status="ready" if db_healthy else "not_ready",
        database=db_healthy,
        environment=settings.ENVIRONMENT
    )
