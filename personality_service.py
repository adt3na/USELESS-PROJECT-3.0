import random
from typing import Dict, Any, Optional
from backend.models.chat_models import BehaviorType, MoodType
from backend.models.game_models import GameType
from backend.services.mood_service import mood_service

class PersonalityService:
    def __init__(self):
        self.games = [
            GameType.TIC_TAC_TOE.value,
            GameType.BUBBLE_SHOOTER.value,
            GameType.SPEED_MATH.value,
            GameType.SCIENCE_QUIZ.value
        ]

    def decide_behavior(
        self,
        question: str,
        current_mood: str,
        turns_count: int,
        active_challenge_exists: bool
    ) -> Dict[str, Any]:
        """
        FR-002, FR-052: Determines Vadakkunokki's action based on mood, question, and history.
        """
        # If user has an active challenge they abandoned or didn't finish, tease them about it
        if active_challenge_exists:
            return {
                "behavior": BehaviorType.RAGEBAIT.value,
                "mood": MoodType.RAGEBAIT.value,
                "message": "Hey! You haven't finished your previous challenge yet! Finish it or surrender before asking more questions!"
            }

        # Check for angry mode triggers (e.g. repeated punctuation, ALL CAPS, rude words)
        if question.isupper() and len(question) > 10:
            return {
                "behavior": BehaviorType.DELETE_INPUT.value,
                "mood": MoodType.ANGRY.value,
                "action": "delete_input",
                "message": "STOP SHOUTING AT ME! Let me just delete that nonsense for you..."
            }

        # Determine mood shift
        next_mood = mood_service.transition_mood(current_mood, "question_asked")
        game_prob = mood_service.evaluate_game_probability(next_mood)

        # First turn has higher game chance to immediately showcase the retro gimmick
        if turns_count == 0:
            game_prob = 0.85

        roll = random.random()

        if roll < game_prob:
            selected_game = random.choice(self.games)
            return {
                "behavior": BehaviorType.START_GAME.value,
                "mood": next_mood,
                "game": selected_game
            }
        
        # Non-game behaviors
        remaining_behaviors = [
            BehaviorType.RAGEBAIT.value,
            BehaviorType.ASK_BACK.value,
            BehaviorType.REFUSE.value,
            BehaviorType.ANSWER.value,
            BehaviorType.SILENT.value
        ]
        weights = [0.35, 0.25, 0.20, 0.15, 0.05]
        selected_behavior = random.choices(remaining_behaviors, weights=weights)[0]

        return {
            "behavior": selected_behavior,
            "mood": next_mood,
            "game": None
        }

personality_service = PersonalityService()
