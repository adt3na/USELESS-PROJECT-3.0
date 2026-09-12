from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.routes import chat, games, challenge, session
from backend.utils.helpers import logger

app = FastAPI(
    title="Vadakkunokki.ai API",
    description="Backend API for Vadakkunokki.ai - Retro Game AI Character Powered by Gemini",
    version="1.0.0",
    docs_url="/docs"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount sub-routers
app.include_router(chat.router)
app.include_router(games.router)
app.include_router(challenge.router)
app.include_router(session.router)

@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "online",
        "app": "Vadakkunokki.ai",
        "version": "1.0.0",
        "model": settings.GEMINI_MODEL
    }

# Friendly global exception handler per FR-044
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "type": "error",
            "mood": "chaotic",
            "message": "Uh oh. Even I don't know what happened. Something broke. Try again!",
            "action": None,
            "character_state": "CONFUSED"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=settings.PORT, reload=settings.DEBUG)
