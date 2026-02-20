#!/bin/bash

# 🔧 REPARACIÓN PROFESIONAL — EL CRACK QUIZ
# Este script repara y configura todo el sistema para funcionamiento óptimo

set -e  # Exit on error

clear

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                   ⚙️  REPARACIÓN PROFESIONAL                       ║"
echo "║                      EL CRACK QUIZ v1.0                           ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# 1. VERIFICAR PYTHON
echo "📦 Verificando Python..."
python3 --version

# 2. INSTALAR DEPENDENCIAS
echo ""
echo "📥 Instalando dependencias..."
pip3 install -q fastapi uvicorn pydantic 2>/dev/null || pip install -q fastapi uvicorn pydantic

# 3. LIMPIAR BD ANTERIOR
echo ""
echo "🗑️  Limpiando base de datos anterior..."
rm -f futquiz.db
echo "✅ Base de datos limpiada"

# 4. CREAR DIRECTORIO TEMPORAL PARA SERVIDORES
echo ""
echo "🚀 Iniciando servidores (en background)..."
echo ""

# Matar procesos anteriores
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "http.server" 2>/dev/null || true
sleep 1

# Iniciar backend en background
echo "⚙️  Iniciando backend en puerto 8000..."
nohup python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend iniciado (PID: $BACKEND_PID)"

# Esperar a que el backend esté listo
sleep 3

# Verificar que backend está corriendo
if curl -s http://127.0.0.1:8000/api/info > /dev/null 2>&1; then
    echo "✅ Backend respondiendo correctamente"
else
    echo "❌ El backend no responde. Revisa /tmp/backend.log"
    cat /tmp/backend.log
    exit 1
fi

# Iniciar frontend en background
echo ""
echo "🌐 Iniciando frontend en puerto 3000..."
cd frontend
nohup python3 -m http.server 3000 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "✅ Frontend iniciado (PID: $FRONTEND_PID)"

# Esperar a que frontend esté listo
sleep 2

# Verificar que frontend está corriendo
if curl -s http://127.0.0.1:3000 > /dev/null 2>&1; then
    echo "✅ Frontend respondiendo correctamente"
else
    echo "❌ El frontend no responde. Revisa /tmp/frontend.log"
    cat /tmp/frontend.log
    exit 1
fi

# 5. EJECUTAR TESTS
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 EJECUTANDO TESTS..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 test_api.py

TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
    echo ""
    echo "✅ TODOS LOS TESTS PASARON"
else
    echo ""
    echo "⚠️  Algunos tests fallaron. Revisa arriba."
fi

# 6. MOSTRAR INFORMACIÓN
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ SISTEMA LISTO                               ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

echo "🌐 ACCEDE A LA APLICACIÓN:"
echo ""
echo "   🎮 Frontend:  http://127.0.0.1:3000"
echo "   ⚙️  Backend:   http://127.0.0.1:8000"
echo "   📚 API Docs:  http://127.0.0.1:8000/docs"
echo ""

echo "📊 INFORMACIÓN DE PROCESOS:"
echo ""
echo "   Backend  PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""

echo "🛑 PARA DETENER LOS SERVICIOS:"
echo ""
echo "   Ejecuta: pkill -f 'uvicorn\\|http.server'"
echo "   O        kill $BACKEND_PID $FRONTEND_PID"
echo ""

echo "📋 LOGS EN TIEMPO REAL:"
echo ""
echo "   Backend:  tail -f /tmp/backend.log"
echo "   Frontend: tail -f /tmp/frontend.log"
echo ""

echo "🎯 PRÓXIMOS PASOS:"
echo ""
echo "   1. Abre el navegador: http://127.0.0.1:3000"
echo "   2. Ingresa tu nombre de usuario (o uno aleatorio)"
echo "   3. Selecciona un modo y categoría"
echo "   4. ¡Comienza a jugar!"
echo ""

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           🎊 ¡EL CRACK QUIZ ESTÁ LISTO PARA JUGAR! 🎊            ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Mantener vivo hasta que el usuario cierre
read -p "Presiona ENTER para continuar viendo logs (o Ctrl+C para salir)..." dummy
tail -f /tmp/backend.log
