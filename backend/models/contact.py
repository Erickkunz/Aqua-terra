from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ContactSubmission(Base):
    __tablename__ = "contact_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(60), default="")
    inquiry_type: Mapped[str] = mapped_column(String(60), default="general")
    pillar: Mapped[str] = mapped_column(String(60), default="")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class QuoteRequest(Base):
    __tablename__ = "quote_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(200), default="")
    phone: Mapped[str] = mapped_column(String(60), default="")
    country: Mapped[str] = mapped_column(String(80), default="")
    items: Mapped[list] = mapped_column(JSON, default=list)  # [{product_id, qty, name, price}]
    estimated_total: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(60), default="footer")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
