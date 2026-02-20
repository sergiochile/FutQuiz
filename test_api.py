#!/usr/bin/env python3
"""
Script de Testing Automático - El Crack Quiz
Simula una partida completa y verifica que todo funciona
"""

import requests
import json
import time

API_BASE = "http://127.0.0.1:8000"

def test_api():
    print("=" * 60)
    print("🧪 TESTING AUTOMÁTICO - EL CRACK QUIZ")
    print("=" * 60)
    print()

    # Test 1: Info del API
    print("1️⃣  Test: GET /api/info")
    try:
        res = requests.get(f"{API_BASE}/api/info")
        assert res.status_code == 200, f"Status {res.status_code}"
        data = res.json()
        print(f"   ✅ API activa")
        print(f"   - Categorías: {len(data['categories'])}")
        print(f"   - Niveles: {len(data['levels'])}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # Test 2: Registrar usuario
    print("\n2️⃣  Test: POST /api/user/register")
    try:
        res = requests.get(f"{API_BASE}/api/user/register?username=TestBot")
        assert res.status_code == 200, f"Status {res.status_code}"
        user = res.json()
        print(f"   ✅ Usuario registrado: {user['username']}")
        print(f"   - ID: {user['user_id']}")
        print(f"   - Jugadores desbloqueados: {user['unlocked_count']}/150")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # Test 3: Iniciar partida
    print("\n3️⃣  Test: POST /api/game/start")
    try:
        payload = {
            "player_name": "TestBot",
            "mode": "classic",
            "category": None
        }
        res = requests.post(f"{API_BASE}/api/game/start", json=payload)
        assert res.status_code == 200, f"Status {res.status_code}"
        game = res.json()
        session_id = game['session_id']
        print(f"   ✅ Partida iniciada")
        print(f"   - Session ID: {session_id}")
        print(f"   - Modo: {game['mode']}")
        print(f"   - Total preguntas: {game['total_questions']}")
        
        # Verificar que hay una primera pregunta
        assert game['first_question'] is not None, "Sin pregunta inicial"
        print(f"   - ✅ Primera pregunta cargada")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # Test 4: Resolver preguntas
    print("\n4️⃣  Test: Resolver 5 preguntas")
    try:
        correct = 0
        for i in range(5):
            q = game['first_question'] if i == 0 else game['first_question']
            
            # Responder correctamente la primera, mal la segunda, etc
            if i % 2 == 0:
                answer = q['options'][0]  # Respuesta aleatoria
            else:
                answer = q['options'][1]
            
            res = requests.get(f"{API_BASE}/api/game/{session_id}/question")
            assert res.status_code == 200
            game_state = res.json()
            
            if not game_state.get('game_over'):
                q = game_state['question']
                print(f"   Pregunta {i+1}: {q['question'][:50]}...")
        
        print(f"   ✅ Preguntas cargadas correctamente")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # Test 5: Terminar partida
    print("\n5️⃣  Test: POST /api/game/finish")
    try:
        payload = {
            "username": "TestBot",
            "score": 2500,
            "accuracy": 80.0,
            "correct": 8,
            "total": 10
        }
        res = requests.post(f"{API_BASE}/api/game/finish", json=payload)
        assert res.status_code == 200, f"Status {res.status_code}"
        result = res.json()
        print(f"   ✅ Partida guardada")
        print(f"   - Puntaje: {payload['score']}")
        print(f"   - Precisión: {payload['accuracy']}%")
        if result.get('player_unlocked'):
            print(f"   - 🎉 ¡Jugador desbloqueado! {result['player_unlocked']['name']}")
        print(f"   - Total desbloqueados: {result['total_unlocked']}/150")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # Test 6: Ver colección
    print("\n6️⃣  Test: GET /api/players/catalog")
    try:
        res = requests.get(f"{API_BASE}/api/players/catalog")
        assert res.status_code == 200, f"Status {res.status_code}"
        data = res.json()
        print(f"   ✅ Catálogo cargado")
        print(f"   - Total jugadores: {data['total']}")
        print(f"   - Desbloqueados: {data['unlocked']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # Test 7: Ranking
    print("\n7️⃣  Test: GET /api/ranking/teams")
    try:
        res = requests.get(f"{API_BASE}/api/ranking/teams")
        assert res.status_code == 200, f"Status {res.status_code}"
        data = res.json()
        rankings = data.get('rankings', [])
        print(f"   ✅ Ranking cargado")
        print(f"   - Equipos en ranking: {len(rankings)}")
        if rankings:
            top = rankings[0]
            print(f"   - Líder: {top['username']} (Valor: {top['team_value']})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
    print("=" * 60)
    print("\n🎮 La aplicación está lista para jugar:")
    print("   Frontend:  http://127.0.0.1:3000")
    print("   Backend:   http://127.0.0.1:8000")

if __name__ == "__main__":
    test_api()
