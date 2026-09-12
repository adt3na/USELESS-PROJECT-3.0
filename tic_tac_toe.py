import random
from typing import List, Tuple, Dict, Any

class TicTacToeGame:
    @staticmethod
    def create_empty_board() -> List[List[str]]:
        return [["" for _ in range(3)] for _ in range(3)]

    @staticmethod
    def check_winner(board: List[List[str]]) -> str:
        """
        Returns 'X', 'O', 'DRAW', or 'ONGOING'
        """
        # Check rows
        for row in board:
            if row[0] and row[0] == row[1] == row[2]:
                return row[0]

        # Check cols
        for c in range(3):
            if board[0][c] and board[0][c] == board[1][c] == board[2][c]:
                return board[0][c]

        # Check diagonals
        if board[0][0] and board[0][0] == board[1][1] == board[2][2]:
            return board[0][0]
        if board[0][2] and board[0][2] == board[1][1] == board[2][0]:
            return board[0][2]

        # Check if full
        for r in range(3):
            for c in range(3):
                if not board[r][c]:
                    return "ONGOING"

        return "DRAW"

    @classmethod
    def get_available_moves(cls, board: List[List[str]]) -> List[Tuple[int, int]]:
        moves = []
        for r in range(3):
            for c in range(3):
                if not board[r][c]:
                    moves.append((r, c))
        return moves

    @classmethod
    def make_ai_move(cls, board: List[List[str]]) -> Tuple[int, int]:
        available = cls.get_available_moves(board)
        if not available:
            return (-1, -1)

        # 1. Check if AI can win immediately
        for r, c in available:
            board[r][c] = "O"
            if cls.check_winner(board) == "O":
                board[r][c] = ""
                return (r, c)
            board[r][c] = ""

        # 2. Check if user can win and block (80% chance to block, 20% mistake for fun)
        if random.random() < 0.85:
            for r, c in available:
                board[r][c] = "X"
                if cls.check_winner(board) == "X":
                    board[r][c] = ""
                    return (r, c)
                board[r][c] = ""

        # 3. Take center if open
        if (1, 1) in available:
            return (1, 1)

        # 4. Take random corner
        corners = [m for m in available if m in [(0, 0), (0, 2), (2, 0), (2, 2)]]
        if corners:
            return random.choice(corners)

        return random.choice(available)
