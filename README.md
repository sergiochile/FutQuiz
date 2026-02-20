# ⚽ El Crack — Quiz Futbolero

> Quiz de fútbol 1980–actualidad. Inspirado en los formatos de La Cobra, Davoo Xeneize y Ezzequiel.

---

## 📁 Estructura del Proyecto

```
elcrack/
├── backend/
│   ├── main.py              ← API FastAPI (rutas REST)
│   ├── quiz_engine.py       ← Motor del juego (lógica, puntos, sesiones)
│   └── data/
│       └── questions.py     ← Base de 30 preguntas curadas (6 niveles)
├── frontend/
│   └── index.html           ← Frontend completo (funciona standalone)
├── scripts/
│   └── play_cli.py          ← Modo consola para probar
├── requirements.txt
└── README.md
```

---

## 🚀 Cómo correr

### Modo Consola (sin instalar nada)
```bash
python scripts/play_cli.py
```

### Modo Web (frontend standalone)
Abrí `frontend/index.html` directo en el navegador.
No necesita backend — funciona con las preguntas integradas.

### Modo Completo (backend + frontend)
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
# Luego abrí frontend/index.html
```

---

## 🎮 Modos de Juego

| Modo | Descripción |
|------|-------------|
| **Clásico** | 30 preguntas, 6 niveles, 3 vidas |
| **Velocidad** | Preguntas rápidas, bonus por tiempo |
| **Escalada** | Subís de nivel respondiendo bien |

## 📊 Sistema de Puntos

```
Puntos = Puntos_base × Bonus_velocidad × Bonus_racha

Puntos base por nivel:
  Nivel 1: 100 pts   Nivel 4: 500 pts
  Nivel 2: 200 pts   Nivel 5: 750 pts
  Nivel 3: 350 pts   Nivel 6: 1000 pts

Bonus velocidad: hasta +50% si respondés en la mitad del tiempo
Bonus racha:     +10% por cada respuesta correcta consecutiva (máx +50%)
```

## 🗂️ Categorías

- 🌍 Mundiales
- 🏆 Champions League
- 🇦🇷 Fútbol Argentino
- ⭐ Jugadores
- 🏟️ Clubes

## 🔮 Próximos Pasos (Roadmap)

- [ ] Integrar API-Football para preguntas dinámicas
- [ ] Modo duelo 1v1 (WebSockets)
- [ ] Leaderboard con PostgreSQL
- [ ] Compartir resultado como imagen (OG cards)
- [ ] Modo streamer (overlay para Kick/Twitch)
- [ ] App mobile (React Native)
- [ ] Pregunta del día (tipo Wordle)
- [ ] Sistema de temporadas semanales

## 🏗️ Stack Técnico

| Capa | Tecnología |
|------|-----------|
| Backend | Python + FastAPI |
| Base de datos | SQLite → PostgreSQL |
| Frontend | HTML/CSS/JS vanilla → Next.js |
| Cache/Ranking | Redis |
| Deploy | Railway / Fly.io |
| Datos fútbol | API-Football, football-data.org |