from fastapi import APIRouter, HTTPException
from backend.models.session_models import UserSession
from backend.services.chat_service import chat_service
from backend.utils.helpers import generate_id

router = APIRouter(prefix="/api/session", tags=["Session"])

@router.post("/new", response_model=UserSession)
async def create_new_session():
    new_sess = chat_service.get_or_create_session()
    return new_sess

@router.get("/{session_id}", response_model=UserSession)
async def get_session(session_id: str):
    sess = chat_service.get_or_create_session(session_id)
    return sess

@router.post("/{session_id}/reset")
async def reset_session(session_id: str):
    sess = chat_service.get_or_create_session(session_id)
    sess.active_challenge = None
    sess.answer_unlocked = False
    sess.current_mood = "neutral"
    sess.unlocked_answer_text = None
    return {"status": "ok", "message": "Session reset."}
