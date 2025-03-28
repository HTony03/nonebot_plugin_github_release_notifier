from nonebot import require

require("nonebot_plugin_htmlrender")
import nonebot_plugin_htmlrender as htmlrender


async def text_to_pic(text: str):
    return await htmlrender.html_to_pic(
        html=text,
        screenshot_timeout=10000,
        viewport={'width': 600, 'height': 10}
    )
