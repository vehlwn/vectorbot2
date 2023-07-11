from datetime import datetime
import typing
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
)
from sqlalchemy import ForeignKey, UniqueConstraint, select

import database
from settings import settings
from logger import logger


class Base(DeclarativeBase):
    pass


class Currency(Base):
    __tablename__ = "currencies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    def __repr__(self) -> str:
        return f"Currency(id={self.id!r}, name={self.name!r})"


class Point(Base):
    __tablename__ = "points"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int]
    currency_id = mapped_column(ForeignKey("currencies.id", ondelete="CASCADE"))
    user_id = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    currency: Mapped["Currency"] = relationship()

    __table_args__ = (UniqueConstraint("currency_id", "user_id"),)

    def __repr__(self) -> str:
        return f"Point(id={self.id!r}, value={self.value!r}, currency_id={self.currency_id!r}, user_id={self.user_id!r})"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int]
    user_id: Mapped[int]

    points: Mapped[typing.List["Point"]] = relationship(cascade="all, delete-orphan")
    token_bucket: Mapped["TokenBucket"] = relationship(cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("chat_id", "user_id"),)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, chat_id={self.chat_id!r}, user_id={self.user_id!r})"


class TokenBucket(Base):
    __tablename__ = "token_buckets"
    id: Mapped[int] = mapped_column(primary_key=True)
    current_size: Mapped[float] = mapped_column(nullable=False)
    last_refill: Mapped[datetime] = mapped_column(nullable=False)
    user_id = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    def __repr__(self) -> str:
        return "TokenBucket(id={!r}, current_size={!r}, last_refill={!r}, user_id={!r})".format(
            self.id, self.current_size, self.last_refill, self.user_id
        )

    def consume(self, N: float) -> bool:
        if N > settings.POINTS_BURST_SIZE:
            return False

        self._refill()
        if N <= self.current_size:
            self.current_size -= N
            return True
        return False

    def _refill(self):
        now = datetime.utcnow()
        time_elapsed = (now - self.last_refill).total_seconds()
        tokens_to_add = time_elapsed * settings.POINTS_REFILL_RATE
        self.current_size = min(
            settings.POINTS_BURST_SIZE, self.current_size + tokens_to_add
        )
        self.last_refill = now


def garbage_collect_currencies(session: Session):
    logger.info("garbage_collect_currencies")
    result = session.scalars(
        select(Currency).outerjoin(Point).where(Point.currency_id.is_(None))
    )
    logger.info("Deleting orphaned currencies:")
    for row in result:
        logger.info(row)
        session.delete(row)


def create_all():
    Base.metadata.create_all(database.engine)
