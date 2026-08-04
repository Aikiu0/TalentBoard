# TalentBoard

App con frontend SPA (una sola página que carga vistas en `<div>`) y backend Flask + MySQL.

## ⚠️ 1. Arreglar la conexión a la base de datos (lo primero)

El error *"No se pudo conectar con la base de datos"* casi siempre es porque
los datos de `backend/config.py` **no coinciden** con tu MySQL Workbench.

Abre `backend/config.py` y ajusta:

```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",                 # tu usuario de MySQL
    "password": "TU_CONTRASEÑA_AQUI",   # tu contraseña de MySQL
    "database": "talentboard",          # nombre del schema en Workbench
    "charset":  "utf8mb4",
}
```

Para saber EXACTAMENTE qué falla, ejecuta el diagnóstico:

```bash
cd backend
python test_db.py
```

Te dirá si el problema es: usuario/contraseña incorrectos, la base no existe,
MySQL apagado, o falta el conector.

## ⚠️ 2. El usuario admin de prueba NO podrá iniciar sesión

En tu script insertaste:

```sql
INSERT INTO Usuarios (correo, password, rol)
VALUES ('usuariosadmin1@test.com', '123456', 'administrador');
```

El problema: el backend verifica contraseñas con **bcrypt**, pero `'123456'`
está en **texto plano**. bcrypt no puede comparar contra texto plano, así que
ese login siempre dará "Credenciales incorrectas".

**Solución:** registra los usuarios desde la app (así se hashean bien), o genera
un hash bcrypt para el admin. Para generarlo:

```bash
cd backend
python -c "import bcrypt; print(bcrypt.hashpw(b'123456', bcrypt.gensalt()).decode())"
```

Copia el resultado (empieza con `$2b$...`) y actualiza el admin en Workbench:

```sql
UPDATE Usuarios
SET password = '<pega-aqui-el-hash>'
WHERE correo = 'usuariosadmin1@test.com';
```

## 3. Cómo correr el proyecto

**Backend** (puerto 5000):
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Frontend** (con un servidor, NO doble clic):
```bash
cd frontend
python -m http.server 5500
```
Luego abre http://localhost:5500

> Importante: el frontend usa `fetch` para cargar las vistas y para hablar con
> el backend, por eso necesita un servidor. Si abres el `index.html` con doble
> clic (`file://`) NADA funcionará. Usa Live Server de VS Code o el comando de
> arriba. Si usas otro puerto, agrégalo en la lista CORS de `backend/app.py`.

## 4. Registro: Empresa o Persona

La pantalla de registro muestra primero dos tarjetas:

- **Soy una persona** → se guarda con rol `candidato`. Pide nombre y apellido
  (se combinan en `nombre_completo` en la tabla `Candidatos`).
- **Soy una empresa** → se guarda con rol `empresa`. Pide nombre de empresa y
  descripción (tabla `Empresas`, queda `aprobada = FALSE` hasta que un admin
  la apruebe).

El registro inserta en dos tablas dentro de una **transacción**: si algo falla,
se revierte todo (no quedan usuarios huérfanos).

## Estructura del frontend (SPA)

```
frontend/
├── index.html              ← cascarón: solo #app + router
├── public/
│   ├── css/style.css       ← estilos compartidos por TODAS las vistas
│   └── js/router.js        ← decide qué vista se muestra (API_URL aquí)
└── views/
    ├── login.html          ← pantalla de login
    ├── register.html       ← selección de rol + formularios
    └── _plantilla.html     ← molde para nuevas pantallas
```

### Agregar una pantalla nueva (3 pasos)

1. Copia `views/_plantilla.html` → `views/dashboard.html` y renombra dentro la
   función `init__plantilla` → `init_dashboard`.
2. Regístrala en `public/js/router.js`:
   ```js
   const routes = {
       "login":     "views/login.html",
       "register":  "views/register.html",
       "dashboard": "views/dashboard.html",   // ← nueva
   };
   ```
3. Navega hacia ella con `navegarA("dashboard")` (p. ej. tras un login exitoso).

---

## NUEVO: Dashboards de candidato y empresa

