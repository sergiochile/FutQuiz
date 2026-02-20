#!/bin/bash
# Script de inicio para El Crack Quiz
cd /Users/sergecchile./Desktop/Futquiz

# Matar cualquier proceso anterior en puerto 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Activar entorno virtual
source venv/bin/activate

echo "🚀 Iniciando El Crack Quiz en http://127.0.0.1:8000"
echo "   Presiona Ctrl+C para detener"
echo ""

# SIN --reload: las sesiones de juego se mantienen en memoria
uvicorn backend.main:app \
    --host 127.0.0.1 \
    --port 8000
