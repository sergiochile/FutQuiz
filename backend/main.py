"""
API Backend - El Crack Quiz
FastAPI REST API para el motor del juego
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import sys, os
import hashlib
import secrets
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.quiz_engine import QuizEngine
from backend.data.questions import CATEGORIES, LEVELS_CONFIG
from backend.data.players import PLAYERS, RARITY_CONFIG
from backend.data.challenge_questions import get_challenge_questions
from backend.database import (
    init_db, get_or_create_user, get_user_players, unlock_player,
    unlock_player_by_type, get_user_team, set_user_team, save_game,
    get_team_rankings, get_global_leaderboard, get_player_by_id,
    get_user_league, record_league_result, LEAGUE_DIVISIONS,
    get_daily_reward_status, claim_daily_reward,
    get_user_energy, consume_energy, refill_energy,
    get_user_xp, add_xp,
    create_duel_challenge, get_pending_duels, get_active_duels,
    accept_duel_challenge, reject_duel_challenge, resolve_duel,
    join_matchmaking_queue, cancel_matchmaking, get_matchmaking_status, respond_to_match,
    start_duel_session, update_duel_heartbeat, finish_duel_session,
    get_duel_session_status, get_duel_stats, abandon_duel,
)
from backend.verification import (
    session_verifier, answer_verifier, user_verifier,
    integrity_verifier, VerificationReport
)

# ──────────────────────────────────────────────
# Configuración desde variables de entorno
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,null"
).split(",")

# En producción usar wildcard para cubrir todos los dominios de Facebook CDN
# (auth usa tokens en body, no cookies, por lo que credentials=False es seguro)
IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"

app = FastAPI(title="El Crack Quiz API", version="0.2.0")
engine = QuizEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if IS_PRODUCTION else ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# Inicializar DB al arrancar
init_db()

# ──────────────────────────────────────────────
# HEALTH CHECK (necesario para Railway/Render)
# ──────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.2.0"}

# ──────────────────────────────────────────────
# MODELOS PYDANTIC
# ──────────────────────────────────────────────

# AUTENTICACIÓN
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    success: bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    auth_token: Optional[str] = None
    message: str = ""

# JUEGO
class StartGameRequest(BaseModel):
    player_name: str
    mode: str = "classic"        # classic | speed | level_up
    category: Optional[str] = None
    num_questions: int = 30      # 10 | 20 | 30 (solo aplica en modo classic)

class AnswerRequest(BaseModel):
    session_id: str
    question_id: int
    selected_option: str
    time_taken: float            # segundos

class FinishGameRequest(BaseModel):
    username: str
    score: int
    accuracy: float
    correct: int
    total: int
    mode: Optional[str] = "classic"   # classic | speed | level_up | duel | challenge | pvp
    won: Optional[bool] = None        # Victoria explícita (usado en duelos)

class SaveTeamRequest(BaseModel):
    team: dict[str, int]         # {"POR": 76, "DEF1": 79, ...}

class ChallengeStartRequest(BaseModel):
    username: str
    challenge_id: int

class ChallengeCompleteRequest(BaseModel):
    username: str
    challenge_id: int
    score: int
    correct: int
    total: int

class UsernameRequest(BaseModel):
    username: str

class EnergyRefillRequest(BaseModel):
    username: str
    amount: int = 1

class BotSimulateRequest(BaseModel):
    total_questions: int = 10
    difficulty: str = "medium"

class DuelChallengeRequest(BaseModel):
    challenger: str
    opponent_username: str
    wager_type: Optional[str] = None       # 'xp' | 'player' | None
    wager_xp_amount: int = 0
    wager_player_id: Optional[int] = None

class DuelAcceptRequest(BaseModel):
    username: str
    challenge_id: int
    accept: bool = True                    # True=aceptar, False=rechazar

class DuelResultRequest(BaseModel):
    username: str                          # quien reporta el resultado
    challenge_id: int
    winner_username: str
    challenger_score: int = 0
    opponent_score: int = 0

# ──────────────────────────────────────────────
# UTILIDADES DE AUTENTICACIÓN
# ──────────────────────────────────────────────

# Almacenamiento de sesiones (en prod: usar Redis)
sessions = {}

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hashea una contraseña con PBKDF2"""
    if salt is None:
        salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hash_obj.hex()}", salt

def verify_password(password: str, hash_with_salt: str) -> bool:
    """Verifica una contraseña contra su hash"""
    try:
        salt = hash_with_salt.split('$')[0]
        new_hash, _ = hash_password(password, salt)
        return new_hash == hash_with_salt
    except Exception:
        return False

def generate_token() -> str:
    """Genera un token único de sesión"""
    return secrets.token_urlsafe(32)

def get_player_photo_url(player_name: str, player_id: int) -> str:
    """Obtiene la URL de foto de un jugador usando el campo photo del catálogo"""
    from backend.data.players import get_player_by_id as _gpbi
    p = _gpbi(player_id)
    if p and p.get("photo"):
        return p["photo"]
    # fallback silueta genérica
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Unknown_person.jpg/240px-Unknown_person.jpg"

# ──────────────────────────────────────────────
# ENDPOINTS — AUTENTICACIÓN
# ──────────────────────────────────────────────

