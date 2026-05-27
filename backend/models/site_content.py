"""Key-value store for editable page texts (hero, about, footer, etc.)."""
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class SiteContent(Base):
    __tablename__ = "site_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # logical key like "home.hero.title", "about.mission", "footer.tagline"
    key: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, default="")
    label: Mapped[str] = mapped_column(String(160), default="")
    section: Mapped[str] = mapped_column(String(60), default="general", index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
