"""
Base de datos SQLite para El Crack Quiz
Maneja usuarios, jugadores desbloqueados, equipos e historial
"""

import sqlite3
import os
import random
import threading
from datetime import datetime, timezone, timedelta
from typing import Optional
from backend.data.players import PLAYERS, get_player_by_id

DB_PATH = os.path.join(os.path.dirname(__file__), "elcrack.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            favorite_team TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            player_id INTEGER NOT NULL,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, player_id)
        );

        CREATE TABLE IF NOT EXISTS user_team (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            position TEXT NOT NULL,
            player_id INTEGER NOT NULL,
            UNIQUE(user_id, position)
        );

        CREATE TABLE IF NOT EXISTS game_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            score INTEGER NOT NULL,
            accuracy REAL NOT NULL,
            correct_count INTEGER NOT NULL,
            total_count INTEGER NOT NULL,
            player_unlocked_id INTEGER,
            mode TEXT DEFAULT 'classic',
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ─── LIGAS ───────────────────────────────────────────────
        -- division: 10 (más baja) → 1 (más alta)
        -- wins_in_division: victorias acumuladas en la división actual
        -- losses_in_division: derrotas acumuladas en la división actual
        -- wins_needed: victorias necesarias para ascender (empieza en 3, max 5)
        -- losses_to_drop: derrotas para descender (empieza en 3)
        CREATE TABLE IF NOT EXISTS user_league (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
            division INTEGER NOT NULL DEFAULT 10,
            wins_in_division INTEGER NOT NULL DEFAULT 0,
            losses_in_division INTEGER NOT NULL DEFAULT 0,
            wins_needed INTEGER NOT NULL DEFAULT 3,
            losses_to_drop INTEGER NOT NULL DEFAULT 3,
            total_promotions INTEGER NOT NULL DEFAULT 0,
            total_relegations INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ─── RECOMPENSAS DIARIAS ─────────────────────────────────
        CREATE TABLE IF NOT EXISTS daily_rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
            last_claim_date TEXT DEFAULT NULL,   -- formato YYYY-MM-DD
            streak_days INTEGER NOT NULL DEFAULT 0,
            total_claims INTEGER NOT NULL DEFAULT 0
        );

        -- ─── ENERGÍA ─────────────────────────────────────────────
        -- energy: 0-5, max_energy: 5 por defecto
        -- last_recharge: timestamp de la última recarga automática
        CREATE TABLE IF NOT EXISTS user_energy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
            energy INTEGER NOT NULL DEFAULT 5,
            max_energy INTEGER NOT NULL DEFAULT 5,
            last_recharge TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ─── DUELOS PVP ──────────────────────────────────────────
        -- status: pending | accepted | completed | rejected | cancelled
        -- wager_type: 'xp' | 'player' | NULL (sin apuesta)
        -- winner_id: NULL hasta que se complete el duelo
        CREATE TABLE IF NOT EXISTS duel_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenger_id INTEGER NOT NULL REFERENCES users(id),
            opponent_id INTEGER NOT NULL REFERENCES users(id),
            status TEXT NOT NULL DEFAULT 'pending',
            wager_type TEXT DEFAULT NULL,
            wager_xp_amount INTEGER NOT NULL DEFAULT 0,
            wager_player_id INTEGER DEFAULT NULL,
            winner_id INTEGER DEFAULT NULL,
            challenger_score INTEGER DEFAULT NULL,
            opponent_score INTEGER DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP DEFAULT NULL
        );

        -- ─── MEJOR PUNTAJE POR USUARIO (ranking global) ──────────
        -- Una fila por usuario. Se actualiza solo si el nuevo puntaje es mayor.
        -- Esto garantiza que el ranking muestre una entrada única por jugador
        -- con su mejor marca histórica acumulada, ordenada de mayor a menor.
        CREATE TABLE IF NOT EXISTS user_best_score (
            user_id INTEGER PRIMARY KEY REFERENCES users(id),
            best_score INTEGER NOT NULL DEFAULT 0,
            total_games INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ─── MATCHMAKING (cola automática 1v1) ───────────────────
        -- status de queue: waiting | matched | cancelled
        CREATE TABLE IF NOT EXISTS matchmaking_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
            username TEXT NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'waiting',
            match_id INTEGER DEFAULT NULL,
            wager_type TEXT DEFAULT NULL,
            wager_xp_amount INTEGER NOT NULL DEFAULT 0,
            wager_player_id INTEGER DEFAULT NULL
        );

        -- status de match: pending | both_accepted | cancelled | expired
        -- player1_accepted / player2_accepted: 0=sin respuesta, 1=acepta, -1=rechaza
        CREATE TABLE IF NOT EXISTS matchmaking_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player1_id INTEGER NOT NULL REFERENCES users(id),
            player2_id INTEGER NOT NULL REFERENCES users(id),
            player1_accepted INTEGER NOT NULL DEFAULT 0,
            player2_accepted INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'pending',
            challenge_id INTEGER DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL
        );

        -- ─── SESIONES DE DUELO EN TIEMPO REAL ────────────────────
        -- Una fila por duelo activo. Se elimina al finalizar.
        -- state: 'waiting' (esperando que ambos entren) | 'active' | 'finished' | 'abandoned'
        -- *_finished: 0=no terminó, 1=terminó
        -- *_score: puntaje final del jugador
        -- *_heartbeat: último timestamp recibido (NULL = no ha conectado)
        CREATE TABLE IF NOT EXISTS duel_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_id INTEGER NOT NULL UNIQUE REFERENCES duel_challenges(id),
            player1_id INTEGER NOT NULL REFERENCES users(id),
            player2_id INTEGER NOT NULL REFERENCES users(id),
            state TEXT NOT NULL DEFAULT 'waiting',
            p1_heartbeat TIMESTAMP DEFAULT NULL,
            p2_heartbeat TIMESTAMP DEFAULT NULL,
            p1_finished INTEGER NOT NULL DEFAULT 0,
            p2_finished INTEGER NOT NULL DEFAULT 0,
            p1_score INTEGER NOT NULL DEFAULT 0,
            p2_score INTEGER NOT NULL DEFAULT 0,
            winner_id INTEGER DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP DEFAULT NULL
        );

        -- ─── ESTADÍSTICAS DE DUELO (solo stats esenciales) ───────
        -- Una fila por usuario. Se actualiza acumulativamente.
        CREATE TABLE IF NOT EXISTS duel_stats (
            user_id INTEGER PRIMARY KEY REFERENCES users(id),
            games_played INTEGER NOT NULL DEFAULT 0,
            wins INTEGER NOT NULL DEFAULT 0,
            losses INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    # Migración segura: añadir columna xp si no existe
    try:
        conn.execute("ALTER TABLE users ADD COLUMN xp INTEGER NOT NULL DEFAULT 0")
        conn.commit()
    except Exception:
        pass  # Ya existe

    # Migración: columnas de apuesta en matchmaking_queue
    for col_sql in [
        "ALTER TABLE matchmaking_queue ADD COLUMN wager_type TEXT DEFAULT NULL",
        "ALTER TABLE matchmaking_queue ADD COLUMN wager_xp_amount INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE matchmaking_queue ADD COLUMN wager_player_id INTEGER DEFAULT NULL",
    ]:
        try:
            conn.execute(col_sql)
            conn.commit()
        except Exception:
            pass  # Ya existe

    # Migración: tabla duel_sessions (real-time duels)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS duel_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_id INTEGER NOT NULL UNIQUE REFERENCES duel_challenges(id),
                player1_id INTEGER NOT NULL REFERENCES users(id),
                player2_id INTEGER NOT NULL REFERENCES users(id),
                state TEXT NOT NULL DEFAULT 'waiting',
                p1_heartbeat TIMESTAMP DEFAULT NULL,
                p2_heartbeat TIMESTAMP DEFAULT NULL,
                p1_finished INTEGER NOT NULL DEFAULT 0,
                p2_finished INTEGER NOT NULL DEFAULT 0,
                p1_score INTEGER NOT NULL DEFAULT 0,
                p2_score INTEGER NOT NULL DEFAULT 0,
                winner_id INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                finished_at TIMESTAMP DEFAULT NULL
            )
        """)
        conn.commit()
    except Exception:
        pass

    # Migración: tabla duel_stats
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS duel_stats (
                user_id INTEGER PRIMARY KEY REFERENCES users(id),
                games_played INTEGER NOT NULL DEFAULT 0,
                wins INTEGER NOT NULL DEFAULT 0,
                losses INTEGER NOT NULL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except Exception:
        pass

    # Migración segura: poblar user_best_score con historial previo
    # Solo inserta filas para usuarios que aún no tienen entrada en user_best_score
    try:
        conn.execute("""
            INSERT OR IGNORE INTO user_best_score (user_id, best_score, total_games, updated_at)
            SELECT
                user_id,
                MAX(score)      AS best_score,
                COUNT(*)        AS total_games,
                MAX(played_at)  AS updated_at
            FROM game_history
            GROUP BY user_id
        """)
        conn.commit()
    except Exception:
        pass  # La tabla puede no existir todavía en instancias muy antiguas

    conn.close()


def get_or_create_user(username: str, email: str = None, password_hash: str = None) -> dict:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if row:
        user = dict(row)
    else:
        if email is None:
            email = f"{username}@elcrack.local"
        if password_hash is None:
            password_hash = ""
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        user = dict(row)
    conn.close()
    return user


def get_user_players(user_id: int) -> list[int]:
    conn = get_connection()
    rows = conn.execute("SELECT player_id FROM user_players WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return [r["player_id"] for r in rows]


def unlock_player(user_id: int, score: int, mode: str = "classic") -> Optional[dict]:
    """Desbloquea un jugador aleatorio basado en el puntaje de la partida.

    Drop rate table (modos normales — bronce/plata/oro):
      score < 500            → sin recompensa
      500  <= score < 1500   → bronce 100%
      1500 <= score < 3000   → plata 60%, bronce 40%
      3000 <= score < 5000   → oro 20%, plata 55%, bronce 25%
      score >= 5000          → oro 35%, plata 50%, bronce 15%

    Drop rate table (duelos — acceso a diamante y leyenda):
      score >= 8000          → leyenda 8%, diamante 22%, oro 30%, plata 28%, bronce 12%
      score >= 5000          → diamante 15%, oro 35%, plata 35%, bronce 15%
      score >= 3000          → oro 30%, plata 45%, bronce 25%
      500  <= score < 3000   → plata 60%, bronce 40%
      score < 500            → sin recompensa
    """
    owned = set(get_user_players(user_id))
    DUEL_MODES = {"duel", "challenge", "pvp"}

    if score < 500:
        return None

    if mode in DUEL_MODES:
        # ── Modo duelo: probabilidades con diamante y leyenda ──
        if score >= 8000:
            weights = [("leyenda", 8), ("diamante", 22), ("oro", 30), ("plata", 28), ("bronce", 12)]
        elif score >= 5000:
            weights = [("diamante", 15), ("oro", 35), ("plata", 35), ("bronce", 15)]
        elif score >= 3000:
            weights = [("oro", 30), ("plata", 45), ("bronce", 25)]
        else:
            weights = [("plata", 60), ("bronce", 40)]
    else:
        # ── Modo normal: sin diamante ni leyenda ──
        if score >= 5000:
            weights = [("oro", 35), ("plata", 50), ("bronce", 15)]
        elif score >= 3000:
            weights = [("oro", 20), ("plata", 55), ("bronce", 25)]
        elif score >= 1500:
            weights = [("plata", 60), ("bronce", 40)]
        else:
            weights = [("bronce", 100)]

    # Tirar el dado según los pesos
    rarities = [r for r, _ in weights]
    probs = [w for _, w in weights]
    chosen_rarity = random.choices(rarities, weights=probs, k=1)[0]

    # Buscar un jugador disponible de esa rareza; si no queda ninguno, bajar de rareza
    all_rarities_fallback = rarities[rarities.index(chosen_rarity):]
    for rarity in all_rarities_fallback:
        available = [p for p in PLAYERS if p["rarity"] == rarity and p["id"] not in owned]
        if available:
            player = random.choice(available)
            conn = get_connection()
            conn.execute(
                "INSERT INTO user_players (user_id, player_id) VALUES (?, ?)",
                (user_id, player["id"])
            )
            conn.commit()
            conn.close()
            return player

    return None


def unlock_player_by_type(user_id: int, position: Optional[str] = None, rarity: Optional[str] = None, min_rating: Optional[int] = None) -> Optional[dict]:
    """Desbloquea un jugador aleatorio filtrado por posicion, rareza y/o rating minimo."""
    owned = set(get_user_players(user_id))

    available = [p for p in PLAYERS if p["id"] not in owned]

    if position:
        available = [p for p in available if p["position"] == position]
    if rarity:
        available = [p for p in available if p["rarity"] == rarity]
    if min_rating:
        available = [p for p in available if p["rating"] >= min_rating]

    if not available:
        # Si no hay jugadores con los filtros exactos, relajar restricciones
        available = [p for p in PLAYERS if p["id"] not in owned]
        if position:
            available = [p for p in available if p["position"] == position]
        if not available:
            return None

    player = random.choice(available)
    conn = get_connection()
    conn.execute(
        "INSERT INTO user_players (user_id, player_id) VALUES (?, ?)",
        (user_id, player["id"])
    )
    conn.commit()
    conn.close()
    return player


def get_user_team(user_id: int) -> dict:
    conn = get_connection()
    rows = conn.execute("SELECT position, player_id FROM user_team WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    team = {}
    for r in rows:
        player = get_player_by_id(r["player_id"])
        if player:
            team[r["position"]] = player
    return team


def set_user_team(user_id: int, team: dict[str, int]) -> bool:
    """Guarda el equipo titular. team = {position: player_id}"""
    valid_positions = {"POR", "DEF1", "DEF2", "DEF3", "DEF4", "MED1", "MED2", "MED3", "DEL1", "DEL2", "DEL3"}
    owned = set(get_user_players(user_id))

    for pos, pid in team.items():
        if pos not in valid_positions:
            return False
        if pid not in owned:
            return False

    conn = get_connection()
    conn.execute("DELETE FROM user_team WHERE user_id = ?", (user_id,))
    for pos, pid in team.items():
        conn.execute(
            "INSERT INTO user_team (user_id, position, player_id) VALUES (?, ?, ?)",
            (user_id, pos, pid)
        )
    conn.commit()
    conn.close()
    return True


def save_game(user_id: int, score: int, accuracy: float, correct: int, total: int, unlocked_id: Optional[int] = None):
    conn = get_connection()
    # Guardar historial completo de la partida
    conn.execute(
        "INSERT INTO game_history (user_id, score, accuracy, correct_count, total_count, player_unlocked_id) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, score, accuracy, correct, total, unlocked_id)
    )
    # Actualizar best_score: solo actualiza si el nuevo puntaje es MAYOR al previo.
    # INSERT OR IGNORE crea la fila si no existe; el UPDATE solo actúa si score > best_score.
    conn.execute(
        "INSERT OR IGNORE INTO user_best_score (user_id, best_score, total_games) VALUES (?, 0, 0)",
        (user_id,)
    )
    conn.execute(
        """UPDATE user_best_score
           SET best_score  = CASE WHEN ? > best_score THEN ? ELSE best_score END,
               total_games = total_games + 1,
               updated_at  = CURRENT_TIMESTAMP
           WHERE user_id = ?""",
        (score, score, user_id)
    )
    conn.commit()
    conn.close()


def get_team_rankings() -> list[dict]:
    """Ranking de equipos por valor total (suma de ratings de los 11 titulares)."""
    conn = get_connection()
    users = conn.execute("SELECT id, username FROM users").fetchall()
    rankings = []
    for u in users:
        rows = conn.execute("SELECT player_id FROM user_team WHERE user_id = ?", (u["id"],)).fetchall()
        if len(rows) == 0:
            continue
        total_rating = 0
        player_count = 0
        for r in rows:
            player = get_player_by_id(r["player_id"])
            if player:
                total_rating += player["rating"]
                player_count += 1
        rankings.append({
            "username": u["username"],
            "team_value": total_rating,
            "players_in_team": player_count,
            "total_unlocked": len(get_user_players(u["id"])),
        })
    conn.close()
    rankings.sort(key=lambda x: x["team_value"], reverse=True)
    return rankings[:20]


def get_global_leaderboard() -> list[dict]:
    """Ranking global: una entrada por usuario, ordenada por mejor puntaje histórico.
    
    Usa la tabla user_best_score que se actualiza en cada partida mediante upsert,
    garantizando que cada usuario aparezca una sola vez con su mejor marca.
    Para usuarios con partidas previas al sistema nuevo, hace fallback al MAX de
    game_history para no perder datos históricos.
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            u.username,
            COALESCE(ubs.best_score,
                     (SELECT MAX(gh2.score) FROM game_history gh2 WHERE gh2.user_id = u.id),
                     0) AS score,
            COALESCE(ubs.total_games, 0) AS total_games,
            COALESCE(ubs.updated_at, u.last_login, u.created_at) AS updated_at
        FROM users u
        LEFT JOIN user_best_score ubs ON ubs.user_id = u.id
        WHERE COALESCE(ubs.best_score,
                       (SELECT MAX(gh2.score) FROM game_history gh2 WHERE gh2.user_id = u.id),
                       0) > 0
        ORDER BY score DESC
        LIMIT 50
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════
# SISTEMA DE LIGAS
# ═══════════════════════════════════════════════════════════

