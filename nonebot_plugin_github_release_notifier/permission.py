from typing import Any
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import MessageEvent


async def check_group_admin(event: MessageEvent, bot: Bot) -> bool:
    '''
    Check if the user is a group admin or owner.
    
    Args:
        event (nonebot.adapters.onebot.v11.event.MessageEvent): The event to check.
        bot (nonebot.adapters.onebot.v11.bot.Bot): The bot instance.
    
    Returns:
        bool: True if the user is an admin or owner.
    '''
    if not isinstance(event, GroupMessageEvent):
        return False
    group_id: int = event.group_id
    user_id: int = event.user_id
    member: dict[str, Any] = await bot.get_group_member_info(group_id=group_id,
                                             user_id=user_id)

    return member.get('role','') == 'admin' or member.get('role','') == 'owner'
