import random
from typing import Dict, Any
from backend.models.chat_models import MoodType, CharacterState

class MoodService:
    def __init__(self):
        self.mood_character_map = {
            MoodType.NEUTRAL.value: CharacterState.IDLE.value,
            MoodType.SARCASTIC.value: CharacterState.TAUNTING.value,
            MoodType.ANGRY.value: CharacterState.ANGRY.value,
            MoodType.SAD.value: CharacterState.SAD.value,
            MoodType.LAZY.value: CharacterState.BORED.value,
            MoodType.CHAOTIC.value: CharacterState.LAUGHING.value,
            MoodType.RAGEBAIT.value: CharacterState.TAUNTING.value,
        }

    def get_character_state(self, mood: str) -> str:
        return self.mood_character_map.get(mood, CharacterState.IDLE.value)

    def transition_mood(self, current_mood: str, event: str) -> str:
        """
        Transitions the mood based on user interactions:
        - "question_asked"
        - "game_won"
        - "game_lost"
        - "annoying_input"
        """
        if event == "game_won":
            return random.choice([MoodType.SARCASTIC.value, MoodType.SAD.value, MoodType.NEUTRAL.value])
        elif event == "game_lost":
            return random.choice([MoodType.RAGEBAIT.value, MoodType.CHAOTIC.value, MoodType.SARCASTIC.value])
        elif event == "annoying_input":
            return MoodType.ANGRY.value
        elif event == "question_asked":
            # Natural mood shift or slight decay
            choices = [
                MoodType.RAGEBAIT.value,
                MoodType.SARCASTIC.value,
                MoodType.CHAOTIC.value,
                MoodType.LAZY.value,
                MoodType.NEUTRAL.value
            ]
            weights = [0.35, 0.25, 0.20, 0.10, 0.10]
            return random.choices(choices, weights=weights)[0]

        return current_mood

    def evaluate_game_probability(self, mood: str) -> float:
        """
        Returns probability of triggering a game challenge based on mood.
        """
        probabilities = {
            MoodType.RAGEBAIT.value: 0.65,
            MoodType.CHAOTIC.value: 0.55,
            MoodType.SARCASTIC.value: 0.45,
            MoodType.ANGRY.value: 0.40,
            MoodType.LAZY.value: 0.20,
            MoodType.NEUTRAL.value: 0.30,
            MoodType.SAD.value: 0.15
        }
        return probabilities.get(mood, 0.40)

mood_service = MoodService()
