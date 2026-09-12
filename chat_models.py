from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class BehaviorType(str, Enum):
    ANSWER = "ANSWER"
    RAGEBAIT = "RAGEBAIT"
    ASK_BACK = "ASK_BACK"
    REFUSE = "REFUSE"
    START_GAME = "START_GAME"
    DELETE_INPUT = "DELETE_INPUT"
    SILENT = "SILENT"
    MOOD_REACTION = "MOOD_REACTION"

class MoodType(str, Enum):
    NEUTRAL = "neutral"
    SARCASTIC = "sarcastic"
    ANGRY = "angry"
    SAD = "sad"
    LAZY = "lazy"
    CHAOTIC = "chaotic"
    RAGEBAIT = "ragebait"

class CharacterState(str, Enum):
    IDLE = "IDLE"
    HAPPY = "HAPPY"
    ANGRY = "ANGRY"
    SAD = "SAD"
    BORED = "BORED"
    CONFUSED = "CONFUSED"
    LAUGHING = "LAUGHING"
    TAUNTING = "TAUNTING"
    THINKING = "THINKING"
    VICTORY = "VICTORY"
    DEFEATED = "DEFEATED"

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique ID for user session")
    message: str = Field(..., description="User message text")

class ChatResponse(BaseModel):
    type: str = Field(..., description="Response type: answer, ragebait, ask_back, refusal, game, action, silent, error")
    mood: str = Field(..., description="Vadakkunokki's mood")
    message: Optional[str] = Field(None, description="Dialogue text")
    action: Optional[str] = Field(None, description="Action for UI to perform e.g. delete_input")
    game: Optional[str] = Field(None, description="Game identifier if game is triggered")
    challenge_id: Optional[str] = Field(None, description="Active challenge identifier")
    target_score: Optional[int] = Field(None, description="Required target score or condition")
    target_condition: Optional[str] = Field(None, description="Textual target condition")
    time_limit: Optional[int] = Field(None, description="Time limit in seconds")
    character_state: Optional[str] = Field(default="IDLE", description="Current visual character state")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context or game parameters")

class StartupGreetingResponse(BaseModel):
    session_id: str
    mood: str
    message: str
    character_state: str
