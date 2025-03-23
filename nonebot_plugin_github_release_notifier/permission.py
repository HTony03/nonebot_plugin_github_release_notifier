from nonebot import logger
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import MessageEvent

# -----------------------------Permisssion&exclusive only commands---------------------------
async def permission_check(event:MessageEvent, bot: Bot):
    if isinstance(event, PrivateMessageEvent):
        return False
    group_id = event.group_id
    id = event.user_id
    member = await bot.get_group_member_info(group_id=group_id,
                                                             user_id=id)
    '''
    temp_member = member
    temp_member.pop('sex')
    temp_member.pop('age')
    temp_member.pop('title_expire_time')
    temp_member.pop('last_sent_time')
    temp_member.pop('area')
    temp_member.pop('level')
    temp_member.pop('qq_level')
    temp_member.pop('join_time')
    temp_member.pop('is_robot')
    temp_member.pop('card_changeable')
    temp_member.pop('shut_up_timestamp')
    logger.debug(temp_member)'''
    
    if member['role'] == 'admin' or \
        member['role'] == 'owner':
        return True
    else:
        return False
