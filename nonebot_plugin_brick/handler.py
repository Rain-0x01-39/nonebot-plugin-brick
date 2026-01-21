from arclet.alconna import Alconna
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
)
from nonebot_plugin_alconna import CommandMeta, Subcommand, on_alconna
from nonebot_plugin_orm import async_scoped_session
from sqlalchemy import select

from .config import plugin_config as config
from .models import Brick

brick_alc = Alconna(
    "brick",
    meta=CommandMeta(
        description="功夫再好，一砖撂倒。群聊砖头娱乐插件",
        usage="砖头 <子命令>",
        example="砖头 查看\n砖头 签到\n砖头 拍人 @某人",
        compact=True,
    ),
)

brick_alc.add(
    Subcommand("烧砖", alias=["烧点砖头拍人", "烧砖"], help_text="烧点砖头拍人")
)

brick_alc.add(
    Subcommand(
        "拍人", alias=["拍人"], help_text="拍晕（禁言）对方随机时间，有概率被反将一军"
    )
)

brick_alc.add(
    Subcommand(
        "随机拍人",
        alias=["随机拍人"],
        help_text="随机拍晕（禁言）某个群友随机时间，有概率被反将一军",
    )
)

brick_alc.add(
    Subcommand(
        "查看", alias=["查看砖头", "查砖"], help_text="看看自己在这个群有多少砖头"
    )
)

brick_alc.add(Subcommand("签到", alias=["砖头签到"], help_text="签到获取随机数量砖头"))


brick_matcher = on_alconna(
    brick_alc,
    aliases={"砖头", "砖块"},
    priority=10,
    block=True,
    use_cmd_start=True,
    auto_send_output=True,
)


@brick_matcher.assign("烧砖")
async def _(event: GroupMessageEvent, session: async_scoped_session):
    await brick_matcher.send("[TODO] 咕咕")


@brick_matcher.assign("拍人")
async def _(event: GroupMessageEvent, session: async_scoped_session):
    await brick_matcher.send("[TODO] 咕咕")


@brick_matcher.assign("随机拍人")
async def _(event: GroupMessageEvent, session: async_scoped_session):
    await brick_matcher.send("[TODO] 咕咕")


@brick_matcher.assign("查看")
async def _(event: GroupMessageEvent, session: async_scoped_session):
    user_id = event.user_id
    group_id = event.group_id

    # 从数据库查询用户砖头信息
    result = await session.execute(
        select(Brick).where(Brick.user_id == user_id, Brick.group_id == group_id)
    )
    brick_data = result.scalar_one_or_none()

    if brick_data:
        await brick_matcher.send(f"你有 {brick_data.bricks}/{config.max_brick} 块砖头")
    else:
        await brick_matcher.send("你还没有砖头，使用 /砖头 烧砖 烧点吧")


@brick_matcher.assign("签到")
async def _(event: GroupMessageEvent, session: async_scoped_session):
    await brick_matcher.send("[TODO] 咕咕")
