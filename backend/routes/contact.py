from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from database import get_db
from models import ContactSubmission
from schemas import ContactIn
from ._common import templates, base_ctx

import logging
logger = logging.getLogger("aquaterra.contact")

router = APIRouter()


OFFICES = [
    {"city": "Lima", "country": "Peru", "address": "Av. Javier Prado Este 1234, San Isidro", "phone": "+51 1 234 5678", "email": "lima@aquaterra.com", "lat": -12.0931, "lng": -77.0466},
    {"city": "Ciudad de Mexico", "country": "Mexico", "address": "Av. Reforma 222, Cuauhtemoc", "phone": "+52 55 1234 5678", "email": "mexico@aquaterra.com", "lat": 19.4326, "lng": -99.1332},
    {"city": "Bogota", "country": "Colombia", "address": "Cra 11 #82-01, Bogota", "phone": "+57 1 234 5678", "email": "bogota@aquaterra.com", "lat": 4.7110, "lng": -74.0721},
    {"city": "Santiago", "country": "Chile", "address": "Av. Apoquindo 4500, Las Condes", "phone": "+56 2 2345 6789", "email": "santiago@aquaterra.com", "lat": -33.4489, "lng": -70.6693},
]


@router.get("/contact")
def contact_page(request: Request, inquiry: str = "general", pillar: str = ""):
    return templates.TemplateResponse(
        "contact.html",
        base_ctx(request, offices=OFFICES, preselect_inquiry=inquiry, preselect_pillar=pillar),
    )


@router.post("/contact/submit")
def contact_submit(payload: ContactIn, db: Session = Depends(get_db)):
    sub = ContactSubmission(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        inquiry_type=payload.inquiry_type,
        pillar=payload.pillar,
        message=payload.message,
    )
    db.add(sub)
    db.commit()
    logger.info(
        "[CONTACT] #%s %s <%s> inquiry=%s pillar=%s",
        sub.id, payload.name, payload.email, payload.inquiry_type, payload.pillar,
    )
    return {"ok": True, "id": sub.id}
