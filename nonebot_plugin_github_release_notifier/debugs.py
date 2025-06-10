# pylint: disable=missing-module-docstring
from nonebot import CommandGroup
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, Message, MessageEvent, GroupMessageEvent
import ast

from .pic_process import md_to_pic
from .repo_activity import send_release_files


def checker() -> bool:  # pylint: disable=missing-function-docstring
    from . import DEBUG
    return DEBUG


debugs = CommandGroup(
    "debugs",
    rule=checker,
)


@debugs.command("markdown").handle()
async def markdown(
    bot: Bot, event: MessageEvent, args: Message = CommandArg()
) -> None:
    """
    Convert Markdown text to image and send it.
    """
    pic: bytes = await md_to_pic(args.extract_plain_text())
    await bot.send(event, MessageSegment.image(pic))


@debugs.command("release").handle()
async def release(
    bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()
) -> None:
    """
    Send release files to the group.
    """
    if not args:
        await bot.send(event, "No release files specified.")
        return

    try:
        files = ast.literal_eval(args.extract_plain_text())
        if not isinstance(files, list):
            raise ValueError
    except Exception:
        await bot.send(event, "参数格式错误，请输入合法的列表。")
        return

    await send_release_files(bot, event.group_id, files)
