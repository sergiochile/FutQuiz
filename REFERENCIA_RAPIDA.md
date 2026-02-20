# 🎯 REFERENCIA RÁPIDA - EL CRACK QUIZ

## ⚡ Comandos Esenciales

### Iniciar Aplicación

```bash
# Terminal 1: Backend (http://127.0.0.1:8000)
cd /Users/sergecchile./Desktop/Futquiz
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Terminal 2: Frontend (http://127.0.0.1:3000)
cd /Users/sergecchile./Desktop/Futquiz/frontend
python3 -m http.server 3000

# Terminal 3: Abrir navegador
open http://127.0.0.1:3000
```

### Testing

```bash
# Ejecutar todos los tests
python3 /Users/sergecchile./Desktop/Futquiz/test_api.py

# Resultado esperado: 7/7 tests PASADOS ✅
```

### Detener Servicios

```bash
# Matar ambos procesos
pkill -f "uvicorn|http.server"

# O Ctrl+C en cada terminal
```

---

## 🎮 Cómo Jugar

### Paso 1: Seleccionar Modo
- **Clásico**: 30 preguntas + 3 vidas
- **Speed**: 60 segundos máximo
- **Escalada**: Subida progresiva de niveles

### Paso 2: Seleccionar Categoría
- Mundiales
- Champions
- Ligas
- Jugadores
- Clubes
- Transferencias
- Entrenadores
- Curiosidades

### Paso 3: Jugar
- Responde preguntas de opción múltiple
- Acumula puntos: (nivel × 100) + (racha × 10)
- Construye racha de respuestas correctas
- Evita perder vidas (modo clásico)

### Paso 4: Ver Resultados
- Score final
- Accuracy (%)
- Respuestas correctas
- Mejor racha
- ¿Desbloqueaste jugador? → Animación 🎉

---

## 👥 Sistema de Jugadores

### Raridades y Thresholds

| Rareza | Rango Score | Color | Emoji |
|--------|-------------|-------|-------|
| Bronce | 500+ | Marrón | 🥉 |
| Plata | 1500+ | Plata | 🥈 |
| Oro | 3000+ | Oro | 🥇 |
| Diamante | 5000+ | Azul | 💎 |
| Leyenda | 8000+ | Púrpura | 👑 |

---

## ⚽ Construcción de Equipo (4-3-3)

### Formación
```
        POR
    DEF1 DEF2 DEF3 DEF4
      MED1 MED2 MED3
        DEL1 DEL2 DEL3
```

### Cómo Asignar
1. Ve a tab "Mi Equipo"
2. Haz clic en una posición
3. Selecciona un jugador
4. Haz clic en "Asignar"
5. Haz clic en "Guardar Equipo"

---

## 🎯 Challenges (6 Total)

| # | Nombre | Objetivo | Progreso |
|---|--------|----------|----------|
| 1 | Coleccionista | Desbloquear 10 jugadores | Barra |
| 2 | Especialista Ataque | 5 delanteros en equipo | 5/5 |
| 3 | Murallazo | Llenar todas defensas | 4/4 |
| 4 | Mediapunta | 3 mediocampistas | 3/3 |
| 5 | Squad Value | Equipo 5000+ rating | 4500/5000 |
| 6 | Collector | Desbloquear 50 jugadores | 0/50 |

---

## 🏆 Ranking

### Cómo Acceder
1. Tab "Ranking"
2. Ver top 20 equipos

### Comparar Equipos
1. Busca usuario
2. Haz clic "vs"
3. Compara lado a lado

---

## 🔧 API Endpoints

### Info
```
GET /api/info
```

### Usuario
```
GET /api/user/register?username=Nombre
POST /api/user/register {username: "Nombre"}
GET /api/user/{username}
POST /api/user/{username}/team [11 players]
GET /api/user/{username}/challenges
GET /api/user/{u1}/vs/{u2}
```

### Juego
```
POST /api/game/start {username, mode, category}
GET /api/game/{sessionId}/question
POST /api/game/finish {sessionId, answers, time}
```

### Datos
```
GET /api/players/catalog
GET /api/ranking/teams
```

---

## 📊 Scoring System

### Puntos por Pregunta
```
Puntos = (Nivel × 100) + (Racha × 10)

Ejemplo:
- Nivel 3 + Racha 5 = (3 × 100) + (5 × 10) = 350 puntos
```

### Bonificaciones
- Racha: +10 puntos por respuesta correcta consecutiva
- Combo: Racha de 10 = ¡Combo 🔥!

