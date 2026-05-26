from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models import Project, Product
from ._common import templates, base_ctx, PILLARS, get_pillar

router = APIRouter()


@router.get("/pillars")
def pillars_index(request: Request):
    return templates.TemplateResponse("pillars/index.html", base_ctx(request))


@router.get("/pillars/{slug}")
def pillar_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    pillar = get_pillar(slug)
    if not pillar:
        raise HTTPException(status_code=404, detail="Pilar no encontrado")

    related_projects = db.query(Project).limit(3).all()
    related_products = []
    if slug == "materiales":
        related_products = db.query(Product).filter(Product.is_featured == True).limit(6).all()  # noqa: E712

    template = f"pillars/{slug}.html"
    return templates.TemplateResponse(
        template,
        base_ctx(
            request,
            pillar=pillar,
            related_projects=related_projects,
            related_products=related_products,
        ),
    )
