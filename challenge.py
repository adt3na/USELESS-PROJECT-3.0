from fastapi import APIRouter, HTTPException
from backend.models.game_models import AnswerUnlockRequest, AnswerUnlockResponse, ChallengeStatus
from backend.models.chat_models import CharacterState
from backend.services.game_service import game_service
from backend.services.chat_service import chat_service
from backend.services.gemini_service import gemini_service
from backend.utils.helpers import log_event

router = APIRouter(prefix="/api/challenge", tags=["Challenge"])

@router.post("/answer", response_model=AnswerUnlockResponse)
async def unlock_answer(req: AnswerUnlockRequest):
    """
    FR-013, FR-030:
    Only unlocks when challenge.status == WON.
    Retrieves preserved original_question and passes to Gemini.
    """
    challenge = game_service.get_challenge(req.challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found.")

    if challenge.status != ChallengeStatus.WON:
        raise HTTPException(
            status_code=403,
            detail="Answer remains LOCKED! You haven't won the challenge yet."
        )

    session = chat_service.get_or_create_session(req.session_id)
    original_question = challenge.original_question or session.original_question

    if not original_question:
        original_question = "What is the secret of life?"

    # Generate factual answer via Gemini
    actual_answer = await gemini_service.generate_actual_answer(original_question)

    # Generate personality wrapper
    personality_msg = await gemini_service.generate_personality_dialogue(
        mood=session.current_mood,
        prompt_type="won_wrapper",
        context=f"The user won the game and proved themselves for: '{original_question}'"
    )

    # Mark session state
    session.answer_unlocked = True
    session.unlocked_answer_text = actual_answer
    log_event("ANSWER_UNLOCKED", req.session_id, challenge_id=req.challenge_id)

    return AnswerUnlockResponse(
        personality_message=personality_msg,
        actual_answer=actual_answer,
        mood=session.current_mood,
        original_question=original_question,
        character_state=CharacterState.HAPPY.value
    )
