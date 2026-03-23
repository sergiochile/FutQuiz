/**
 * FutQuiz - Configuración de la Aplicación
 *
 * Frontend en Netlify + Backend en Render.
 * En local apunta a localhost, en producción a la URL de Render.
 */

(function() {
    const isLocal = window.location.hostname === 'localhost'
                 || window.location.hostname === '127.0.0.1'
                 || window.location.protocol === 'file:';

    const LOCAL_API_URL      = 'http://127.0.0.1:8000/api';
    const PRODUCTION_API_URL = 'https://futquiz.onrender.com/api';

    window.GAME_CONFIG = {
        apiUrl:       isLocal ? LOCAL_API_URL : PRODUCTION_API_URL,
        isProduction: !isLocal,
        version:      '1.0.0',
        gameName:     'FutQuiz',
        fbAppId:      '757919567386850',
    };

    console.log('[FutQuiz] API URL:', window.GAME_CONFIG.apiUrl);
})();
