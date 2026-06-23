"""
AI Application Compiler — Backend Entry Point.

FastAPI application that serves the compiler pipeline API.
Converts natural language software requirements into structured
application specifications through a multi-stage pipeline.

Day 1: Intent Extraction active.
Day 2: System Design active.
Day 3: Schema Generation active.
Day 4: Validation active.
Day 5: Repair active.
Day 6: Runtime Simulator active.
Day 7: Evaluation Framework active.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import generate, evaluation, auth, user

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

# Load environment variables from .env file
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Application Lifecycle
# ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager.

    Handles startup and shutdown events.
    Database connections will be initialized here in future stages.
    """
    # Startup
    logger.info("=" * 60)
    logger.info("AI Application Compiler — Starting Up")
    logger.info("=" * 60)

    # Optional verification of environment
    if not os.getenv("GEMINI_API_KEY"):
        logger.warning(
            "GEMINI_API_KEY is not set. Generative stages will fail. Set it in your .env file or environment."
        )

    # TODO: Initialize PostgreSQL connection pool here in Day 2+
    # db_url = os.getenv("DATABASE_URL")
    # if db_url:
    #     logger.info("Connecting to PostgreSQL...")

    logger.info("Pipeline stages loaded:")
    logger.info("  ✅ Stage 1: Intent Extraction (active)")
    logger.info("  ✅ Stage 2: System Design (active)")
    logger.info("  ✅ Stage 3: Schema Generation (active)")
    logger.info("  ✅ Stage 4: Validation (active)")
    logger.info("  ✅ Stage 5: Repair (active)")
    logger.info("  ✅ Stage 6: Runtime Simulation (active)")
    logger.info("  ✅ Stage 7: Evaluation Framework (active)")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("AI Application Compiler — Shutting Down")
    # TODO: Close database connections here in Day 2+


# ──────────────────────────────────────────────
# FastAPI App
# ──────────────────────────────────────────────

app = FastAPI(
    title="AI Application Compiler",
    description=(
        "Converts natural language software requirements into structured "
        "application specifications through a multi-stage compiler pipeline. "
        "Stages: Intent Extraction → System Design → Schema Generation → Validation → Repair → Runtime → Evaluation."
    ),
    version="0.7.0",
    lifespan=lifespan,
)

# CORS — allow the Next.js frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "")
cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if FRONTEND_URL:
    cors_origins.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ] + ([FRONTEND_URL] if FRONTEND_URL else []),
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
@app.on_event("startup")
async def startup_event():
    if os.environ.get("DATABASE_URL"):
        from database import init_db
        init_db()

app.include_router(generate.router)
app.include_router(evaluation.router)
app.include_router(auth.router)
app.include_router(user.router)


# ──────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────

@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint.

    Returns the server status and which pipeline stages are available.
    """
    return {
        "status": "healthy",
        "version": "0.7.0",
        "stages": {
            "intent_extraction": "active",
            "system_design": "active",
            "schema_generation": "active",
            "validation": "active",
            "repair": "active",
            "runtime_simulation": "active",
            "evaluation_framework": "active",
        },
    }
