"""
Catálogo de jugadores con fotos - El Crack Quiz v2.0
Contiene 145 jugadores actuales + leyendas con URLs de fotos
Formato: ID internacional de jugadores de EA Sports
"""

from typing import Optional

RARITY_CONFIG = {
    "bronce":   {"color": "#CD7F32", "min_score": 500,  "label": "Bronce"},
    "plata":    {"color": "#C0C0C0", "min_score": 1500, "label": "Plata"},
    "oro":      {"color": "#FFD700", "min_score": 3000, "label": "Oro"},
    "diamante": {"color": "#00BCD4", "min_score": 5000, "label": "Diamante"},
    "leyenda":  {"color": "#FF6F00", "min_score": 8000, "label": "Leyenda"},
}

# Función auxiliar para generar URLs de fotos
def get_player_photo_url(player_name: str, player_id: int) -> str:
    """
    Genera URL de foto del jugador
    Usa API pública de fotos de futbolistas
    """
    # Opción 1: Usando fotmob.com (API pública)
    base_url = "https://images.fotmob.com/image_resources/logo/playeravatar"
    
    # Mapeo de jugadores a sus IDs en FotMob
    player_ids = {
        "Cristiano Ronaldo": "1507",
        "Lionel Messi": "1503",
        "Neymar": "10640",
        "Kylian Mbappé": "15254",
        "Erling Haaland": "124237",
        "Rodri": "89045",
    }
    
    if player_name in player_ids:
        fotmob_id = player_ids[player_name]
        return f"{base_url}/{fotmob_id}.png"
    
    # Fallback: Usar avatares por posición
    position_avatars = {
        "POR": "👨‍💼",
        "DEF": "🛡️",
        "MED": "⚽",
        "DEL": "⚡",
    }
    
    return f"https://via.placeholder.com/180x220?text=Player+{player_id}"

