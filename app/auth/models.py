from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils import UserSex, uuid_pk


class User(Base):
    __tablename__ = "base_user"

    user_id: Mapped[uuid_pk]
    telegram_id: Mapped[int]
    name: Mapped[str]
    age: Mapped[int] = mapped_column(nullable=True)
    sex: Mapped[UserSex] = mapped_column(Enum(UserSex), nullable=True)