@app.post("/api/auth/register", response_model=AuthResponse)
def register(req: RegisterRequest):
    """Registrar un nuevo usuario"""
    try:
        # Validaciones básicas
        if len(req.username) < 3 or len(req.username) > 20:
            return AuthResponse(success=False, message="Usuario debe tener 3-20 caracteres")

        if len(req.password) < 4:
            return AuthResponse(success=False, message="Contraseña debe tener mínimo 4 caracteres")

        # Generar email interno automáticamente
        internal_email = f"{req.username.lower()}@futquiz.internal"

        # Verificar que el usuario no exista ya
        import sqlite3 as _sqlite3
        from backend.database import DB_PATH as _DB_PATH
        _conn = _sqlite3.connect(_DB_PATH)
        _existing = _conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (req.username,)
        ).fetchone()
        _conn.close()
        if _existing:
            return AuthResponse(success=False, message="Ese nombre de usuario ya está en uso")

        # Hash de contraseña
        password_hash, _ = hash_password(req.password)

        # Crear usuario
        user = get_or_create_user(req.username, internal_email, password_hash)

        if user is None:
            return AuthResponse(success=False, message="Error al crear el usuario")
        
        # Generar token
        token = generate_token()
        sessions[token] = {
            "user_id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "created_at": datetime.now()
        }
        
        return AuthResponse(
            success=True,
            user_id=user["id"],
            username=user["username"],
            email=user["email"],
            auth_token=token,
            message="Usuario registrado exitosamente"
        )
    except Exception as e:
        return AuthResponse(success=False, message=f"Error: {str(e)}")

@app.post("/api/auth/login", response_model=AuthResponse)
def login(req: LoginRequest):
    """Iniciar sesión"""
    try:
        # Buscar usuario por username
        import sqlite3
        from backend.database import DB_PATH
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM users WHERE username = ?", (req.username,)).fetchone()
        conn.close()
        
        if not row:
            return AuthResponse(success=False, message="Usuario o contraseña incorrectos")
        
        user = dict(row)
        
        # Verificar contraseña
        if not verify_password(req.password, user["password_hash"]):
            return AuthResponse(success=False, message="Usuario o contraseña incorrectos")
        
        # Generar token
        token = generate_token()
        sessions[token] = {
            "user_id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "created_at": datetime.now()
        }
        
        return AuthResponse(
            success=True,
            user_id=user["id"],
            username=user["username"],
            email=user["email"],
            auth_token=token,
            message="Inicio de sesión exitoso"
        )
    except Exception as e:
        return AuthResponse(success=False, message=f"Error: {str(e)}")

@app.post("/api/auth/logout")
def logout(auth_token: str):
    """Cerrar sesión"""
    if auth_token in sessions:
        del sessions[auth_token]
        return {"success": True, "message": "Sesión cerrada"}
    return {"success": False, "message": "Token inválido"}

@app.get("/api/auth/me")
def get_current_user(auth_token: str):
    """Obtener info del usuario actual"""
    if auth_token not in sessions:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    session = sessions[auth_token]
    return {
        "user_id": session["user_id"],
        "username": session["username"],
        "email": session["email"]
    }

# ──────────────────────────────────────────────
# ENDPOINTS — JUEGO
# ──────────────────────────────────────────────

@app.get("/")
def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html"))


# Pequeño endpoint para servir config.js (el frontend incluye <script src="config.js">)
@app.get("/config.js")
def get_config_js():
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "config.js")
    return FileResponse(path, media_type="application/javascript")

# Servir translations.js (el frontend incluye <script src="translations.js">)
@app.get("/translations.js")
def get_translations_js():
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "translations.js")
    return FileResponse(path, media_type="application/javascript")

@app.get("/api/info")
def get_game_info():
    """Info del juego: categorías, niveles y modos"""
    return {
        "categories": CATEGORIES,
        "levels": LEVELS_CONFIG,
        "modes": {
            "classic": "Modo Clasico - 30 preguntas, 6 niveles, 3 vidas",
            "speed": "Modo Velocidad - 60 segundos, preguntas sin parar",
            "level_up": "Modo Escalada - subes de nivel respondiendo correctamente",
        }
    }

@app.post("/api/game/start")
def start_game(req: StartGameRequest):
    """Iniciar una nueva partida"""
    if not req.player_name.strip():
        raise HTTPException(400, "El nombre no puede estar vacío")
    if req.category and req.category not in CATEGORIES:
        raise HTTPException(400, f"Categoría inválida. Opciones: {list(CATEGORIES.keys())}")

    session = engine.create_session(
        player_name=req.player_name.strip(),
        mode=req.mode,
        category=req.category,
        num_questions=req.num_questions,
    )

    first_q = engine.get_current_question(session)

    return {
        "session_id": session.session_id,
        "player_name": session.player_name,
        "mode": session.mode,
        "total_questions": len(session.questions_queue),
        "first_question": first_q,
        "lives": session.lives,
    }

@app.get("/api/game/{session_id}/question")
def get_question(session_id: str):
    """Obtener la pregunta actual de la sesión"""
    if session_id not in engine.sessions:
        raise HTTPException(404, "Sesión no encontrada")

    session = engine.sessions[session_id]
    question = engine.get_current_question(session)

    if question is None:
        return {"game_over": True, "message": "Partida finalizada"}

    # Obtener limite de tiempo basado en el nivel de la pregunta
    time_limit = 20 # Default
    if question:
        lvl = question.get("level", 1)
        time_limit = LEVELS_CONFIG.get(lvl, {}).get("time", 20)

    return {
        "game_over": False,
        "score": session.score,
        "streak": session.streak,
        "lives": session.lives,
        "question": question,
        "time_limit": time_limit
    }

@app.post("/api/game/answer")
def submit_answer(req: AnswerRequest):
    """Enviar respuesta a una pregunta"""
    if req.session_id not in engine.sessions:
        raise HTTPException(404, "Sesión no encontrada")

    session = engine.sessions[req.session_id]
    result = engine.submit_answer(
        session=session,
        question_id=req.question_id,
        selected_option=req.selected_option,
        time_taken=req.time_taken,
    )

    if result.get("game_over"):
        return {**result, "redirect": f"/api/game/{req.session_id}/results"}

    return result

