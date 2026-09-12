import time
from fastapi import APIRouter, HTTPException
from backend.models.game_models import (
    GameStartRequest,
    GameStartResponse,
    GameResultRequest,
    GameValidationResponse,
    TicTacToeMoveRequest,
    TicTacToeStateResponse,
    SpeedMathAnswerRequest,
    SpeedMathResponse,
    ScienceQuizAnswerRequest,
    ScienceQuizResponse,
    ChallengeStatus
)
from backend.models.chat_models import CharacterState
from backend.services.game_service import game_service
from backend.services.chat_service import chat_service
from backend.games.tic_tac_toe import TicTacToeGame
from backend.games.speed_math import SpeedMathGame
from backend.games.science_quiz import ScienceQuizGame

router = APIRouter(prefix="/api/game", tags=["Games"])

@router.post("/start", response_model=GameStartResponse)
async def start_game(req: GameStartRequest):
    """
    FR-028: Starts a mini-game challenge.
    """
    session = chat_service.get_or_create_session(req.session_id)
    game_type = req.game or "tic_tac_toe"

    # Use existing original_question or create placeholder
    orig_q = session.original_question or "Why is the sky blue?"
    challenge = game_service.create_challenge(req.session_id, orig_q, game_type)
    session.active_challenge = challenge

    game_state = {}
    instructions = ""
    taunt = ""

    if game_type == "tic_tac_toe":
        instructions = "Get 3-in-a-row to beat Vadakkunokki!"
        taunt = "You think you can outsmart my 3x3 brain? Try it."
        game_state = {"board": TicTacToeGame.create_empty_board(), "turn": "X"}
    elif game_type == "bubble_shooter":
        instructions = f"Pop colored bubbles to reach {challenge.target_score} points in {challenge.time_limit} seconds!"
        taunt = "Hurry up before your time runs out!"
        game_state = challenge.metadata
    elif game_type == "speed_math":
        instructions = f"Solve {challenge.target_score} arithmetic questions correctly before time runs out!"
        taunt = "Let's see if your mental math matches your confidence."
        game_state = {
            "first_problem": challenge.metadata["current_problem"],
            "target": challenge.target_score
        }
    elif game_type == "science_quiz":
        instructions = "Answer all 3 science questions correctly!"
        taunt = "Let's test if you actually paid attention in science class."
        questions = await ScienceQuizGame.create_quiz()
        challenge.metadata["questions"] = questions
        # Strip correct_index before sending to client for security
        client_questions = [
            {"question": q["question"], "options": q["options"]}
            for q in questions
        ]
        game_state = {"questions": client_questions}

    return GameStartResponse(
        challenge_id=challenge.challenge_id,
        game=game_type,
        target_score=challenge.target_score,
        target_condition=challenge.target_condition,
        time_limit=challenge.time_limit,
        status=challenge.status.value,
        game_state=game_state,
        instructions=instructions,
        taunt=taunt
    )

