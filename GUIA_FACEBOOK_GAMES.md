# Guía: Publicar El Crack Quiz en Facebook Instant Games

## Resumen del flujo

```
Tu PC (código) → GitHub → Railway (backend) → Facebook Instant Games (frontend ZIP)
```

---

## PASO 1: Subir el Backend a Railway (gratis)

Railway hospeda el servidor Python gratis hasta cierto límite.

### 1.1 Crear cuenta
1. Ve a https://railway.app y crea una cuenta (puedes usar GitHub)

### 1.2 Subir el código
**Opción A — Desde GitHub (recomendado):**
1. Sube tu proyecto a GitHub
2. En Railway: `New Project` → `Deploy from GitHub repo`
3. Selecciona tu repositorio
4. Railway detectará el `Procfile` automáticamente

**Opción B — CLI:**
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### 1.3 Variables de entorno en Railway
En el panel de Railway → tu proyecto → `Variables`:
```
ENVIRONMENT=production
ALLOWED_ORIGINS=https://fb.gg,https://apps.facebook.com,https://www.facebook.com
PORT=                     # Railway lo asigna solo, no tocar
```

### 1.4 Obtener tu URL
Railway te dará una URL como:
```
https://futquiz-production.up.railway.app
```
**Guarda esta URL** — la necesitarás en el siguiente paso.

---

## PASO 2: Configurar config.js con la URL de producción

Edita `frontend/config.js`:

```javascript
const IS_PRODUCTION = true;  // <-- cambiar a true

const PRODUCTION_API_URL = 'https://futquiz-production.up.railway.app/api';
//                          ↑ Tu URL de Railway + /api
```

Verifica que el backend responde:
```bash
curl https://TU-URL.railway.app/health
# Debe responder: {"status":"ok","version":"0.2.0"}
```

---

## PASO 3: Crear la App en Facebook Developers

1. Ve a https://developers.facebook.com/apps
2. Haz clic en **"Crear App"**
3. Tipo de app: **"Instant Games"** (o "Juegos")
4. Nombre: `El Crack Quiz`
5. Categoría: **Sports** (Deportes)

### 3.1 Obtener el App ID
En el panel de la app verás tu **App ID** (número de 16 dígitos).

Agrégalo en `frontend/config.js`:
```javascript
fbAppId: '123456789012345',  // <-- tu App ID aquí
```

### 3.2 Configurar dominio del backend (CORS)
En Facebook Developers → tu app → `Configuración` → `Básico`:
- **Dominio de la app:** tu dominio de Railway

---

## PASO 4: Crear y Subir el Bundle

```bash
# Desde la carpeta raíz del proyecto:
bash build_facebook_bundle.sh
```

Esto genera `facebook-bundle.zip` (8 KB aprox).

### 4.1 Subir a Facebook
1. En tu app de Facebook: `Instant Games` → `Web Hosting`
2. Haz clic en **"Subir versión"**
3. Sube el archivo `facebook-bundle.zip`
4. Después de subir: haz clic en **"Enviar para revisión"** o **"Publicar"**

---

## PASO 5: Probar el juego

### Prueba en modo staging (antes de publicar)
1. En Facebook Developers → `Instant Games` → `Hosting`
2. Busca tu versión subida
3. Haz clic en **"Ver"** para probarlo

### Prueba en Facebook Messenger
1. Abre Facebook Messenger
2. Inicia un chat
3. Botón `+` → **Juegos** → busca tu app (en estado de prueba solo lo ven los testers)

---

## PASO 6: Publicar (Revisión de Facebook)

Para que cualquier usuario pueda encontrar el juego:
1. En tu app → `Revisión de la app`
2. Solicita el permiso: `gaming.required_frame`
3. Facebook revisa el juego (suele tardar 2-5 días)
4. Una vez aprobado: `Estado de la app` → **Activo**

---

## Requisitos mínimos de Facebook para aprobación

- [ ] El juego debe cargar en menos de 10 segundos
- [ ] Debe funcionar en móvil (responsive)
- [ ] No debe haber errores de consola críticos
- [ ] Debe llamar a `FBInstant.startGameAsync()` en máximo 60 segundos
- [ ] Icono del juego: 1024×1024 px PNG
- [ ] Banner: 1200×628 px PNG
- [ ] Descripción en inglés y en el idioma principal

---

## Activos gráficos que necesitas crear

| Asset | Tamaño | Formato |
|-------|--------|---------|
| Icono de la app | 1024×1024 px | PNG |
| Banner | 1200×628 px | PNG |
| Captura de pantalla | 1280×720 px (mínimo 3) | PNG/JPG |

Puedes crearlos con Canva (gratis): https://canva.com

---

## Estructura de archivos generados

```
Futquiz/
├── Procfile                    ← Railway/Heroku (NUEVO)
├── railway.toml                ← Configuración Railway (NUEVO)
├── .env.example                ← Variables de entorno ejemplo (NUEVO)
├── build_facebook_bundle.sh    ← Script de build (NUEVO)
├── facebook-bundle.zip         ← ZIP para subir a Facebook (GENERADO)
├── facebook-bundle/            ← Carpeta del bundle
│   ├── index.html
│   └── config.js
├── frontend/
│   ├── index.html              ← Modificado: FB SDK + config.js
│   └── config.js               ← NUEVO: URL dinámica del API
└── backend/
    └── main.py                 ← Modificado: CORS + dotenv + health check
```

---

## Solución de problemas comunes

| Problema | Solución |
|----------|----------|
| CORS error | Agrega tu dominio de Railway a `ALLOWED_ORIGINS` en Railway |
| `FBInstant is not defined` | Normal en local, solo funciona dentro de Facebook |
| El juego no carga en FB | Verifica que `index.html` esté en la raíz del ZIP |
| Backend 500 error | Revisa los logs en Railway: `railway logs` |
| Login no funciona | Verifica que `PRODUCTION_API_URL` apunte a tu Railway URL |
