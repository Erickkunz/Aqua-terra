from datetime import date, datetime
from sqlalchemy import String, Integer, Float, Date, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(String(320), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    country: Mapped[str] = mapped_column(String(80), default="")
    region: Mapped[str] = mapped_column(String(120), default="")
    latitude: Mapped[float] = mapped_column(Float, default=0.0)
    longitude: Mapped[float] = mapped_column(Float, default=0.0)
    client_type: Mapped[str] = mapped_column(String(80), default="")  # agro, municipal, industrial
    technology: Mapped[str] = mapped_column(String(80), default="")  # drip, pivot, iot...
    water_saved_m3: Mapped[float] = mapped_column(Float, default=0.0)
    hectares: Mapped[float] = mapped_column(Float, default=0.0)
    co2_reduced_t: Mapped[float] = mapped_column(Float, default=0.0)
    duration_months: Mapped[int] = mapped_column(Integer, default=6)
    completion_date: Mapped[date] = mapped_column(Date, default=date.today)
    image_before: Mapped[str] = mapped_column(String(400), default="")
    image_after: Mapped[str] = mapped_column(String(400), default="")
    gallery: Mapped[list] = mapped_column(JSON, default=list)
    testimonial_text: Mapped[str] = mapped_column(Text, default="")
    testimonial_author: Mapped[str] = mapped_column(String(160), default="")
    is_featured: Mapped[bool] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
