# Plataforma Hidrica - Soluciones Integradas en Riego y Gestion Hidrica

Plataforma web profesional para empresa multisectorial dedicada a soluciones de riego sostenible.
Sitio corporativo + centro de informacion + tienda + dashboard de impacto.

## Stack

- **Backend:** Python 3.11 + FastAPI + SQLAlchemy 2 + Jinja2
- **DB:** PostgreSQL 15
- **Frontend:** HTML5 + CSS3 (custom) + Vanilla JS + Chart.js + Leaflet.js
- **Infra:** Docker Compose (postgres + backend + nginx)

## Levantamiento rapido

```bash
cp .env.example .env
docker-compose up --build
```

- Sitio: http://localhost
- API (directo): http://localhost:8000
- DB: localhost:5432

El primer arranque crea tablas y carga datos iniciales automaticamente (controlado por `SEED_ON_STARTUP=true` en `.env`).

## Estructura

```
Proyecto hidrico/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── nginx/
│   └── nginx.conf
├── postgres/
└── backend/
    ├── main.py            # entrada FastAPI
    ├── config.py          # settings (pydantic)
    ├── database.py        # engine + session
    ├── seed.py            # datos iniciales
    ├── utils.py
    ├── models/            # SQLAlchemy
    ├── schemas/           # Pydantic
    ├── routes/            # routers FastAPI
    ├── templates/         # Jinja2
    └── static/            # css, js, images
```

## Secciones implementadas

- **Home:** hero, 4 pilares, proyectos destacados, estadisticas animadas, testimonios, CTA
- **Sobre nosotros:** mision/vision/valores, timeline, equipo, alianzas
- **4 Pilares:**
  1. Tecnologia e Innovacion
  2. Consultoria y Analisis (incluye calculadora ROI)
  3. Materiales y Distribucion
  4. Consultoria Internacional (mapa global)
- **Tienda:** catalogo con filtros, ficha de producto, carrito (sesion), wishlist, comparador, cotizacion
- **Proyectos:** galeria filtrable + mapa Leaflet
- **Blog:** posts con categorias + suscripcion a newsletter
- **Contacto:** formulario con tipo de consulta + cotizacion
- **Dashboard:** contadores animados + graficos Chart.js + mapa global de impacto

## Notas

- El checkout es demo (no procesa pagos).
- Emails se loguean en consola.
- Imagenes usan placeholders (`picsum.photos`) por defecto; reemplaza por las definitivas en `backend/static/images/`.
- Para regenerar datos: `docker-compose exec backend python seed.py --reset`.

## Desarrollo local sin Docker

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows PowerShell
pip install -r requirements.txt
# (requiere postgres local con DATABASE_URL en .env)
cd backend
uvicorn main:app --reload
```
