from typing import Literal
from nonebot.adapters.onebot.v11 import Bot
from nonebug import App
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class ANY:
    def __eq__(self, other) -> Literal[True]:
        return True


@pytest.mark.asyncio
async def test_add_repo(app: App) -> None:
    import nonebot
    from nonebot import require
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    assert require("nonebot_plugin_github_release_notifier")

    from nonebot.adapters.onebot.v11.event import MessageEvent
    from nonebot.adapters.onebot.v11 import Message

    event1 = MessageEvent(
        time=123456,
        self_id=123456,
        post_type="message",
        user_id=1234567890,
        message_type="group",
        message_id=1234567890,
        message=Message("/repo.add HTony03/nonebot_plugin_github_release_notifier"),
        raw_message="/repo.add HTony03/nonebot_plugin_github_release_notifier",
        original_message=Message("/repo.add HTony03/nonebot_plugin_github_release_notifier"),
        sub_type="normal",
        sender={"user_id": 1234567890, "nickname": "测试用户"},
        font=123,
    )
    event2 = MessageEvent(
        time=123456,
        self_id=123456,
        post_type="message",
        user_id=1234567890,
        message_type="group",
        message_id=1234567890,
        message=Message("/repo.refresh"),
        raw_message="/repo.refresh",
        original_message=Message("/repo.refresh"),
        sub_type="normal",
        sender={"user_id": 1234567890, "nickname": "测试用户"},
        font=123,
    )

    async with app.test_matcher() as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        ctx.receive_event(bot, event1)
        ctx.should_call_send(event1, ANY())
        ctx.receive_event(bot, event2)
        ctx.should_call_send(event2, ANY())
        ctx.should_finished()


@pytest.mark.asyncio
async def test_check_usage(app: App):
    import nonebot
    from nonebot import require
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    assert require("nonebot_plugin_github_release_notifier")

    # 构造 shell command 事件
    from nonebot.adapters.onebot.v11.event import MessageEvent
    from nonebot.adapters.onebot.v11 import Message

    event1 = MessageEvent(
        time=123456,
        self_id=123456,
        post_type="message",
        user_id=1234567890,
        message_type="group",
        message_id=1234567890,
        message=Message("/check_api_usage"),
        raw_message="/check_api_usage",
        original_message=Message("/check_api_usage"),
        sub_type="normal",
        sender={"user_id": 1234567890, "nickname": "测试用户"},
        font=123,
    )

    async with app.test_matcher() as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        ctx.receive_event(bot, event1)
        ctx.should_call_send(event1, ANY(), result=None, bot=bot)
        ctx.should_finished()

