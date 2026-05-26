from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models import Project
from ._common import templates, base_ctx

router = APIRouter()


@router.get("/projects")
def projects_index(
    request: Request,
    db: Session = Depends(get_db),
    country: str | None = None,
    client_type: str | None = None,
    technology: str | None = None,
):
    q = db.query(Project)
    if country:
        q = q.filter(Project.country == country)
    if client_type:
        q = q.filter(Project.client_type == client_type)
    if technology:
        q = q.filter(Project.technology == technology)
    items = q.order_by(Project.completion_date.desc()).all()

    countries = sorted({p.country for p in db.query(Project).all() if p.country})
    client_types = sorted({p.client_type for p in db.query(Project).all() if p.client_type})
    technologies = sorted({p.technology for p in db.query(Project).all() if p.technology})

    map_points = [
        {
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "lat": p.latitude,
            "lng": p.longitude,
            "country": p.country,
            "hectares": p.hectares,
            "water_saved_m3": p.water_saved_m3,
        }
        for p in items
        if p.latitude and p.longitude
    ]

    return templates.TemplateResponse(
        "projects.html",
        base_ctx(
            request,
            projects=items,
            countries=countries,
            client_types=client_types,
            technologies=technologies,
            map_points=map_points,
            filters={"country": country or "", "client_type": client_type or "", "technology": technology or ""},
        ),
    )


@router.get("/projects/{slug}")
def project_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.slug == slug).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    related = db.query(Project).filter(Project.id != project.id).limit(3).all()
    return templates.TemplateResponse(
        "project_detail.html",
        base_ctx(request, project=project, related=related),
    )
