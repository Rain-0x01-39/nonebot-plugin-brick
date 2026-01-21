from arclet.alconna import Alconna
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
)
from nonebot_plugin_alconna import CommandMeta, on_alconna
from nonebot_plugin_orm import async_scoped_session
from sqlalchemy import select

from .config import plugin_config as config
from .models import Brick

brick_alc = Alconna(
    ["砖头", "砖块"],
    meta=CommandMeta(
        description="功夫再好，一砖撂倒。群聊砖头娱乐插件",
        usage="砖头 <子命令>",
        example="砖头 查看\n砖头 签到\n砖头 拍人 @某人",
        compact=True,
    )
)

# brick_alc.add(
#     Subcommand(
#         "查看",
#         alias=["查看砖头", "查砖"],
#         help_text="查看自己当前砖头数和冷却状态"
#     )
# )

brick_matcher = on_alconna(
    brick_alc,
    aliases={"砖头"},
    priority=10,
    block=True,
    use_cmd_start=True,
)

@brick_matcher.assign("查看")
async def _(event: GroupMessageEvent, session: async_scoped_session):
    user_id = event.user_id
    group_id = event.group_id
    
    # 从数据库查询用户砖头信息
    result = await session.execute(
        select(Brick).where(
            Brick.user_id == user_id,
            Brick.group_id == group_id
        )
    )
    brick_data = result.scalar_one_or_none()

    if brick_data:
        await brick_matcher.send(f"你有 {brick_data.bricks}/{config.max_brick} 块砖头")
    else:
        await brick_matcher.send("你还没有砖头，使用 /砖头 烧砖 烧点吧")