Ahora al iniciar sesión, cada rol llega a su propio panel:

- **Persona (candidato)** → `dashboard-candidato`: buscar vacantes, postularse,
  ver el estado de sus postulaciones, y editar su perfil.
- **Empresa** → `dashboard-empresa`: ver estadísticas, crear vacantes, ver sus
  vacantes publicadas, ver los candidatos que se postularon y cambiarles el
  estado (pendiente / revisado / aceptado / rechazado).

### Cargar datos de ejemplo (seed)

Para ver vacantes desde el primer momento, ejecuta UNA vez:

```bash
cd backend
python seed.py
```

Esto crea 3 empresas con vacantes (en CDMX, Guadalajara y Monterrey) y un
candidato de prueba. **Todos los usuarios de prueba usan la contraseña `123456`:**

| Rol       | Correo                  |
|-----------|-------------------------|
| Empresa   | greensoft@test.com      |
| Empresa   | digitalent@test.com     |
| Empresa   | nucleo@test.com         |
| Candidato | ana@test.com            |

> El seed es seguro de correr varias veces: si un usuario ya existe, lo omite.

### Cómo probar el flujo completo

1. Inicia sesión como **candidato** (`ana@test.com` / `123456`) y verás las
   vacantes de ejemplo. Postúlate a alguna.
2. Cierra sesión e inicia como **empresa** (`greensoft@test.com` / `123456`).
   En "Mis vacantes" → "Ver candidatos" verás a quién se postuló, y podrás
   cambiar el estado de la postulación.

### Nuevos endpoints del backend

```
GET    /api/vacantes              listar vacantes activas (?q= para buscar)
GET    /api/vacantes/<id>         detalle de una vacante
POST   /api/vacantes              crear vacante (empresa)
GET    /api/mis-vacantes          vacantes de la empresa logueada
DELETE /api/vacantes/<id>         desactivar vacante (empresa)
POST   /api/postulaciones         postularse (candidato)
GET    /api/mis-postulaciones     postulaciones del candidato
GET    /api/vacantes/<id>/postulaciones   candidatos de una vacante (empresa)
PUT    /api/postulaciones/<id>/estado     cambiar estado (empresa)
GET    /api/me                    datos + estadísticas del usuario logueado
PUT    /api/perfil/candidato      actualizar perfil candidato
PUT    /api/perfil/empresa        actualizar perfil empresa
```

## 🗺️ APIs externas: mapa de vacantes (Leaflet + OpenStreetMap + Nominatim)

El proyecto consume **dos APIs externas**, sin necesidad de API key ni registro:

| API | Para qué se usa | Dónde está en el código |
|---|---|---|
| **Leaflet + tiles de OpenStreetMap** (`tile.openstreetmap.org`) | Dibujar los mapas interactivos | `index.html` (CDN) y `router.js` → `crearMapa()` |
| **Nominatim** (`nominatim.openstreetmap.org/search`) | Geocodificación REST: convierte una dirección escrita en latitud/longitud (respuesta JSON) | `router.js` → `geocodificarDireccion()` |

### Qué se agregó

**Candidato → "Mapa de vacantes"** (nueva opción del sidebar)
- Mapa con un pin por cada vacante activa que tenga ubicación.
- Cada pin abre un popup con título, empresa, salario y botón **Postularme** (usa el mismo endpoint `POST /api/postulaciones`).
- El mapa se encuadra solo para mostrar todos los pines.

**Empresa → "Crear vacante"**
- Campo **Dirección** + botón **Buscar ubicación**: llama a Nominatim y llena
  automáticamente latitud/longitud (los inputs ahora son de solo lectura).
- Mini-mapa de vista previa: también puedes **hacer clic** sobre el mapa para
  colocar o ajustar el pin manualmente.
- Al publicar, el pin y el formulario se limpian.

### Notas
- El backend **no cambió**: `GET /api/vacantes` ya devolvía `latitud` y `longitud`.
- Nominatim se llama directo desde el navegador (permite CORS). Su política de
  uso pide máximo ~1 petición por segundo: suficiente para esta app.
- Requiere internet para cargar los tiles del mapa y la geocodificación.
