from contextlib import suppress

with suppress(ImportError):
    from nonebot.adapters.onebot.v11 import GroupMessageEvent as OnebotGroupMessageEvent

__all__ = ["OnebotGroupMessageEvent"]
