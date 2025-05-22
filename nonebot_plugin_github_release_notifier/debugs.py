from nonebot import CommandGroup
from nonebot.params import CommandArg
from .pic_process import md_to_pic
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, Message, MessageEvent

def checker() -> bool:
    from . import DEBUG
    return DEBUG

debugs = CommandGroup('debugs',
                      rule=checker,)

@debugs.command('markdown').handle()
async def markdown(bot:Bot, event: MessageEvent, args: Message = CommandArg()
) -> None:
    """
    Convert markdown text to image and send it.
    """
    pic: bytes = await md_to_pic(args.extract_plain_text())
    await bot.send(event, MessageSegment.image(pic))
