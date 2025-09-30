from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Float
from app.models.base import Base

class DocTicker(Base):
    __tablename__ = "doc_tickers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doc_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    ticker: Mapped[str] = mapped_column(String(10), index=True)
    relevance: Mapped[float] = mapped_column(Float, default=1.0)

    document = relationship("Document", back_populates="tickers")


class DocTicker(Base):
    __tablename__ = "doc_tickers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doc_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    ticker: Mapped[str] = mapped_column(String(10), index=True)
    relevance: Mapped[float] = mapped_column(Float, default=1.0)

    document = relationship("Document", back_populates="tickers")