@app.get("/api/game/{session_id}/results")
def get_results(session_id: str):
    """Obtener resultados finales de la partida"""
    if session_id not in engine.sessions:
        raise HTTPException(404, "Sesión no encontrada")

    session = engine.sessions[session_id]
    if not session.finished:
        raise HTTPException(400, "La partida aún no ha terminado")

    return engine.get_results(session)

# ──────────────────────────────────────────────
# ENDPOINTS — USUARIOS Y EQUIPO
# ──────────────────────────────────────────────

@app.post("/api/user/register")
@app.get("/api/user/register")
def register_user(username: str):
    """Registrar o recuperar usuario"""
    if not username.strip():
        raise HTTPException(400, "El nombre no puede estar vacío")
    user = get_or_create_user(username.strip())
    owned = get_user_players(user["id"])
    team = get_user_team(user["id"])
    return {
        "user_id": user["id"],
        "username": user["username"],
        "unlocked_count": len(owned),
        "unlocked_ids": owned,
        "team": team,
    }

@app.post("/api/game/finish")
def finish_game(req: FinishGameRequest):
    """Finalizar partida, guardar en historial y desbloquear jugador"""
    user = get_or_create_user(req.username.strip())
    game_mode = req.mode or "classic"
    unlocked = unlock_player(user["id"], req.score, mode=game_mode)
    save_game(
        user_id=user["id"],
        score=req.score,
        accuracy=req.accuracy,
        correct=req.correct,
        total=req.total,
        unlocked_id=unlocked["id"] if unlocked else None,
    )
    # Sumar XP equivalente al score de la partida
    xp_earned = req.score
    total_xp = add_xp(user["id"], xp_earned)
    return {
        "saved": True,
        "player_unlocked": unlocked,
        "total_unlocked": len(get_user_players(user["id"])),
        "total_catalog": len(PLAYERS),
        "xp_earned": xp_earned,
        "total_xp": total_xp,
    }

@app.get("/api/user/{username}/xp")
def user_xp(username: str):
    """Devuelve el XP total acumulado del usuario."""
    user = get_or_create_user(username.strip())
    return {"username": username, "xp": get_user_xp(user["id"])}

@app.get("/api/user/{username}/players")
def get_players(username: str):
    """Ver jugadores desbloqueados de un usuario"""
    user = get_or_create_user(username)
    owned_ids = get_user_players(user["id"])
    owned_players = [get_player_by_id(pid) for pid in owned_ids if get_player_by_id(pid)]
    return {
        "username": username,
        "unlocked": owned_players,
        "unlocked_count": len(owned_players),
        "total_catalog": len(PLAYERS),
    }

@app.get("/api/user/{username}/team")
def get_team(username: str):
    """Ver equipo titular"""
    user = get_or_create_user(username)
    team = get_user_team(user["id"])
    total_rating = sum(p["rating"] for p in team.values()) if team else 0
    return {
        "username": username,
        "team": team,
        "team_value": total_rating,
        "players_count": len(team),
    }

@app.post("/api/user/{username}/team")
def save_team(username: str, req: SaveTeamRequest):
    """Guardar equipo titular"""
    user = get_or_create_user(username)
    success = set_user_team(user["id"], req.team)
    if not success:
        raise HTTPException(400, "Equipo invalido: posicion incorrecta o jugador no desbloqueado")
    team = get_user_team(user["id"])
    total_rating = sum(p["rating"] for p in team.values())
    return {"saved": True, "team_value": total_rating}

@app.get("/api/players/catalog")
def get_catalog(username: Optional[str] = None):
    """Catalogo completo de jugadores con fotos"""
    owned_ids = set()
    if username:
        user = get_or_create_user(username)
        owned_ids = set(get_user_players(user["id"]))

    catalog = []
    for p in PLAYERS:
        photo_url = p.get("photo") or get_player_photo_url(p["name"], p["id"])
        catalog.append({
            **p,
            "photo": photo_url,
            "unlocked": p["id"] in owned_ids,
        })
    return {
        "players": catalog,
        "total": len(PLAYERS),
        "unlocked": len(owned_ids),
        "rarity_config": RARITY_CONFIG,
    }

@app.get("/api/ranking/teams")
def ranking_teams():
    """Ranking de mejores equipos por valor"""
    return {"rankings": get_team_rankings()}

# ──────────────────────────────────────────────
# LEADERBOARD (ahora con DB)
# ──────────────────────────────────────────────

@app.get("/api/leaderboard")
def get_leaderboard():
    """Top 20 mejores partidas"""
    return {"leaderboard": get_global_leaderboard()}

# ──────────────────────────────────────────────
# NUEVOS ENDPOINTS — COMPARACIÓN Y CHALLENGES
# ──────────────────────────────────────────────

@app.get("/api/user/{username1}/vs/{username2}")
def compare_teams(username1: str, username2: str):
    """Comparar dos equipos lado a lado"""
    user1 = get_or_create_user(username1)
    user2 = get_or_create_user(username2)
    
    team1 = get_user_team(user1["id"])
    team2 = get_user_team(user2["id"])
    
    value1 = sum(p["rating"] for p in team1.values()) if team1 else 0
    value2 = sum(p["rating"] for p in team2.values()) if team2 else 0
    
    return {
        "comparison": {
            "user1": {
                "username": username1,
                "team": team1,
                "team_value": value1,
                "team_complete": len(team1) == 11,
            },
            "user2": {
                "username": username2,
                "team": team2,
                "team_value": value2,
                "team_complete": len(team2) == 11,
            },
            "winner": "user1" if value1 > value2 else "user2" if value2 > value1 else "tie",
            "difference": abs(value1 - value2),
        }
    }

