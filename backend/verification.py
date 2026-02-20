"""
SISTEMA DE VERIFICACIÓN - El Crack Quiz
Verifica integridad, sesiones, usuarios y previene trampas
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import hashlib
import json

# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICADOR DE SESIONES
# ═══════════════════════════════════════════════════════════════════════════════

class SessionVerifier:
    """Verifica la integridad y validez de las sesiones de juego"""
    
    def __init__(self):
        self.active_sessions: Dict[str, dict] = {}
        self.session_timeout = 3600  # 1 hora en segundos
    
    def create_session(self, username: str, session_id: str, mode: str, category: str) -> Dict:
        """Crear y verificar una nueva sesión"""
        timestamp = datetime.now()
        
        session_data = {
            "username": username,
            "session_id": session_id,
            "mode": mode,
            "category": category,
            "created_at": timestamp,
            "expires_at": timestamp + timedelta(seconds=self.session_timeout),
            "verified": True,
            "hash": self._generate_session_hash(username, session_id),
            "questions_answered": 0,
            "answers_log": []
        }
        
        self.active_sessions[session_id] = session_data
        return session_data
    
    def verify_session(self, session_id: str) -> Tuple[bool, str]:
        """Verifica que una sesión sea válida"""
        if session_id not in self.active_sessions:
            return False, "❌ Sesión no encontrada"
        
        session = self.active_sessions[session_id]
        
        # Verificar que no haya expirado
        if datetime.now() > session["expires_at"]:
            del self.active_sessions[session_id]
            return False, "❌ Sesión expirada"
        
        # Verificar hash
        expected_hash = self._generate_session_hash(session["username"], session_id)
        if session["hash"] != expected_hash:
            return False, "❌ Sesión comprometida (hash inválido)"
        
        return True, "✅ Sesión válida"
    
    def log_answer(self, session_id: str, question_id: int, answer: str, correct: bool, time_taken: float) -> bool:
        """Registra una respuesta en el log de sesión"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session["answers_log"].append({
            "question_id": question_id,
            "answer": answer,
            "correct": correct,
            "time_taken": time_taken,
            "timestamp": datetime.now().isoformat()
        })
        session["questions_answered"] += 1
        return True
    
    def get_session_stats(self, session_id: str) -> Optional[Dict]:
        """Obtiene estadísticas de la sesión"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        answers = session["answers_log"]
        correct = sum(1 for a in answers if a["correct"])
        
        return {
            "session_id": session_id,
            "username": session["username"],
            "mode": session["mode"],
            "category": session["category"],
            "questions_answered": len(answers),
            "correct_answers": correct,
            "accuracy": (correct / len(answers) * 100) if answers else 0,
            "created_at": session["created_at"].isoformat(),
            "duration": (datetime.now() - session["created_at"]).total_seconds()
        }
    
    def close_session(self, session_id: str) -> bool:
        """Cierra una sesión"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False
    
    @staticmethod
    def _generate_session_hash(username: str, session_id: str) -> str:
        """Genera un hash para verificar la integridad de la sesión"""
        data = f"{username}:{session_id}:verified"
        return hashlib.sha256(data.encode()).hexdigest()

# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICADOR DE RESPUESTAS
# ═══════════════════════════════════════════════════════════════════════════════

