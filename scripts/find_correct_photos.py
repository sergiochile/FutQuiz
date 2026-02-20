#!/usr/bin/env python3
"""
Busca URLs correctas de Wikimedia para los 16 jugadores con URLs rotas.
Usa la API de Wikipedia para obtener la imagen principal de cada jugador.
"""
import urllib.request
import urllib.parse
import json
import time

BROKEN_PLAYERS = [
    (9,   "Denzel Dumfries",        "Denzel Dumfries"),
    (10,  "Nuno Mendes",            "Nuno Mendes footballer born 2002"),
    (11,  "Matthijs de Ligt",       "Matthijs de Ligt"),
    (13,  "Aurélien Tchouaméni",    "Aurélien Tchouaméni"),
    (25,  "Dušan Vlahović",         "Dušan Vlahović"),
    (32,  "Julián Álvarez",         "Julián Álvarez footballer"),
    (45,  "Raphaël Varane",         "Raphaël Varane"),
    (46,  "Ederson",                "Ederson Moraes"),
    (65,  "Gavi",                   "Gavi footballer"),
    (74,  "Cole Palmer",            "Cole Palmer"),
    (80,  "Trent Alexander-Arnold", "Trent Alexander-Arnold"),
    (94,  "N'Golo Kanté",           "N'Golo Kanté"),
    (100, "Federico Chiesa",        "Federico Chiesa"),
    (123, "Michel Platini",         "Michel Platini"),
    (136, "Dennis Bergkamp",        "Dennis Bergkamp"),
    (144, "Ferenc Puskás",          "Ferenc Puskás"),
]

def get_wikipedia_image(search_term):
    """Busca la imagen principal de un jugador en Wikipedia"""
    # Primero buscar el título correcto de la página
    search_url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
        'action': 'query',
        'list': 'search',
        'srsearch': search_term,
        'srlimit': 1,
        'format': 'json'
    })
    
    try:
        req = urllib.request.Request(search_url, headers={'User-Agent': 'FutquizBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        
        results = data.get('query', {}).get('search', [])
        if not results:
            return None, "No search results"
        
        page_title = results[0]['title']
        
        # Obtener imagen principal de esa página
        img_url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
            'action': 'query',
            'titles': page_title,
            'prop': 'pageimages',
            'pithumbsize': 240,
            'format': 'json'
        })
        
        req2 = urllib.request.Request(img_url, headers={'User-Agent': 'FutquizBot/1.0'})
        with urllib.request.urlopen(req2, timeout=10) as r2:
            data2 = json.loads(r2.read())
        
        pages = data2.get('query', {}).get('pages', {})
        for page_id, page_data in pages.items():
            thumb = page_data.get('thumbnail', {})
            if thumb.get('source'):
                # Convertir URL de thumb a URL de commons/thumb completa
                thumb_url = thumb['source']
                return thumb_url, page_title
        
        return None, f"No image for page: {page_title}"
    
    except Exception as e:
        return None, str(e)

print("Buscando imágenes para jugadores con URLs rotas...")
print("=" * 70)

for player_id, name, search_term in BROKEN_PLAYERS:
    url, info = get_wikipedia_image(search_term)
    if url:
        print(f"ID {player_id:3d} | {name}")
        print(f"         URL: {url}")
        print(f"         PAGE: {info}")
    else:
        print(f"ID {player_id:3d} | {name} | FAILED: {info}")
    print()
    time.sleep(0.3)  # respetar rate limit

print("Búsqueda completada.")
