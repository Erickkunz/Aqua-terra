from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models import BlogPost
from schemas import NewsletterIn
from models import NewsletterSubscriber
from ._common import templates, base_ctx

import logging
logger = logging.getLogger("aquaterra.blog")

router = APIRouter()


@router.get("/blog")
def blog_index(
    request: Request,
    db: Session = Depends(get_db),
    category: str | None = None,
    search: str | None = None,
):
    q = db.query(BlogPost)
    if category:
        q = q.filter(BlogPost.category == category)
    if search:
        like = f"%{search}%"
        q = q.filter(BlogPost.title.ilike(like) | BlogPost.excerpt.ilike(like))
    posts = q.order_by(BlogPost.publish_date.desc()).all()
    categories = sorted({p.category for p in db.query(BlogPost).all() if p.category})
    return templates.TemplateResponse(
        "blog.html",
        base_ctx(request, posts=posts, categories=categories, filters={"category": category or "", "search": search or ""}),
    )


@router.get("/blog/{slug}")
def blog_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    post = db.query(BlogPost).filter(BlogPost.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    related = db.query(BlogPost).filter(BlogPost.id != post.id).order_by(BlogPost.publish_date.desc()).limit(3).all()
    return templates.TemplateResponse("blog_detail.html", base_ctx(request, post=post, related=related))


@router.post("/newsletter/subscribe")
def newsletter_subscribe(payload: NewsletterIn, db: Session = Depends(get_db)):
    existing = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.email == payload.email).first()
    if existing:
        return {"ok": True, "already": True}
    sub = NewsletterSubscriber(email=payload.email, source=payload.source)
    db.add(sub)
    db.commit()
    logger.info("[NEWSLETTER] new subscriber: %s (source=%s)", payload.email, payload.source)
    return {"ok": True, "already": False}
