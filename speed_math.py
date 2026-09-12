import random
import time
import uuid
from typing import Dict, Any, Tuple

class SpeedMathGame:
    TARGET_CORRECT = 8
    TIME_LIMIT = 30  # seconds

    @classmethod
    def generate_problem(cls, difficulty: int = 1) -> Dict[str, Any]:
        """
        Generates an arithmetic problem based on difficulty level (1..8)
        """
        problem_id = f"prob_{uuid.uuid4().hex[:6]}"

        if difficulty <= 2:
            # Simple addition / subtraction
            op = random.choice(["+", "-"])
            a = random.randint(3, 20)
            b = random.randint(2, 15)
            if op == "-" and a < b:
                a, b = b, a
            ans = a + b if op == "+" else a - b
            text = f"{a} {op} {b} = ?"
        elif difficulty <= 5:
            # Medium addition, subtraction, simple multiplication
            op = random.choice(["+", "-", "*"])
            if op == "*":
                a = random.randint(2, 9)
                b = random.randint(3, 9)
                ans = a * b
            else:
                a = random.randint(15, 60)
                b = random.randint(10, 45)
                if op == "-" and a < b:
                    a, b = b, a
                ans = a + b if op == "+" else a - b
            text = f"{a} {op} {b} = ?"
        else:
            # Advanced: multiplication or exact division
            op = random.choice(["*", "/"])
            if op == "/":
                divisor = random.randint(2, 10)
                quotient = random.randint(2, 12)
                dividend = divisor * quotient
                ans = quotient
                text = f"{dividend} ÷ {divisor} = ?"
            else:
                a = random.randint(6, 15)
                b = random.randint(4, 12)
                ans = a * b
                text = f"{a} × {b} = ?"

        return {
            "problem_id": problem_id,
            "display": text,
            "expected_answer": ans,
            "difficulty": difficulty
        }

    @classmethod
    def validate_answer(
        cls,
        active_problem: Dict[str, Any],
        user_answer: int
    ) -> bool:
        return user_answer == active_problem.get("expected_answer")
