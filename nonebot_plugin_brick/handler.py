from asyncio import create_task

from arclet.alconna import Alconna
from nonebot import get_driver, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.message import event_preprocessor
from nonebot_plugin_alconna import (
    CommandMeta,
    Subcommand,
    Target,
    UniMessage,
    on_alconna,
)
from nonebot_plugin_orm import get_session
from sqlalchemy import select

# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .config import plugin_config as config
from .models import Brick

driver = get_driver()

burn_states: dict[tuple[str, str], dict] = {}

# engine = create_async_engine(echo=False)

# AsyncSession = async_sessionmaker(
#     engine,
#     expire_on_commit=False
# )

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
async def _(event: GroupMessageEvent, session=get_session()):
    # 查砖，满了不能烧
    result = await session.execute(
        select(Brick).where(
            Brick.user_id == event.user_id, Brick.group_id == event.group_id
        )
    )
    brick_data = result.scalar_one_or_none()

    if not brick_data:
        # 创建记录
        logger.info(f"创建砖头记录: {event.group_id}:{event.user_id}")
        brick_data = Brick(user_id=event.user_id, group_id=event.group_id, bricks=0)
        session.add(brick_data)
        await session.commit()
    elif brick_data.bricks >= config.max_brick:
        await brick_matcher.finish(f"你最多只能拥有{config.max_brick}块砖")

    # 烧砖
    burn_states[(str(event.group_id), str(event.user_id))] = {
        "burning": True,
        "count": 0,
    }

    await brick_matcher.send(
        f"现在开始烧砖啦，群友每发送{config.cost}条消息就烧好一块砖"
    )


@brick_matcher.assign("拍人")
async def _(event: GroupMessageEvent):
    await brick_matcher.send("[TODO] 咕咕")


@brick_matcher.assign("随机拍人")
async def _(event: GroupMessageEvent):
    await brick_matcher.send("[TODO] 咕咕")


@brick_matcher.assign("查看")
async def _(event: GroupMessageEvent, session=get_session()):
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
async def _(event: GroupMessageEvent):
    await brick_matcher.send("[TODO] 咕咕")


@event_preprocessor
async def burn_brick_counter(event: GroupMessageEvent, bot: Bot):
    if not burn_states:
        logger.debug("无人烧砖")
        return

    logger.debug("开始检查烧砖状态")

    sender_id = str(event.user_id)
    group_id = str(event.group_id)

    for key, state in list(burn_states.items()):
        g, u = key
        if g != group_id:
            continue
        if sender_id == str(bot.self_id) or sender_id == u:
            continue
        state["count"] += 1
        logger.debug(f"{g}:{u} 消息: {state['count']}")

        if state["count"] >= config.cost:
            # db 砖 +1
            create_task(commit_brick(g, u))
            state["count"] = 0
            del burn_states[key]


async def commit_brick(group_id: str, user_id: str):
    async with get_session() as session:
        result = await session.execute(
            select(Brick).where(Brick.group_id == group_id, Brick.user_id == user_id)
        )
        brick = result.scalar_one_or_none()

        if brick:
            # 直接增加一块砖（前面已创建记录并检查上限）
            brick.bricks += 1
            logger.info(f"{group_id}:{user_id} 烧砖完成，更新数据库: {brick.bricks} 砖")
            await session.commit()
            # 下面这个是典型的 OneBot V11 思维
            # await bot.send_group_msg(
            #     group_id=int(group_id),
            #     message=MessageSegment.at(user_id) + "砖已经烧好啦",
            # )
            # 用 UniMessage 发送还跨平台
            msg = UniMessage.at(user_id).text(" 砖已经烧好啦")
            await msg.send(target=Target.group(group_id))
        else:
            logger.warning(f"{group_id}:{user_id} 烧砖完成但未找到记录，跳过数据库更新")
