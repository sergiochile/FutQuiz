// ============================================================
//  El Crack Quiz — Sistema de Internacionalización (i18n)
//  Idiomas: es (Español), en (English)
// ============================================================

const TRANSLATIONS = {

  // ─────────────────────────────────────────────
  // ESPAÑOL (base)
  // ─────────────────────────────────────────────
  es: {
    // Auth
    auth_subtitle:        'Juega y desbloquea jugadores',
    auth_tab_login:       'Entrar',
    auth_tab_register:    'Crear Cuenta',
    auth_label_email:     'Email',
    auth_label_password:  'Contraseña',
    auth_label_username:  'Usuario',
    auth_ph_email:        'tu@email.com',
    auth_ph_password:     '••••••••',
    auth_ph_username:     'tu_usuario',
    auth_btn_login:       'Entrar',
    auth_btn_register:    'Crear Cuenta',

    // Top bar
    topbar_logout:        'Salir',

    // Menú principal
    menu_title:           'El Crack Quiz',
    menu_ready:           '¡Listo para jugar?',
    menu_btn_quiz:        '🎮 Jugar Quiz',
    menu_btn_xi:          '📝 Completa el XI',
    menu_btn_team:        '⚽ Mi Equipo',
    menu_btn_catalog:     '📸 Catálogo',
    menu_btn_ranking:     '🏆 Ranking',

    // Selector de modo
    mode_title:           'Elige el Modo',
    mode_subtitle:        '¿Cómo quieres jugar?',
    mode_back:            '← Menú',

    mode_classic_fast_name: 'Clásico Rápido',
    mode_classic_fast_desc: '10 preguntas, 3 vidas, dificultad progresiva',
    mode_classic_normal_name: 'Clásico Normal',
    mode_classic_normal_desc: '20 preguntas, 3 vidas, dificultad progresiva',
    mode_classic_full_name: 'Clásico Completo',
    mode_classic_full_desc: '30 preguntas, 3 vidas, dificultad progresiva',
    mode_speed_name:      'Velocidad',
    mode_speed_desc:      'Responde todo lo que puedas antes de que acabe el tiempo',
    mode_levelup_name:    'Subir de Nivel',
    mode_levelup_desc:    'Las preguntas se vuelven cada vez más difíciles',

    tag_10q:              '10 preguntas',
    tag_20q:              '20 preguntas',
    tag_30q:              '30 preguntas',
    tag_3lives:           '3 vidas',
    tag_6levels:          '6 niveles',
    tag_nolimit:          'Sin límite',
    tag_nolives:          'Sin vidas',
    tag_speed:            'Contrarreloj',
    tag_growing:          'Dificultad creciente',

    // Quiz
    quiz_loading:         'Cargando pregunta...',
    quiz_abandon:         'Abandonar',
    quiz_abandon_confirm: '¿Seguro que quieres abandonar la partida? Perderás el progreso.',
    quiz_next:            'Siguiente →',
    quiz_see_results:     '🏆 Ver Resultados',
    quiz_correct:         '¡Correcto!',
    quiz_answer:          'Respuesta: ',
    quiz_streak:          '🔥 Racha x',

    // Resultados
    results_points:       'PUNTOS',
    results_accuracy:     'PRECISIÓN',
    results_correct:      'CORRECTAS',
    results_streak:       'RACHA MÁX.',
    results_new_player:   '🎉 ¡Nuevo Jugador Desbloqueado!',
    results_play_again:   '🎮 Jugar de Nuevo',
    results_menu:         '← Menú',

    // Equipo
    team_back:            '← Menú',
    team_title:           '⚽ Mi Equipo',
    team_subtitle:        'Toca una posición para cambiar el jugador',
    team_value:           'Valor del equipo',
    team_save:            '💾 Guardar Equipo',
    team_saved_ok:        '✅ Equipo guardado correctamente',
    team_save_error:      'Error al guardar el equipo',
    team_conn_error:      'Error de conexión al guardar equipo',
    modal_title_default:  'Elige un jugador',
    modal_pick_for:       'Elige jugador para ',
    modal_remove:         'Quitar jugador',
    modal_empty:          'Aún no tienes jugadores desbloqueados. ¡Juega para desbloquear!',

    // Catálogo
    catalog_back:         '← Menú',
    catalog_title:        '📸 Catálogo',
    catalog_loading:      'Cargando...',
    catalog_unlocked_of:  'desbloqueados',
    filter_all:           'Todos',
    filter_unlocked:      'Desbloqueados',

    // Ranking
    ranking_back:         '← Menú',
    ranking_title:        '🏆 Ranking Global',
    ranking_tab_scores:   'Puntuaciones',
    ranking_tab_teams:    'Equipos',
    ranking_loading:      'Cargando...',
    ranking_empty:        'Sin datos aún. ¡Sé el primero!',
    ranking_error:        'Error al cargar el ranking',
    ranking_pts:          'pts',
    ranking_val:          'val.',
    ranking_accuracy:     '% precisión',
    ranking_starters:     'titulares',

    // XI
    xi_back:              '← Menú',
    xi_title:             '📝 Completa el XI',
    xi_subtitle:          'Adivina los jugadores que faltan en el equipo',
    xi_random:            '🎲 Equipo aleatorio',
    xi_timer_label:       '⏱ ',
    xi_time_up:           '⏰ ¡Tiempo!',
    xi_verify:            '✅ Verificar respuestas',
    xi_next:              '⏭ Siguiente',
    xi_hidden_count:      'a adivinar',
    xi_input_title:       '¿Quién ocupa el ',
    xi_input_hint:        'Escribe el apellido del jugador',
    xi_input_ph:          'Escribe el apellido...',
    xi_input_cancel:      'Cancelar',
    xi_input_confirm:     'Confirmar',
    xi_no_answer:         '¡Escribe al menos una respuesta! Toca los slots con ❓ para responder.',
    xi_verify_time:       'Se acabó el tiempo, verificando...',
    xi_verifying:         'Verificando...',
    xi_conn_error:        'Error de conexión',
    xi_time_msg:          ' · ⏰ ¡Tiempo agotado!',
    xi_correct_pct:       '% de acierto',
    xi_line_por:          'Portero',
    xi_line_def:          'Defensa',
    xi_line_med:          'Mediocampo',
    xi_line_del:          'Delantera',
    xi_curiosity_label:   '💡 ¿Sabías que…?',
    xi_pts:               'pts',
    xi_of:                '/',
    xi_corrects:          ' correctos — ',

    // General
    loading_default:      'Cargando...',
    loading_login:        'Iniciando sesión...',
    loading_register:     'Creando cuenta...',
    loading_game:         'Preparando partida...',
    loading_results:      'Calculando resultados...',
    loading_team:         'Cargando equipo...',
    loading_saving:       'Guardando equipo...',
    error_credentials:    'Credenciales incorrectas',
    error_create_account: 'No se pudo crear la cuenta',
    error_connection:     'Error de conexión con el servidor',
    error_start_game:     'No se pudo iniciar la partida',
    error_server:         'Error de conexión. ¿Está el servidor corriendo?',
    error_results:        'Error al obtener resultados',
    logout_confirm:       '¿Cerrar sesión?',
    hello:                '¡Hola, ',
    hello_suffix:         '!',
  },

  // ─────────────────────────────────────────────
  // ENGLISH
  // ─────────────────────────────────────────────
  en: {
    // Auth
    auth_subtitle:        'Play and unlock players',
    auth_tab_login:       'Sign In',
    auth_tab_register:    'Create Account',
    auth_label_email:     'Email',
    auth_label_password:  'Password',
    auth_label_username:  'Username',
    auth_ph_email:        'you@email.com',
    auth_ph_password:     '••••••••',
    auth_ph_username:     'your_username',
    auth_btn_login:       'Sign In',
    auth_btn_register:    'Create Account',

    // Top bar
    topbar_logout:        'Log Out',

    // Main menu
    menu_title:           'El Crack Quiz',
    menu_ready:           'Ready to play?',
    menu_btn_quiz:        '🎮 Play Quiz',
    menu_btn_xi:          '📝 Complete the XI',
    menu_btn_team:        '⚽ My Team',
    menu_btn_catalog:     '📸 Catalog',
    menu_btn_ranking:     '🏆 Ranking',

    // Mode selector
    mode_title:           'Choose Mode',
    mode_subtitle:        'How do you want to play?',
    mode_back:            '← Menu',

    mode_classic_fast_name: 'Quick Classic',
    mode_classic_fast_desc: '10 questions, 3 lives, progressive difficulty',
    mode_classic_normal_name: 'Normal Classic',
    mode_classic_normal_desc: '20 questions, 3 lives, progressive difficulty',
    mode_classic_full_name: 'Full Classic',
    mode_classic_full_desc: '30 questions, 3 lives, progressive difficulty',
    mode_speed_name:      'Speed',
    mode_speed_desc:      'Answer as many as you can before time runs out',
    mode_levelup_name:    'Level Up',
    mode_levelup_desc:    'Questions get harder and harder',

    tag_10q:              '10 questions',
    tag_20q:              '20 questions',
    tag_30q:              '30 questions',
    tag_3lives:           '3 lives',
    tag_6levels:          '6 levels',
    tag_nolimit:          'No limit',
    tag_nolives:          'No lives',
    tag_speed:            'Against the clock',
    tag_growing:          'Growing difficulty',

    // Quiz
    quiz_loading:         'Loading question...',
    quiz_abandon:         'Abandon',
    quiz_abandon_confirm: 'Are you sure you want to quit? You will lose your progress.',
    quiz_next:            'Next →',
    quiz_see_results:     '🏆 See Results',
    quiz_correct:         'Correct!',
    quiz_answer:          'Answer: ',
    quiz_streak:          '🔥 Streak x',

    // Results
    results_points:       'POINTS',
    results_accuracy:     'ACCURACY',
    results_correct:      'CORRECT',
    results_streak:       'MAX STREAK',
    results_new_player:   '🎉 New Player Unlocked!',
    results_play_again:   '🎮 Play Again',
    results_menu:         '← Menu',

    // Team
    team_back:            '← Menu',
    team_title:           '⚽ My Team',
    team_subtitle:        'Tap a position to change the player',
    team_value:           'Team value',
    team_save:            '💾 Save Team',
    team_saved_ok:        '✅ Team saved successfully',
    team_save_error:      'Error saving the team',
    team_conn_error:      'Connection error while saving team',
    modal_title_default:  'Choose a player',
    modal_pick_for:       'Pick player for ',
    modal_remove:         'Remove player',
    modal_empty:          'You have no unlocked players yet. Play to unlock them!',

    // Catalog
    catalog_back:         '← Menu',
    catalog_title:        '📸 Catalog',
    catalog_loading:      'Loading...',
    catalog_unlocked_of:  'unlocked',
    filter_all:           'All',
    filter_unlocked:      'Unlocked',

    // Ranking
    ranking_back:         '← Menu',
    ranking_title:        '🏆 Global Ranking',
    ranking_tab_scores:   'Scores',
    ranking_tab_teams:    'Teams',
    ranking_loading:      'Loading...',
    ranking_empty:        'No data yet. Be the first!',
    ranking_error:        'Error loading ranking',
    ranking_pts:          'pts',
    ranking_val:          'val.',
    ranking_accuracy:     '% accuracy',
    ranking_starters:     'starters',

    // XI
    xi_back:              '← Menu',
    xi_title:             '📝 Complete the XI',
    xi_subtitle:          'Guess the missing players in the team',
    xi_random:            '🎲 Random team',
    xi_timer_label:       '⏱ ',
    xi_time_up:           '⏰ Time\'s up!',
    xi_verify:            '✅ Check answers',
    xi_next:              '⏭ Next',
    xi_hidden_count:      'to guess',
    xi_input_title:       'Who plays at ',
    xi_input_hint:        'Write the player\'s last name',
    xi_input_ph:          'Type the surname...',
    xi_input_cancel:      'Cancel',
    xi_input_confirm:     'Confirm',
    xi_no_answer:         'Write at least one answer! Tap the ❓ slots to answer.',
    xi_verify_time:       'Time\'s up, checking...',
    xi_verifying:         'Checking...',
    xi_conn_error:        'Connection error',
    xi_time_msg:          ' · ⏰ Time\'s up!',
    xi_correct_pct:       '% accuracy',
    xi_line_por:          'Goalkeeper',
    xi_line_def:          'Defense',
    xi_line_med:          'Midfield',
    xi_line_del:          'Attack',
    xi_curiosity_label:   '💡 Did you know…?',
    xi_pts:               'pts',
    xi_of:                '/',
    xi_corrects:          ' correct — ',

    // General
    loading_default:      'Loading...',
    loading_login:        'Signing in...',
    loading_register:     'Creating account...',
    loading_game:         'Preparing game...',
    loading_results:      'Calculating results...',
    loading_team:         'Loading team...',
    loading_saving:       'Saving team...',
    error_credentials:    'Wrong credentials',
    error_create_account: 'Could not create account',
    error_connection:     'Connection error with server',
    error_start_game:     'Could not start the game',
    error_server:         'Connection error. Is the server running?',
    error_results:        'Error getting results',
    logout_confirm:       'Log out?',
    hello:                'Hello, ',
    hello_suffix:         '!',
  },

};


