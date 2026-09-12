import time
from typing import Dict, Any, Tuple

class BubbleShooterGame:
    DEFAULT_TARGET_SCORE = 500
    DEFAULT_TIME_LIMIT = 25  # seconds (ample yet exciting)

    @classmethod
    def create_game_config(cls) -> Dict[str, Any]:
        return {
            "target_score": cls.DEFAULT_TARGET_SCORE,
            "time_limit": cls.DEFAULT_TIME_LIMIT,
            "colors": ["#ff2a85", "#00f0ff", "#ffe600", "#05ffa1", "#b842ff"],
            "bubble_radius": 20,
            "rows": 5,
            "cols": 8
        }

    @classmethod
    def validate_result(
        cls,
        created_at: float,
        time_limit: int,
        target_score: int,
        reported_score: int,
        client_won: bool
    ) -> Tuple[bool, str]:
        elapsed = time.time() - created_at
        # Allow 3 second network latency buffer
        if elapsed > (time_limit + 4.0):
            return False, f"Time expired! You took {int(elapsed)}s for a {time_limit}s challenge!"

        if reported_score < target_score:
            return False, f"Score too low! You scored {reported_score}, but I demanded {target_score}!"

        return True, "Bubble challenge cleared! Vadakkunokki is displeased you succeeded."
