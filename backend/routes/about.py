from fastapi import APIRouter, Request

from ._common import templates, base_ctx

router = APIRouter()


TIMELINE = [
    {"year": "2012", "title": "Fundacion", "text": "Nace Aqua-Terra en Lima, enfocada en consultoria de riego para pequenos productores."},
    {"year": "2015", "title": "Primera expansion", "text": "Apertura de oficina en Mexico y primer contrato con un organismo multilateral."},
    {"year": "2018", "title": "Brazo de I+D", "text": "Lanzamos la division de tecnologia con sensores propios y modelos predictivos."},
    {"year": "2021", "title": "Distribucion regional", "text": "Cubrimos 4 paises con red propia de servicio postventa."},
    {"year": "2024", "title": "Alianzas globales", "text": "Proyectos activos en 18 paises con socios como BID, FAO y GIZ."},
    {"year": "2026", "title": "Hoy", "text": "+500 proyectos implementados y mas de 12 millones de m3 ahorrados."},
]

TEAM = [
    {"name": "Dra. Lucia Carrasco", "role": "CEO & Fundadora", "bio": "Ingeniera agricola con 20 anios en gestion hidrica multisectorial.", "image": "https://i.pravatar.cc/300?img=47"},
    {"name": "Ing. Mateo Diaz", "role": "CTO", "bio": "Lidera I+D de sensorica IoT y plataformas de monitoreo.", "image": "https://i.pravatar.cc/300?img=12"},
    {"name": "Ana Rojas, PhD", "role": "Directora de Consultoria", "bio": "Especialista en modelos de ROI hidrico para agricultura y municipios.", "image": "https://i.pravatar.cc/300?img=32"},
    {"name": "Carlos Mendieta", "role": "Director de Operaciones", "bio": "Coordina la red de distribucion regional y el servicio postventa.", "image": "https://i.pravatar.cc/300?img=15"},
    {"name": "Sofia Linares", "role": "Directora Internacional", "bio": "Gestiona alianzas con BID, FAO y gobiernos regionales.", "image": "https://i.pravatar.cc/300?img=44"},
    {"name": "Roberto Pena", "role": "Director Financiero", "bio": "Estructura el financiamiento de proyectos de gran escala.", "image": "https://i.pravatar.cc/300?img=33"},
]

ALLIANCES = [
    "Universidad Agraria La Molina",
    "Universidad Nacional de Mexico",
    "BID - Banco Interamericano",
    "FAO",
    "GIZ - Cooperacion Alemana",
    "ISO 14001 / 46001",
    "Smart Water Networks Forum",
    "International Water Association",
]

VALUES = [
    {"icon": "leaf", "title": "Sostenibilidad", "text": "Cada decision se mide por su impacto hidrico y de carbono."},
    {"icon": "lightbulb", "title": "Innovacion", "text": "Inversion permanente en I+D y adopcion temprana de tecnologias."},
    {"icon": "handshake", "title": "Confianza", "text": "Acompanamiento de largo plazo, no proyectos transaccionales."},
    {"icon": "globe", "title": "Visión global", "text": "Estandar internacional con sensibilidad local en cada geografia."},
]


@router.get("/about")
def about(request: Request):
    return templates.TemplateResponse(
        "about.html",
        base_ctx(request, timeline=TIMELINE, team=TEAM, alliances=ALLIANCES, values=VALUES),
    )
