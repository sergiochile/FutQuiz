# ⚽ El Crack Quiz — Guía de Uso

## 🚀 Cómo Iniciar la Aplicación

### 1. Iniciar el Backend (FastAPI)

```bash
cd /Users/sergecchile./Desktop/Futquiz
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

El backend estará disponible en: `http://127.0.0.1:8000`

### 2. Iniciar el Frontend (HTTP Server)

En otra terminal:

```bash
cd /Users/sergecchile./Desktop/Futquiz/frontend
python3 -m http.server 3000
```

El frontend estará disponible en: `http://127.0.0.1:3000`

### 3. Abrir en el Navegador

Abre tu navegador en: **http://127.0.0.1:3000**

---

## 🎮 Cómo Jugar

### Pantalla Principal

1. **Escribe tu nombre** (o deja que se genere automáticamente)
2. **Selecciona un modo de juego**:
   - 🏆 **Clásico**: 30 preguntas en 6 niveles, 3 vidas
   - ⚡ **Velocidad**: Contrarreloj, responde en 60 segundos
   - 📈 **Escalada**: Sube de nivel respondiendo correctamente

3. **Elige una categoría**:
   - 🌍 Mundiales
   - 🏆 Champions League
   - ⚽ Ligas Europeas
   - ⭐ Jugadores
   - 🏟️ Clubes
   - 💰 Transferencias
   - 🎩 Entrenadores
   - 🤯 Curiosidades
   - 🎯 Todas

4. **Haz clic en "EMPEZAR A JUGAR"**

### Durante la Partida

- Cada respuesta correcta suma puntos (depende del nivel + racha)
- Mantén tu racha respondiendo correctamente
- Recibiras una vida si respondes mal (modo clásico)
- Cuando termines, verás tus resultados

### Sistema de Puntos

| Nivel | Puntos Base | Bonus de Racha |
|-------|------------|-----------------|
| 1     | 100 pts    | +10 por respuesta |
| 2     | 200 pts    | +10 por respuesta |
| 3     | 350 pts    | +10 por respuesta |
| 4     | 500 pts    | +10 por respuesta |
| 5     | 750 pts    | +10 por respuesta |
| 6     | 1000 pts   | +10 por respuesta |

---

## 👥 Mi Equipo

### Construcción del Equipo (4-3-3)

1. **Posiciones a llenar**:
   - 1 Portero (🧤)
   - 4 Defensas (🛡️)
   - 3 Mediocampistas (🎯)
   - 3 Delanteros (⚡)

2. **Haz clic en una posición** para seleccionar un jugador

3. **Selecciona de tu colección** de jugadores desbloqueados

4. **Guarda tu equipo** con el botón "Guardar Equipo"

### Colección de Jugadores

- **Desbloqueados** (con oro): Listos para usar
- **Bloqueados** (grises): Desbloquéalos ganando partidas
- **150 jugadores totales** en 5 niveles de rareza

---

## 🎯 Challenges (Desafíos)

Completa estos objetivos para probar que eres un **true crack**:

1. 🥇 **El Triángulo de Oro**: Desbloquea 3 leyendas
2. 🧤 **Portazo Perfecto**: Desbloquea todos los porteros
3. 🛡️ **Defensa Inquebrantable**: 5 defensas oro+
4. 🎯 **Mediocampo Dominador**: 3 mediocampistas diamante+
5. ⚡ **Ataque Letal**: Desbloquea 4 delanteros
6. 💯 **Equipo Perfecto 100**: Valor total del equipo ≥ 1000

---

## 🏆 Ranking Global

- **Visualiza** los mejores equipos del servidor
- **Compara** tu equipo vs otros usuarios
- **Busca** jugadores específicos
- **Ve las estadísticas** de cada equipo

---

## 📊 Desbloqueo de Jugadores

### Sistema de Rareza

Cada partida que termines con cierto puntaje, desbloquea un jugador:

| Puntuación | Rareza |
|-----------|--------|
| 500+      | Bronce 🟶 |
| 1500+     | Plata ⚪ |
| 3000+     | Oro 🟡 |
| 5000+     | Diamante 💎 |
| 8000+     | Leyenda 🔥 |

### Animación de Desbloqueo

Cuando desbloquees un jugador:
- ¡Verás una animación especial!
- Se añadirá a tu colección
- Aparecerá en "Mi Equipo" para asignar

---

## ⚙️ Funcionalidades Técnicas

### API Endpoints Principales

```
GET  /                              → Estado del API
GET  /api/info                      → Categorías, modos y niveles
POST /api/game/start                → Iniciar partida
GET  /api/game/{session_id}/question → Siguiente pregunta
POST /api/game/finish               → Terminar partida
GET  /api/players/catalog           → Catálogo de 150 jugadores
GET  /api/ranking/teams             → Top 20 equipos
```

### Persistencia

- **Nombres de usuario**: Guardados en localStorage
- **Equipos**: Guardados en SQLite (backend)
- **Progreso**: Sincronizado automáticamente

---

## 🐛 Troubleshooting

### "Aún no hay equipos guardados"
→ Juega una partida primero para desbloquear jugadores

### Las preguntas no aparecen
→ Asegúrate de que el backend está corriendo en puerto 8000

### El frontend no se conecta
→ Verifica que la URL sea `http://127.0.0.1:3000` (no `localhost`)

---

## 📝 Notas Importantes

- El juego se guardará automáticamente
- Los desbloqueos son permanentes
- Puedes cambiar de usuario en cualquier momento
- Los desafíos se actualizan en tiempo real

---

¡**Diviértete y demuestra que eres El Crack!** ⚽🏆
