#!/usr/bin/env python3
"""
🔧 DIAGNÓSTICO COMPLETO — EL CRACK QUIZ
Verifica todos los sistemas y genera reporte
"""

import sys
import json
import requests
from pathlib import Path

print("\n" + "="*70)
print("🔧 DIAGNÓSTICO DEL SISTEMA - EL CRACK QUIZ")
print("="*70 + "\n")

# 1. VERIFICAR ESTRUCTURA DE ARCHIVOS
print("📁 VERIFICANDO ESTRUCTURA DE ARCHIVOS...\n")
required_files = {
    "frontend/index.html": "Aplicación frontend",
    "backend/main.py": "API backend",
    "backend/quiz_engine.py": "Motor de juego",
    "backend/database.py": "Base de datos",
    "backend/data/questions.py": "Preguntas",
    "backend/data/players.py": "Jugadores",
}

missing = []
for file_path, desc in required_files.items():
    full_path = Path(file_path)
    if full_path.exists():
        size = full_path.stat().st_size
        print(f"✅ {file_path:40} ({size:,} bytes) - {desc}")
    else:
        print(f"❌ {file_path:40} FALTA")
        missing.append(file_path)

if missing:
    print(f"\n⚠️  Faltan {len(missing)} archivo(s)")
    sys.exit(1)

print("\n✅ Todos los archivos presentes")

# 2. VERIFICAR BACKEND API
print("\n" + "-"*70)
print("🌐 VERIFICANDO BACKEND API...\n")

API_BASE = "http://127.0.0.1:8000"
endpoints = [
    ("GET", "/api/info", {}),
    ("GET", "/api/players/catalog", {}),
    ("GET", "/api/ranking/teams", {}),
]

backend_ok = False
for method, endpoint, params in endpoints:
    try:
        if method == "GET":
            resp = requests.get(f"{API_BASE}{endpoint}", timeout=3)
        else:
            resp = requests.post(f"{API_BASE}{endpoint}", json=params, timeout=3)
        
        if resp.status_code == 200:
            print(f"✅ {method} {endpoint:30} → 200 OK")
            backend_ok = True
        else:
            print(f"⚠️  {method} {endpoint:30} → {resp.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint:30} → NO RESPONDE (¿está corriendo?)")
    except Exception as e:
        print(f"❌ {method} {endpoint:30} → ERROR: {e}")

if not backend_ok:
    print("\n⚠️  El backend no está respondiendo.")
    print("👉 Inicia el backend: python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000")

# 3. VERIFICAR FRONTEND
print("\n" + "-"*70)
print("🎨 VERIFICANDO FRONTEND...\n")

frontend_html = Path("frontend/index.html")
if frontend_html.exists():
    content = frontend_html.read_text()
    checks = {
        "startGame function": "async function startGame" in content,
        "renderQuestion function": "function renderQuestion" in content,
        "submitAnswer function": "function submitAnswer" in content,
        "endGame function": "function endGame" in content,
        "showResults function": "function showResults" in content,
        "Game state object": "const gameState" in content,
        "API_BASE variable": "const API_BASE" in content,
    }
    
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name:35} {'PRESENTE' if result else 'FALTA'}")

# 4. VERIFICAR BACKEND LÓGICA
print("\n" + "-"*70)
print("⚙️  VERIFICANDO LÓGICA DEL BACKEND...\n")

quiz_engine = Path("backend/quiz_engine.py")
if quiz_engine.exists():
    content = quiz_engine.read_text()
    checks = {
        "QuizEngine class": "class QuizEngine" in content,
        "start_session method": "def start_session" in content,
        "get_question method": "def get_question" in content,
        "check_answer method": "def check_answer" in content,
        "get_session method": "def get_session" in content,
    }
    
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name:35} {'IMPLEMENTADO' if result else 'FALTA'}")

# 5. VERIFICAR DATABASE
print("\n" + "-"*70)
print("💾 VERIFICANDO BASE DE DATOS...\n")

db_file = Path("futquiz.db")
if db_file.exists():
    print(f"✅ Base de datos existe ({db_file.stat().st_size:,} bytes)")
else:
    print("⚠️  Base de datos no existe (se crea al primer acceso)")

# 6. DATOS DE PREGUNTAS Y JUGADORES
print("\n" + "-"*70)
print("📊 VERIFICANDO DATOS...\n")

questions_file = Path("backend/data/questions.py")
if questions_file.exists():
    content = questions_file.read_text()
    # Contar preguntas
    q_count = content.count('"question":')
    print(f"✅ Preguntas encontradas: {q_count}")

players_file = Path("backend/data/players.py")
if players_file.exists():
    content = players_file.read_text()
    # Contar jugadores
    p_count = content.count('"name":')
    print(f"✅ Jugadores encontrados: {p_count}")

# 7. RESUMEN
print("\n" + "="*70)
print("📋 RESUMEN DEL DIAGNÓSTICO")
print("="*70 + "\n")

print("""
PRÓXIMOS PASOS:

1. Si el backend NO responde:
   Terminal 1: python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

2. Si el frontend NO responde:
   Terminal 2: cd frontend && python3 -m http.server 3000

3. Abre el navegador:
   http://127.0.0.1:3000

4. Ejecuta los tests:
   python3 test_api.py

Si aún hay problemas, ejecuta:
   python3 -c "import backend.main; print('✅ Backend importa correctamente')"
""")

print("="*70 + "\n")
