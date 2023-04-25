from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
import datetime
from sqlalchemy import func


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now())

    updated_at: Mapped[datetime.datetime] = mapped_column(onupdate=func.now())
