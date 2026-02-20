#!/usr/bin/env python3
"""
TEST SUITE - SISTEMA DE VERIFICACIÓN
Pruebas para validar todos los componentes de verificación
"""

import requests
import json
from datetime import datetime

API_BASE = 'http://127.0.0.1:8000'

def test_header(test_num, test_name):
    print(f"\n{'='*60}")
    print(f"🧪 TEST {test_num}: {test_name}")
    print('='*60)

def test_pass(message):
    print(f"   ✅ {message}")

def test_fail(message):
    print(f"   ❌ {message}")

def test_warning(message):
    print(f"   ⚠️  {message}")

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: VERIFY SESSION
# ═══════════════════════════════════════════════════════════════════════════════
def test_verify_session():
    test_header(1, "Verificación de Sesión")
    
    # Primero crear una sesión de juego
    response = requests.post(
        f"{API_BASE}/api/game/start",
        json={
            "player_name": "TestVerification",
            "mode": "classic",
            "category": "todos"
        }
    )
    
    if response.status_code != 200:
        test_fail("No se pudo crear sesión de juego")
        return False
    
    session_id = response.json()["session_id"]
    test_pass(f"Sesión creada: {session_id}")
    
    # Ahora verificar la sesión
    response = requests.get(f"{API_BASE}/api/verify/session/{session_id}")
    
    if response.status_code != 200:
        test_fail("Error al verificar sesión")
        return False
    
    data = response.json()
    
    if not data["verified"]:
        test_fail(f"Sesión no verificada: {data['status']}")
        return False
    
    test_pass(f"Sesión verificada correctamente")
    test_pass(f"  ID: {data['session_id']}")
    test_pass(f"  Activa: {data['is_active']}")
    
    return True

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: VERIFY USER
# ═══════════════════════════════════════════════════════════════════════════════
def test_verify_user():
    test_header(2, "Verificación de Usuario")
    
    test_cases = [
        ("ValidUser", True),
        ("A", False),  # Muy corto
        ("UserName123", True),
        ("Invalid@User", False),  # Carácter no permitido
    ]
    
    for username, should_be_valid in test_cases:
        response = requests.get(f"{API_BASE}/api/verify/user/{username}")
        data = response.json()
        
        if data["valid"] == should_be_valid:
            test_pass(f"Usuario '{username}': {data['status']}")
        else:
            test_fail(f"Usuario '{username}': validación incorrecta")
    
    return True

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: VERIFY ANSWER
# ═══════════════════════════════════════════════════════════════════════════════
def test_verify_answer():
    test_header(3, "Verificación de Respuesta")
    
    test_cases = [
        (1, "Messi", "Messi", True),
        (2, "Ronaldo", "Messi", False),
        (3, "Manchester United", "Manchester United", True),
    ]
    
    for q_id, selected, correct, should_be_correct in test_cases:
        response = requests.post(
            f"{API_BASE}/api/verify/answer",
            json={
                "question_id": q_id,
                "selected_option": selected,
                "correct_option": correct,
                "time_taken": 3.5
            }
        )
        
        data = response.json()
        
        if data["correct"] == should_be_correct:
            test_pass(f"Pregunta {q_id}: {data['status']}")
        else:
            test_fail(f"Pregunta {q_id}: resultado incorrecto")
    
    return True

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 4: VERIFY SCORE
# ═══════════════════════════════════════════════════════════════════════════════
def test_verify_score():
    test_header(4, "Verificación de Puntuación")
    
    test_cases = [
        (2500, 20, 30, True),   # 80% - válido
        (5000, 30, 30, True),   # 100% - válido
        (0, 0, 30, True),       # 0% - válido
        (100000, 30, 30, False),  # Score imposible - inválido
    ]
    
    for score, correct, total, should_be_valid in test_cases:
        response = requests.post(
            f"{API_BASE}/api/verify/score",
            json={
                "score": score,
                "correct": correct,
                "total": total
            }
        )
        
        data = response.json()
        
        if data["valid"] == should_be_valid:
            accuracy = (correct / total * 100) if total > 0 else 0
            test_pass(f"Score {score} ({accuracy:.1f}%): {data['status']}")
        else:
            test_fail(f"Score {score}: validación incorrecta")
    
    return True

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 5: CHEAT DETECTION
# ═══════════════════════════════════════════════════════════════════════════════
def test_cheat_detection():
    test_header(5, "Detección de Trampa")
    
    # Caso 1: Respuestas normales (sin trampa)
    normal_answers = [
        {"question_id": i, "correct": True, "time_taken": 4.5}
        for i in range(10)
    ]
    
    response = requests.post(
        f"{API_BASE}/api/verify/cheat-detection",
        json={
            "session_id": "test_session_normal",
            "answers": normal_answers
        }
    )
    
    data = response.json()
    
    if not data["cheating_detected"]:
        test_pass("Respuestas normales: Sin trampa detectada")
    else:
        test_warning(f"Respuestas normales: {data['status']}")
    
    # Caso 2: Respuestas sospechosas (100% correctas muy rápido)
    suspicious_answers = [
        {"question_id": i, "correct": True, "time_taken": 0.8}
        for i in range(10)
    ]
    
    response = requests.post(
        f"{API_BASE}/api/verify/cheat-detection",
        json={
            "session_id": "test_session_suspicious",
            "answers": suspicious_answers
        }
    )
    
    data = response.json()
    
    if data["cheating_detected"]:
        test_pass(f"Respuestas sospechosas: Trampa detectada - {data['status']}")
    else:
        test_fail("Respuestas sospechosas: No se detectó trampa")
    
    return True

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 6: SESSION STATS
# ═══════════════════════════════════════════════════════════════════════════════
def test_session_stats():
    test_header(6, "Estadísticas de Sesión")
    
    # Crear sesión
    response = requests.post(
        f"{API_BASE}/api/game/start",
        json={
            "player_name": "TestStats",
            "mode": "speed",
            "category": "mundiales"
        }
    )
    
    session_id = response.json()["session_id"]
    
    # Responder una pregunta
    response = requests.post(
        f"{API_BASE}/api/game/{session_id}/answer",
        json={
            "question_id": 1,
            "selected_option": "Test",
            "time_taken": 3.5
        }
    )
    
    # Obtener estadísticas
    response = requests.get(f"{API_BASE}/api/verify/session-stats/{session_id}")
    
    if response.status_code == 200:
        data = response.json()
        test_pass(f"Estadísticas obtenidas")
        test_pass(f"  Username: {data.get('username', 'N/A')}")
        test_pass(f"  Mode: {data.get('mode', 'N/A')}")
        test_pass(f"  Accuracy: {data.get('accuracy_percent', 0):.1f}%")
        test_pass(f"  Duration: {data.get('duration_seconds', 0):.1f}s")
    else:
        test_fail("No se pudieron obtener estadísticas")
        return False
    
    return True

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 7: SYSTEM HEALTH
# ═══════════════════════════════════════════════════════════════════════════════
def test_system_health():
    test_header(7, "Salud del Sistema de Verificación")
    
    response = requests.get(f"{API_BASE}/api/verify/system-health")
    
    if response.status_code != 200:
        test_fail("No se pudo obtener salud del sistema")
        return False
    
    data = response.json()
    
    test_pass(f"Status: {data['status']}")
    test_pass(f"Sesiones activas: {data['active_sessions']}")
    test_pass(f"Timeout de sesión: {data['session_timeout_minutes']} minutos")
    
    # Verificar componentes
    all_ok = True
    for component, status in data.get("components", {}).items():
        if "OK" in status:
            test_pass(f"  {component}: {status}")
        else:
            test_fail(f"  {component}: {status}")
            all_ok = False
    
    return all_ok

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print(f"\n{'='*60}")
    print("🔐 TEST SUITE - SISTEMA DE VERIFICACIÓN")
    print(f"{'='*60}")
    print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}")
    print(f"API Base: {API_BASE}")
    
    tests = [
        ("Verificación de Sesión", test_verify_session),
        ("Verificación de Usuario", test_verify_user),
        ("Verificación de Respuesta", test_verify_answer),
        ("Verificación de Puntuación", test_verify_score),
        ("Detección de Trampa", test_cheat_detection),
        ("Estadísticas de Sesión", test_session_stats),
        ("Salud del Sistema", test_system_health),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASS" if result else "FAIL"))
        except Exception as e:
            test_fail(f"Excepción: {str(e)}")
            results.append((test_name, "ERROR"))
    
    # Resumen
    print(f"\n{'='*60}")
    print("📊 RESUMEN DE TESTS")
    print('='*60)
    
    passed = sum(1 for _, result in results if result == "PASS")
    total = len(results)
    
    for test_name, result in results:
        emoji = "✅" if result == "PASS" else "❌" if result == "FAIL" else "⚠️"
        print(f"{emoji} {test_name}: {result}")
    
    print(f"\n{'='*60}")
    print(f"RESULTADO FINAL: {passed}/{total} tests pasaron ({passed*100//total}%)")
    print('='*60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
