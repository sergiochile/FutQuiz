/**
 * FutQuiz - Configuración de la Aplicación
 *
 * ✅ RENDER: El backend sirve el frontend directamente,
 *    así que la API URL es siempre relativa (/api).
 *    No hace falta cambiar nada al desplegar en Render.
 *
 * Para Facebook Bundle (archivo .zip):
 *    Cambia PRODUCTION_API_URL a tu URL de Render.
 */

(function() {
    // true  → usa PRODUCTION_API_URL (para el bundle de Facebook)
    // false → usa /api relativo (perfecto para Render y desarrollo)
    const IS_PRODUCTION = false;

    // Solo necesaria para el bundle de Facebook (archivo zip independiente)
    // Cámbiala por tu URL de Render cuando la tengas:
    // ej: 'https://futquiz.onrender.com/api'
    const PRODUCTION_API_URL = 'https://futquiz.onrender.com/api';

    const LOCAL_API_URL = window.location.protocol === 'file:'
        ? 'http://127.0.0.1:8000/api'
        : '/api';

    window.GAME_CONFIG = {
        apiUrl:       IS_PRODUCTION ? PRODUCTION_API_URL : LOCAL_API_URL,
        isProduction: IS_PRODUCTION,
        version:      '1.0.0',
        gameName:     'FutQuiz',
        fbAppId:      '757919567386850',
    };
})();
