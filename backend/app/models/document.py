from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Text, Index
from datetime import datetime
from app.models.base import Base

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(1024), unique=True)
    source: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(1024))
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    clean_text: Mapped[str] = mapped_column(Text)
    text_hash: Mapped[str] = mapped_column(String(64), index=True)   # sha256
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    tickers = relationship("DocTicker", back_populates="document")

Index("ix_documents_source_pub", Document.source, Document.published_at)