from nonebot import require

require("nonebot_plugin_htmlrender")
# pylint: disable=wrong-import-position
import nonebot_plugin_htmlrender as htmlrender


async def html_to_pic(html: str) -> bytes:
    """
    Converts text into image

    :arg html: The HTML content to be rendered into an image.
    :returns: The generated image in bytes format.
    """
    return await htmlrender.html_to_pic(
        html=html,
        screenshot_timeout=10000,
        viewport={'width': 300, 'height': 10}
    )


async def md_to_pic(md_text: str) -> bytes:
    """
    Converts the given Markdown text into an image.

    :arg md_text: The Markdown text to be rendered into an image.
    :returns: The generated image in bytes format.
    """
    md_text = md_text.replace("\n", "\n\r\n")
    from .config import CACHE_DIR
    with open(f"{CACHE_DIR}/md_text.md", "w", encoding="utf-8") as f:
        f.write(md_text)

    return await htmlrender.md_to_pic(md=md_text)
