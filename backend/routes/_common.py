from pathlib import Path
from fastapi import Request
from fastapi.templating import Jinja2Templates

from config import settings

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


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
    }
    ctx.update(extra)
    return ctx