LEAGUE_DIVISIONS = {
    10: {"name": "División 10",  "emoji": "⚽", "color": "#8B4513"},
    9:  {"name": "División 9",   "emoji": "🏅", "color": "#8B4513"},
    8:  {"name": "División 8",   "emoji": "🏅", "color": "#708090"},
    7:  {"name": "División 7",   "emoji": "🥈", "color": "#708090"},
    6:  {"name": "División 6",   "emoji": "🥈", "color": "#708090"},
    5:  {"name": "División 5",   "emoji": "🥇", "color": "#FFD700"},
    4:  {"name": "División 4",   "emoji": "🥇", "color": "#FFD700"},
    3:  {"name": "División 3",   "emoji": "💎", "color": "#00BCD4"},
    2:  {"name": "División 2",   "emoji": "💎", "color": "#00BCD4"},
    1:  {"name": "División 1",   "emoji": "🏆", "color": "#FF6F00"},
}


def get_user_league(user_id: int) -> dict:
    """Obtiene el estado de liga del usuario. Lo crea si no existe."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM user_league WHERE user_id = ?", (user_id,)).fetchone()
    if not row:
        conn.execute(
            "INSERT INTO user_league (user_id, division, wins_in_division, losses_in_division, wins_needed, losses_to_drop) VALUES (?,10,0,0,3,3)",
            (user_id,)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM user_league WHERE user_id = ?", (user_id,)).fetchone()
    data = dict(row)
    conn.close()
    div = data["division"]
    data["division_info"] = LEAGUE_DIVISIONS.get(div, LEAGUE_DIVISIONS[10])
    data["progress_pct"] = int((data["wins_in_division"] / max(data["wins_needed"], 1)) * 100)
    return data


def record_league_result(user_id: int, won: bool) -> dict:
    """
    Registra una victoria o derrota en la liga.
    Devuelve dict con: promoted, relegated, division_before, division_after, league (estado actual).
    """
    league = get_user_league(user_id)
    div = league["division"]
    wins = league["wins_in_division"]
    losses = league["losses_in_division"]
    wins_needed = league["wins_needed"]
    losses_to_drop = league["losses_to_drop"]

    promoted = False
    relegated = False
    division_before = div

    if won:
        wins += 1
        if wins >= wins_needed:
            # ASCENSO
            if div > 1:
                div -= 1
                wins = 0
                losses = 0
                promoted = True
                # En divisiones altas cuesta más ascender
                wins_needed = min(5, 3 + (10 - div) // 3)
            else:
                # Ya está en D1, resetear contadores
                wins = 0
                losses = 0
    else:
        losses += 1
        if losses >= losses_to_drop:
            # DESCENSO
            if div < 10:
                div += 1
                wins = 0
                losses = 0
                relegated = True
            else:
                losses = 0  # En D10 no puede bajar más

    conn = get_connection()
    conn.execute("""
        UPDATE user_league
        SET division=?, wins_in_division=?, losses_in_division=?,
            wins_needed=?,
            total_promotions = total_promotions + ?,
            total_relegations = total_relegations + ?,
            updated_at=CURRENT_TIMESTAMP
        WHERE user_id=?
    """, (div, wins, losses, wins_needed, 1 if promoted else 0, 1 if relegated else 0, user_id))
    conn.commit()
    conn.close()

    updated_league = get_user_league(user_id)
    return {
        "promoted": promoted,
        "relegated": relegated,
        "division_before": division_before,
        "division_after": div,
        "league": updated_league,
    }


# ═══════════════════════════════════════════════════════════
# SISTEMA DE RECOMPENSAS DIARIAS
# ═══════════════════════════════════════════════════════════

# Recompensas por día de racha (se repite cíclico cada 7 días)
DAILY_REWARD_SCHEDULE = {
    1: {"type": "xp",     "amount": 100,  "label": "+100 XP",         "emoji": "⭐"},
    2: {"type": "xp",     "amount": 150,  "label": "+150 XP",         "emoji": "⭐"},
    3: {"type": "player", "amount": 1,    "label": "Carta bronce",    "emoji": "🃏"},
    4: {"type": "xp",     "amount": 200,  "label": "+200 XP",         "emoji": "⭐"},
    5: {"type": "player", "amount": 1,    "label": "Carta plata",     "emoji": "🥈"},
    6: {"type": "xp",     "amount": 300,  "label": "+300 XP",         "emoji": "⭐"},
    7: {"type": "player", "amount": 1,    "label": "Carta ORO 🔥",   "emoji": "🥇"},
}


def get_daily_reward_status(user_id: int) -> dict:
    """Devuelve el estado de recompensa diaria del usuario."""
    from datetime import date
    today = date.today().isoformat()

    conn = get_connection()
    row = conn.execute("SELECT * FROM daily_rewards WHERE user_id=?", (user_id,)).fetchone()
    if not row:
        conn.execute("INSERT INTO daily_rewards (user_id) VALUES (?)", (user_id,))
        conn.commit()
        row = conn.execute("SELECT * FROM daily_rewards WHERE user_id=?", (user_id,)).fetchone()
    data = dict(row)
    conn.close()

    last = data.get("last_claim_date")
    streak = data.get("streak_days", 0)
    can_claim = (last != today)

    # Si pasaron más de 2 días sin reclamar, se rompe la racha
    if last:
        from datetime import date as _date
        last_date = _date.fromisoformat(last)
        diff = (_date.today() - last_date).days
        if diff > 1:
            streak = 0

    # Siguiente recompensa (día 1-7 cíclico)
    next_day = (streak % 7) + 1
    next_reward = DAILY_REWARD_SCHEDULE[next_day]

    # Preview de toda la semana
    week_preview = []
    for day in range(1, 8):
        r = DAILY_REWARD_SCHEDULE[day].copy()
        r["day"] = day
        r["claimed"] = (day <= streak % 7) if streak > 0 else False
        r["is_next"] = (day == next_day)
        week_preview.append(r)

    return {
        "can_claim": can_claim,
        "streak_days": streak,
        "next_day": next_day,
        "next_reward": next_reward,
        "week_preview": week_preview,
        "last_claim_date": last,
    }


def claim_daily_reward(user_id: int) -> dict:
    """
    Reclama la recompensa del día. Devuelve la recompensa obtenida.
    Retorna error si ya reclamó hoy.
    """
    from datetime import date
    today = date.today().isoformat()

    status = get_daily_reward_status(user_id)
    if not status["can_claim"]:
        return {"success": False, "message": "Ya reclamaste tu recompensa hoy"}

    # Calcular nueva racha
    last = status["last_claim_date"]
    streak = status["streak_days"]

    if last:
        from datetime import date as _date
        last_date = _date.fromisoformat(last)
        diff = (_date.today() - last_date).days
        if diff == 1:
            streak += 1
        else:
            streak = 1  # racha rota, reinicia
    else:
        streak = 1

    # Determinar recompensa
    day_num = ((streak - 1) % 7) + 1
    reward = DAILY_REWARD_SCHEDULE[day_num].copy()
    reward["day"] = day_num

    # Aplicar recompensa
    unlocked_player = None
    xp_gained = 0
    new_total_xp = None
    if reward["type"] == "player":
        rarity_map = {3: "bronce", 5: "plata", 7: "oro"}
        rarity = rarity_map.get(day_num, "bronce")
        unlocked_player = unlock_player_by_type(user_id, rarity=rarity)
        if unlocked_player:
            reward["player"] = unlocked_player
    elif reward["type"] == "xp":
        xp_gained = reward["amount"]
        new_total_xp = add_xp(user_id, xp_gained)

    # Guardar en DB
    conn = get_connection()
    conn.execute("""
        UPDATE daily_rewards
        SET last_claim_date=?, streak_days=?, total_claims=total_claims+1
        WHERE user_id=?
    """, (today, streak, user_id))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "reward": reward,
        "streak_days": streak,
        "unlocked_player": unlocked_player,
        "xp_gained": xp_gained,
        "total_xp": new_total_xp if new_total_xp is not None else get_user_xp(user_id),
    }


# ═══════════════════════════════════════════════════════════
# SISTEMA DE XP
# ═══════════════════════════════════════════════════════════

def get_user_xp(user_id: int) -> int:
    """Devuelve el XP total acumulado del usuario."""
    conn = get_connection()
    row = conn.execute("SELECT xp FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return row["xp"] if row else 0


def add_xp(user_id: int, amount: int) -> int:
    """Suma XP al usuario y devuelve el nuevo total."""
    conn = get_connection()
    conn.execute("UPDATE users SET xp = xp + ? WHERE id=?", (amount, user_id))
    conn.commit()
    row = conn.execute("SELECT xp FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return row["xp"] if row else amount


# ═══════════════════════════════════════════════════════════
# SISTEMA DE ENERGÍA
# ═══════════════════════════════════════════════════════════

ENERGY_RECHARGE_MINUTES = 30   # 1 energía cada 30 min
ENERGY_MAX = 5


def get_user_energy(user_id: int) -> dict:
    """Obtiene la energía del usuario, calculando recargas automáticas."""
    from datetime import datetime as _dt
    conn = get_connection()
    row = conn.execute("SELECT * FROM user_energy WHERE user_id=?", (user_id,)).fetchone()
    if not row:
        conn.execute("INSERT INTO user_energy (user_id, energy, max_energy) VALUES (?,3,5)", (user_id,))
        conn.commit()
        row = conn.execute("SELECT * FROM user_energy WHERE user_id=?", (user_id,)).fetchone()
    data = dict(row)

    # Calcular energía recargada desde la última vez
    now = _dt.utcnow()
    last_str = data["last_recharge"]
    try:
        last = _dt.fromisoformat(last_str)
    except Exception:
        last = now

    elapsed_minutes = (now - last).total_seconds() / 60
    recharges = int(elapsed_minutes / ENERGY_RECHARGE_MINUTES)

    if recharges > 0 and data["energy"] < ENERGY_MAX:
        new_energy = min(ENERGY_MAX, data["energy"] + recharges)
        conn.execute(
            "UPDATE user_energy SET energy=?, last_recharge=? WHERE user_id=?",
            (new_energy, now.isoformat(), user_id)
        )
        conn.commit()
        data["energy"] = new_energy
        data["last_recharge"] = now.isoformat()

    conn.close()

    # Calcular minutos hasta la próxima recarga
    if data["energy"] >= ENERGY_MAX:
        minutes_to_next = None
    else:
        try:
            last_dt = _dt.fromisoformat(data["last_recharge"])
        except Exception:
            last_dt = now
        elapsed = (now - last_dt).total_seconds() / 60
        minutes_to_next = max(0, ENERGY_RECHARGE_MINUTES - (elapsed % ENERGY_RECHARGE_MINUTES))
        minutes_to_next = round(minutes_to_next)

    return {
        "energy": data["energy"],
        "max_energy": ENERGY_MAX,
        "minutes_to_next_recharge": minutes_to_next,
        "is_full": data["energy"] >= ENERGY_MAX,
    }


def consume_energy(user_id: int) -> dict:
    """Consume 1 energía. Devuelve error si no hay."""
    energy_data = get_user_energy(user_id)
    if energy_data["energy"] <= 0:
        return {"success": False, "message": "Sin energía. Espera o ve un anuncio.", "energy": 0}

    conn = get_connection()
    conn.execute("UPDATE user_energy SET energy=energy-1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

    new_energy = energy_data["energy"] - 1
    return {"success": True, "energy": new_energy, "max_energy": ENERGY_MAX}


def refill_energy(user_id: int, amount: int = 1) -> dict:
    """Recarga energía (por anuncio visto o premio)."""
    conn = get_connection()
    conn.execute(
        "UPDATE user_energy SET energy=MIN(energy+?,?) WHERE user_id=?",
        (amount, ENERGY_MAX, user_id)
    )
    conn.commit()
    row = conn.execute("SELECT energy FROM user_energy WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return {"success": True, "energy": row["energy"] if row else amount, "max_energy": ENERGY_MAX}


# ═══════════════════════════════════════════════════════════
# SISTEMA DE DUELOS PVP
# ═══════════════════════════════════════════════════════════

def _serialize_duel(row: dict, challenger_name: str = None, opponent_name: str = None, extra: dict = None) -> dict:
    """Convierte una fila de duel_challenges a dict enriquecido."""
    d = dict(row)
    if d.get("wager_player_id"):
        player = get_player_by_id(d["wager_player_id"])
        d["wager_player"] = player
    else:
        d["wager_player"] = None
    if challenger_name:
        d["challenger_name"] = challenger_name
    if opponent_name:
        d["opponent_name"] = opponent_name
    if extra:
        d.update(extra)
    return d


def create_duel_challenge(
    challenger_id: int,
    opponent_username: str,
    wager_type: Optional[str] = None,
    wager_xp_amount: int = 0,
    wager_player_id: Optional[int] = None,
) -> dict:
    """
    Crea un desafío PvP.
    Valida:
    - El oponente existe
    - Si wager_type='xp': el retador tiene suficiente XP
    - Si wager_type='player': el retador posee ese jugador
    Devuelve el challenge creado o {'error': mensaje}.
    """
    conn = get_connection()

    # Buscar oponente
    opp_row = conn.execute("SELECT id, username FROM users WHERE username=?", (opponent_username.strip(),)).fetchone()
    if not opp_row:
        conn.close()
        return {"error": f"Usuario '{opponent_username}' no encontrado"}

    opponent_id = opp_row["id"]
    if opponent_id == challenger_id:
        conn.close()
        return {"error": "No puedes desafiarte a ti mismo"}

    # Validar apuesta
    if wager_type == "xp":
        if wager_xp_amount <= 0:
            conn.close()
            return {"error": "La apuesta de XP debe ser mayor a 0"}
        current_xp = conn.execute("SELECT xp FROM users WHERE id=?", (challenger_id,)).fetchone()
        if not current_xp or current_xp["xp"] < wager_xp_amount:
            conn.close()
            return {"error": "No tienes suficiente XP para esta apuesta"}

    elif wager_type == "player":
        if not wager_player_id:
            conn.close()
            return {"error": "Debes indicar el jugador a apostar"}
        owned = set(get_user_players(challenger_id))
        if wager_player_id not in owned:
            conn.close()
            return {"error": "No posees ese jugador"}

    # Crear desafío
    conn.execute(
        """INSERT INTO duel_challenges
           (challenger_id, opponent_id, status, wager_type, wager_xp_amount, wager_player_id)
           VALUES (?,?,?,?,?,?)""",
        (challenger_id, opponent_id, "pending", wager_type, wager_xp_amount, wager_player_id)
    )
    conn.commit()
    challenge_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    row = conn.execute("SELECT * FROM duel_challenges WHERE id=?", (challenge_id,)).fetchone()
    conn.close()

    challenger_row = get_or_create_user_by_id(challenger_id)
    return _serialize_duel(row, challenger_name=challenger_row.get("username"), opponent_name=opp_row["username"])


def get_or_create_user_by_id(user_id: int) -> dict:
    """Obtiene un usuario por id."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else {}