@app.get("/api/user/{username}/challenges")
def get_challenges(username: str):
    """Ver progreso de challenges del usuario"""
    user = get_or_create_user(username)
    owned_ids = get_user_players(user["id"])
    owned_players = [get_player_by_id(pid) for pid in owned_ids]
    team = get_user_team(user["id"])
    team_value = sum(p["rating"] for p in team.values()) if team else 0
    
    # Definir challenges
    challenges = [
        {
            "id": 1,
            "name": "El Triángulo de Oro",
            "emoji": "🥇",
            "description": "Desbloquea 3 leyendas",
            "progress": len([p for p in owned_players if p.get("rarity") == "leyenda"]),
            "target": 3,
            "completed": len([p for p in owned_players if p.get("rarity") == "leyenda"]) >= 3,
        },
        {
            "id": 2,
            "name": "Portazo Perfecto",
            "emoji": "🧤",
            "description": "Desbloquea todos los porteros",
            "progress": len([p for p in owned_players if p.get("position") == "POR"]),
            "target": len([p for p in PLAYERS if p.get("position") == "POR"]),
            "completed": len([p for p in owned_players if p.get("position") == "POR"]) >= len([p for p in PLAYERS if p.get("position") == "POR"]),
        },
        {
            "id": 3,
            "name": "La Defensa Inquebrantable",
            "emoji": "🛡️",
            "description": "Desbloquea 5 defensas oro+",
            "progress": len([p for p in owned_players if p.get("position") == "DEF" and p.get("rating", 0) >= 85]),
            "target": 5,
            "completed": len([p for p in owned_players if p.get("position") == "DEF" and p.get("rating", 0) >= 85]) >= 5,
        },
        {
            "id": 4,
            "name": "Mediocampo Dominador",
            "emoji": "🎯",
            "description": "Desbloquea 3 mediocampistas diamante+",
            "progress": len([p for p in owned_players if p.get("position") == "MED" and p.get("rating", 0) >= 90]),
            "target": 3,
            "completed": len([p for p in owned_players if p.get("position") == "MED" and p.get("rating", 0) >= 90]) >= 3,
        },
        {
            "id": 5,
            "name": "Ataque Letal",
            "emoji": "⚡",
            "description": "Desbloquea 4 delanteros",
            "progress": len([p for p in owned_players if p.get("position") == "DEL"]),
            "target": 4,
            "completed": len([p for p in owned_players if p.get("position") == "DEL"]) >= 4,
        },
        {
            "id": 6,
            "name": "Equipo Perfecto 100",
            "emoji": "💯",
            "description": "Logra un equipo con valor total 1000+",
            "progress": team_value,
            "target": 1000,
            "completed": team_value >= 1000,
        },
    ]
    
    return {
        "username": username,
        "challenges": challenges,
        "challenges_completed": sum(1 for c in challenges if c["completed"]),
        "total_challenges": len(challenges),
    }

# ──────────────────────────────────────────────
# ENDPOINTS — CHALLENGE QUIZ
# ──────────────────────────────────────────────

# Mapeo de challenge_id a tipo de jugador que desbloquea
CHALLENGE_UNLOCK_MAP = {
    1: {"rarity": "leyenda"},                              # El Triangulo de Oro
    2: {"position": "POR"},                                # Portazo Perfecto
    3: {"position": "DEF", "min_rating": 85},              # Defensa Inquebrantable
    4: {"position": "MED", "min_rating": 90},              # Mediocampo Dominador
    5: {"position": "DEL"},                                # Ataque Letal
    6: {},                                                 # Equipo Perfecto (cualquier jugador)
}

@app.post("/api/challenge/start")
def start_challenge(req: ChallengeStartRequest):
    """Iniciar un quiz de challenge tematico"""
    if req.challenge_id not in range(1, 7):
        raise HTTPException(400, "Challenge ID invalido (1-6)")

    questions = get_challenge_questions(req.challenge_id)
    if not questions:
        raise HTTPException(500, "No hay preguntas para este challenge")

    get_or_create_user(req.username.strip())  # Asegurar que el usuario existe

    session = engine.create_session(
        player_name=req.username.strip(),
        mode="challenge",
        category=f"challenge_{req.challenge_id}",
        custom_questions=questions,
    )

    first_q = engine.get_current_question(session)

    return {
        "session_id": session.session_id,
        "challenge_id": req.challenge_id,
        "total_questions": len(session.questions_queue),
        "first_question": first_q,
    }

@app.post("/api/challenge/complete")
def complete_challenge(req: ChallengeCompleteRequest):
    """Completar un challenge quiz y desbloquear jugador si aprueba"""
    if req.challenge_id not in range(1, 7):
        raise HTTPException(400, "Challenge ID invalido (1-6)")

    user = get_or_create_user(req.username.strip())
    min_correct = 7  # Necesita 7/10 para aprobar

    if req.correct < min_correct:
        return {
            "success": False,
            "passed": False,
            "player_unlocked": None,
            "message": f"Necesitas {min_correct}/{req.total} correctas para aprobar. Conseguiste {req.correct}/{req.total}.",
            "min_required": min_correct,
        }

    # Desbloquear jugador del tipo correcto
    unlock_params = CHALLENGE_UNLOCK_MAP.get(req.challenge_id, {})
    unlocked = unlock_player_by_type(user["id"], **unlock_params)

    # Guardar partida en historial
    accuracy = (req.correct / req.total * 100) if req.total > 0 else 0
    save_game(
        user_id=user["id"],
        score=req.score,
        accuracy=accuracy,
        correct=req.correct,
        total=req.total,
        unlocked_id=unlocked["id"] if unlocked else None,
    )

    return {
        "success": True,
        "passed": True,
        "player_unlocked": unlocked,
        "message": f"Challenge completado con {req.correct}/{req.total} correctas!",
        "total_unlocked": len(get_user_players(user["id"])),
    }

# ──────────────────────────────────────────────
# ENDPOINTS — VERIFICACIÓN
# ──────────────────────────────────────────────

