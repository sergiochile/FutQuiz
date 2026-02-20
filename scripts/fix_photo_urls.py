#!/usr/bin/env python3
"""
Detecta y corrige URLs de Wikimedia malformadas en players.py
"""
import sys
import os
import re
import hashlib

sys.path.insert(0, '/Users/sergecchile./Desktop/Futquiz')

from backend.data.players import PLAYERS

def check_url_format(url):
    """Verifica si la URL tiene el formato correcto de Wikimedia"""
    if not url:
        return 'EMPTY'
    if 'Unknown_person' in url or 'SILHOUETTE' in url:
        return 'SILHOUETTE'
    
    # URL válida con /thumb/: https://upload.wikimedia.org/wikipedia/commons/thumb/X/XX/Filename.jpg/240px-Filename.jpg
    # URL inválida sin /thumb/: https://upload.wikimedia.org/wikipedia/commons/X/XX/240px-Filename.jpg
    
    if '240px-' in url and '/thumb/' not in url:
        return 'MISSING_THUMB'
    
    if not url.startswith('https://'):
        return 'BAD_SCHEME'
    
    return 'OK'

# Encontrar todos los problemas
bad_players = []
for p in PLAYERS:
    url = p.get('photo', '')
    status = check_url_format(url)
    if status != 'OK':
        bad_players.append({
            'id': p['id'],
            'name': p['name'],
            'url': url,
            'status': status
        })

print(f"Total jugadores: {len(PLAYERS)}")
print(f"URLs problemáticas: {len(bad_players)}")
print()

for bp in bad_players:
    print(f"ID {bp['id']:3d} | {bp['status']:15s} | {bp['name']}")
    print(f"         URL: {bp['url'][:100]}")
    print()
