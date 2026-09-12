import time
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.models.chat_models import MoodType
from backend.models.game_models import Challenge

class ConversationTurn(BaseModel):
    role: str  # "user" or "assistant"
    type: str  # "question", "answer", "ragebait", "refusal", "game_prompt", etc.
    content: str
    mood: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)

class UserSession(BaseModel):
    session_id: str
    current_mood: str = MoodType.NEUTRAL.value
    conversation_history: List[ConversationTurn] = Field(default_factory=list)
    original_question: Optional[str] = None
    active_challenge: Optional[Challenge] = None
    game_state: Dict[str, Any] = Field(default_factory=dict)
    answer_unlocked: bool = False
    unlocked_answer_text: Optional[str] = None
    turns_count: int = 0
    games_played: int = 0
    games_won: int = 0
    created_at: float = Field(default_factory=time.time)
    last_activity: float = Field(default_factory=time.time)
