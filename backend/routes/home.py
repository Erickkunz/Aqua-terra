from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Project, Testimonial, Product
from ._common import templates, base_ctx

router = APIRouter()


@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    featured_projects = (
        db.query(Project).order_by(Project.is_featured.desc(), Project.completion_date.desc()).limit(4).all()
    )
    testimonials = db.query(Testimonial).filter(Testimonial.is_featured == True).limit(5).all()  # noqa: E712
    if not testimonials:
        testimonials = db.query(Testimonial).limit(5).all()

    featured_products = db.query(Product).filter(Product.is_featured == True).limit(4).all()  # noqa: E712

    stats = {
        "water_saved_m3": int(db.query(func.coalesce(func.sum(Project.water_saved_m3), 0)).scalar() or 0),
        "hectares": int(db.query(func.coalesce(func.sum(Project.hectares), 0)).scalar() or 0),
        "co2_reduced_t": int(db.query(func.coalesce(func.sum(Project.co2_reduced_t), 0)).scalar() or 0),
        "projects_total": db.query(Project).count(),
        "countries": db.query(func.count(func.distinct(Project.country))).scalar() or 0,
    }

    return templates.TemplateResponse(
        "home.html",
        base_ctx(
            request,
            featured_projects=featured_projects,
            testimonials=testimonials,
            featured_products=featured_products,
            stats=stats,
        ),
    )
