import pytest
from backend.games.tic_tac_toe import TicTacToeGame
from backend.games.bubble_shooter import BubbleShooterGame
from backend.games.speed_math import SpeedMathGame
from backend.games.science_quiz import ScienceQuizGame

def test_tic_tac_toe_win_detection():
    # Row win
    board = [
        ["X", "X", "X"],
        ["O", "", "O"],
        ["", "", ""]
    ]
    assert TicTacToeGame.check_winner(board) == "X"

    # Column win
    col_board = [
        ["O", "X", ""],
        ["O", "X", ""],
        ["O", "", ""]
    ]
    assert TicTacToeGame.check_winner(col_board) == "O"

    # Diagonal win
    diag_board = [
        ["X", "O", ""],
        ["O", "X", ""],
        ["", "", "X"]
    ]
    assert TicTacToeGame.check_winner(diag_board) == "X"

    # Draw
    draw_board = [
        ["X", "O", "X"],
        ["X", "O", "O"],
        ["O", "X", "X"]
    ]
    assert TicTacToeGame.check_winner(draw_board) == "DRAW"

def test_tic_tac_toe_ai_move():
    board = [
        ["X", "X", ""],
        ["O", "", ""],
        ["", "", ""]
    ]
    ai_r, ai_c = TicTacToeGame.make_ai_move(board)
    assert (ai_r, ai_c) == (0, 2)  # Should block X's winning move

def test_bubble_shooter_validation():
    import time
    created_at = time.time() - 10  # 10s elapsed
    # Passes score 500 in 25s
    valid, msg = BubbleShooterGame.validate_result(created_at, 25, 500, 600, True)
    assert valid is True

    # Fails if score too low
    valid_low, msg_low = BubbleShooterGame.validate_result(created_at, 25, 500, 350, False)
    assert valid_low is False

    # Fails if expired (e.g. 40s on 25s limit)
    created_old = time.time() - 40
    valid_exp, msg_exp = BubbleShooterGame.validate_result(created_old, 25, 500, 600, True)
    assert valid_exp is False

def test_speed_math_generation_and_validation():
    prob = SpeedMathGame.generate_problem(difficulty=1)
    assert "display" in prob
    assert "expected_answer" in prob
    assert SpeedMathGame.validate_answer(prob, prob["expected_answer"]) is True
    assert SpeedMathGame.validate_answer(prob, prob["expected_answer"] + 99) is False

def test_science_quiz_validation():
    sample_questions = [
        {"question": "Q1", "options": ["A", "B"], "correct_index": 0, "explanation": "E1"},
        {"question": "Q2", "options": ["A", "B"], "correct_index": 1, "explanation": "E2"}
    ]
    correct, expl = ScienceQuizGame.validate_answer(sample_questions, 0, 0)
    assert correct is True
    wrong, _ = ScienceQuizGame.validate_answer(sample_questions, 0, 1)
    assert wrong is False
