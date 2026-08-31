from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.api.health import router as health_router
from backend.app.ingestion.webhook import router as webhook_router
from backend.app.api.dashboard import router as dashboard_router
from backend.app.api.cases import router as cases_router
from backend.app.api.policy import router as policy_router
from backend.app.api.simulator import router as simulator_router
from backend.app.api.contacts import router as contacts_router
from backend.app.api.audit import router as audit_router
from backend.app.api.integration import router as integration_router

from backend.app.core.state_machine import InvalidStateTransitionError
from backend.app.core.idempotency import DuplicateEventError, DuplicateActionError

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="RecoverAI — AI Revenue Recovery Control Plane for Razorpay Merchants",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(InvalidStateTransitionError)
async def invalid_state_transition_handler(request: Request, exc: InvalidStateTransitionError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": {
                "code": "INVALID_STATE_TRANSITION",
                "message": str(exc),
                "details": {
                    "current_state": exc.current_state,
                    "target_state": exc.target_state,
                    "reason": exc.reason
                }
            }
        }
    )

@app.exception_handler(DuplicateEventError)
async def duplicate_event_handler(request: Request, exc: DuplicateEventError):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "data": {
                "status": "IDEMPOTENT_REPLAY",
                "external_event_id": exc.external_event_id,
                "message": "Event already processed."
            }
        }
    )

@app.exception_handler(DuplicateActionError)
async def duplicate_action_handler(request: Request, exc: DuplicateActionError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": {
                "code": "DUPLICATE_ACTION",
                "message": str(exc),
                "details": {"idempotency_key": exc.idempotency_key}
            }
        }
    )

# Include All API Routers
app.include_router(health_router)
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(webhook_router)
app.include_router(dashboard_router)
app.include_router(cases_router)
app.include_router(policy_router)
app.include_router(simulator_router)
app.include_router(contacts_router)
app.include_router(audit_router)
app.include_router(integration_router)