---

## 📁 Estructura de Archivos

```
/Users/sergecchile./Desktop/Futquiz/
├── README.md                    # Descripción proyecto
├── requirements.txt             # Dependencias Python
├── GUIA_USO.md                 # Guía completa de usuario
├── ESPECIFICACION.md           # Especificación técnica
├── RESULTADOS.md               # Resumen de implementación
├── REFERENCIA_RAPIDA.md        # Este archivo
├── test_api.py                 # Suite de testing
├── INICIO_RAPIDO.sh            # Script de inicio
│
├── frontend/
│   └── index.html              # SPA principal (1700+ líneas)
│
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI (377 líneas)
│   ├── quiz_engine.py          # Motor de juego (230 líneas)
│   ├── database.py             # SQLite ORM (199 líneas)
│   └── data/
│       ├── __init__.py
│       ├── questions.py        # 102 preguntas
│       └── players.py          # 145 jugadores
│
└── scripts/
    └── play_cli.py             # CLI legacy
```

---

## 🐛 Troubleshooting

### El backend no inicia
```bash
# Verificar puerto 8000 libre
lsof -i :8000

# Matar proceso existente
kill -9 <PID>

# Reintentar
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### El frontend no carga
```bash
# Verificar puerto 3000 libre
lsof -i :3000

# Ir a directorio frontend
cd frontend

# Iniciar servidor
python3 -m http.server 3000
```

### Errores en el juego
```bash
# Abrir consola del navegador
⌘ + Option + J (Chrome)
⌘ + Option + I (Firefox)

# Ver errores JavaScript
# Recargar página: ⌘ + R
```

### Datos perdidos
```bash
# Base de datos en RAM entre sesiones
# Para persistencia permanente: agregar archivo .db

# Limpiar localStorage
# Abre DevTools → Application → Local Storage → Clear
```

---

## 📈 Estadísticas Útiles

### Preguntas por Categoría (17 por nivel × 6 niveles)
- Mundiales: 102 preguntas
- Champions: 102 preguntas
- Ligas: 102 preguntas
- Jugadores: 102 preguntas
- Clubes: 102 preguntas
- Transferencias: 102 preguntas
- Entrenadores: 102 preguntas
- Curiosidades: 102 preguntas

### Jugadores por Rareza
- Bronce: 30 jugadores
- Plata: 35 jugadores
- Oro: 25 jugadores
- Diamante: 15 jugadores
- Leyenda: 10 jugadores
- **Total: 145 jugadores**

---

## 🎨 Colores y Temas

```css
/* Colores principales */
Primary:    #1ABC9C (Teal FIFA)
Secondary:  #F1C40F (Gold)
Error:      #E74C3C (Red)
Success:    #27AE60 (Green)
Background: #0F1419 (Dark)
Text:       #ECF0F1 (Light)

/* Raridades */
Bronce:     #CD7F32
Plata:      #C0C0C0
Oro:        #FFD700
Diamante:   #00BFFF
Leyenda:    #9932CC
```

---

## 💡 Tips para Mejores Scores

1. **Mantén racha**: Respuestas correctas = más puntos
2. **Sube de nivel**: Preguntas nivel 6 dan más puntos
3. **Modo Speed**: Máximas preguntas en 60 segundos
4. **Desbloquea rápido**: Primeras partidas → puntos rápido
5. **Equipo fuerte**: Combina raridades altas

---

## 🚀 Mejoras Futuras (Road Map)

- [ ] Autenticación de usuarios
- [ ] Leaderboard en línea
- [ ] Modo multijugador
- [ ] Predicciones con ML
- [ ] App móvil nativa
- [ ] Badges y achievements
- [ ] Daily challenges
- [ ] Tournament mode

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo jugar sin internet?**
R: No, necesita conexión para sincronizar con el backend.

**P: ¿Mis datos se guardan?**
R: Sí, en SQLite. El username en localStorage.

**P: ¿Cuántos jugadores hay?**
R: 145 jugadores en 5 raridades.

**P: ¿Cuántas preguntas?**
R: 102 preguntas × 8 categorías = 816 preguntas únicas.

**P: ¿Puedo resetear mi progreso?**
R: Necesitarías un nuevo username.

**P: ¿Hay modo offline?**
R: No, requiere backend activado.

---

**Última actualización**: Febrero 2026  
**Versión**: 1.0 Final  
**Estado**: ✅ Listo para producción
