from nonebot_plugin_orm import Model
from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class Brick(Model):
    __tablename__ = "brick"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    group_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    bricks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_slap: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    checking_day: Mapped[str] = mapped_column(String(32), default="", nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "group_id", name="uq_user_group"),)
