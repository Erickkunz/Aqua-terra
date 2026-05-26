from fastapi import APIRouter, Depends, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Project
from ._common import templates, base_ctx

router = APIRouter()


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    projects = db.query(Project).all()

    totals = {
        "water_saved_m3": int(sum(p.water_saved_m3 for p in projects)),
        "hectares": int(sum(p.hectares for p in projects)),
        "co2_reduced_t": int(sum(p.co2_reduced_t for p in projects)),
        "projects": len(projects),
        "countries": len({p.country for p in projects if p.country}),
    }

    by_country = {}
    for p in projects:
        c = p.country or "Otros"
        by_country.setdefault(c, {"projects": 0, "hectares": 0, "water_saved_m3": 0})
        by_country[c]["projects"] += 1
        by_country[c]["hectares"] += p.hectares
        by_country[c]["water_saved_m3"] += p.water_saved_m3
    by_country_list = sorted(
        [{"country": k, **v} for k, v in by_country.items()],
        key=lambda r: r["water_saved_m3"],
        reverse=True,
    )

    by_year = {}
    for p in projects:
        y = p.completion_date.year if p.completion_date else 0
        by_year.setdefault(y, {"projects": 0, "water_saved_m3": 0})
        by_year[y]["projects"] += 1
        by_year[y]["water_saved_m3"] += p.water_saved_m3
    growth = sorted(
        [{"year": k, **v} for k, v in by_year.items() if k],
        key=lambda r: r["year"],
    )

    by_tech = {}
    for p in projects:
        t = p.technology or "otros"
        by_tech[t] = by_tech.get(t, 0) + 1
    tech_distribution = [{"label": k, "value": v} for k, v in by_tech.items()]

    map_points = [
        {
            "name": p.name,
            "lat": p.latitude,
            "lng": p.longitude,
            "country": p.country,
            "hectares": p.hectares,
            "water_saved_m3": p.water_saved_m3,
            "slug": p.slug,
        }
        for p in projects
        if p.latitude and p.longitude
    ]

    return templates.TemplateResponse(
        "dashboard.html",
        base_ctx(
            request,
            totals=totals,
            by_country=by_country_list,
            growth=growth,
            tech_distribution=tech_distribution,
            map_points=map_points,
        ),
    )
