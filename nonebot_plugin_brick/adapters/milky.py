from contextlib import suppress

with suppress(ImportError):
    from nonebot.adapters.milky.event import GroupMessageEvent as MilkyGroupMessageEvent

__all__ = ["MilkyGroupMessageEvent"]
