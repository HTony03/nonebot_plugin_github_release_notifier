from nonebot import require

require("nonebot_plugin_htmlrender")
# pylint: disable=wrong-import-position 
import nonebot_plugin_htmlrender as htmlrender


async def text_to_pic(text: str):
    """
    Converts the given text into an image using the htmlrender plugin.

    Args:
        text (str): The HTML content to be rendered into an image.

    Returns:
        The generated image in bytes format.
        type: bytes
    """
    return await htmlrender.html_to_pic(
        html=text,
        screenshot_timeout=10000,
        viewport={'width': 300, 'height': 10}
    )
