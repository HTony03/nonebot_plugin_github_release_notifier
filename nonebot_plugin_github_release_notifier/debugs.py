# pylint: disable=missing-module-docstring
import aiohttp
from nonebot import CommandGroup, logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, Message, MessageEvent, GroupMessageEvent

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
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.github.com/repos/{args.extract_plain_text()}/releases') as response:
                files = await response.json()

        await send_release_files(bot, event.group_id, files, True)
    except Exception as e:  # pylint: disable=broad-exception-caught
        await bot.send(event, f"Failed to send release files: {e}")
        logger.opt(exception=True).error(f"Failed to send release files: {e}")
