/**
 * El Crack Quiz - Configuración de la Aplicación
 *
 * Para desarrollo local:  API_URL apunta a localhost
 * Para producción (Facebook Games): cambia API_URL al dominio de Railway/Render
 *
 * INSTRUCCIONES:
 * 1. Despliega el backend en Railway: https://railway.app
 * 2. Copia la URL que te da Railway (ej: https://futquiz-backend.railway.app)
 * 3. Reemplaza la línea PRODUCTION_API_URL con esa URL
 * 4. Cambia IS_PRODUCTION = true antes de subir a Facebook
 */

(function() {
    const IS_PRODUCTION = false; // <-- Cambiar a true antes de subir a Facebook

    const PRODUCTION_API_URL = 'https://TU-BACKEND.railway.app/api'; // <-- Tu URL de Railway aquí
    const LOCAL_API_URL      = window.location.protocol === 'file:'
        ? 'http://127.0.0.1:8000/api'
        : '/api';

    window.GAME_CONFIG = {
        apiUrl:        IS_PRODUCTION ? PRODUCTION_API_URL : LOCAL_API_URL,
        isProduction:  IS_PRODUCTION,
        version:       '1.0.0',
        gameName:      'El Crack Quiz',
        // Facebook App ID (obtenlo en developers.facebook.com)
        fbAppId:       '',
    };
})();
