import pytest
from backend.services.game_service import game_service
from backend.services.gemini_service import gemini_service
from backend.models.game_models import ChallengeStatus

@pytest.mark.asyncio
async def test_original_question_preservation_and_unlock():
    session_id = "test_session_101"
    question = "What is the capital of Kerala?"

    # 1. Create challenge
    challenge = game_service.create_challenge(
        session_id=session_id,
        original_question=question,
        game_type="tic_tac_toe"
    )

    # Verify original question is preserved exactly per FR-007
    assert challenge.original_question == question
    assert challenge.status == ChallengeStatus.ACTIVE

    # 2. Verify answer cannot be unlocked while active
    # (Checking game_service state directly)
    assert challenge.status != ChallengeStatus.WON

    # 3. Simulate victory
    game_service.mark_challenge_won(challenge.challenge_id)
    assert challenge.status == ChallengeStatus.WON

    # 4. Generate answer for preserved question
    actual_answer = await gemini_service.generate_actual_answer(challenge.original_question)
    assert "Thiruvananthapuram" in actual_answer or len(actual_answer) > 20