// ─────────────────────────────────────────────────────────────
//  Motor i18n — expuesto globalmente
// ─────────────────────────────────────────────────────────────

let currentLang = 'es';

/** Devuelve el texto traducido para la clave dada */
function T(key) {
  const lang = TRANSLATIONS[currentLang] || TRANSLATIONS['es'];
  return lang[key] !== undefined ? lang[key] : (TRANSLATIONS['es'][key] || key);
}

/**
 * Cambia el idioma activo, actualiza el DOM (elementos con data-i18n)
 * y guarda la preferencia en localStorage.
 */
function setLanguage(lang) {
  if (!TRANSLATIONS[lang]) return;
  currentLang = lang;
  localStorage.setItem('lang', lang);

  // Actualizar todos los elementos estáticos con data-i18n
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const attr = el.getAttribute('data-i18n-attr'); // p.ej. "placeholder"
    const translated = T(key);
    if (attr) {
      el.setAttribute(attr, translated);
    } else {
      el.textContent = translated;
    }
  });

  // Actualizar placeholders marcados con data-i18n-ph
  document.querySelectorAll('[data-i18n-ph]').forEach(el => {
    el.placeholder = T(el.getAttribute('data-i18n-ph'));
  });

  // Marcar botón activo en el selector de idioma
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });

  // Disparar evento para que el JS del juego pueda reaccionar
  document.dispatchEvent(new CustomEvent('langchange', { detail: { lang } }));
}

/** Inicializa el idioma desde localStorage, FB locale, o navegador */
function initLanguage() {
  // 1. Preferencia guardada
  const saved = localStorage.getItem('lang');
  if (saved && TRANSLATIONS[saved]) { setLanguage(saved); return; }

  // 2. Locale de Facebook Instant Games
  if (typeof FBInstant !== 'undefined') {
    try {
      const fbLocale = FBInstant.getLocale(); // p.ej. "fr_FR", "pt_BR", "en_US"
      const fbLang   = fbLocale ? fbLocale.substring(0, 2).toLowerCase() : null;
      if (fbLang && TRANSLATIONS[fbLang]) { setLanguage(fbLang); return; }
    } catch (_) {}
  }

  // 3. Idioma del navegador
  const navLang = (navigator.language || navigator.userLanguage || 'es').substring(0, 2).toLowerCase();
  setLanguage(TRANSLATIONS[navLang] ? navLang : 'es');
}
