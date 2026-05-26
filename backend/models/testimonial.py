from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Testimonial(Base):
    __tablename__ = "testimonials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_name: Mapped[str] = mapped_column(String(160), nullable=False)
    client_role: Mapped[str] = mapped_column(String(200), default="")
    company: Mapped[str] = mapped_column(String(160), default="")
    text: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, default=5)
    image_url: Mapped[str] = mapped_column(String(400), default="")
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