@app.get("/api/verify/session/{session_id}")
def verify_session(session_id: str):
    """Verifica la integridad de una sesión activa"""
    is_valid, msg = session_verifier.verify_session(session_id)
    
    return {
        "session_id": session_id,
        "verified": is_valid,
        "status": msg,
        "is_active": session_id in session_verifier.active_sessions
    }

@app.get("/api/verify/user/{username}")
def verify_user(username: str):
    """Verifica que el nombre de usuario sea válido"""
    is_valid, msg = user_verifier.verify_username(username)
    
    return {
        "username": username,
        "valid": is_valid,
        "status": msg
    }

class VerifyAnswerRequest(BaseModel):
    question_id: int
    selected_option: str
    correct_option: str
    time_taken: float = 0.0

@app.post("/api/verify/answer")
def verify_answer(req: VerifyAnswerRequest):
    """Verifica una respuesta individual"""
    is_correct, msg = answer_verifier.verify_answer(
        req.question_id,
        req.selected_option,
        req.correct_option
    )
    
    return {
        "question_id": req.question_id,
        "correct": is_correct,
        "status": msg,
        "message": "Respuesta correcta ✅" if is_correct else "Respuesta incorrecta ❌"
    }

class VerifyScoreRequest(BaseModel):
    score: int
    correct: int
    total: int

@app.post("/api/verify/score")
def verify_score(req: VerifyScoreRequest):
    """Verifica que una puntuación sea coherente"""
    is_valid, msg = user_verifier.verify_score(req.score, req.correct, req.total)
    
    accuracy = (req.correct / req.total * 100) if req.total > 0 else 0
    
    return {
        "score": req.score,
        "correct": req.correct,
        "total": req.total,
        "accuracy": accuracy,
        "valid": is_valid,
        "status": msg
    }

class VerifyTeamRequest(BaseModel):
    team: dict
    available_players: list

@app.post("/api/verify/team")
def verify_team(req: VerifyTeamRequest):
    """Verifica que un equipo 4-3-3 sea válido"""
    is_valid, msg = user_verifier.verify_team(req.team, req.available_players)
    
    return {
        "team": req.team,
        "valid": is_valid,
        "status": msg,
        "positions": list(req.team.keys()),
        "formation": "4-3-3"
    }

class DetectCheatRequest(BaseModel):
    session_id: str
    answers: list

@app.post("/api/verify/cheat-detection")
def detect_cheat(req: DetectCheatRequest):
    """Detecta patrones de trampa en las respuestas"""
    is_cheating, msg = answer_verifier.detect_cheating(req.session_id, req.answers)
    
    stats = {}
    if req.answers:
        correct = sum(1 for a in req.answers if a.get("correct"))
        accuracy = (correct / len(req.answers) * 100)
        avg_time = sum(a.get("time_taken", 10) for a in req.answers) / len(req.answers)
        stats = {
            "total_answers": len(req.answers),
            "correct_answers": correct,
            "accuracy": accuracy,
            "average_time": round(avg_time, 2)
        }
    
    return {
        "session_id": req.session_id,
        "cheating_detected": is_cheating,
        "status": msg,
        "severity": "🔴 ALTA" if is_cheating else "✅ BAJA",
        "stats": stats
    }

@app.get("/api/verify/session-stats/{session_id}")
def get_session_stats(session_id: str):
    """Obtiene estadísticas completas de una sesión"""
    stats = session_verifier.get_session_stats(session_id)
    
    if not stats:
        return {
            "error": "Sesión no encontrada",
            "session_id": session_id
        }
    
    return {
        "session_id": session_id,
        "username": stats["username"],
        "mode": stats["mode"],
        "category": stats["category"],
        "questions_answered": stats["questions_answered"],
        "correct_answers": stats["correct_answers"],
        "accuracy_percent": round(stats["accuracy"], 2),
        "duration_seconds": round(stats["duration"], 2),
        "created_at": stats["created_at"]
    }

@app.get("/api/verify/system-health")
def system_health():
    """Verifica la salud general del sistema de verificación"""
    return {
        "verification_system": "✅ Activo",
        "active_sessions": len(session_verifier.active_sessions),
        "session_timeout_minutes": session_verifier.session_timeout // 60,
        "components": {
            "session_verifier": "✅ OK",
            "answer_verifier": "✅ OK",
            "user_verifier": "✅ OK",
            "integrity_verifier": "✅ OK"
        },
        "status": "✅ SISTEMA VERIFICACIÓN OPERATIVO"
    }


# ──────────────────────────────────────────────
# ENDPOINTS — COMPLETA EL XI
# ──────────────────────────────────────────────
import random as _random
from backend.data.xi_teams import get_all_xi_teams, get_xi_team_by_id

class XiCheckRequest(BaseModel):
    team_id: int
    answers: dict  # {"DEF1": "Carvajal", "DEF3": "Alaba", ...}


def _xi_sanitize(team: dict) -> dict:
    """Quita los nombres de los slots ocultos antes de enviar al cliente.
       La foto siempre se envía (para slots conocidos se muestra desde el inicio;
       para slots ocultos se muestra al revelar la respuesta)."""
    sanitized_players = []
    for p in team["players"]:
        sanitized_players.append({
            "slot":   p["slot"],
            "hidden": p["hidden"],
            "name":   None if p["hidden"] else p["name"],
            "photo":  p.get("photo", ""),
        })
    return {
        "id":           team["id"],
        "name":         team["name"],
        "season":       team["season"],
        "badge":        team["badge"],
        "difficulty":   team["difficulty"],
        "curiosity":    team["curiosity"],
        "formation":    team["formation"],
        "players":      sanitized_players,
        "hidden_count": sum(1 for p in team["players"] if p["hidden"]),
    }


