from pydantic import BaseModel, Field


class ScopedConfig(BaseModel):
    max_brick: int = 1
    cost: int = 10
    cooldown: int = 60
    min_mute_time: int = 10
    max_mute_time: int = 120
    reverse: int = Field(default=10, ge=0, le=100)
    special_user: dict[str, int] = {}
    checking: bool = False
    min_gain: int = 1
    max_gain: int = 5


class Config(BaseModel):
    brick: ScopedConfig
