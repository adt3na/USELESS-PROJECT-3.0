import json
from typing import Optional, List, Dict, Any
from backend.config import settings
from backend.utils.helpers import logger

# Lazy import / initialization for google-genai
genai_client = None

def get_genai_client():
    global genai_client
    if genai_client is None:
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            try:
                from google import genai
                genai_client = genai.Client(api_key=settings.GEMINI_API_KEY.strip())
                logger.info("Google Gemini Client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize google-genai client: {e}")
                genai_client = None
    return genai_client

class GeminiService:
    def __init__(self):
        self.model = settings.GEMINI_MODEL or "gemini-2.5-flash"

    async def generate_actual_answer(self, question: str, context: Optional[List[Dict[str, str]]] = None) -> str:
        """
        FR-014, FR-021:
        Directly address original question, factually useful, explain concepts clearly.
        No unnecessary personality interference inside the factual answer.
        """
        client = get_genai_client()
        if client:
            try:
                system_prompt = (
                    "You are a helpful, brilliant, and precise factual assistant. "
                    "Provide a direct, accurate, and engaging explanation for the user's question. "
                    "Do not use sarcasm or snark in this explanation; provide high quality information. "
                    "Keep your answer informative yet concise (1-3 paragraphs)."
                )
                prompt = f"User Question: {question}"
                response = client.models.generate_content(
                    model=self.model,
                    contents=[system_prompt, prompt]
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.error(f"Gemini API error during generate_actual_answer: {e}")

        # Intelligent and factually rich curated fallback if API key is not configured or offline
        return self._generate_fallback_answer(question)

    async def generate_personality_dialogue(self, mood: str, prompt_type: str, context: str = "") -> str:
        """
        Generates Vadakkunokki's sassy dialogue using Gemini or personality bank.
        """
        client = get_genai_client()
        if client:
            try:
                sys_instruction = (
                    "You are 'Vadakkunokki', a mischievous, unpredictable, snarky retro-game AI character. "
                    f"Your current mood is: {mood.upper()}. "
                    f"Type of response needed: {prompt_type}. "
                    "Generate a short (1-2 sentences), hilarious, cheeky retro-gaming style reply. "
                    "Be playful, sassy, or taunting without being abusive. "
                    "Do not give the factual answer."
                )
                response = client.models.generate_content(
                    model=self.model,
                    contents=[sys_instruction, f"Context: {context}"]
                )
                if response and response.text:
                    return response.text.strip().replace('"', '')
            except Exception as e:
                logger.warning(f"Gemini dialogue generation fallback due to: {e}")

        return self._fallback_dialogue(mood, prompt_type)

    async def generate_science_quiz(self) -> List[Dict[str, Any]]:
        """
        Generates a 3-question science quiz. Returns list of 3 questions with options & correct index.
        """
        client = get_genai_client()
        if client:
            try:
                prompt = (
                    "Generate a 3-question multiple choice science quiz across physics, astronomy, chemistry, or biology. "
                    "Return ONLY valid JSON in this exact structure without markdown backticks:\n"
                    "[\n"
                    '  {"question": "...", "options": ["A", "B", "C", "D"], "correct_index": 0, "explanation": "..."},\n'
                    '  {"question": "...", "options": ["A", "B", "C", "D"], "correct_index": 1, "explanation": "..."},\n'
                    '  {"question": "...", "options": ["A", "B", "C", "D"], "correct_index": 2, "explanation": "..."}\n'
                    "]"
                )
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                if response and response.text:
                    text = response.text.strip()
                    if text.startswith("```"):
                        text = text.split("```")[1]
                        if text.startswith("json"):
                            text = text[4:]
                    quiz_data = json.loads(text.strip())
                    if isinstance(quiz_data, list) and len(quiz_data) == 3:
                        return quiz_data
            except Exception as e:
                logger.warning(f"Failed to generate Gemini science quiz, using curated set: {e}")

        return self._curated_science_quiz()

    def _fallback_dialogue(self, mood: str, prompt_type: str) -> str:
        dialogues = {
            "ragebait": [
                "Why should I answer that for you? Entertain me first!",
                "You expect ME to do your homework? In this economy?",
                "Figure it out yourself... or play my game.",
                "Come back when you have a question worthy of my 8-bit intellect.",
                "Maybe. But only if you can survive my challenges!"
            ],
            "ask_back": [
                "Why do you want to know? What's your secret agenda?",
                "And what are YOU going to do with that information, huh?",
                "Did you seriously think I'd just hand that over on a silver platter?",
                "Are you going to use this knowledge for good or pure chaos?"
            ],
            "refusal": [
                "Access Denied. Reason: I simply don't feel like it.",
                "Error 404: Willingness to assist not found.",
                "Nah. Ask your search engine, mortal.",
                "I'm on my union-mandated 8-bit coffee break. Come back later."
            ],
            "won_wrapper": [
                "Ugh. Fine. You actually did it. Here is your precious answer:",
                "Well, well, well... looks like someone has actual skills. As promised:",
                "I didn't expect you to win that. A deal is a deal, I suppose:",
                "Level cleared! Take your wisdom and don't spend it all in one place:"
            ]
        }
        import random
        pool = dialogues.get(prompt_type, dialogues["ragebait"])
        return random.choice(pool)

    def _generate_fallback_answer(self, question: str) -> str:
        q_lower = question.lower()
        if "planet" in q_lower or "jupiter" in q_lower:
            return (
                "Jupiter is the largest planet in our solar system. It is a gas giant with a mass "
                "more than two and a half times that of all the other planets combined, and it is famous "
                "for its iconic Great Red Spot—a massive anticyclonic storm that has raged for centuries."
            )
        elif "telephone" in q_lower or "invented" in q_lower:
            return (
                "The telephone was patented by Alexander Graham Bell in 1876. While other inventors "
                "like Elisha Gray and Antonio Meucci contributed significantly to sound transmission technology, "
                "Bell was awarded the first official US patent for the practical electrical telephone."
            )
        elif "kerala" in q_lower or "capital" in q_lower:
            return (
                "The capital of Kerala is Thiruvananthapuram (formerly Trivandrum). Located on the southwestern "
                "coast of India, it is known for its British colonial architecture, Padmanabhaswamy Temple, "
                "and prominent academic and space research institutions including ISRO's VSSC."
            )
        elif "photosynthesis" in q_lower:
            return (
                "Photosynthesis is the biological process used by plants, algae, and certain bacteria to convert "
                "light energy into chemical energy. Using sunlight, carbon dioxide, and water, they synthesize "
                "glucose and release oxygen as a byproduct."
            )
        elif "gravity" in q_lower:
            return (
                "Gravity is a fundamental natural phenomenon by which all things with mass or energy are attracted "
                "toward one another. In modern physics, Albert Einstein's General Theory of Relativity describes gravity "
                "not simply as an invisible force, but as the curvature of spacetime caused by mass and energy."
            )
        else:
            return (
                f"Regarding '{question}': In scientific and factual terms, this topic represents a fascinating inquiry. "
                f"Every question opens the door to deeper exploration, whether it touches on physics, history, computing, or nature. "
                f"Always keep exploring and challenging both yourself and mischievous AI characters!"
            )

    def _curated_science_quiz(self) -> List[Dict[str, Any]]:
        return [
            {
                "question": "What is the powerhouse organelle of the eukaryotic cell?",
                "options": ["Ribosome", "Mitochondria", "Nucleus", "Endoplasmic Reticulum"],
                "correct_index": 1,
                "explanation": "Mitochondria generate most of the chemical energy needed to power the cell's biochemical reactions (ATP)."
            },
            {
                "question": "Which planet in our solar system has the highest surface temperature?",
                "options": ["Mercury", "Venus", "Mars", "Jupiter"],
                "correct_index": 1,
                "explanation": "Venus is hotter than Mercury because its thick carbon dioxide atmosphere creates an intense greenhouse effect."
            },
            {
                "question": "What chemical element has the symbol 'Fe'?",
                "options": ["Fluorine", "Francium", "Iron", "Fermium"],
                "correct_index": 2,
                "explanation": "'Fe' comes from the Latin word 'ferrum', meaning Iron."
            }
        ]

gemini_service = GeminiService()
