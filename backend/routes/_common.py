from pathlib import Path
from fastapi import Request
from fastapi.templating import Jinja2Templates

from config import settings

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ============================================================
# Editable site content (admin-managed in /admin/content)
# ============================================================
SITE_CONTENT_DEFAULTS = {
    # Hero / home
    "home.hero.title":     ("Soluciones hidricas integrales para LATAM",      "Titulo principal del hero",        "home"),
    "home.hero.subtitle":  ("Tecnologia, consultoria, materiales y proyectos internacionales para una gestion eficiente del agua.", "Subtitulo del hero", "home"),
    "home.hero.cta":       ("Solicita una consultoria",                       "Texto del boton principal",        "home"),
    "home.hero.cta2":      ("Ver proyectos",                                  "Texto del boton secundario",       "home"),
    # About
    "about.mission":       ("Llevar gestion hidrica sostenible a cada productor y comunidad de Latinoamerica.", "Mision corporativa", "about"),
    "about.vision":        ("Ser el aliado tecnico-comercial de referencia en gestion hidrica de la region.", "Vision corporativa", "about"),
    "about.story":         ("Nacimos en 2014 fusionando equipos de ingenieria, agronomia y consultoria internacional.", "Historia breve", "about"),
    # Contact
    "contact.address":     ("Av. Principal 123, Lima - Peru",                 "Direccion fisica",                 "contact"),
    "contact.hours":       ("Lun-Vie 9:00 - 18:00",                           "Horario de atencion",              "contact"),
    # Footer
    "footer.tagline":      ("Gestion hidrica inteligente para LATAM.",        "Tagline del footer",               "footer"),
    "footer.copyright":    ("(c) 2026 Aqua-Terra. Todos los derechos reservados.", "Texto de copyright",          "footer"),
}


def load_site_content(db):
    """Return dict {key: value} from SiteContent table, falling back to defaults."""
    try:
        from models import SiteContent
        rows = db.query(SiteContent).all()
        existing = {r.key: r.value for r in rows}
    except Exception:
        existing = {}
    result = {}
    for k, (default_val, _label, _section) in SITE_CONTENT_DEFAULTS.items():
        result[k] = existing.get(k, default_val)
    # also expose any custom keys an admin added
    for k, v in existing.items():
        result.setdefault(k, v)
    return result


PILLARS = [
    {
        "slug": "tecnologia",
        "number": 1,
        "name": "Tecnologia e Innovacion",
        "icon": "cpu",
        "tagline": "I+D aplicada al agua",
        "color": "#2E75B6",
        "short": "Desarrollamos tecnologia de punta para riego inteligente con socios academicos.",
        "long": (
            "Trabajamos en I+D con universidades y centros de investigacion para llevar al campo "
            "soluciones de riego inteligente, sensorica avanzada y agricultura de precision. "
            "Nuestros prototipos se prueban en pilotos reales antes de escalar."
        ),
        "highlights": [
            "Sensores LoRa y NB-IoT propios",
            "Modelos predictivos de demanda hidrica",
            "Convenios con 6 universidades de la region",
            "12 prototipos en pilotos activos",
        ],
    },
    {
        "slug": "consultoria",
        "number": 2,
        "name": "Consultoria y Analisis",
        "icon": "chart-line",
        "tagline": "Decisiones basadas en datos",
        "color": "#3D5A80",
        "short": "Diagnosticos, estudios y modelos de ROI para optimizar la gestion hidrica.",
        "long": (
            "Analizamos tus operaciones, suelos, clima y cultivos para entregar diagnosticos accionables. "
            "Nuestros consultores combinan experiencia agronomica con modelos cuantitativos para identificar "
            "ahorros reales y proyectar el ROI de cada inversion."
        ),
        "highlights": [
            "Diagnostico hidrico in-situ",
            "Modelos de ROI a 5 anios",
            "Auditoria de eficiencia energetica",
            "Calculadora interactiva de ahorro",
        ],
    },
    {
        "slug": "materiales",
        "number": 3,
        "name": "Materiales y Distribucion",
        "icon": "boxes",
        "tagline": "Equipos listos para escalar",
        "color": "#70AD47",
        "short": "Cataloga, compara y solicita los equipos que tu proyecto necesita.",
        "long": (
            "Operamos una red de distribucion de equipos certificados: bombas, controladores, tuberias, "
            "filtros y kits de riego automatico. Trabajamos con marcas premium y ofrecemos garantia "
            "extendida con servicio postventa regional."
        ),
        "highlights": [
            "+80 referencias en catalogo",
            "Descuentos por volumen escalonados",
            "Garantia extendida 3-5 anios",
            "Centros de servicio en 4 paises",
        ],
    },
    {
        "slug": "internacional",
        "number": 4,
        "name": "Consultoria Internacional",
        "icon": "globe",
        "tagline": "Alianzas globales, impacto local",
        "color": "#1F4E79",
        "short": "Proyectos en Latinoamerica, Africa y Sudeste Asiatico con socios globales.",
        "long": (
            "Colaboramos con organismos multilaterales, ONGs y gobiernos en proyectos de gran escala. "
            "Aportamos estandar internacional y entendimiento local para implementar soluciones de riego "
            "sostenible en geografias diversas."
        ),
        "highlights": [
            "Proyectos en 18 paises",
            "Socios: BID, FAO, GIZ",
            "Equipos multilingues",
            "Cumplimiento ISO 14001 / 46001",
        ],
    },
]


def get_pillar(slug: str):
    return next((p for p in PILLARS if p["slug"] == slug), None)


def base_ctx(request: Request, **extra):
    cart = request.session.get("cart", {})
    wishlist = request.session.get("wishlist", [])
    # Lazy import db helper to avoid circular import at module load
    site_content = {}
    try:
        from database import SessionLocal
        with SessionLocal() as db:
            site_content = load_site_content(db)
    except Exception:
        # fall back to defaults only
        site_content = {k: v[0] for k, v in SITE_CONTENT_DEFAULTS.items()}
    ctx = {
        "request": request,
        "site_name": settings.SITE_NAME,
        "site_tagline": settings.SITE_TAGLINE,
        "contact_email": settings.CONTACT_EMAIL,
        "contact_phone": settings.CONTACT_PHONE,
        "pillars": PILLARS,
        "cart_count": sum(cart.values()) if isinstance(cart, dict) else 0,
        "wishlist_count": len(wishlist),
        "current_year": 2026,
        # Session-derived auth flags (lightweight, no DB hit for nav rendering)
        "current_user_id": request.session.get("user_id"),
        "current_username": request.session.get("username"),
        "is_admin": bool(request.session.get("is_admin")),
        "is_authenticated": bool(request.session.get("user_id")),
        # Editable site content (admin-managed, exposed to all templates)
        "sc": site_content,
    }
    ctx.update(extra)
    return ctx
