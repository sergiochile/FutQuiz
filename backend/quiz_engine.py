"""
Motor del Quiz - FutQuiz
Maneja la lógica del juego: sesiones, niveles, puntuación, rachas
"""

import random
import time
from dataclasses import dataclass, field
from typing import Optional
from backend.data.questions import QUESTIONS, LEVELS_CONFIG, get_questions_by_level


@dataclass
class Answer:
    question_id: int
    selected: str
    correct: bool
    time_taken: float  # segundos
    points_earned: int


@dataclass
class GameSession:
    session_id: str
    player_name: str
    mode: str              # "classic", "speed", "level_up", "duel"
    category: Optional[str] = None
    current_level: int = 1
    score: int = 0
    streak: int = 0        # racha actual
    max_streak: int = 0
    answers: list = field(default_factory=list)
    questions_queue: list = field(default_factory=list)
    current_question_idx: int = 0
    started_at: float = field(default_factory=time.time)
    finished: bool = False
    lives: int = 3         # modo clásico tiene 3 vidas


class QuizEngine:
    """Motor principal del quiz"""

    def __init__(self):
        self.sessions: dict[str, GameSession] = {}

    # ──────────────────────────────────────────────
    # CREAR SESIÓN
    # ──────────────────────────────────────────────
    def create_session(
        self,
        player_name: str,
        mode: str = "classic",
        category: Optional[str] = None,
        levels: list[int] = None,
        custom_questions: list = None,
        num_questions: int = 30
    ) -> GameSession:

        session_id = f"{player_name}_{int(time.time())}"

        # Modo challenge: usar preguntas personalizadas directamente
        if mode == "challenge" and custom_questions:
            pool = custom_questions.copy()
            random.shuffle(pool)
            session = GameSession(
                session_id=session_id,
                player_name=player_name,
                mode=mode,
                category=category,
                questions_queue=pool,
                lives=99,  # Sin limite de vidas en challenges
            )
            self.sessions[session_id] = session
            return session

        # Seleccionar preguntas según modo
        if levels:
            pool = [q for q in QUESTIONS if q["level"] in levels]
        else:
            pool = QUESTIONS.copy()

        # Modo duelo: SOLO preguntas difíciles (nivel 5-6 = Experto/Leyenda)
        if mode == "duel":
            hard_pool = [q for q in QUESTIONS if q["level"] >= 5]
            if len(hard_pool) >= num_questions:
                pool = hard_pool
            else:
                # Si hay pocas preguntas duras, tomar las de nivel más alto disponibles
                pool = sorted(QUESTIONS, key=lambda q: q["level"], reverse=True)[:num_questions * 2]

        if category:
            pool = [q for q in pool if q["category"] == category]

        # Ordenar por nivel para el modo clásico
        if mode == "classic" or mode == "level_up":
            pool = sorted(pool, key=lambda q: q["level"])
        else:
            random.shuffle(pool)

        # Limitar preguntas según num_questions (solo modo classic)
        # Distribuye uniformemente entre los 6 niveles
        if mode == "classic":
            per_level = max(1, num_questions // 6)
            remainder = num_questions - per_level * 6  # preguntas extra para niveles bajos
            selected = []
            for level in range(1, 7):
                level_q = [q for q in pool if q["level"] == level]
                extra = 1 if (level - 1) < remainder else 0
                selected.extend(random.sample(level_q, min(per_level + extra, len(level_q))))
            pool = selected

        session = GameSession(
            session_id=session_id,
            player_name=player_name,
            mode=mode,
            category=category,
            questions_queue=pool,
        )

        self.sessions[session_id] = session
        return session

    # ──────────────────────────────────────────────
    # OBTENER PREGUNTA ACTUAL
    # ──────────────────────────────────────────────
    def get_current_question(self, session: GameSession) -> Optional[dict]:
        if session.finished:
            return None
        if session.current_question_idx >= len(session.questions_queue):
            session.finished = True
            return None

        q = session.questions_queue[session.current_question_idx]

        # Barajar opciones y aplicar el mismo orden a las traducciones i18n
        indices = list(range(len(q["options"])))
        random.shuffle(indices)
        shuffled_options = [q["options"][i] for i in indices]

        # Construir i18n barajando las opciones con el mismo orden
        shuffled_i18n = {}
        if q.get("i18n"):
            for lang, trans in q["i18n"].items():
                lang_opts = trans.get("options", [])
                shuffled_i18n[lang] = {
                    "question":    trans.get("question", ""),
                    "options":     [lang_opts[i] for i in indices] if lang_opts else [],
                    "answer":      trans.get("answer", ""),
                    "explanation": trans.get("explanation", ""),
                }

        return {
            "question_id": q["id"],
            "level": q["level"],
            "level_name": LEVELS_CONFIG[q["level"]]["name"],
            "level_emoji": LEVELS_CONFIG[q["level"]]["emoji"],
            "category": q["category"],
            "question": q["question"],
            "options": shuffled_options,
            "time_limit": LEVELS_CONFIG[q["level"]]["time"],
            "question_number": session.current_question_idx + 1,
            "total_questions": len(session.questions_queue),
            "i18n": shuffled_i18n,
        }

    # ──────────────────────────────────────────────
    # RESPONDER PREGUNTA
    # ──────────────────────────────────────────────
    def submit_answer(
        self,
        session: GameSession,
        question_id: int,
        selected_option: str,
        time_taken: float
    ) -> dict:

        if session.finished:
            return {"error": "Sesión finalizada"}

        q = session.questions_queue[session.current_question_idx]
        if q["id"] != question_id:
            return {"error": "Pregunta no coincide"}

        is_correct = selected_option.strip().lower() == q["answer"].strip().lower()
        level_config = LEVELS_CONFIG[q["level"]]

        # ── Calcular puntos ──
        points = 0
        if is_correct:
            base_points = level_config["points"]
            time_limit = level_config["time"]
            # Bonus por velocidad: hasta +50% si responde en la mitad del tiempo
            time_bonus = max(0, 1 - (time_taken / time_limit))
            speed_multiplier = 1 + (time_bonus * 0.5)
            # Bonus por racha
            streak_multiplier = 1 + (min(session.streak, 5) * 0.1)
            points = int(base_points * speed_multiplier * streak_multiplier)

            session.score += points
            session.streak += 1
            session.max_streak = max(session.max_streak, session.streak)
        else:
            session.streak = 0
            if session.mode == "classic":
                session.lives -= 1
                if session.lives <= 0:
                    session.finished = True

        # Guardar respuesta
        session.answers.append(Answer(
            question_id=question_id,
            selected=selected_option,
            correct=is_correct,
            time_taken=time_taken,
            points_earned=points
        ))

        # Avanzar pregunta
        session.current_question_idx += 1
        if session.current_question_idx >= len(session.questions_queue):
            session.finished = True

        return {
            "correct": is_correct,
            "correct_answer": q["answer"],
            "explanation": q["explanation"],
            "points_earned": points,
            "total_score": session.score,
            "streak": session.streak,
            "lives_remaining": session.lives,
            "game_over": session.finished,
        }

    # ──────────────────────────────────────────────
    # RESULTADOS FINALES
    # ──────────────────────────────────────────────
    def get_results(self, session: GameSession) -> dict:
        total_q = len(session.answers)
        correct_q = sum(1 for a in session.answers if a.correct)
        accuracy = round((correct_q / total_q * 100) if total_q > 0 else 0, 1)
        elapsed = round(time.time() - session.started_at, 1)

        # Determinar rango del jugador
        rank = self._get_rank(session.score, accuracy)

        return {
            "player_name": session.player_name,
            "score": session.score,
            "correct": correct_q,
            "total": total_q,
            "accuracy": accuracy,
            "max_streak": session.max_streak,
            "elapsed_seconds": elapsed,
            "rank": rank,
            "rank_emoji": rank["emoji"],
            "answers_detail": [
                {
                    "question_id": a.question_id,
                    "correct": a.correct,
                    "points": a.points_earned,
                    "time": a.time_taken
                } for a in session.answers
            ]
        }

    def _get_rank(self, score: int, accuracy: float) -> dict:
        if accuracy >= 95 and score >= 20000:
            return {"name": "⚽ LEYENDA DEL FUTBOL", "emoji": "🐐", "color": "#FFD700"}
        elif accuracy >= 85:
            return {"name": "🧠 Crack Supremo", "emoji": "👑", "color": "#C0C0C0"}
        elif accuracy >= 70:
            return {"name": "🔥 Enciclopedia del Futbol", "emoji": "📚", "color": "#CD7F32"}
        elif accuracy >= 55:
            return {"name": "📺 Aficionado", "emoji": "🎯", "color": "#4FC3F7"}
        else:
            return {"name": "🏠 Novato", "emoji": "😅", "color": "#90A4AE"}