@router.post("/result", response_model=GameValidationResponse)
async def submit_result(req: GameResultRequest):
    """
    FR-029: Validates game result (authoritative server validation).
    """
    challenge = game_service.get_challenge(req.challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found.")

    session = chat_service.get_or_create_session(req.session_id)

    if challenge.game_type == "bubble_shooter":
        won, message = game_service.validate_bubble_shooter(
            challenge, req.score or 0, req.client_won or False
        )
        if won:
            session.answer_unlocked = True
            session.games_won += 1
            return GameValidationResponse(
                status="WON",
                answer_unlocked=True,
                score=req.score,
                message="Incredible! You cleared the Bubble challenge. Answer is unlocked!",
                character_state=CharacterState.DEFEATED.value
            )
        else:
            session.games_played += 1
            return GameValidationResponse(
                status="FAILED",
                answer_unlocked=False,
                score=req.score,
                message=message,
                character_state=CharacterState.LAUGHING.value
            )

    raise HTTPException(status_code=400, detail="Invalid result verification endpoint for this game type.")

@router.post("/ttt-move", response_model=TicTacToeStateResponse)
async def ttt_move(req: TicTacToeMoveRequest):
    """
    Interactive server-authoritative move for Tic-Tac-Toe.
    """
    challenge = game_service.get_challenge(req.challenge_id)
    if not challenge or challenge.game_type != "tic_tac_toe":
        raise HTTPException(status_code=404, detail="Active Tic-Tac-Toe challenge not found.")

    board = challenge.metadata.get("board", TicTacToeGame.create_empty_board())

    if req.row < 0 or req.row > 2 or req.col < 0 or req.col > 2:
        raise HTTPException(status_code=400, detail="Move out of bounds.")

    if board[req.row][req.col] != "":
        raise HTTPException(status_code=400, detail="Cell already occupied.")

    # 1. Apply player's move
    board[req.row][req.col] = "X"
    winner = TicTacToeGame.check_winner(board)

    session = chat_service.get_or_create_session(req.session_id)

    if winner == "X":
        challenge.status = ChallengeStatus.WON
        session.answer_unlocked = True
        session.games_won += 1
        return TicTacToeStateResponse(
            board=board,
            status="PLAYER_WIN",
            challenge_won=True,
            message="No way... you actually defeated me at Tic-Tac-Toe?!",
            character_state=CharacterState.DEFEATED.value
        )
    elif winner == "DRAW":
        challenge.status = ChallengeStatus.FAILED
        return TicTacToeStateResponse(
            board=board,
            status="DRAW",
            challenge_won=False,
            message="A draw! A draw is NOT a victory. Try again!",
            character_state=CharacterState.TAUNTING.value
        )

    # 2. Make AI Counter Move
    ai_r, ai_c = TicTacToeGame.make_ai_move(board)
    if ai_r != -1:
        board[ai_r][ai_c] = "O"

    winner_after_ai = TicTacToeGame.check_winner(board)

    if winner_after_ai == "O":
        challenge.status = ChallengeStatus.FAILED
        return TicTacToeStateResponse(
            board=board,
            status="AI_WIN",
            challenge_won=False,
            message="I WIN! Better luck next millennium, amateur!",
            character_state=CharacterState.LAUGHING.value
        )
    elif winner_after_ai == "DRAW":
        challenge.status = ChallengeStatus.FAILED
        return TicTacToeStateResponse(
            board=board,
            status="DRAW",
            challenge_won=False,
            message="Cat's game! Tie means you lose the challenge!",
            character_state=CharacterState.TAUNTING.value
        )

    challenge.metadata["board"] = board
    return TicTacToeStateResponse(
        board=board,
        status="ONGOING",
        challenge_won=False,
        message="Your turn! Don't take all day.",
        character_state=CharacterState.THINKING.value
    )

@router.post("/speed-math/answer", response_model=SpeedMathResponse)
async def speed_math_answer(req: SpeedMathAnswerRequest):
    """
    Validates Speed Math problem and serves next problem.
    """
    challenge = game_service.get_challenge(req.challenge_id)
    if not challenge or challenge.game_type != "speed_math":
        raise HTTPException(status_code=404, detail="Active Speed Math challenge not found.")

    meta = challenge.metadata
    start_time = meta.get("start_time", time.time())
    elapsed = time.time() - start_time
    time_remaining = max(0, int(SpeedMathGame.TIME_LIMIT - elapsed))

    if time_remaining <= 0:
        challenge.status = ChallengeStatus.FAILED
        return SpeedMathResponse(
            correct=False,
            correct_count=meta.get("correct_count", 0),
            target_count=SpeedMathGame.TARGET_CORRECT,
            time_remaining=0,
            next_problem=None,
            status="FAILED",
            answer_unlocked=False,
            message="TIME'S UP! Your math skills were too sluggish!"
        )

    current_prob = meta.get("current_problem", {})
    is_correct = SpeedMathGame.validate_answer(current_prob, req.answer)

    session = chat_service.get_or_create_session(req.session_id)

    if is_correct:
        meta["correct_count"] = meta.get("correct_count", 0) + 1
        count = meta["correct_count"]

        if count >= SpeedMathGame.TARGET_CORRECT:
            challenge.status = ChallengeStatus.WON
            session.answer_unlocked = True
            session.games_won += 1
            return SpeedMathResponse(
                correct=True,
                correct_count=count,
                target_count=SpeedMathGame.TARGET_CORRECT,
                time_remaining=time_remaining,
                next_problem=None,
                status="WON",
                answer_unlocked=True,
                message="8/8! How did you compute so fast?! You unlocked your answer!"
            )

        # Generate next difficulty problem
        next_prob = SpeedMathGame.generate_problem(difficulty=min(8, count + 1))
        meta["current_problem"] = next_prob
        return SpeedMathResponse(
            correct=True,
            correct_count=count,
            target_count=SpeedMathGame.TARGET_CORRECT,
            time_remaining=time_remaining,
            next_problem=next_prob,
            status="ACTIVE",
            answer_unlocked=False,
            message="Correct! Next one!"
        )
    else:
        return SpeedMathResponse(
            correct=False,
            correct_count=meta.get("correct_count", 0),
            target_count=SpeedMathGame.TARGET_CORRECT,
            time_remaining=time_remaining,
            next_problem=current_prob,
            status="ACTIVE",
            answer_unlocked=False,
            message="Wrong! Try again quickly!"
        )

@router.post("/science-quiz/answer", response_model=ScienceQuizResponse)
async def science_quiz_answer(req: ScienceQuizAnswerRequest):
    """
    Validates Science Quiz answer and checks 3/3 win condition.
    """
    challenge = game_service.get_challenge(req.challenge_id)
    if not challenge or challenge.game_type != "science_quiz":
        raise HTTPException(status_code=404, detail="Active Science Quiz challenge not found.")

    questions = challenge.metadata.get("questions", [])
    if req.question_index < 0 or req.question_index >= len(questions):
        raise HTTPException(status_code=400, detail="Question index out of range.")

    is_correct, explanation = ScienceQuizGame.validate_answer(
        questions, req.question_index, req.selected_option
    )

    meta = challenge.metadata
    if is_correct:
        meta["correct_count"] = meta.get("correct_count", 0) + 1

    next_idx = req.question_index + 1
    session = chat_service.get_or_create_session(req.session_id)

    if next_idx >= len(questions):
        # Completed all 3 questions
        final_correct = meta.get("correct_count", 0)
        if final_correct == ScienceQuizGame.TARGET_CORRECT:
            challenge.status = ChallengeStatus.WON
            session.answer_unlocked = True
            session.games_won += 1
            return ScienceQuizResponse(
                correct=is_correct,
                correct_count=final_correct,
                total_questions=len(questions),
                current_index=next_idx,
                status="WON",
                answer_unlocked=True,
                message="A perfect 3/3 score! Fine, your wisdom is undeniable. Answer unlocked!"
            )
        else:
            challenge.status = ChallengeStatus.FAILED
            return ScienceQuizResponse(
                correct=is_correct,
                correct_count=final_correct,
                total_questions=len(questions),
                current_index=next_idx,
                status="FAILED",
                answer_unlocked=False,
                message=f"You scored {final_correct}/3. I required PERFECTION. Try again!"
            )

    return ScienceQuizResponse(
        correct=is_correct,
        correct_count=meta.get("correct_count", 0),
        total_questions=len(questions),
        current_index=next_idx,
        status="ACTIVE",
        answer_unlocked=False,
        message=explanation
    )
