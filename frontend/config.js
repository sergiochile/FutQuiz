/**
 * FutQuiz - Configuración de la Aplicación
 *
 * En Render: el backend sirve el frontend directamente,
 * la API URL es siempre relativa (/api). No hay que cambiar nada.
 */

(function() {
    // Detecta automáticamente si es Render/producción o local
    const isLocal = window.location.hostname === 'localhost'
                 || window.location.hostname === '127.0.0.1'
                 || window.location.protocol === 'file:';

    const LOCAL_API_URL      = 'http://127.0.0.1:8000/api';
    const PRODUCTION_API_URL = '/api';  // Relativo — funciona en Render automáticamente

    window.GAME_CONFIG = {
        apiUrl:       isLocal ? LOCAL_API_URL : PRODUCTION_API_URL,
        isProduction: !isLocal,
        version:      '1.0.0',
        gameName:     'FutQuiz',
        fbAppId:      '757919567386850',
    };

    console.log('[FutQuiz] API URL:', window.GAME_CONFIG.apiUrl);
})();