@app.get("/api/xi/random")
def xi_random(difficulty: str = None):
    """Devuelve un equipo aleatorio para el juego Completa el XI."""
    teams = get_all_xi_teams()
    if difficulty:
        filtered = [t for t in teams if t.get("difficulty") == difficulty]
        if filtered:
            teams = filtered
    team = _random.choice(teams)
    return _xi_sanitize(team)


@app.get("/api/xi/list")
def xi_list():
    """Lista todos los equipos disponibles (sin revelar respuestas)."""
    teams = get_all_xi_teams()
    return [
        {
            "id":         t["id"],
            "name":       t["name"],
            "season":     t["season"],
            "badge":      t["badge"],
            "difficulty": t["difficulty"],
        }
        for t in teams
    ]


@app.get("/api/xi/{team_id}")
def xi_by_id(team_id: int):
    """Devuelve un equipo específico por id."""
    team = get_xi_team_by_id(team_id)
    if not team:
        raise HTTPException(404, "Equipo no encontrado")
    return _xi_sanitize(team)


@app.post("/api/xi/check")
def xi_check(req: XiCheckRequest):
    """Valida las respuestas del jugador para un equipo XI.
       Devuelve qué slots acertó, cuáles falló y la puntuación (100 pts por acierto).
    """
    team = get_xi_team_by_id(req.team_id)
    if not team:
        raise HTTPException(404, "Equipo no encontrado")

    results = []
    score   = 0
    correct = 0
    total_hidden = 0

    for p in team["players"]:
        if not p["hidden"]:
            continue
        total_hidden += 1
        slot          = p["slot"]
        correct_name  = p["name"].strip().lower()
        user_answer   = req.answers.get(slot, "").strip().lower()

        # Aceptar respuesta si contiene el apellido principal (tolerancia parcial)
        is_correct = (
            user_answer == correct_name
            or (len(user_answer) >= 3 and user_answer in correct_name)
            or (len(correct_name) >= 3 and correct_name in user_answer)
        )

        if is_correct:
            score   += 100
            correct += 1

        results.append({
            "slot":          slot,
            "correct_name":  p["name"],
            "user_answer":   req.answers.get(slot, ""),
            "is_correct":    is_correct,
            "photo":         p.get("photo", ""),
        })

    return {
        "team_id":      req.team_id,
        "team_name":    team["name"],
        "score":        score,
        "correct":      correct,
        "total_hidden": total_hidden,
        "accuracy":     round(correct / total_hidden * 100) if total_hidden else 0,
        "results":      results,
        "curiosity":    team["curiosity"],
    }


# ══════════════════════════════════════════════════════════════
# SISTEMA DE LIGAS
# ══════════════════════════════════════════════════════════════

@app.get("/api/league/{username}")
def league_status(username: str):
    """Devuelve el estado de liga del usuario."""
    user = get_or_create_user(username.strip())
    return get_user_league(user["id"])


@app.post("/api/league/result")
def league_result(req: FinishGameRequest):
    """Registra resultado de liga. won=True si score>=umbral."""
    user = get_or_create_user(req.username.strip())
    # Si el frontend envía 'won' explícito (duelos), usarlo directamente.
    # De lo contrario, calcular por accuracy/correct (modos quiz clásicos).
    if req.won is not None:
        won = req.won
    else:
        won = (req.accuracy >= 60.0 and req.correct >= 5)
    result = record_league_result(user["id"], won)

    # Recompensa especial por victoria en duelo de liga:
    # División 1-3 → puede recibir Leyenda; División 4-7 → Diamante; resto → Oro
    duel_player_reward = None
    if won:
        division = result["league"].get("division", 10)
        if division <= 3:
            duel_player_reward = unlock_player_by_type(user["id"], rarity="leyenda")
        if not duel_player_reward and division <= 7:
            duel_player_reward = unlock_player_by_type(user["id"], rarity="diamante")
        if not duel_player_reward:
            duel_player_reward = unlock_player_by_type(user["id"], rarity="oro")

    result["duel_player_reward"] = duel_player_reward
    return result


# ══════════════════════════════════════════════════════════════
# RECOMPENSAS DIARIAS
# ══════════════════════════════════════════════════════════════

@app.get("/api/daily/{username}")
def daily_status(username: str):
    """Estado de la recompensa diaria."""
    user = get_or_create_user(username.strip())
    return get_daily_reward_status(user["id"])


@app.post("/api/daily/claim")
def daily_claim(req: UsernameRequest):
    """Reclama la recompensa diaria."""
    user = get_or_create_user(req.username.strip())
    return claim_daily_reward(user["id"])


# ══════════════════════════════════════════════════════════════
# SISTEMA DE ENERGÍA
# ══════════════════════════════════════════════════════════════

@app.get("/api/energy/{username}")
def energy_status(username: str):
    """Devuelve la energía actual del usuario."""
    user = get_or_create_user(username.strip())
    return get_user_energy(user["id"])


@app.post("/api/energy/consume")
def energy_consume(req: UsernameRequest):
    """Consume 1 energía al iniciar una partida."""
    user = get_or_create_user(req.username.strip())
    return consume_energy(user["id"])


@app.post("/api/energy/refill")
def energy_refill(req: EnergyRefillRequest):
    """Recarga energía (tras ver un anuncio recompensado)."""
    user = get_or_create_user(req.username.strip())
    return refill_energy(user["id"], req.amount)


# ══════════════════════════════════════════════════════════════
# RIVAL BOT
# ══════════════════════════════════════════════════════════════

import random as _bot_random  # noqa: E402 (ya importado, alias para bot)

