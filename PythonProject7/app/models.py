from datetime import datetime
from enum import Enum

from sqlalchemy import (
    BigInteger, Column, Integer, String, Text, DateTime, ForeignKey,
    Enum as SAEnum, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base


# ENUM статусов модерации
class PerevalStatus(str, Enum):
    new = "new"
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class AppUser(Base):
    __tablename__ = "app_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fam: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    otc: Mapped[str | None] = mapped_column(String(255), nullable=True)

    perevals = relationship("PerevalAdded", back_populates="user")


class Coords(Base):
    __tablename__ = "coords"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="coords_lat_check"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="coords_lon_check"),
        CheckConstraint("height IS NULL OR height BETWEEN -500 AND 9000", name="coords_height_check"),
    )

    pereval = relationship("PerevalAdded", back_populates="coords", uselist=False)


class Level(Base):
    __tablename__ = "level"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    winter: Mapped[str | None] = mapped_column(String(3), nullable=True)
    spring: Mapped[str | None] = mapped_column(String(3), nullable=True)
    summer: Mapped[str | None] = mapped_column(String(3), nullable=True)
    autumn: Mapped[str | None] = mapped_column(String(3), nullable=True)


class PerevalAdded(Base):
    __tablename__ = "pereval_added"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("app_user.id", ondelete="RESTRICT"), nullable=False)
    coords_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("coords.id", ondelete="RESTRICT"), nullable=False)
    level_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("level.id", ondelete="SET NULL"), nullable=True)

    beauty_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    other_titles: Mapped[str | None] = mapped_column(Text, nullable=True)
    connect: Mapped[str | None] = mapped_column(Text, nullable=True)

    add_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    status: Mapped[PerevalStatus] = mapped_column(
        SAEnum(PerevalStatus, name="pereval_status", native_enum=True),
        nullable=False,
        default=PerevalStatus.new
    )

    user = relationship("AppUser", back_populates="perevals")
    coords = relationship("Coords", back_populates="pereval")
    level = relationship("Level")
    images = relationship("Image", back_populates="pereval", cascade="all, delete-orphan")


class Image(Base):
    __tablename__ = "image"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pereval_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("pereval_added.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("pereval_id", "url", name="uq_image_pereval_url"),
    )

    pereval = relationship("PerevalAdded", back_populates="images")