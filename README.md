# TalentBoard 

> Bolsa de trabajo institucional para conectar egresados universitarios con empresas locales.

## Stack

| Capa       | Tecnología              |
|------------|-------------------------|
| Frontend   | React + Vite            |
| Backend    | Node.js + Express       |
| Base datos | MySQL 8.0               |
| Auth       | JWT (multi-rol)         |
| Mapas      | Mapbox GL JS            |

## Roles del Sistema

- **Administrador** – Gestión institucional y estadísticas
- **Egresado** – Perfil, búsqueda y postulación a vacantes
- **Empresa** – Publicación de vacantes y gestión de candidatos

## Estructura de Carpetas (planificada)

talentboard/
├── client/          # React SPA
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── services/
├── server/          # Express API
│   ├── src/
│   │   ├── controllers/
│   │   ├── routes/
│   │   ├── middlewares/
│   │   ├── models/
│   │   └── services/
├── database/
│   ├── schema.sql
│   └── seed.sql
└── docs/

## Fases de Desarrollo

- [x] Fase 1 – Diseño y Arquitectura
- [ ] Fase 2 – Desarrollo Core (Backend + Frontend base)
- [ ] Fase 3 – Integración y Pruebas
- [ ] Fase 4 – Entrega Final

## Variables de Entorno (ver `.env.example` en Fase 3)

PORT, DB_HOST, DB_USER, DB_PASS, DB_NAME, JWT_SECRET,
JWT_EXPIRES_IN, MAPBOX_TOKEN, LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET
