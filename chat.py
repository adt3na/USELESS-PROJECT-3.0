import random
from fastapi import APIRouter, HTTPException
from backend.models.chat_models import ChatRequest, ChatResponse, StartupGreetingResponse, CharacterState
from backend.services.chat_service import chat_service
from backend.utils.helpers import generate_id

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty questions are not entertained!")
    return await chat_service.process_chat(req.session_id, req.message)

@router.get("/startup", response_model=StartupGreetingResponse)
async def startup_greeting():
    """
    FR-037 Application Startup Experience:
    Welcomes the user and immediately establishes Vadakkunokki's cheeky personality.
    """
    greetings = [
        "Oh. You came.",
        "Welcome. Unfortunately, I'm here.",
        "You actually opened me? Bold move.",
        "Ready to waste some time together?",
        "I know everything. But whether you get to hear it is another story."
    ]
    new_sess = chat_service.get_or_create_session()
    return StartupGreetingResponse(
        session_id=new_sess.session_id,
        mood="sarcastic",
        message=random.choice(greetings),
        character_state=CharacterState.TAUNTING.value
    )