_BOT_NAMES = [
    "CrackFutbolero", "MadridCentral", "Messidependiente",
    "ElReyDeLaChampions", "FutbolTáctico", "GolDeOro",
    "TerceraVuelta", "OffsideTrap", "TiquitaqueFC",
    "SombreroBicicleta", "CañoMaestro", "ParedYSigue",
    "UltraFutbol", "CatenacioBoss", "RojiblancoPuro",
    "VamosAscender", "PressingAlto", "JugonDelBarrio",
    "ElCascarrabias", "MarcadorFinal",
]

_BOT_FLAGS = ["🇪🇸","🇦🇷","🇧🇷","🇲🇽","🇨🇴","🇺🇾","🇨🇱","🇵🇪","🇫🇷","🇩🇪","🇮🇹","🇵🇹","🇬🇧","🇳🇱","🇧🇪"]

_BOT_AVATARS = [
    "https://api.dicebear.com/7.x/bottts/svg?seed=crack1",
    "https://api.dicebear.com/7.x/bottts/svg?seed=crack2",
    "https://api.dicebear.com/7.x/bottts/svg?seed=crack3",
    "https://api.dicebear.com/7.x/bottts/svg?seed=crack4",
    "https://api.dicebear.com/7.x/bottts/svg?seed=crack5",
    "https://api.dicebear.com/7.x/bottts/svg?seed=crack6",
    "https://api.dicebear.com/7.x/bottts/svg?seed=crack7",
    "https://api.dicebear.com/7.x/bottts/svg?seed=crack8",
]

# Dificultades según la división del jugador
# division 10-8 → fácil, 7-5 → medio, 4-2 → difícil, 1 → experto
_BOT_DIFFICULTY_BY_DIVISION = {
    10: "easy", 9: "easy", 8: "easy",
    7: "medium", 6: "medium", 5: "medium",
    4: "hard", 3: "hard",
    2: "expert", 1: "expert",
}

_BOT_ACCURACY = {
    "easy":   (0.35, 0.55),
    "medium": (0.50, 0.70),
    "hard":   (0.65, 0.82),
    "expert": (0.78, 0.92),
}

_BOT_SPEED = {
    "easy":   (8, 20),   # segundos por respuesta
    "medium": (5, 14),
    "hard":   (3, 10),
    "expert": (2, 7),
}


@app.get("/api/bot/generate/{username}")
def bot_generate(username: str):
    """Genera un rival bot adaptado a la división del jugador."""
    division = 10
    try:
        user = get_or_create_user(username.strip())
        league = get_user_league(user["id"])
        division = league.get("division", 10)
    except Exception:
        pass

    difficulty = _BOT_DIFFICULTY_BY_DIVISION.get(division, "medium")
    acc_range = _BOT_ACCURACY[difficulty]
    spd_range = _BOT_SPEED[difficulty]

    name = _bot_random.choice(_BOT_NAMES)
    flag = _bot_random.choice(_BOT_FLAGS)
    avatar = _bot_random.choice(_BOT_AVATARS)

    return {
        "name": name,
        "flag": flag,
        "avatar": avatar,
        "difficulty": difficulty,
        "division": division,
        # Parámetros para simular en frontend
        "accuracy_min": acc_range[0],
        "accuracy_max": acc_range[1],
        "speed_min": spd_range[0],
        "speed_max": spd_range[1],
    }


@app.post("/api/bot/simulate_score")
def bot_simulate_score(req: BotSimulateRequest):
    """
    Simula la puntuación final del bot dado un número de preguntas.
    Útil para calcular el resultado del duelo.
    """
    total = req.total_questions
    difficulty = req.difficulty

    acc_range = _BOT_ACCURACY.get(difficulty, (0.5, 0.7))
    spd_range = _BOT_SPEED.get(difficulty, (5, 14))

    accuracy = _bot_random.uniform(*acc_range)
    correct = round(total * accuracy)

    # Calcular puntos simulando velocidad por pregunta
    score = 0
    for _ in range(correct):
        time_taken = _bot_random.uniform(*spd_range)
        # Puntos base ~150 (nivel medio), bonus velocidad
        base = 150
        time_limit = 30
        time_bonus = max(0, 1 - (time_taken / time_limit))
        score += int(base * (1 + time_bonus * 0.5))

    return {
        "correct": correct,
        "total": total,
        "accuracy": round(accuracy * 100),
        "score": score,
        "difficulty": difficulty,
    }


# ══════════════════════════════════════════════════════════════
# SISTEMA DE DUELOS PVP
# ══════════════════════════════════════════════════════════════

@app.post("/api/duel/challenge")
def duel_challenge(req: DuelChallengeRequest):
    """
    Envía un desafío de duelo a otro usuario.
    Opcionalmente incluye apuesta (XP o jugador).
    """
    challenger = get_or_create_user(req.challenger.strip())
    result = create_duel_challenge(
        challenger_id=challenger["id"],
        opponent_username=req.opponent_username.strip(),
        wager_type=req.wager_type,
        wager_xp_amount=req.wager_xp_amount,
        wager_player_id=req.wager_player_id,
    )
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@app.get("/api/duel/pending/{username}")
def duel_pending(username: str):
    """
    Devuelve los desafíos pendientes recibidos por el usuario.
    El frontend los muestra como notificaciones/badges.
    """
    user = get_or_create_user(username.strip())
    pending = get_pending_duels(user["id"])
    active = get_active_duels(user["id"])
    return {
        "pending": pending,
        "pending_count": len(pending),
        "active": active,
        "active_count": len(active),
    }


@app.post("/api/duel/accept")
def duel_accept(req: DuelAcceptRequest):
    """
    El oponente acepta o rechaza un desafío.
    Si acepta, el duelo pasa a estado 'accepted' y ambos deben jugar.
    """
    user = get_or_create_user(req.username.strip())
    if req.accept:
        result = accept_duel_challenge(req.challenge_id, user["id"])
    else:
        result = reject_duel_challenge(req.challenge_id, user["id"])

    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@app.post("/api/duel/result")
