#!/bin/bash

# 🎯 INICIO RÁPIDO - EL CRACK QUIZ
# Este script inicia todos los servicios necesarios

echo "⚽ Iniciando El Crack Quiz..."
echo "================================"

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Ejecuta este script desde /Users/sergecchile./Desktop/Futquiz"
    exit 1
fi

echo ""
echo "📦 Verificando dependencias..."
python3 -c "import fastapi" 2>/dev/null || {
    echo "📥 Instalando dependencias..."
    pip3 install -r requirements.txt
}

echo ""
echo "🎮 Iniciando servicios..."
echo ""

# Abrir terminal 1 con backend
osascript <<EOF &
tell application "Terminal"
    do script "cd /Users/sergecchile./Desktop/Futquiz && echo '⚙️ Backend iniciando...' && python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
end tell
EOF

sleep 2

# Abrir terminal 2 con frontend
osascript <<EOF &
tell application "Terminal"
    do script "cd /Users/sergecchile./Desktop/Futquiz/frontend && echo '🌐 Frontend iniciando...' && python3 -m http.server 3000"
end tell
EOF

sleep 3

echo ""
echo "✅ Servicios iniciados"
echo ""
echo "📱 Abriendo navegador..."
sleep 2

# Abrir en navegador
open "http://127.0.0.1:3000"

echo ""
echo "================================"
echo "✅ ¡El Crack Quiz está LISTO!"
echo "================================"
echo ""
echo "🎮 Accede a: http://127.0.0.1:3000"
echo "⚙️  Backend en: http://127.0.0.1:8000"
echo "📊 API docs: http://127.0.0.1:8000/docs"
echo ""
echo "Para detener los servicios:"
echo "1. Escribe 'exit' en cada terminal"
echo "2. O ejecuta: pkill -f 'uvicorn|http.server'"
echo ""
