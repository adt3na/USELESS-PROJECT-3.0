from typing import List, Dict, Any, Tuple
from backend.services.gemini_service import gemini_service

class ScienceQuizGame:
    TARGET_CORRECT = 3

    @classmethod
    async def create_quiz(cls) -> List[Dict[str, Any]]:
        # Fetches 3 questions via Gemini or curated science pool
        return await gemini_service.generate_science_quiz()

    @classmethod
    def validate_answer(
        cls,
        quiz_questions: List[Dict[str, Any]],
        question_index: int,
        selected_option: int
    ) -> Tuple[bool, str]:
        if question_index < 0 or question_index >= len(quiz_questions):
            return False, "Invalid question index"

        question_obj = quiz_questions[question_index]
        is_correct = (selected_option == question_obj["correct_index"])
        explanation = question_obj.get("explanation", "")
        return is_correct, explanation
