from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class GameType(str, Enum):
    TIC_TAC_TOE = "tic_tac_toe"
    BUBBLE_SHOOTER = "bubble_shooter"
    SPEED_MATH = "speed_math"
    SCIENCE_QUIZ = "science_quiz"

class ChallengeStatus(str, Enum):
    LOCKED = "LOCKED"
    ACTIVE = "ACTIVE"
    WON = "WON"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

class Challenge(BaseModel):
    challenge_id: str
    session_id: str
    original_question: str
    game_type: str
    target_score: Optional[int] = None
    target_condition: Optional[str] = None
    time_limit: Optional[int] = None
    status: ChallengeStatus = ChallengeStatus.ACTIVE
    created_at: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GameStartRequest(BaseModel):
    session_id: str
    game: Optional[str] = None

class GameStartResponse(BaseModel):
    challenge_id: str
    game: str
    target_score: Optional[int] = None
    target_condition: Optional[str] = None
    time_limit: Optional[int] = None
    status: str
    game_state: Dict[str, Any] = Field(default_factory=dict)
    instructions: str
    taunt: str

class GameResultRequest(BaseModel):
    session_id: str
    challenge_id: str
    score: Optional[int] = 0
    client_won: Optional[bool] = False
    game_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class GameValidationResponse(BaseModel):
    status: str  # WON, FAILED, ACTIVE
    answer_unlocked: bool
    score: Optional[int] = 0
    message: str
    character_state: str

class TicTacToeMoveRequest(BaseModel):
    session_id: str
    challenge_id: str
    row: int
    col: int

class TicTacToeStateResponse(BaseModel):
    board: List[List[str]]  # 3x3 array containing "", "X", "O"
    status: str  # ONGOING, PLAYER_WIN, AI_WIN, DRAW
    challenge_won: bool
    message: str
    character_state: str

class SpeedMathAnswerRequest(BaseModel):
    session_id: str
    challenge_id: str
    problem_id: str
    answer: int

class SpeedMathResponse(BaseModel):
    correct: bool
    correct_count: int
    target_count: int
    time_remaining: int
    next_problem: Optional[Dict[str, Any]] = None
    status: str  # ACTIVE, WON, FAILED
    answer_unlocked: bool
    message: str

class ScienceQuizAnswerRequest(BaseModel):
    session_id: str
    challenge_id: str
    question_index: int
    selected_option: int

class ScienceQuizResponse(BaseModel):
    correct: bool
    correct_count: int
    total_questions: int
    current_index: int
    status: str  # ACTIVE, WON, FAILED
    answer_unlocked: bool
    message: str

class AnswerUnlockRequest(BaseModel):
    session_id: str
    challenge_id: str

class AnswerUnlockResponse(BaseModel):
    personality_message: str
    actual_answer: str
    mood: str
    original_question: str
    character_state: str