def get_pending_duels(user_id: int) -> list:
    """Devuelve los desafíos pendientes donde el usuario es el OPONENTE."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT dc.*, uc.username AS challenger_name, uo.username AS opponent_name
        FROM duel_challenges dc
        JOIN users uc ON dc.challenger_id = uc.id
        JOIN users uo ON dc.opponent_id = uo.id
        WHERE dc.opponent_id=? AND dc.status='pending'
        ORDER BY dc.created_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [_serialize_duel(dict(r), r["challenger_name"], r["opponent_name"]) for r in rows]


def get_active_duels(user_id: int) -> list:
    """
    Devuelve los duelos activos (accepted) donde el usuario participa.
    Auto-abandona los que llevan más de 2 horas sin que ningún jugador
    haya iniciado sesión de duelo (never connected).
    """
    DUEL_EXPIRY_SECS = 7200  # 2 horas
    conn = get_connection()
    now_dt = datetime.now(timezone.utc)

    rows = conn.execute("""
        SELECT dc.*, uc.username AS challenger_name, uo.username AS opponent_name
        FROM duel_challenges dc
        JOIN users uc ON dc.challenger_id = uc.id
        JOIN users uo ON dc.opponent_id = uo.id
        WHERE (dc.challenger_id=? OR dc.opponent_id=?) AND dc.status='accepted'
        ORDER BY dc.created_at DESC
    """, (user_id, user_id)).fetchall()

    valid = []
    for r in rows:
        d = dict(r)
        # Calcular antigüedad
        try:
            created = datetime.fromisoformat(d["created_at"])
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            age_secs = (now_dt - created).total_seconds()
        except Exception:
            age_secs = 0

        # Comprobar si existe sesión activa (algún jugador conectado)
        session = conn.execute(
            "SELECT state, p1_heartbeat, p2_heartbeat FROM duel_sessions WHERE challenge_id=?",
            (d["id"],)
        ).fetchone()

        has_active_session = False
        if session:
            sess = dict(session)
            if sess["state"] in ("active", "waiting"):
                # Ver si algún heartbeat es reciente
                for hb_str in [sess["p1_heartbeat"], sess["p2_heartbeat"]]:
                    if hb_str:
                        try:
                            hb = datetime.fromisoformat(hb_str)
                            if hb.tzinfo is None:
                                hb = hb.replace(tzinfo=timezone.utc)
                            if (now_dt - hb).total_seconds() < HEARTBEAT_TIMEOUT_SECS * 4:
                                has_active_session = True
                        except Exception:
                            pass

        # Si llevan > 2h y nadie está conectado → abandonar
        if age_secs > DUEL_EXPIRY_SECS and not has_active_session:
            conn.execute(
                "UPDATE duel_challenges SET status='abandoned' WHERE id=?",
                (d["id"],)
            )
            if session and dict(session)["state"] in ("waiting", "active"):
                conn.execute(
                    "UPDATE duel_sessions SET state='abandoned', finished_at=? WHERE challenge_id=?",
                    (now_dt.isoformat(), d["id"])
                )
            conn.commit()
            continue  # no incluir en la lista

        # Añadir campo de antigüedad para que el frontend pueda informar
        d["age_minutes"] = int(age_secs // 60)
        d["has_active_session"] = has_active_session
        valid.append(d)

    conn.close()
    return [_serialize_duel(dict(r), r["challenger_name"], r["opponent_name"],
                            extra={"age_minutes": r.get("age_minutes", 0),
                                   "has_active_session": r.get("has_active_session", False)})
            for r in valid]


def accept_duel_challenge(challenge_id: int, opponent_id: int) -> dict:
    """
    El oponente acepta el desafío.
    Valida que el oponente también tenga la apuesta disponible.
    Devuelve {'success': True, challenge} o {'error': mensaje}.
    """
    conn = get_connection()
    row = conn.execute("SELECT * FROM duel_challenges WHERE id=?", (challenge_id,)).fetchone()
    if not row:
        conn.close()
        return {"error": "Desafío no encontrado"}

    d = dict(row)
    if d["opponent_id"] != opponent_id:
        conn.close()
        return {"error": "No eres el oponente de este desafío"}
    if d["status"] != "pending":
        conn.close()
        return {"error": f"El desafío ya está en estado '{d['status']}'"}

    # Validar que el oponente también puede pagar la apuesta
    if d["wager_type"] == "xp":
        opp_xp = conn.execute("SELECT xp FROM users WHERE id=?", (opponent_id,)).fetchone()
        if not opp_xp or opp_xp["xp"] < d["wager_xp_amount"]:
            conn.close()
            return {"error": "No tienes suficiente XP para aceptar esta apuesta"}

    elif d["wager_type"] == "player":
        # El oponente debe tener UN jugador de igual rareza del jugador apostado
        wager_player = get_player_by_id(d["wager_player_id"])
        if wager_player:
            owned = set(get_user_players(opponent_id))
            opp_same_rarity = [p for p in PLAYERS if p["rarity"] == wager_player["rarity"] and p["id"] in owned]
            if not opp_same_rarity:
                conn.close()
                return {"error": f"Necesitas al menos un jugador {wager_player['rarity']} para aceptar"}

    conn.execute("UPDATE duel_challenges SET status='accepted' WHERE id=?", (challenge_id,))
    conn.commit()

    row = conn.execute("""
        SELECT dc.*, uc.username AS challenger_name, uo.username AS opponent_name
        FROM duel_challenges dc
        JOIN users uc ON dc.challenger_id = uc.id
        JOIN users uo ON dc.opponent_id = uo.id
        WHERE dc.id=?
    """, (challenge_id,)).fetchone()
    conn.close()
    return {"success": True, "challenge": _serialize_duel(dict(row), row["challenger_name"], row["opponent_name"])}


def reject_duel_challenge(challenge_id: int, opponent_id: int) -> dict:
    """El oponente rechaza el desafío."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM duel_challenges WHERE id=?", (challenge_id,)).fetchone()
    if not row or dict(row)["opponent_id"] != opponent_id:
        conn.close()
        return {"error": "Desafío no encontrado o no eres el oponente"}
    conn.execute("UPDATE duel_challenges SET status='rejected' WHERE id=?", (challenge_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Desafío rechazado"}


def resolve_duel(challenge_id: int, winner_username: str, challenger_score: int, opponent_score: int) -> dict:
    """
    Resuelve un duelo completado.
    - Determina ganador y perdedor
    - Transfiere la apuesta
    - Desbloquea jugador diamante/leyenda al ganador como recompensa
    - Devuelve dict completo con resultado
    """
    conn = get_connection()
    row = conn.execute("""
        SELECT dc.*, uc.username AS challenger_name, uo.username AS opponent_name
        FROM duel_challenges dc
        JOIN users uc ON dc.challenger_id = uc.id
        JOIN users uo ON dc.opponent_id = uo.id
        WHERE dc.id=?
    """, (challenge_id,)).fetchone()

    if not row:
        conn.close()
        return {"error": "Desafío no encontrado"}

    d = dict(row)
    if d["status"] not in ("accepted", "pending"):
        conn.close()
        return {"error": f"El duelo ya está en estado '{d['status']}'"}

    # Determinar IDs
    challenger_id = d["challenger_id"]
    opponent_id = d["opponent_id"]
    winner_id = challenger_id if winner_username == d["challenger_name"] else opponent_id
    loser_id = opponent_id if winner_id == challenger_id else challenger_id

    # Transferir apuesta
    wager_result = {}
    if d["wager_type"] == "xp":
        amount = d["wager_xp_amount"]
        conn.execute("UPDATE users SET xp = MAX(0, xp - ?) WHERE id=?", (amount, loser_id))
        conn.execute("UPDATE users SET xp = xp + ? WHERE id=?", (amount, winner_id))
        conn.commit()
        wager_result = {"type": "xp", "amount": amount}

    elif d["wager_type"] == "player":
        pid = d["wager_player_id"]
        if pid:
            # Transferir: quitar al perdedor, dar al ganador
            conn.execute("DELETE FROM user_players WHERE user_id=? AND player_id=?", (loser_id, pid))
            try:
                conn.execute("INSERT INTO user_players (user_id, player_id) VALUES (?,?)", (winner_id, pid))
            except Exception:
                pass  # Ya lo tiene el ganador (edge case)
            # También quitar del equipo del perdedor si estaba puesto
            conn.execute("DELETE FROM user_team WHERE user_id=? AND player_id=?", (loser_id, pid))
            conn.commit()
            wager_result = {"type": "player", "player": get_player_by_id(pid)}

    # Recompensa por victoria: 25% crack (diamante/oro) · 75% mid-tier (plata/bronce)
    if random.random() < 0.25:
        duel_reward = unlock_player_by_type(winner_id, rarity="diamante")
        if not duel_reward:
            duel_reward = unlock_player_by_type(winner_id, rarity="oro")
    else:
        duel_reward = unlock_player_by_type(winner_id, rarity="plata")
        if not duel_reward:
            duel_reward = unlock_player_by_type(winner_id, rarity="bronce")

    # Añadir XP de victoria al ganador
    xp_bonus = 500
    add_xp(winner_id, xp_bonus)

    # Marcar duelo como completado
    conn.execute("""
        UPDATE duel_challenges
        SET status='completed', winner_id=?, challenger_score=?, opponent_score=?,
            completed_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (winner_id, challenger_score, opponent_score, challenge_id))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "winner_username": winner_username,
        "wager_result": wager_result,
        "duel_player_reward": duel_reward,
        "xp_bonus": xp_bonus,
        "challenger_score": challenger_score,
        "opponent_score": opponent_score,
    }


# ══════════════════════════════════════════════════════════════════
#  MATCHMAKING — cola automática 1v1
# ══════════════════════════════════════════════════════════════════

_matchmaking_lock = threading.Lock()


def join_matchmaking_queue(
    user_id: int,
    username: str,
    wager_type: Optional[str] = None,
    wager_xp_amount: int = 0,
    wager_player_id: Optional[int] = None,
) -> dict:
    """
    Añade al usuario a la cola de matchmaking con su configuración de apuesta.
    Valida la apuesta antes de entrar en cola.
    wager_type: None | 'xp' | 'player'
    """
    conn = get_connection()

    # ── Validar apuesta ──────────────────────────────────────────
    if wager_type == "xp":
        if wager_xp_amount <= 0:
            conn.close()
            return {"error": "La apuesta de pts debe ser mayor a 0"}
        row_xp = conn.execute("SELECT xp FROM users WHERE id=?", (user_id,)).fetchone()
        if not row_xp or row_xp["xp"] < wager_xp_amount:
            conn.close()
            return {"error": f"No tienes suficientes pts (necesitas {wager_xp_amount:,})"}

    elif wager_type == "player":
        if not wager_player_id:
            conn.close()
            return {"error": "Debes seleccionar el jugador a apostar"}
        owned = set(get_user_players(user_id))
        if wager_player_id not in owned:
            conn.close()
            return {"error": "No posees ese jugador"}

    # ── Limpiar match anterior expirado si lo hay ────────────────
    row = conn.execute(
        "SELECT match_id FROM matchmaking_queue WHERE user_id=?", (user_id,)
    ).fetchone()
    if row and row["match_id"]:
        match = conn.execute(
            "SELECT * FROM matchmaking_matches WHERE id=?", (row["match_id"],)
        ).fetchone()
        if match and match["status"] in ("pending", "both_accepted"):
            conn.close()
            return {"ok": True, "already_in_match": True}
        conn.execute(
            "UPDATE matchmaking_queue SET match_id=NULL, status='waiting', joined_at=CURRENT_TIMESTAMP WHERE user_id=?",
            (user_id,)
        )
        conn.commit()

    # ── Insertar / actualizar en cola ───────────────────────────
    conn.execute(
        """INSERT INTO matchmaking_queue
               (user_id, username, status, joined_at, match_id, wager_type, wager_xp_amount, wager_player_id)
           VALUES (?,?,'waiting',CURRENT_TIMESTAMP,NULL,?,?,?)
           ON CONFLICT(user_id) DO UPDATE SET
               status='waiting', joined_at=CURRENT_TIMESTAMP, match_id=NULL,
               username=excluded.username,
               wager_type=excluded.wager_type,
               wager_xp_amount=excluded.wager_xp_amount,
               wager_player_id=excluded.wager_player_id""",
        (user_id, username, wager_type, wager_xp_amount, wager_player_id)
    )
    conn.commit()
    conn.close()

    # Intentar emparejar
    _try_match_players()

    return {"ok": True}


def cancel_matchmaking(user_id: int) -> dict:
    """Saca al usuario de la cola y cancela su match pendiente si lo tiene."""
    conn = get_connection()
    row = conn.execute(
        "SELECT match_id FROM matchmaking_queue WHERE user_id=? AND status='waiting'",
        (user_id,)
    ).fetchone()

    if row and row["match_id"]:
        conn.execute(
            "UPDATE matchmaking_matches SET status='cancelled' WHERE id=? AND status='pending'",
            (row["match_id"],)
        )
        # También poner a waiting al otro jugador por si quiere reintentar
        match = conn.execute(
            "SELECT player1_id, player2_id FROM matchmaking_matches WHERE id=?",
            (row["match_id"],)
        ).fetchone()
        if match:
            other = match["player2_id"] if match["player1_id"] == user_id else match["player1_id"]
            conn.execute(
                "UPDATE matchmaking_queue SET status='cancelled', match_id=NULL WHERE user_id=?",
                (other,)
            )

    conn.execute(
        "UPDATE matchmaking_queue SET status='cancelled', match_id=NULL WHERE user_id=?",
        (user_id,)
    )
    conn.commit()
    conn.close()
    return {"ok": True}


def get_matchmaking_status(user_id: int) -> dict:
    """
    Devuelve el estado actual del jugador en el sistema de matchmaking.
    Usado por el frontend en polling cada 2-3 s.

    Posibles valores de 'state':
      'not_in_queue'   — el usuario no está en cola
      'waiting'        — en cola, buscando oponente
      'matched'        — oponente encontrado, esperando aceptación
      'both_accepted'  — ambos aceptaron → challenge_id disponible
      'cancelled'      — match rechazado o expirado
    """

    conn = get_connection()
    q_row = conn.execute(
        "SELECT * FROM matchmaking_queue WHERE user_id=?", (user_id,)
    ).fetchone()

    if not q_row:
        conn.close()
        return {"state": "not_in_queue"}

    q = dict(q_row)

    if q["status"] == "cancelled":
        conn.close()
        return {"state": "cancelled"}

    if q["status"] == "waiting" and not q["match_id"]:
        conn.close()
        return {"state": "waiting"}

    if not q["match_id"]:
        conn.close()
        return {"state": "waiting"}

    # Tiene un match_id — consultar
    match_row = conn.execute(
        "SELECT * FROM matchmaking_matches WHERE id=?", (q["match_id"],)
    ).fetchone()

    if not match_row:
        conn.close()
        return {"state": "waiting"}

    m = dict(match_row)

    # Comprobar expiración
    try:
        expires = datetime.fromisoformat(m["expires_at"])
        now = datetime.now(timezone.utc)
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if now > expires and m["status"] == "pending":
            # Expirado: marcar como expired
            conn.execute("UPDATE matchmaking_matches SET status='expired' WHERE id=?", (m["id"],))
            conn.execute(
                "UPDATE matchmaking_queue SET status='cancelled', match_id=NULL WHERE user_id=? OR user_id=?",
                (m["player1_id"], m["player2_id"])
            )
            conn.commit()
            conn.close()
            return {"state": "cancelled", "reason": "expired"}
    except Exception:
        pass

    if m["status"] == "both_accepted":
        # Obtener nombre del oponente
        opp_id = m["player2_id"] if m["player1_id"] == user_id else m["player1_id"]
        opp_row = conn.execute("SELECT username FROM users WHERE id=?", (opp_id,)).fetchone()
        opp_name = opp_row["username"] if opp_row else "Desconocido"
        conn.close()
        return {
            "state": "both_accepted",
            "match_id": m["id"],
            "challenge_id": m["challenge_id"],
            "opponent": opp_name,
        }

    if m["status"] in ("cancelled", "expired"):
        conn.close()
        return {"state": "cancelled", "reason": m["status"]}

    if m["status"] == "pending":
        opp_id = m["player2_id"] if m["player1_id"] == user_id else m["player1_id"]
        opp_row = conn.execute("SELECT username FROM users WHERE id=?", (opp_id,)).fetchone()
        opp_name = opp_row["username"] if opp_row else "Desconocido"

        # Calcular segundos restantes
        try:
            expires = datetime.fromisoformat(m["expires_at"])
            now = datetime.now(timezone.utc)
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            seconds_left = max(0, int((expires - now).total_seconds()))
        except Exception:
            seconds_left = 30

        # Leer apuesta del player1 (quien creó la partida / primero en entrar)
        q1_row = conn.execute(
            "SELECT wager_type, wager_xp_amount, wager_player_id FROM matchmaking_queue WHERE user_id=?",
            (m["player1_id"],)
        ).fetchone()
        wager_info = {}
        if q1_row and q1_row["wager_type"]:
            wager_info["wager_type"] = q1_row["wager_type"]
            if q1_row["wager_type"] == "xp":
                wager_info["wager_xp_amount"] = q1_row["wager_xp_amount"]
            elif q1_row["wager_type"] == "player" and q1_row["wager_player_id"]:
                p = get_player_by_id(q1_row["wager_player_id"])
                if p:
                    wager_info["wager_player_id"]   = q1_row["wager_player_id"]
                    wager_info["wager_player_name"]  = p.get("name", "")
                    wager_info["wager_player_rarity"] = p.get("rarity", "")

        conn.close()
        return {
            "state": "matched",
            "match_id": m["id"],
            "opponent": opp_name,
            "seconds_left": seconds_left,
            **wager_info,
        }

    conn.close()
    return {"state": "waiting"}


def respond_to_match(user_id: int, match_id: int, accept: bool) -> dict:
    """
    El jugador acepta (accept=True) o rechaza (accept=False) el match.
    Si ambos aceptan → crea un duel_challenge real y devuelve challenge_id.
    Si alguien rechaza → cancela match y limpia la cola de ambos.
    """

    with _matchmaking_lock:
        conn = get_connection()
        match_row = conn.execute(
            "SELECT * FROM matchmaking_matches WHERE id=?", (match_id,)
        ).fetchone()

        if not match_row:
            conn.close()
            return {"error": "Match no encontrado"}

        m = dict(match_row)

        if m["status"] != "pending":
            conn.close()
            return {"error": f"El match ya no está pendiente (estado: {m['status']})"}

        # Comprobar expiración
        try:
            expires = datetime.fromisoformat(m["expires_at"])
            now = datetime.now(timezone.utc)
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            if now > expires:
                conn.execute("UPDATE matchmaking_matches SET status='expired' WHERE id=?", (match_id,))
                conn.execute(
                    "UPDATE matchmaking_queue SET status='cancelled', match_id=NULL WHERE user_id=? OR user_id=?",
                    (m["player1_id"], m["player2_id"])
                )
                conn.commit()
                conn.close()
                return {"error": "El tiempo de respuesta expiró"}
        except Exception:
            pass

        is_player1 = (m["player1_id"] == user_id)
        is_player2 = (m["player2_id"] == user_id)

        if not is_player1 and not is_player2:
            conn.close()
            return {"error": "No eres participante de este match"}

        response_val = 1 if accept else -1

        if is_player1:
            conn.execute(
                "UPDATE matchmaking_matches SET player1_accepted=? WHERE id=?",
                (response_val, match_id)
            )
        else:
            conn.execute(
                "UPDATE matchmaking_matches SET player2_accepted=? WHERE id=?",
                (response_val, match_id)
            )
        conn.commit()

        # Releer estado actualizado
        m2 = dict(conn.execute(
            "SELECT * FROM matchmaking_matches WHERE id=?", (match_id,)
        ).fetchone())

        # Si alguien rechazó → cancelar
        if m2["player1_accepted"] == -1 or m2["player2_accepted"] == -1:
            conn.execute("UPDATE matchmaking_matches SET status='cancelled' WHERE id=?", (match_id,))
            conn.execute(
                "UPDATE matchmaking_queue SET status='cancelled', match_id=NULL WHERE user_id=? OR user_id=?",
                (m["player1_id"], m["player2_id"])
            )
            conn.commit()
            conn.close()
            return {"ok": True, "state": "cancelled"}

        # Si ambos aceptaron → crear duel_challenge
        if m2["player1_accepted"] == 1 and m2["player2_accepted"] == 1:
            # Obtener usernames
            p1_row = conn.execute("SELECT username FROM users WHERE id=?", (m["player1_id"],)).fetchone()
            p2_row = conn.execute("SELECT username FROM users WHERE id=?", (m["player2_id"],)).fetchone()
            p1_name = p1_row["username"] if p1_row else ""
            p2_name = p2_row["username"] if p2_row else ""

            # Leer apuesta del player1
            q1 = conn.execute(
                "SELECT wager_type, wager_xp_amount, wager_player_id FROM matchmaking_queue WHERE user_id=?",
                (m["player1_id"],)
            ).fetchone()
            w_type   = q1["wager_type"]       if q1 else None
            w_xp     = q1["wager_xp_amount"]  if q1 else 0
            w_player = q1["wager_player_id"]  if q1 else None

            conn.execute(
                """INSERT INTO duel_challenges
                   (challenger_id, opponent_id, status, wager_type, wager_xp_amount, wager_player_id)
                   VALUES (?,?,'accepted',?,?,?)""",
                (m["player1_id"], m["player2_id"], w_type, w_xp or 0, w_player)
            )
            conn.commit()
            challenge_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

            conn.execute(
                "UPDATE matchmaking_matches SET status='both_accepted', challenge_id=? WHERE id=?",
                (challenge_id, match_id)
            )
            # Actualizar cola de ambos
            conn.execute(
                "UPDATE matchmaking_queue SET status='matched' WHERE user_id=? OR user_id=?",
                (m["player1_id"], m["player2_id"])
            )
            conn.commit()
            conn.close()
            return {
                "ok": True,
                "state": "both_accepted",
                "challenge_id": challenge_id,
                "opponent": p2_name if is_player1 else p1_name,
            }

        # Solo uno aceptó hasta ahora
        conn.close()
        return {"ok": True, "state": "waiting_other"}


def _try_match_players():
    """
    Busca dos jugadores con status='waiting' en la cola y los empareja.
    Llamado automáticamente al hacer join.
    Usa lock para evitar race conditions.
    """

    with _matchmaking_lock:
        conn = get_connection()
        # Tomar los dos jugadores más antiguos en espera sin match
        rows = conn.execute(
            """SELECT user_id, username FROM matchmaking_queue
               WHERE status='waiting' AND match_id IS NULL
               ORDER BY joined_at ASC LIMIT 2"""
        ).fetchall()

        if len(rows) < 2:
            conn.close()
            return

        p1_id = rows[0]["user_id"]
        p2_id = rows[1]["user_id"]

        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat()

        conn.execute(
            """INSERT INTO matchmaking_matches
               (player1_id, player2_id, status, expires_at)
               VALUES (?,?,'pending',?)""",
            (p1_id, p2_id, expires_at)
        )
        conn.commit()
        match_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            "UPDATE matchmaking_queue SET status='waiting', match_id=? WHERE user_id=?",
            (match_id, p1_id)
        )
        conn.execute(
            "UPDATE matchmaking_queue SET status='waiting', match_id=? WHERE user_id=?",
            (match_id, p2_id)
        )
        conn.commit()
        conn.close()


# ══════════════════════════════════════════════════════════════════
#  SESIONES DE DUELO EN TIEMPO REAL
# ══════════════════════════════════════════════════════════════════

# Timeout de heartbeat: si el jugador no envía heartbeat en este tiempo → desconectado
HEARTBEAT_TIMEOUT_SECS = 15
# Espera máxima al rival después de que uno termina
WAIT_RIVAL_SECS = 60


def abandon_duel(challenge_id: int, user_id: int) -> dict:
    """
    Un jugador abandona/cancela una partida en curso manualmente.
    - Si nunca hubo sesión activa → simplemente marca el challenge como 'abandoned'.
    - Si había sesión → el otro jugador gana por WO (si aplica apuesta).
    """
    conn = get_connection()
    ch = conn.execute("SELECT * FROM duel_challenges WHERE id=?", (challenge_id,)).fetchone()
    if not ch:
        conn.close()
        return {"error": "Desafío no encontrado"}

    d = dict(ch)
    if d["challenger_id"] != user_id and d["opponent_id"] != user_id:
        conn.close()
        return {"error": "No participas en este desafío"}

    if d["status"] in ("finished", "abandoned"):
        conn.close()
        return {"ok": True, "already_done": True}

    # Buscar sesión
    session = conn.execute(
        "SELECT * FROM duel_sessions WHERE challenge_id=?", (challenge_id,)
    ).fetchone()

    now_str = datetime.now(timezone.utc).isoformat()

    if session:
        s = dict(session)
        if s["state"] not in ("finished", "abandoned"):
            # Determinar ganador por WO: el rival (quien NO abandona)
            rival_id = d["opponent_id"] if user_id == d["challenger_id"] else d["challenger_id"]
            is_p1 = (s["player1_id"] == rival_id)
            rival_score = s["p1_score"] if is_p1 else s["p2_score"]
            my_score    = s["p2_score"] if is_p1 else s["p1_score"]

            conn.execute(
                """UPDATE duel_sessions SET state='abandoned', winner_id=?, finished_at=?
                   WHERE challenge_id=?""",
                (rival_id, now_str, challenge_id)
            )
            conn.commit()
            conn.close()
            # Resolver: rival gana por WO
            _resolve_duel_session(
                challenge_id, rival_id,
                rival_score if is_p1 else my_score,
                my_score    if is_p1 else rival_score
            )
            return {"ok": True, "wo": True, "winner_id": rival_id}

    # Sin sesión activa → solo marcar como abandoned sin transferir apuesta
    conn.execute(
        "UPDATE duel_challenges SET status='abandoned' WHERE id=?",
        (challenge_id,)
    )
    conn.commit()
    conn.close()
    return {"ok": True, "cancelled": True}


def start_duel_session(challenge_id: int) -> dict:
    """
    Crea una sesión de duelo en tiempo real para el challenge dado.
    Si ya existe, la devuelve. Cambia estado a 'active' cuando los dos han conectado.
    """
    conn = get_connection()
    # Buscar el challenge
    ch = conn.execute(
        "SELECT * FROM duel_challenges WHERE id=?", (challenge_id,)
    ).fetchone()
    if not ch:
        conn.close()
        return {"error": "Duelo no encontrado"}

    ch = dict(ch)
    # Crear o devolver sesión existente
    existing = conn.execute(
        "SELECT * FROM duel_sessions WHERE challenge_id=?", (challenge_id,)
    ).fetchone()

    if not existing:
        conn.execute(
            """INSERT INTO duel_sessions
               (challenge_id, player1_id, player2_id, state)
               VALUES (?,?,?,'waiting')""",
            (challenge_id, ch["challenger_id"], ch["opponent_id"])
        )
        conn.commit()
        session = dict(conn.execute(
            "SELECT * FROM duel_sessions WHERE challenge_id=?", (challenge_id,)
        ).fetchone())
    else:
        session = dict(existing)

    conn.close()
    return {"ok": True, "session": session}


def update_duel_heartbeat(challenge_id: int, user_id: int) -> dict:
    """
    Registra que el usuario sigue conectado (heartbeat).
    Actualiza el timestamp y activa la sesión si ambos han conectado.
    Devuelve el estado actual de la sesión (para que el cliente detecte desconexiones).
    """
    conn = get_connection()
    now_str = datetime.now(timezone.utc).isoformat()

    session = conn.execute(
        "SELECT * FROM duel_sessions WHERE challenge_id=?", (challenge_id,)
    ).fetchone()
    if not session:
        conn.close()
        return {"error": "Sesión no encontrada"}

    s = dict(session)

    is_p1 = (s["player1_id"] == user_id)
    is_p2 = (s["player2_id"] == user_id)
    if not is_p1 and not is_p2:
        conn.close()
        return {"error": "No eres participante de esta sesión"}

    col = "p1_heartbeat" if is_p1 else "p2_heartbeat"
    conn.execute(
        f"UPDATE duel_sessions SET {col}=? WHERE challenge_id=?",
        (now_str, challenge_id)
    )

    # Activar sesión si ambos han conectado al menos una vez
    if s["state"] == "waiting":
        # Necesitamos que ambos hayan enviado heartbeat
        other_hb = s["p2_heartbeat"] if is_p1 else s["p1_heartbeat"]
        if other_hb is not None:
            conn.execute(
                "UPDATE duel_sessions SET state='active' WHERE challenge_id=?",
                (challenge_id,)
            )
    conn.commit()

    # Releer y analizar estado
    s2 = dict(conn.execute(
        "SELECT * FROM duel_sessions WHERE challenge_id=?", (challenge_id,)
    ).fetchone())

    # Detectar desconexión del rival
    now_dt = datetime.now(timezone.utc)
    rival_col = "p2_heartbeat" if is_p1 else "p1_heartbeat"
    rival_hb_str = s2[rival_col]
    rival_disconnected = False
    if rival_hb_str:
        try:
            rival_hb = datetime.fromisoformat(rival_hb_str)
            if rival_hb.tzinfo is None:
                rival_hb = rival_hb.replace(tzinfo=timezone.utc)
            rival_disconnected = (now_dt - rival_hb).total_seconds() > HEARTBEAT_TIMEOUT_SECS
        except Exception:
            pass

    conn.close()
    return {
        "ok": True,
        "state": s2["state"],
        "rival_disconnected": rival_disconnected,
        "p1_finished": bool(s2["p1_finished"]),
        "p2_finished": bool(s2["p2_finished"]),
        "p1_score": s2["p1_score"],
        "p2_score": s2["p2_score"],
        "winner_id": s2["winner_id"],
    }


def finish_duel_session(challenge_id: int, user_id: int, score: int) -> dict:
    """
    El jugador terminó su partida. Guarda su score.
    Si el rival también terminó → resolver automáticamente y guardar stats.
    Si el rival no termina en WAIT_RIVAL_SECS → WO al jugador que terminó.
    Devuelve: { ok, waiting_rival, resolved?, winner_id?, ... }
    """
    conn = get_connection()
    now_str = datetime.now(timezone.utc).isoformat()

    session = conn.execute(
        "SELECT * FROM duel_sessions WHERE challenge_id=?", (challenge_id,)
    ).fetchone()
    if not session:
        conn.close()
        return {"error": "Sesión no encontrada"}

    s = dict(session)
    is_p1 = (s["player1_id"] == user_id)
    is_p2 = (s["player2_id"] == user_id)
    if not is_p1 and not is_p2:
        conn.close()
        return {"error": "No eres participante"}

    if s["state"] == "finished":
        conn.close()
        return {"ok": True, "already_finished": True, "winner_id": s["winner_id"]}

    # Marcar como terminado y guardar score
    score_col    = "p1_score"    if is_p1 else "p2_score"
    finished_col = "p1_finished" if is_p1 else "p2_finished"
    conn.execute(
        f"UPDATE duel_sessions SET {score_col}=?, {finished_col}=1 WHERE challenge_id=?",
        (score, challenge_id)
    )
    conn.commit()

    # Releer
    s2 = dict(conn.execute(
        "SELECT * FROM duel_sessions WHERE challenge_id=?", (challenge_id,)
    ).fetchone())

    both_finished = bool(s2["p1_finished"]) and bool(s2["p2_finished"])

    if both_finished:
        # Resolver → quien tenga más puntos gana
        p1_score = s2["p1_score"]
        p2_score = s2["p2_score"]
        if p1_score > p2_score:
            winner_id = s2["player1_id"]
        elif p2_score > p1_score:
            winner_id = s2["player2_id"]
        else:
            winner_id = None  # empate

        conn.execute(
            """UPDATE duel_sessions SET state='finished', winner_id=?, finished_at=?
               WHERE challenge_id=?""",
            (winner_id, now_str, challenge_id)
        )
        conn.commit()
        conn.close()

        # Actualizar stats y resolver apuesta
        result = _resolve_duel_session(challenge_id, winner_id, p1_score, p2_score)
        return {
            "ok": True,
            "resolved": True,
            "winner_id": winner_id,
            "p1_score": p1_score,
            "p2_score": p2_score,
            **result,
        }

    conn.close()
    # El jugador terminó pero el rival no → el frontend debe esperar y hacer poll
    return {
        "ok": True,
        "waiting_rival": True,
        "my_score": score,
    }


def get_duel_session_status(challenge_id: int, user_id: int) -> dict:
    """
    Estado actual de la sesión de duelo.
    Usado por el frontend en polling después de terminar para esperar al rival
    o detectar desconexión.
    """
    conn = get_connection()
    session = conn.execute(
        "SELECT * FROM duel_sessions WHERE challenge_id=?", (challenge_id,)
    ).fetchone()
    if not session:
        conn.close()
        return {"state": "not_found"}

    s = dict(session)
    is_p1 = (s["player1_id"] == user_id)

    # Detectar desconexión del rival
    now_dt = datetime.now(timezone.utc)
    rival_hb_str = s["p2_heartbeat"] if is_p1 else s["p1_heartbeat"]
    rival_disconnected = False
    rival_connected_at_all = rival_hb_str is not None
    if rival_hb_str:
        try:
            rival_hb = datetime.fromisoformat(rival_hb_str)
            if rival_hb.tzinfo is None:
                rival_hb = rival_hb.replace(tzinfo=timezone.utc)
            rival_disconnected = (now_dt - rival_hb).total_seconds() > HEARTBEAT_TIMEOUT_SECS
        except Exception:
            pass

    result = {
        "state": s["state"],
        "p1_finished": bool(s["p1_finished"]),
        "p2_finished": bool(s["p2_finished"]),
        "p1_score": s["p1_score"],
        "p2_score": s["p2_score"],
        "winner_id": s["winner_id"],
        "rival_disconnected": rival_disconnected,
        "rival_connected_at_all": rival_connected_at_all,
    }

    # Si no terminó pero el rival se desconectó → WO
    if s["state"] == "active" and rival_disconnected:
        # Forzar WO: el jugador que sigue conectado gana
        my_finished = s["p1_finished"] if is_p1 else s["p2_finished"]
        if my_finished:
            wo_winner = user_id
            now_str = now_dt.isoformat()
            my_score = s["p1_score"] if is_p1 else s["p2_score"]
            rival_score = s["p2_score"] if is_p1 else s["p1_score"]
            conn.execute(
                """UPDATE duel_sessions SET state='finished', winner_id=?, finished_at=?
                   WHERE challenge_id=?""",
                (wo_winner, now_str, challenge_id)
            )
            conn.commit()
            conn.close()
            wo_result = _resolve_duel_session(challenge_id, wo_winner, my_score if is_p1 else rival_score, rival_score if is_p1 else my_score)
            return {**result, "state": "finished", "winner_id": wo_winner, "wo": True, **wo_result}

    conn.close()
    return result


def _resolve_duel_session(challenge_id: int, winner_id: Optional[int], p1_score: int, p2_score: int) -> dict:
    """
    Resuelve el duel_challenge (transfiere apuesta, da XP/stats, limpia sesión).
    Llamado internamente cuando la sesión termina.
    """
    conn = get_connection()
    ch = conn.execute("SELECT * FROM duel_challenges WHERE id=?", (challenge_id,)).fetchone()
    if not ch:
        conn.close()
        return {}

    d = dict(ch)
    p1_id = d["challenger_id"]
    p2_id = d["opponent_id"]

    # Obtener usernames
    p1_row = conn.execute("SELECT username FROM users WHERE id=?", (p1_id,)).fetchone()
    p2_row = conn.execute("SELECT username FROM users WHERE id=?", (p2_id,)).fetchone()
    p1_name = p1_row["username"] if p1_row else ""
    p2_name = p2_row["username"] if p2_row else ""

    winner_name = ""
    if winner_id == p1_id:
        winner_name = p1_name
        loser_id = p2_id
    elif winner_id == p2_id:
        winner_name = p2_name
        loser_id = p1_id
    else:
        loser_id = None  # empate

    wager_result = {}

    if winner_id and loser_id:
        # Transferir apuesta
        if d["wager_type"] == "xp" and d["wager_xp_amount"]:
            amt = d["wager_xp_amount"]
            conn.execute("UPDATE users SET xp = MAX(0, xp - ?) WHERE id=?", (amt, loser_id))
            conn.execute("UPDATE users SET xp = xp + ? WHERE id=?", (amt, winner_id))
            conn.commit()
            wager_result = {"type": "xp", "amount": amt}
        elif d["wager_type"] == "player" and d["wager_player_id"]:
            pid = d["wager_player_id"]
            conn.execute("DELETE FROM user_players WHERE user_id=? AND player_id=?", (loser_id, pid))
            try:
                conn.execute("INSERT INTO user_players (user_id, player_id) VALUES (?,?)", (winner_id, pid))
            except Exception:
                pass
            conn.execute("DELETE FROM user_team WHERE user_id=? AND player_id=?", (loser_id, pid))
            conn.commit()
            wager_result = {"type": "player", "player": get_player_by_id(pid)}

        # Bonus XP al ganador
        add_xp(winner_id, 500)

    # Marcar duel_challenge como completado
    conn.execute(
        """UPDATE duel_challenges
           SET status='completed', winner_id=?, challenger_score=?, opponent_score=?,
               completed_at=CURRENT_TIMESTAMP
           WHERE id=?""",
        (winner_id, p1_score, p2_score, challenge_id)
    )
    conn.commit()

    # Actualizar duel_stats para ambos
    for uid, won in [(p1_id, winner_id == p1_id), (p2_id, winner_id == p2_id)]:
        is_win  = 1 if won else 0
        is_loss = 1 if (winner_id is not None and not won) else 0
        conn.execute(
            """INSERT INTO duel_stats (user_id, games_played, wins, losses, updated_at)
               VALUES (?, 1, ?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(user_id) DO UPDATE SET
                   games_played = games_played + 1,
                   wins   = wins   + ?,
                   losses = losses + ?,
                   updated_at = CURRENT_TIMESTAMP""",
            (uid, is_win, is_loss, is_win, is_loss)
        )
    conn.commit()

    # Limpiar cola de matchmaking de ambos (datos temporales)
    conn.execute(
        "DELETE FROM matchmaking_queue WHERE user_id=? OR user_id=?",
        (p1_id, p2_id)
    )
    conn.commit()
    conn.close()

    return {
        "wager_result": wager_result,
        "winner_username": winner_name,
        "p1_score": p1_score,
        "p2_score": p2_score,
        "p1_name": p1_name,
        "p2_name": p2_name,
    }


def get_duel_stats(user_id: int) -> dict:
    """Estadísticas esenciales de duelo del usuario."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM duel_stats WHERE user_id=?", (user_id,)
    ).fetchone()
    conn.close()
    if not row:
        return {"games_played": 0, "wins": 0, "losses": 0, "win_rate": 0}
    d = dict(row)
    win_rate = round(d["wins"] / d["games_played"] * 100) if d["games_played"] > 0 else 0
    return {**d, "win_rate": win_rate}
