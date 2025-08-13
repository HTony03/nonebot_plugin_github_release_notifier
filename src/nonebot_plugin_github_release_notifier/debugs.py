# pylint: disable=missing-module-docstring
import aiohttp
from nonebot import CommandGroup, logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, Message, MessageEvent, GroupMessageEvent

from .pic_process import md_to_pic
from .repo_activity_new import send_release_files


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


@debugs.command("render").handle()
async def render(
        bot: Bot, event: GroupMessageEvent
) -> None:
    """
    Send release files to the group.
    """
    from .repo_activity_new import github
    from .renderer import issue_commented_to_image
    from nonebot.adapters.onebot.v11 import MessageSegment
    from githubkit.exception import PrimaryRateLimitExceeded
    logger.info(f"current auth: {github.auth.__class__}")
    owner, repo_name = 'KuaYueTeam/NeoKuayue'.split('/')
    issue_number = 9
    try:
        repo_response = await github.rest.repos.async_get(owner=owner, repo=repo_name)
        repo = repo_response.parsed_data
        issue_response = await github.rest.issues.async_get(
            owner=owner, repo=repo_name, issue_number=issue_number
        )
        issue = issue_response.parsed_data
        logger.info((await github.rest.issues.async_list_for_repo(owner=owner, repo=repo_name)).parsed_data)
        logger.info(repo.__repr__())
        comments_response = await github.rest.issues.async_list_comments(
            owner=owner, repo=repo_name, issue_number=issue_number
        )
        comments = comments_response.parsed_data
        if not comments:
            await bot.send(event, "This issue has no comments to render.")
            return
        comment = comments[-1]
        image_bytes = await issue_commented_to_image(repo, issue, comment)
        await bot.send(event, MessageSegment.image(image_bytes))
    except PrimaryRateLimitExceeded as e:
        logger.opt(exception=True).error(
            "GitHub API rate limit exceeded. Please try again later."
        )
        await bot.send(event, "GitHub API rate limit exceeded. Please try again later.")
    except Exception as e:
        logger.opt(exception=True).error(f"Failed to render or send image: {e}")
        await bot.send(event, f"An error occurred: {e}")

@debugs.command('render2').handle()
async def deeee(bot:Bot, event: MessageEvent):
    from .repo_activity_new import github
    from .renderer import issue_to_image
    from nonebot.adapters.onebot.v11 import MessageSegment
    from githubkit.exception import PrimaryRateLimitExceeded
    logger.info(f"current auth: {github.auth.__class__}")
    owner, repo_name = 'KuaYueTeam/NeoKuayue'.split('/')
    dat = (await github.rest.issues.async_list_for_repo(
            owner=owner, repo=repo_name, state="all",sort="created",per_page=1000)).parsed_data
    await bot.send(event, MessageSegment.image(await issue_to_image(dat[0])))

@debugs.command('render3').handle()
async def deeee(bot:Bot, event: MessageEvent):
    from .repo_activity_new import github
    from .renderer import issue_to_image
    from .repo_activity_new import committer
    from nonebot.adapters.onebot.v11 import MessageSegment
    from githubkit.exception import PrimaryRateLimitExceeded
    logger.info(f"current auth: {github.auth.__class__}")
    owner, repo_name = 'KuaYueTeam/NeoKuayue'.split('/')
    await committer(repo_name, owner,"issues",977787918,bot)