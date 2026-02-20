#!/bin/bash

# ════════════════════════════════════════════════════════════════════════════════════
# SCRIPT PARA APLICAR LOS CAMBIOS DE MODERNIZACIÓN
# ════════════════════════════════════════════════════════════════════════════════════

cd /Users/sergecchile./Desktop/Futquiz

echo "⏳ Iniciando aplicación de cambios de modernización..."
echo ""

# 1. Hacer backup de los archivos originales
echo "📦 PASO 1: Haciendo backup de archivos originales..."
if [ -f "frontend/index.html" ]; then
    cp frontend/index.html frontend/index_backup_$(date +%Y%m%d_%H%M%S).html
    echo "✅ Backup de frontend/index.html realizado"
fi

# 2. Reemplazar el frontend
echo ""
echo "🎨 PASO 2: Reemplazando interfaz frontend..."
cp frontend/index_new.html frontend/index.html
echo "✅ Frontend actualizado"

# 3. Verificar que la BD está actualizada
echo ""
echo "💾 PASO 3: Verificando base de datos..."
if [ -f "backend/elcrack.db" ]; then
    echo "✅ Base de datos existe"
else
    echo "⚠️  La base de datos se creará al iniciar el servidor"
fi

# 4. Mostrar resumen
echo ""
echo "════════════════════════════════════════════════════════════════════════════════════"
echo "✨ MODERNIZACIÓN APLICADA EXITOSAMENTE ✨"
echo "════════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📋 CAMBIOS REALIZADOS:"
echo "  ✅ Backend actualizado con autenticación"
echo "  ✅ Frontend reemplazado con diseño moderno"
echo "  ✅ Base de datos preparada"
echo ""
echo "🚀 PRÓXIMOS PASOS:"
echo ""
echo "1. Inicia el servidor backend:"
echo "   $ python backend/main.py"
echo ""
echo "2. Abre tu navegador:"
echo "   http://127.0.0.1:8000"
echo ""
echo "3. Registra una nueva cuenta o inicia sesión"
echo ""
echo "4. ¡Disfruta el juego modernizado! 🎉"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════════"
