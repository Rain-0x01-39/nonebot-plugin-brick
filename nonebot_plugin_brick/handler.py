from asyncio import create_task
from random import choice, randint, random

from arclet.alconna import Alconna
from nonebot import logger
from nonebot.adapters import Bot
from nonebot.adapters.milky.event import GroupMessageEvent as MilkyGroupMessageEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent as OnebotGroupMessageEvent
from nonebot.message import event_preprocessor
from nonebot_plugin_alconna import (
    Args,
    Arparma,
    At,
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
        "拍人",
        Args["target", At],
        alias=["拍人"],
        help_text="拍晕（禁言）对方随机时间，有概率被反将一军",
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
async def _(
    event: OnebotGroupMessageEvent | MilkyGroupMessageEvent, session=get_session()
):
    # 查砖，满了不能烧
    result = await session.execute(
        select(Brick).where(
            Brick.user_id == event.get_user_id(), Brick.group_id == event.group_id
        )
    )
    brick_data = result.scalar_one_or_none()

    if not brick_data:
        # 创建记录
        logger.bind(group_id=event.group_id, user_id=event.get_user_id()).info(
            "创建砖头记录"
        )
        brick_data = Brick(
            user_id=event.get_user_id(), group_id=event.group_id, bricks=0
        )
        session.add(brick_data)
        await session.commit()
    elif brick_data.bricks >= config.max_brick:
        await brick_matcher.finish(f"你最多只能拥有{config.max_brick}块砖")

    if (str(event.group_id), str(event.get_user_id())) in burn_states:
        await brick_matcher.finish("已经在烧砖了")

    burn_states[(str(event.group_id), str(event.get_user_id()))] = {
        "burning": True,
        "msgcount": 0,
    }

    await brick_matcher.send(
        f"现在开始烧砖啦，群友每发送{config.cost}条消息就烧好一块砖"
    )


@brick_matcher.assign("拍人")
async def _(
    bot: Bot,
    event: OnebotGroupMessageEvent | MilkyGroupMessageEvent,
    args: Arparma,
    session=get_session(),
):
    target_id = str(args.target.target)
    await slap_user(bot, event, target_id, session)


@brick_matcher.assign("随机拍人")
async def _(
    bot: Bot,
    event: OnebotGroupMessageEvent | MilkyGroupMessageEvent,
    session=get_session(),
):
    group_member_list = await bot.get_group_member_list(group_id=int(event.group_id))
    candidates_user_id = [
        str(member["user_id"])
        for member in group_member_list
        if str(member["user_id"]) != event.get_user_id()  # 排除用户自己
        and str(member["user_id"]) != str(event.self_id)  # 排除机器人
        and not member.get("is_robot", False)  # 排除机器人账号 (官鸡?)
    ]
    target_id = choice(candidates_user_id)
    await slap_user(bot, event, target_id, session)


@brick_matcher.assign("查看")
async def _(
    event: OnebotGroupMessageEvent | MilkyGroupMessageEvent, session=get_session()
):
    group_id = event.group_id
    user_id = event.get_user_id()

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
async def _(
    event: OnebotGroupMessageEvent | MilkyGroupMessageEvent, session=get_session()
):
    from datetime import datetime

    group_id = event.group_id
    user_id = event.get_user_id()

    today = datetime.now().strftime("%Y-%m-%d")

    # 查询用户在该群的签到信息
    result = await session.execute(
        select(Brick).where(Brick.user_id == user_id, Brick.group_id == group_id)
    )
    brick_data = result.scalar_one_or_none()

    # 如果没有记录，创建新记录
    if not brick_data:
        logger.bind(group_id=group_id, user_id=user_id).info("创建砖头记录")
        brick_data = Brick(user_id=user_id, group_id=group_id, bricks=0)
        session.add(brick_data)
        await session.commit()
        await session.refresh(brick_data)

    # 检查是否已经签到
    if brick_data.checking_day == today:
        await brick_matcher.finish("你今天已经签到过了")

    # 随机获得砖头数量
    gain = randint(config.min_gain, config.max_gain)

    # 检查是否会超过最大砖头数
    if brick_data.bricks + gain > config.max_brick:
        gain = config.max_brick - brick_data.bricks
        if gain <= 0:
            await brick_matcher.finish("你的砖头已经到上限了，用掉再签到吧")

    # 更新签到信息
    new_bricks = brick_data.bricks + gain
    brick_data.bricks = new_bricks
    brick_data.checking_day = today
    await session.commit()

    logger.bind(group_id=group_id, user_id=user_id).info(
        "签到获得 {gain} 砖头", gain=gain
    )
    await brick_matcher.send(
        f"签到成功，你获得了 {gain} 块砖头，现在有{new_bricks}/{config.max_brick}块砖头"
    )


@event_preprocessor
async def burn_brick_counter(
    event: OnebotGroupMessageEvent | MilkyGroupMessageEvent, bot: Bot
):
    if not burn_states:
        logger.debug("无人烧砖")
        return

    logger.debug("开始检查烧砖状态")

    group_id = str(event.group_id)
    sender_id = str(event.get_user_id())

    for key, state in list(burn_states.items()):
        g, u = key
        if g != group_id:
            continue
        if sender_id == str(bot.self_id) or sender_id == u:
            continue
        state["msgcount"] += 1
        logger.bind(group_id=event.group_id, user_id=event.get_user_id()).debug(
            "烧砖消息计数 {msgcount}", msgcount=state["msgcount"]
        )

        if state["msgcount"] >= config.cost:
            # db 砖 +1
            create_task(commit_brick(g, u))
            state["msgcount"] = 0
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
            logger.bind(group_id=group_id, user_id=user_id).info(
                "烧砖完成，更新数据库 {bricks}砖", bricks=brick.bricks
            )
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
            logger.bind(group_id=group_id, user_id=user_id).warning(
                "烧砖完成但未找到记录，跳过数据库更新"
            )


async def slap_user(
    bot, event: OnebotGroupMessageEvent | MilkyGroupMessageEvent, target_id, session
):
    # 看看用户有没有砖头
    result = await session.execute(
        select(Brick).where(
            Brick.user_id == event.get_user_id(), Brick.group_id == event.group_id
        )
    )
    brick_data = result.scalar_one_or_none()
    if not brick_data or brick_data.bricks <= 0:
        await brick_matcher.finish("你在这个群还没有砖头，使用 /砖头 烧砖 烧点砖头吧")

    # 检查目标是否是自己
    if target_id == event.get_user_id():
        await brick_matcher.finish("不能拍自己哦")

    # 检查目标是否是机器人自己
    if target_id == str(bot.self_id):
        await brick_matcher.finish("不能拍机器人哦")

    # 检查目标是否已禁言
    # [TODO]

    rev_probability = config.special_user.get(target_id, config.reverse) / 100

    mute_time = randint(config.min_mute_time, config.max_mute_time)
    mute_target_id = target_id

    msg = (
        UniMessage.at(target_id)
        .text(" 你被 ")
        .at(event.get_user_id())
        .text(f" 拍晕了 {mute_time} 秒")
    )

    if random() < rev_probability:
        # 反拍：用户自己被禁言
        mute_target_id = event.get_user_id()
        msg = UniMessage.at(target_id).text(f" 夺过你的砖头，把你拍晕了 {mute_time} 秒")

    try:
        # 拍晕（禁言）用户
        await bot.set_group_ban(
            group_id=int(event.group_id),
            user_id=int(mute_target_id),
            duration=mute_time,
        )

        # 减少砖头数量
        brick_data.bricks -= 1
        await session.commit()

        await msg.send(target=event)
    except Exception:
        logger.opt(exception=True).error("禁言失败")
        await brick_matcher.finish("禁言失败，可能是权限不足或目标已被禁言")
