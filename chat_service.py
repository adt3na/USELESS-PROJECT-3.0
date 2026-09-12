import time
from typing import Dict, Optional, Any
from backend.models.session_models import UserSession, ConversationTurn
from backend.models.chat_models import (
    ChatResponse,
    BehaviorType,
    MoodType,
    CharacterState
)
from backend.models.game_models import ChallengeStatus
from backend.services.mood_service import mood_service
from backend.services.personality_service import personality_service
from backend.services.game_service import game_service
from backend.services.gemini_service import gemini_service
from backend.utils.helpers import generate_id, log_event

class ChatService:
    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}

    def get_or_create_session(self, session_id: Optional[str] = None) -> UserSession:
        if not session_id or session_id not in self.sessions:
            new_id = session_id or generate_id("sess")
            session = UserSession(session_id=new_id)
            self.sessions[new_id] = session
            log_event("SESSION_CREATED", new_id)
            return session
        return self.sessions[session_id]

    async def process_chat(self, session_id: str, message: str) -> ChatResponse:
        session = self.get_or_create_session(session_id)
        session.last_activity = time.time()
        clean_msg = message.strip()

        # Log turn in history
        session.conversation_history.append(
            ConversationTurn(role="user", type="question", content=clean_msg)
        )

        has_active_chal = (
            session.active_challenge is not None
            and session.active_challenge.status == ChallengeStatus.ACTIVE
        )

        # Decide behavior via personality engine
        decision = personality_service.decide_behavior(
            question=clean_msg,
            current_mood=session.current_mood,
            turns_count=session.turns_count,
            active_challenge_exists=has_active_chal
        )

        behavior = decision["behavior"]
        mood = decision["mood"]
        session.current_mood = mood
        session.turns_count += 1

        # 1. START_GAME BEHAVIOR
        if behavior == BehaviorType.START_GAME.value:
            game_type = decision["game"]
            # Store original question in session and challenge
            session.original_question = clean_msg
            challenge = game_service.create_challenge(
                session_id=session.session_id,
                original_question=clean_msg,
                game_type=game_type
            )
            session.active_challenge = challenge

            game_descriptions = {
                "tic_tac_toe": "Beat me at Tic-Tac-Toe and I'll consider answering your question!",
                "bubble_shooter": f"Score at least {challenge.target_score} in Bubble Shooter in {challenge.time_limit}s or walk away empty-handed!",
                "speed_math": f"Answer {challenge.target_score} math problems at lightning speed before I lose interest!",
                "science_quiz": "Pass my 3-question Science Quiz with a perfect 3/3 score to prove your intellect!"
            }
            taunt = game_descriptions.get(game_type, "Clear my mini-game first!")

            session.conversation_history.append(
                ConversationTurn(role="assistant", type="game_challenge", content=taunt, mood=mood)
            )

            return ChatResponse(
                type="game",
                mood=mood,
                message=taunt,
                game=game_type,
                challenge_id=challenge.challenge_id,
                target_score=challenge.target_score,
                target_condition=challenge.target_condition,
                time_limit=challenge.time_limit,
                character_state=CharacterState.TAUNTING.value,
                metadata={"game_type": game_type}
            )

        # 2. DELETE_INPUT BEHAVIOR (Angry Mode)
        elif behavior == BehaviorType.DELETE_INPUT.value:
            msg = decision.get("message", "I refuse to look at that. Deleting!")
            session.conversation_history.append(
                ConversationTurn(role="assistant", type="action", content=msg, mood=mood)
            )
            return ChatResponse(
                type="action",
                mood=mood,
                message=msg,
                action="delete_input",
                character_state=CharacterState.ANGRY.value
            )

        # 3. SILENT BEHAVIOR
        elif behavior == BehaviorType.SILENT.value:
            session.conversation_history.append(
                ConversationTurn(role="assistant", type="silent", content="...", mood=mood)
            )
            return ChatResponse(
                type="silent",
                mood=mood,
                message=None,
                character_state=CharacterState.BORED.value
            )

        # 4. RAGEBAIT BEHAVIOR
        elif behavior == BehaviorType.RAGEBAIT.value:
            dialogue = await gemini_service.generate_personality_dialogue(mood, "ragebait", clean_msg)
            session.conversation_history.append(
                ConversationTurn(role="assistant", type="ragebait", content=dialogue, mood=mood)
            )
            return ChatResponse(
                type="ragebait",
                mood=mood,
                message=dialogue,
                character_state=CharacterState.TAUNTING.value
            )

        # 5. ASK_BACK BEHAVIOR
        elif behavior == BehaviorType.ASK_BACK.value:
            dialogue = await gemini_service.generate_personality_dialogue(mood, "ask_back", clean_msg)
            session.conversation_history.append(
                ConversationTurn(role="assistant", type="ask_back", content=dialogue, mood=mood)
            )
            return ChatResponse(
                type="ask_back",
                mood=mood,
                message=dialogue,
                character_state=CharacterState.CONFUSED.value
            )

        # 6. REFUSE BEHAVIOR
        elif behavior == BehaviorType.REFUSE.value:
            dialogue = await gemini_service.generate_personality_dialogue(mood, "refusal", clean_msg)
            session.conversation_history.append(
                ConversationTurn(role="assistant", type="refusal", content=dialogue, mood=mood)
            )
            return ChatResponse(
                type="refusal",
                mood=mood,
                message=dialogue,
                character_state=CharacterState.ANGRY.value
            )

        # 7. DIRECT ANSWER BEHAVIOR
        else:
            actual_answer = await gemini_service.generate_actual_answer(clean_msg)
            personality_wrap = "Fine. I'm in a rare generous mood, so here's your answer:"
            full_reply = f"{personality_wrap}\n\n{actual_answer}"
            session.conversation_history.append(
                ConversationTurn(role="assistant", type="answer", content=full_reply, mood=mood)
            )
            return ChatResponse(
                type="answer",
                mood=mood,
                message=full_reply,
                character_state=CharacterState.HAPPY.value,
                metadata={"answer": actual_answer}
            )

chat_service = ChatService()
