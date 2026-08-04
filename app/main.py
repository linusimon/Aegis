import sys
import asyncio

if sys.platform == "win32":
    # Force ProactorEventLoop
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    # Prevent uvicorn from overriding it
    _orig_set_policy = asyncio.set_event_loop_policy
    def custom_set_policy(policy):
        if isinstance(policy, asyncio.WindowsSelectorEventLoopPolicy):
            return
        _orig_set_policy(policy)
    asyncio.set_event_loop_policy = custom_set_policy

from datetime import datetime, timezone
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.data_routes import router as data_router
from app.api.forecast_routes import router as forecast_router
from app.api.advisory_routes import router as advisory_router
from app.api.simulation_routes import router as simulation_router
from app.api.agent_routes import router as agent_router
from app.api.feedback_routes import router as feedback_router
from app.api.whatif_routes import router as whatif_router
from app.api.diagnostics_routes import router as diagnostics_router
from app.api.auth_routes import router as auth_router

app = FastAPI(
    title="AI-Driven Infrastructure Capacity Planning Advisor API",
    description="Backend API powered by LangGraph Multi-Agent, MCP SQLite Stdio, and RAG Knowledge Engine.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


@app.exception_handler(Exception)
async def debug_exception_handler(request, exc):
    import traceback
    print("=== DEBUG EXCEPTION HANDLER ===")
    traceback.print_exc()
    print("================================")
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": traceback.format_exc()}
    )

# Enable CORS for interactive web frontend (including Angular dev server on port 4200)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount Routers
app.include_router(auth_router)
app.include_router(data_router)
app.include_router(forecast_router)
app.include_router(advisory_router)
app.include_router(simulation_router)
app.include_router(whatif_router)
app.include_router(diagnostics_router)
app.include_router(agent_router)
app.include_router(feedback_router)

# Mount Static Web App Frontend
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def serve_dashboard():
    """Serve the Aegis AI Infrastructure Capacity Advisor Web Dashboard."""
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/health")
def health_check():
    """Health check endpoint confirming API status."""
    return {
        "status": "healthy",
        "service": "AI Infrastructure Capacity Planning Advisor",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