def duel_result(req: DuelResultRequest):
    """
    Registra el resultado final de un duelo PvP.
    Transfiere la apuesta al ganador y otorga recompensa premium.
    """
    get_or_create_user(req.username.strip())  # validar que quien reporta existe
    result = resolve_duel(
        challenge_id=req.challenge_id,
        winner_username=req.winner_username.strip(),
        challenger_score=req.challenger_score,
        opponent_score=req.opponent_score,
    )
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


# ══════════════════════════════════════════════════════════════════
#  MATCHMAKING — cola automática 1v1
# ══════════════════════════════════════════════════════════════════

class MatchmakingJoinRequest(BaseModel):
    username: str
    wager_type: Optional[str] = None          # None | 'xp' | 'player'
    wager_xp_amount: int = 0
    wager_player_id: Optional[int] = None

class MatchmakingCancelRequest(BaseModel):
    username: str

class MatchmakingRespondRequest(BaseModel):
    username: str
    match_id: int
    accept: bool


@app.post("/api/matchmaking/join")
def matchmaking_join(req: MatchmakingJoinRequest):
    """
    El jugador entra en la cola de matchmaking con su apuesta configurada.
    Si hay otro jugador esperando, se crea un match automáticamente.
    """
    user = get_or_create_user(req.username.strip())
    result = join_matchmaking_queue(
        user["id"],
        user["username"],
        wager_type=req.wager_type,
        wager_xp_amount=req.wager_xp_amount,
        wager_player_id=req.wager_player_id,
    )
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@app.post("/api/matchmaking/cancel")
def matchmaking_cancel(req: MatchmakingCancelRequest):
    """Saca al jugador de la cola de matchmaking."""
    user = get_or_create_user(req.username.strip())
    return cancel_matchmaking(user["id"])


@app.get("/api/matchmaking/status/{username}")
def matchmaking_status(username: str):
    """
    Devuelve el estado de matchmaking del jugador.
    Diseñado para polling cada 2-3 s desde el frontend.

    Respuestas posibles:
      { state: 'not_in_queue' }
      { state: 'waiting' }
      { state: 'matched', match_id, opponent, seconds_left }
      { state: 'both_accepted', match_id, challenge_id, opponent }
      { state: 'cancelled', reason? }
    """
    user = get_or_create_user(username.strip())
    return get_matchmaking_status(user["id"])


@app.post("/api/matchmaking/respond")
def matchmaking_respond(req: MatchmakingRespondRequest):
    """
    El jugador acepta o rechaza el match encontrado.
    Si ambos aceptan → crea duel_challenge real y devuelve challenge_id.
    Si uno rechaza → cancela y limpia la cola de ambos.
    """
    user = get_or_create_user(req.username.strip())
    result = respond_to_match(user["id"], req.match_id, req.accept)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


# ══════════════════════════════════════════════════════════════════
#  SESIONES DE DUELO EN TIEMPO REAL
# ══════════════════════════════════════════════════════════════════

class DuelSessionStartRequest(BaseModel):
    username: str
    challenge_id: int

class DuelHeartbeatRequest(BaseModel):
    username: str
    challenge_id: int

class DuelSessionFinishRequest(BaseModel):
    username: str
    challenge_id: int
    score: int


@app.post("/api/duel/session/start")
def duel_session_start(req: DuelSessionStartRequest):
    """
    Crea (o recupera) la sesión de duelo en tiempo real.
    Llamar al entrar a la pantalla de duelo.
    """
    user = get_or_create_user(req.username.strip())
    result = start_duel_session(req.challenge_id)
    if "error" in result:
        raise HTTPException(400, result["error"])
    # Verificar que el usuario es participante
    s = result.get("session", {})
    if user["id"] not in (s.get("player1_id"), s.get("player2_id")):
        raise HTTPException(403, "No eres participante de este duelo")
    return result


@app.post("/api/duel/session/heartbeat")
def duel_session_heartbeat(req: DuelHeartbeatRequest):
    """
    Heartbeat del cliente para mantener sesión activa.
    Enviar cada 8 s desde el cliente mientras dura el duelo.
    Devuelve estado del rival y de la sesión.
    """
    user = get_or_create_user(req.username.strip())
    result = update_duel_heartbeat(req.challenge_id, user["id"])
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@app.post("/api/duel/session/finish")
def duel_session_finish(req: DuelSessionFinishRequest):
    """
    El jugador terminó su partida. Registra su score.
    Si el rival también terminó → resuelve el duelo.
    Si no → responde waiting_rival=True y el cliente hace poll.
    """
    user = get_or_create_user(req.username.strip())
    result = finish_duel_session(req.challenge_id, user["id"], req.score)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@app.get("/api/duel/session/{challenge_id}/status/{username}")
def duel_session_status(challenge_id: int, username: str):
    """
    Estado actual de la sesión de duelo.
    Usado en polling después de finish para esperar al rival o detectar WO.
    """
    user = get_or_create_user(username.strip())
    result = get_duel_session_status(challenge_id, user["id"])
    return result


@app.get("/api/user/{username}/duel-stats")
def user_duel_stats(username: str):
    """Estadísticas de duelo del usuario (partidas, victorias, derrotas)."""
    user = get_or_create_user(username.strip())
    return get_duel_stats(user["id"])


class DuelAbandonRequest(BaseModel):
    username: str
    challenge_id: int

@app.post("/api/duel/abandon")
def duel_abandon(req: DuelAbandonRequest):
    """
    El jugador abandona/cancela manualmente una partida en curso.
    Si el rival ya estaba conectado → WO para el rival (con transferencia de apuesta).
    Si nadie estaba en juego → simple cancelación sin penalización.
    """
    user = get_or_create_user(req.username.strip())
    result = abandon_duel(req.challenge_id, user["id"])
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result