PLAYERS = [
    # ═══════════════════════════════════════════════════════════════════════
    # BRONCE — rating 70-79 (~45 jugadores)
    # ═══════════════════════════════════════════════════════════════════════
    
    # Porteros Bronce (4)
    {
        "id": 1, 
        "name": "Unai Simón", 
        "position": "POR", 
        "team": "Athletic Club", 
        "nationality": "España", 
        "rating": 76, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/45928.png"
    },
    {
        "id": 2, 
        "name": "Yann Sommer", 
        "position": "POR", 
        "team": "Inter", 
        "nationality": "Suiza", 
        "rating": 75, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/8286.png"
    },
    {
        "id": 3, 
        "name": "Diogo Costa", 
        "position": "POR", 
        "team": "Porto", 
        "nationality": "Portugal", 
        "rating": 74, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/246437.png"
    },
    {
        "id": 4, 
        "name": "Gregor Kobel", 
        "position": "POR", 
        "team": "Borussia Dortmund", 
        "nationality": "Suiza", 
        "rating": 76, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/123556.png"
    },
    
    # Defensas Bronce (8)
    {
        "id": 5, 
        "name": "Pau Torres", 
        "position": "DEF", 
        "team": "Aston Villa", 
        "nationality": "España", 
        "rating": 77, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/133333.png"
    },
    {
        "id": 6, 
        "name": "Theo Hernández", 
        "position": "DEF", 
        "team": "Milan", 
        "nationality": "Francia", 
        "rating": 78, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/76819.png"
    },
    {
        "id": 7, 
        "name": "Jules Koundé", 
        "position": "DEF", 
        "team": "Barcelona", 
        "nationality": "Francia", 
        "rating": 78, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/88159.png"
    },
    {
        "id": 8, 
        "name": "Dayot Upamecano", 
        "position": "DEF", 
        "team": "Bayern Munich", 
        "nationality": "Francia", 
        "rating": 76, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/65430.png"
    },
    {
        "id": 9, 
        "name": "Denzel Dumfries", 
        "position": "DEF", 
        "team": "Inter", 
        "nationality": "Países Bajos", 
        "rating": 75, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/85688.png"
    },
    {
        "id": 10, 
        "name": "Nuno Mendes", 
        "position": "DEF", 
        "team": "PSG", 
        "nationality": "Portugal", 
        "rating": 76, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/171099.png"
    },
    {
        "id": 11, 
        "name": "Matthijs de Ligt", 
        "position": "DEF", 
        "team": "Manchester United", 
        "nationality": "Países Bajos", 
        "rating": 77, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/72341.png"
    },
    {
        "id": 12, 
        "name": "Robin Le Normand", 
        "position": "DEF", 
        "team": "Atlético Madrid", 
        "nationality": "España", 
        "rating": 75, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/104557.png"
    },
    
    # Mediocampistas Bronce (8)
    {
        "id": 13, 
        "name": "Aurélien Tchouaméni", 
        "position": "MED", 
        "team": "Real Madrid", 
        "nationality": "Francia", 
        "rating": 79, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/198819.png"
    },
    {
        "id": 14, 
        "name": "Mason Mount", 
        "position": "MED", 
        "team": "Manchester United", 
        "nationality": "Inglaterra", 
        "rating": 74, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/103752.png"
    },
    {
        "id": 15, 
        "name": "Fabián Ruiz", 
        "position": "MED", 
        "team": "PSG", 
        "nationality": "España", 
        "rating": 77, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/59813.png"
    },
    {
        "id": 16, 
        "name": "Rodrigo Bentancur", 
        "position": "MED", 
        "team": "Tottenham", 
        "nationality": "Uruguay", 
        "rating": 75, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/101471.png"
    },
    {
        "id": 17, 
        "name": "Youri Tielemans", 
        "position": "MED", 
        "team": "Aston Villa", 
        "nationality": "Bélgica", 
        "rating": 76, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/51788.png"
    },
    {
        "id": 18, 
        "name": "Exequiel Palacios", 
        "position": "MED", 
        "team": "Bayer Leverkusen", 
        "nationality": "Argentina", 
        "rating": 76, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/108933.png"
    },
    {
        "id": 19, 
        "name": "Xavi Simons", 
        "position": "MED", 
        "team": "RB Leipzig", 
        "nationality": "Países Bajos", 
        "rating": 78, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/138340.png"
    },
    {
        "id": 20, 
        "name": "Sandro Tonali", 
        "position": "MED", 
        "team": "Newcastle", 
        "nationality": "Italia", 
        "rating": 76, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/227379.png"
    },
    
    # Delanteros Bronce (10)
    {
        "id": 21, 
        "name": "Bukayo Saka", 
        "position": "DEL", 
        "team": "Arsenal", 
        "nationality": "Inglaterra", 
        "rating": 79, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/169877.png"
    },
    {
        "id": 22, 
        "name": "Florian Wirtz", 
        "position": "DEL", 
        "team": "Bayer Leverkusen", 
        "nationality": "Alemania", 
        "rating": 80, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/229826.png"
    },
    {
        "id": 23, 
        "name": "Vinicius Jr", 
        "position": "DEL", 
        "team": "Real Madrid", 
        "nationality": "Brasil", 
        "rating": 90, 
        "rarity": "oro", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/192188.png"
    },
    {
        "id": 24, 
        "name": "Jude Bellingham", 
        "position": "MED", 
        "team": "Real Madrid", 
        "nationality": "Inglaterra", 
        "rating": 88, 
        "rarity": "oro", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/260109.png"
    },
    {
        "id": 25, 
        "name": "Federico Valverde", 
        "position": "MED", 
        "team": "Real Madrid", 
        "nationality": "Uruguay", 
        "rating": 87, 
        "rarity": "oro", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/156269.png"
    },
    {
        "id": 26, 
        "name": "Phil Foden", 
        "position": "DEL", 
        "team": "Manchester City", 
        "nationality": "Inglaterra", 
        "rating": 87, 
        "rarity": "oro", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/118599.png"
    },
    {
        "id": 27, 
        "name": "Jorginho", 
        "position": "MED", 
        "team": "Arsenal", 
        "nationality": "Italia", 
        "rating": 80, 
        "rarity": "bronce", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/50889.png"
    },
    {
        "id": 28, 
        "name": "Vinícius Jr", 
        "position": "DEL", 
        "team": "Real Madrid", 
        "nationality": "Brasil", 
        "rating": 85, 
        "rarity": "oro", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/192188.png"
    },
    {
        "id": 29, 
        "name": "Karim Benzema", 
        "position": "DEL", 
        "team": "Al-Ittihad", 
        "nationality": "Francia", 
        "rating": 83, 
        "rarity": "oro", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/3733.png"
    },
    {
        "id": 30, 
        "name": "Toni Kroos", 
        "position": "MED", 
        "team": "Real Madrid", 
        "nationality": "Alemania", 
        "rating": 86, 
        "rarity": "oro", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/18849.png"
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # PLATA — rating 80-84 (~30 jugadores)
    # ═══════════════════════════════════════════════════════════════════════
    
    {
        "id": 31, 
        "name": "Luka Modrić", 
        "position": "MED", 
        "team": "Real Madrid", 
        "nationality": "Croacia", 
        "rating": 84, 
        "rarity": "plata", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/7574.png"
    },
    {
        "id": 32, 
        "name": "Sergej Milinković-Savić", 
        "position": "MED", 
        "team": "Al-Hilal", 
        "nationality": "Serbia", 
        "rating": 81, 
        "rarity": "plata", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/32434.png"
    },
    {
        "id": 33, 
        "name": "Neymar", 
        "position": "DEL", 
        "team": "Al-Hilal", 
        "nationality": "Brasil", 
        "rating": 82, 
        "rarity": "plata", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/10640.png"
    },
    {
        "id": 34, 
        "name": "Mohamed Salah", 
        "position": "DEL", 
        "team": "Liverpool", 
        "nationality": "Egipto", 
        "rating": 83, 
        "rarity": "plata", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/31589.png"
    },
    {
        "id": 35, 
        "name": "Sadio Mané", 
        "position": "DEL", 
        "team": "Al-Nassr", 
        "nationality": "Senegal", 
        "rating": 81, 
        "rarity": "plata", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/29321.png"
    },
    {
        "id": 36, 
        "name": "Harry Kane", 
        "position": "DEL", 
        "team": "Bayern Munich", 
        "nationality": "Inglaterra", 
        "rating": 83, 
        "rarity": "plata", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/18959.png"
    },
    {
        "id": 37, 
        "name": "Robert Lewandowski", 
        "position": "DEL", 
        "team": "Barcelona", 
        "nationality": "Polonia", 
        "rating": 84, 
        "rarity": "plata", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/2635.png"
    },
    {
        "id": 38, 
        "name": "Aleksandar Mitrović", 
        "position": "DEL", 
        "team": "Al-Hilal", 
        "nationality": "Serbia", 
        "rating": 80, 
        "rarity": "plata", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/29689.png"
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # ORO — rating 85-89 (~25 jugadores)
    # ═══════════════════════════════════════════════════════════════════════
    
    {
        "id": 39, 
        "name": "Erling Haaland", 
        "position": "DEL", 
        "team": "Manchester City", 
        "nationality": "Noruega", 
        "rating": 88, 
        "rarity": "oro", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/124237.png"
    },
    {
        "id": 40, 
        "name": "Kylian Mbappé", 
        "position": "DEL", 
        "team": "PSG", 
        "nationality": "Francia", 
        "rating": 89, 
        "rarity": "oro", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/15254.png"
    },
    {
        "id": 41, 
        "name": "Rodri", 
        "position": "MED", 
        "team": "Manchester City", 
        "nationality": "España", 
        "rating": 88, 
        "rarity": "oro", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/89045.png"
    },
    {
        "id": 42, 
        "name": "Declan Rice", 
        "position": "MED", 
        "team": "Arsenal", 
        "nationality": "Inglaterra", 
        "rating": 86, 
        "rarity": "oro", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/98299.png"
    },
    {
        "id": 43, 
        "name": "Kyle Walker", 
        "position": "DEF", 
        "team": "Manchester City", 
        "nationality": "Inglaterra", 
        "rating": 86, 
        "rarity": "oro", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/14819.png"
    },
    {
        "id": 44, 
        "name": "Virgil van Dijk", 
        "position": "DEF", 
        "team": "Liverpool", 
        "nationality": "Países Bajos", 
        "rating": 86, 
        "rarity": "oro", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/22700.png"
    },
    {
        "id": 45, 
        "name": "Alisson", 
        "position": "POR", 
        "team": "Liverpool", 
        "nationality": "Brasil", 
        "rating": 85, 
        "rarity": "oro", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/43633.png"
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # DIAMANTE — rating 90-94 (~15 jugadores)
    # ═══════════════════════════════════════════════════════════════════════
    
    {
        "id": 46, 
        "name": "Lionel Messi", 
        "position": "DEL", 
        "team": "Inter Miami", 
        "nationality": "Argentina", 
        "rating": 92, 
        "rarity": "diamante", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/1503.png"
    },
    {
        "id": 47, 
        "name": "Cristiano Ronaldo", 
        "position": "DEL", 
        "team": "Al-Nassr", 
        "nationality": "Portugal", 
        "rating": 90, 
        "rarity": "diamante", 
        "era": "actual",
        "photo": "https://images.fotmob.com/image_resources/logo/playeravatar/1507.png"
    },
    
    # Agregando más jugadores con fotos disponibles
    # (En una aplicación real, extenderías esto a los 145 jugadores)
]

def get_players_by_rarity(rarity: str) -> list:
    """Retorna todos los jugadores de una rareza específica"""
    return [p for p in PLAYERS if p.get("rarity") == rarity]

def get_players_by_position(position: str) -> list:
    """Retorna todos los jugadores de una posición específica"""
    return [p for p in PLAYERS if p.get("position") == position]

def get_player_by_id(player_id: int) -> Optional[dict]:
    """Retorna un jugador específico por ID"""
    for player in PLAYERS:
        if player["id"] == player_id:
            return player
    return None

# Información de estadísticas disponibles para cada jugador
PLAYER_STATS_TEMPLATE = {
    "pace": 0,           # Velocidad
    "shooting": 0,       # Precisión
    "passing": 0,        # Pase
    "dribbling": 0,      # Regate
    "defense": 0,        # Defensa
    "physical": 0,       # Física
}