class AnswerVerifier:
    """Verifica la integridad y validez de las respuestas"""
    
    def __init__(self):
        self.answer_history: Dict[str, list] = {}
    
    def verify_answer(self, question_id: int, selected_option: str, correct_option: str) -> Tuple[bool, str]:
        """
        Verifica una respuesta
        
        Args:
            question_id: ID de la pregunta
            selected_option: Opción seleccionada por el usuario
            correct_option: Opción correcta (desde la BD)
        
        Returns:
            (is_correct, message)
        """
        
        # Verificar que ambas opciones existan
        if not selected_option or not correct_option:
            return False, "❌ Opción inválida"
        
        # Comparar (case-insensitive)
        is_correct = selected_option.lower().strip() == correct_option.lower().strip()
        
        message = "✅ Respuesta correcta" if is_correct else "❌ Respuesta incorrecta"
        return is_correct, message
    
    def detect_cheating(self, session_id: str, answers: list) -> Tuple[bool, str]:
        """
        Detecta patrones de trampa en las respuestas
        
        Indicadores de trampa:
        - Todas las respuestas correctas en tiempo imposiblemente corto
        - Mismos patrones de respuesta múltiples veces
        - Tiempos de respuesta anormalmente rápidos
        """
        
        if not answers or len(answers) < 3:
            return False, "✅ Sin indicadores de trampa"
        
        correct_count = sum(1 for a in answers if a.get("correct"))
        accuracy = (correct_count / len(answers)) * 100
        
        # ⚠️ Verificación 1: Accuracy 100% con velocidad extrema
        avg_time = sum(a.get("time_taken", 10) for a in answers) / len(answers)
        if accuracy == 100 and avg_time < 2:
            return True, "⚠️  Patrón sospechoso: 100% acertadas demasiado rápido"
        
        # ⚠️ Verificación 2: Todas correctas pero con tiempos muy variables
        if accuracy == 100 and len(set(a.get("time_taken", 0) for a in answers)) == 1:
            return True, "⚠️  Patrón sospechoso: tiempos idénticos en todas"
        
        # ⚠️ Verificación 3: Demasiadas respuestas en muy poco tiempo
        total_time = sum(a.get("time_taken", 0) for a in answers)
        if total_time < len(answers) * 1.5:  # Menos de 1.5 segundos promedio
            return True, "⚠️  Velocidad de respuesta anormalmente rápida"
        
        return False, "✅ Sin indicadores de trampa detectados"
    
    def log_answer(self, session_id: str, answer_data: dict) -> None:
        """Registra una respuesta en el histórico"""
        if session_id not in self.answer_history:
            self.answer_history[session_id] = []
        self.answer_history[session_id].append(answer_data)

# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICADOR DE USUARIO
# ═══════════════════════════════════════════════════════════════════════════════

class UserVerifier:
    """Verifica la validez de los datos del usuario"""
    
    @staticmethod
    def verify_username(username: str) -> Tuple[bool, str]:
        """Verifica que el nombre de usuario sea válido"""
        
        if not username:
            return False, "❌ El nombre no puede estar vacío"
        
        if len(username) < 2:
            return False, "❌ El nombre debe tener al menos 2 caracteres"
        
        if len(username) > 20:
            return False, "❌ El nombre no puede exceder 20 caracteres"
        
        # Solo letras, números y algunos caracteres especiales
        if not all(c.isalnum() or c in "-_ " for c in username):
            return False, "❌ Nombre contiene caracteres no permitidos"
        
        return True, "✅ Nombre válido"
    
    @staticmethod
    def verify_score(score: int, correct: int, total: int) -> Tuple[bool, str]:
        """
        Verifica que la puntuación sea coherente
        
        Score = (correct / total) * max_points
        """
        
        if not (0 <= score <= 250 * total):
            return False, f"❌ Puntuación incoherente: {score} puntos para {correct}/{total}"
        
        if not (0 <= correct <= total):
            return False, "❌ Número de respuestas coherentes inválido"
        
        accuracy = (correct / total * 100) if total > 0 else 0
        if not (0 <= accuracy <= 100):
            return False, "❌ Porcentaje de acurácia inválido"
        
        return True, "✅ Puntuación válida"
    
    @staticmethod
    def verify_team(team: dict, available_players: list) -> Tuple[bool, str]:
        """
        Verifica que el equipo 4-3-3 sea válido
        
        Estructura esperada:
        {
            "POR": player_id,
            "DEF1": player_id, "DEF2": player_id, "DEF3": player_id, "DEF4": player_id,
            "MED1": player_id, "MED2": player_id, "MED3": player_id,
            "DEL1": player_id, "DEL2": player_id, "DEL3": player_id
        }
        """
        
        required_positions = {"POR", "DEF1", "DEF2", "DEF3", "DEF4", "MED1", "MED2", "MED3", "DEL1", "DEL2", "DEL3"}
        
        if set(team.keys()) != required_positions:
            return False, f"❌ Formación inválida. Posiciones requeridas: {required_positions}"
        
        # Verificar que no haya jugadores duplicados
        players = list(team.values())
        if len(players) != len(set(players)):
            return False, "❌ No puedes usar el mismo jugador dos veces"
        
        # Verificar que todos los jugadores estén disponibles
        available_ids = [p["id"] for p in available_players]
        for player_id in players:
            if player_id not in available_ids:
                return False, f"❌ Jugador {player_id} no disponible"
        
        return True, "✅ Equipo válido"

# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICADOR DE INTEGRIDAD
# ═══════════════════════════════════════════════════════════════════════════════

class IntegrityVerifier:
    """Verifica la integridad general del juego"""
    
    def __init__(self):
        self.session_verifier = SessionVerifier()
        self.answer_verifier = AnswerVerifier()
        self.user_verifier = UserVerifier()
    
    def verify_game_data(self, session_data: dict) -> Tuple[bool, Dict]:
        """Verifica todos los datos de una sesión de juego"""
        
        results = {
            "session_valid": False,
            "answers_clean": False,
            "user_valid": False,
            "cheating_detected": False,
            "overall_status": "❌ Verificación fallida",
            "details": []
        }
        
        session_id = session_data.get("session_id")
        username = session_data.get("username")
        answers = session_data.get("answers", [])
        
        # 1. Verificar sesión
        is_valid, msg = self.session_verifier.verify_session(session_id)
        results["session_valid"] = is_valid
        results["details"].append(f"Sesión: {msg}")
        
        # 2. Verificar usuario
        is_valid, msg = self.user_verifier.verify_username(username)
        results["user_valid"] = is_valid
        results["details"].append(f"Usuario: {msg}")
        
        # 3. Detectar trampa
        cheating, msg = self.answer_verifier.detect_cheating(session_id, answers)
        results["cheating_detected"] = cheating
        results["details"].append(f"Anti-trampa: {msg}")
        results["answers_clean"] = not cheating
        
        # Determinar estado general
        if results["session_valid"] and results["user_valid"] and results["answers_clean"]:
            results["overall_status"] = "✅ Verificación exitosa"
        
        return results["overall_status"] == "✅ Verificación exitosa", results

# ═══════════════════════════════════════════════════════════════════════════════
# REPORTADOR DE VERIFICACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

class VerificationReport:
    """Genera reportes de verificación para el cliente"""
    
    @staticmethod
    def generate_report(verification_results: Dict) -> Dict:
        """Genera un reporte visual de la verificación"""
        
        return {
            "status": verification_results["overall_status"],
            "verified": verification_results["overall_status"].startswith("✅"),
            "session_check": "✅ PASS" if verification_results["session_valid"] else "❌ FAIL",
            "user_check": "✅ PASS" if verification_results["user_valid"] else "❌ FAIL",
            "integrity_check": "✅ PASS" if verification_results["answers_clean"] else "❌ FAIL",
            "anti_cheat_check": "✅ PASS" if not verification_results["cheating_detected"] else "⚠️  WARNING",
            "details": verification_results["details"],
            "timestamp": datetime.now().isoformat()
        }

# ═══════════════════════════════════════════════════════════════════════════════
# INSTANCIAS GLOBALES
# ═══════════════════════════════════════════════════════════════════════════════

session_verifier = SessionVerifier()
answer_verifier = AnswerVerifier()
user_verifier = UserVerifier()
integrity_verifier = IntegrityVerifier()
