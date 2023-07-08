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

    __table_args__ = (UniqueConstraint("chat_id", "user_id"),)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, chat_id={self.chat_id!r}, user_id={self.user_id!r})"


def garbage_collect_currencies(session: Session):
    logger.info("garbage_collect_currencies")
    result = session.scalars(
        select(Currency).outerjoin(Point).where(Point.currency_id.is_(None))
    )
    if result:
        logger.info("Deleting orphaned currencies:")
        for row in result:
            logger.info(row)
            session.delete(row)
    else:
        logger.info("Nothing to delete")


def create_all():
    Base.metadata.create_all(database.engine)
