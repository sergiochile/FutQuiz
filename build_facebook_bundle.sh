#!/bin/bash
# ============================================================
# El Crack Quiz - Build Bundle para Facebook Instant Games
#
# USO:
#   bash build_facebook_bundle.sh
#
# Genera: facebook-bundle.zip (listo para subir a Facebook)
# ============================================================

set -e

echo "=============================================="
echo "  El Crack Quiz - Build para Facebook Games"
echo "=============================================="

BUNDLE_DIR="facebook-bundle"
ZIP_NAME="facebook-bundle.zip"

# Limpiar bundle anterior
rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR"

echo ""
echo "▶ Copiando archivos del frontend..."
cp frontend/index.html "$BUNDLE_DIR/index.html"
cp frontend/config.js  "$BUNDLE_DIR/config.js"
cp frontend/translations.js "$BUNDLE_DIR/translations.js"
echo "  ✔ translations.js copiado (i18n: es/en)"

# Copiar imágenes/assets si existen
if [ -d "frontend/assets" ]; then
    cp -r frontend/assets "$BUNDLE_DIR/assets"
    echo "  ✔ Assets copiados"
fi
if [ -d "frontend/images" ]; then
    cp -r frontend/images "$BUNDLE_DIR/images"
    echo "  ✔ Imágenes copiadas"
fi
if [ -f "frontend/favicon.ico" ]; then
    cp frontend/favicon.ico "$BUNDLE_DIR/favicon.ico"
fi

echo ""
echo "▶ Verificando config.js para producción..."
if grep -q "IS_PRODUCTION = false" "$BUNDLE_DIR/config.js"; then
    echo ""
    echo "  ⚠️  ADVERTENCIA: IS_PRODUCTION = false en config.js"
    echo "     Edita frontend/config.js antes de subir a Facebook:"
    echo "     1. Pon IS_PRODUCTION = true"
    echo "     2. Pon tu URL de Railway en PRODUCTION_API_URL"
    echo "     3. Pon tu Facebook App ID en fbAppId"
    echo ""
fi

echo "▶ Creando ZIP..."
rm -f "$ZIP_NAME"

# Usar Python si zip no está disponible
if command -v zip &> /dev/null; then
    cd "$BUNDLE_DIR" && zip -r "../$ZIP_NAME" . && cd ..
else
    python3 -c "
import zipfile, os
with zipfile.ZipFile('$ZIP_NAME', 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk('$BUNDLE_DIR'):
        for file in files:
            filepath = os.path.join(root, file)
            arcname = os.path.relpath(filepath, '$BUNDLE_DIR')
            zf.write(filepath, arcname)
print('ZIP creado con Python')
"
fi

echo ""
echo "✅ Bundle creado exitosamente: $ZIP_NAME"
echo ""
echo "Contenido del bundle:"
ls -la "$BUNDLE_DIR/"
echo ""
echo "Tamaño del ZIP:"
ls -lh "$ZIP_NAME"
echo ""
echo "=============================================="
echo "  PRÓXIMOS PASOS:"
echo "=============================================="
echo ""
echo "  1. Sube el backend a Railway:"
echo "     → Crea cuenta en https://railway.app"
echo "     → Conecta tu repo de GitHub"
echo "     → Railway detectará el Procfile automáticamente"
echo ""
echo "  2. Configura la URL en config.js:"
echo "     → Edita frontend/config.js"
echo "     → Pon IS_PRODUCTION = true"
echo "     → Pon tu URL de Railway en PRODUCTION_API_URL"
echo ""
echo "  3. Vuelve a ejecutar este script para regenerar el ZIP"
echo ""
echo "  4. Sube $ZIP_NAME a Facebook Instant Games:"
echo "     → https://developers.facebook.com/apps"
echo "     → Crea App → Tipo: Instant Games"
echo "     → Sube el ZIP en: Instant Games → Web Hosting"
echo ""
