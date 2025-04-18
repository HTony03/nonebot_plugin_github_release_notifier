from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import MessageEvent


async def permission_check(event: MessageEvent, bot: Bot):
    if not isinstance(event, GroupMessageEvent):
        return False
    group_id = event.group_id
    user_id = event.user_id
    member = await bot.get_group_member_info(group_id=group_id,
                                             user_id=user_id)

    return member['role'] == 'admin' or \
            member['role'] == 'owner'
