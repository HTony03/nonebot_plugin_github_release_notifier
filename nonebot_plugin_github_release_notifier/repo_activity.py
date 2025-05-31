#pylint: disable=missing-module-docstring
from datetime import datetime
import ssl
import asyncio

import aiohttp
from nonebot import get_bot, get_driver
from nonebot.adapters.onebot.v11.message import Message
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, Message


from .db_action import (
    load_last_processed,
    save_last_processed,
    load_group_configs,
    change_group_repo_cfg,
)
from .config import config

# pylint: disable=wrong-import-position
from .pic_process import html_to_pic, md_to_pic
from .data import data_set

superusers: set[str] = get_driver().config.superusers

# Load GitHub token from environment variables
GITHUB_TOKEN: str | None = config.github_token
data_set.set("token", GITHUB_TOKEN)
max_retries: int = config.github_retries
delay: int = config.github_retry_delay
temp_disabled: dict = {}
# Global cache to store API responses
api_cache: dict = {}

default_sending_templates = {
    "commit": "📜 New Commit in {repo}\n\n"
              "Message: {message}\nAuthor: {author}\n"
              "Commit time: {time}\nURL: {url}",
    "issue": "🐛 **New Issue in {repo}!**\n\n"
             "Title: {title}\nAuthor: {author}\n"
             "Issue created time: {time}\nURL: {url}",
    "pull_req": "🔀 **New Pull Request in {repo}!**\n\n"
                "Title: {title}\nAuthor: {author}\n"
                "Pr created at: {time}\nURL: {url}",
    "release": "🚀 **New Release for {repo}!**\n\n"
               "**Name:** {name}\nVersion: {version}\n"
               "Details:\n {details}\nRelease time:{time}\nURL: {url}",
}
config_template: dict = config.github_sending_templates


async def validate_github_token(retries=3, retry_delay=5) -> None:
    """
    Validate the GitHub token by making a test request,
    with retries on SSL errors.
    """
    token: str | None = data_set.get("token")
    if not token:
        logger.warning(
            "No GitHub token provided. Proceeding without authentication."
        )
        return

    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    for _ in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.github.com/user", headers=headers
                ) as response:
                    if response.status == 200:
                        logger.info("GitHub token is valid.")
                        return
                    logger.error(
                                f"GitHub token validation failed: "
                                f"{response.status} - "
                                f"{await response.text()}"
                                )
                    token = None
                    data_set.set("token", token)
                    return
        except ssl.SSLError as e:
            logger.error(
                f"SSL error during GitHub token validation: {e}. "
                f"Retrying in {retry_delay} seconds..."
            )
            await asyncio.sleep(retry_delay)
        # pylint: disable=broad-exception-caught
        except Exception as e:
            logger.error(f"Error validating GitHub token: {e}")

    logger.error("GitHub token validation failed after multiple attempts.")
    token = None
    data_set.set("token", token)
    return

async def notify_qq(bot:Bot, group_id:int=0, user_id:int=0, message:Message=Message(MessageSegment.text(''))) -> None:
    """
    Send a message to a QQ group or user.
    """
    if not group_id and not user_id:
        raise ValueError("Either group_id or user_id must be provided.")
    try:
        if group_id:
            await bot.send_group_msg(group_id=group_id, message=message)
        elif user_id:
            await bot.send_private_msg(user_id=user_id, message=message)
    except Exception as e: #pylint: disable=broad-exception-caught
        recipient = f'group {group_id}' if group_id else f'user {user_id}'
        logger.error(f'failed to send message to {recipient}: {e}')



async def fetch_github_data(repo: str, endpoint: str) -> list | dict | None:
    """
    Fetch data from the GitHub API
    for a specific repo and endpoint.
    """
    cache = api_cache.get(repo, {}).get(endpoint, None)

    # Check if the data exists in the cache
    if cache is not None:
        logger.debug(f'Using cached data for {repo}/{endpoint}')
        if isinstance(cache, list) and cache and cache[0] == []:
            return []
        if isinstance(cache, (list, dict)):
            return cache
        # If cache is not list or dict, ignore and fetch from API

    # If not in cache, fetch from the API
    api_url = f"https://api.github.com/repos/{repo}/{endpoint}"
    headers = (
        {"Authorization": f"token {data_set.get('token')}"}
        if data_set.get("token")
        else {}
    )

    retries = 1
    errs: list = []
    while retries <= max_retries:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    api_cache.setdefault(repo, {})[endpoint] = data if data else [[]]
                    return data
        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP error while fetching GitHub {endpoint} for {repo} in attempt {retries}: {e}")
            errs.append(f'{e.__class__.__name__}: {e}')
        # pylint: disable=broad-exception-caught
        except Exception as e:
            logger.error(f"Unexpected error while fetching GitHub {endpoint} for {repo} in attempt {retries}: {e}")
            errs.append(f'{e.__class__.__name__}: {e}\nargs:{e.args}')
        await asyncio.sleep(delay)
        retries += 1

    return {
        "falt": f"Failed to fetch {endpoint} for {repo} after "
                f"{max_retries} attempts.",
        'errors': errs,
    }


async def notify(
    bot: Bot,
    group_id: int,
    repo: str,
    data: list,
    data_type: str,
    last_processed: dict,
) -> None:
    """Send notifications for new data (commits, issues, PRs, releases)."""
    latest_data: list = data[:3]
    for item in latest_data:
        times = item.get("created_at") or \
                     item.get("published_at") or \
                     item["commit"]["author"]["date"]

        item_time: datetime = datetime.fromisoformat(times)
        last_time: datetime = load_last_processed().get(repo, {}).get(data_type)
        if (
            not last_time or
            item_time > datetime.fromisoformat(
                last_time.replace("Z", "+00:00"))
        ):
            message:str = format_message(repo, item, data_type)
            try:
                if 'issue' == data_type and 'pull' in message:
                    pass
                else:
                    if data_type == 'release':
                        logger.info(item.get('body','None'))
                        msg: list[str] = message.split(item.get("body", "No description provided."))
                        message: MessageSegment = MessageSegment.text(msg[0]) + \
                            MessageSegment.image(await md_to_pic(item.get("body", "No description provided.").replace('\n', '<br>'))) + \
                            (MessageSegment.text(msg[1]) if msg[1] else MessageSegment.text(''))
                    else:
                        message = MessageSegment.text(message)
                    await bot.send_group_msg(group_id=group_id, message=Message(message))
            # pylint: disable=broad-exception-caught
            except Exception as e:
                logger.opt(colors=True).error(f"Failed to notify group {group_id} about {data_type} in {repo}: {e}")
                return

    last_processed.setdefault(repo, {})[data_type] = latest_data[0].get("created_at") or \
                                                     latest_data[0].get("published_at") or \
                                                     latest_data[0]["commit"]["author"]["date"]


def format_message(repo: str, item: dict, data_type: str) -> str:
    """Format the notification message based on the data type."""
    if data_type == "commit":
        datas = {
            "repo": repo,
            "message": item["commit"]["message"],
            "author": item["commit"]["author"]["name"],
            "url": item["html_url"],
            "time": item["commit"]["author"]["date"],
        }
    elif data_type == "issue":
        datas = {
            "repo": repo,
            "title": item["title"],
            "author": item["user"]["login"],
            "url": item["html_url"],
            "time": item["created_at"],
        }
    elif data_type == "pull_req":
        datas = {
            "repo": repo,
            "title": item["title"],
            "author": item["user"]["login"],
            "url": item["html_url"],
            "time": item["created_at"],
        }
    elif data_type == "release":
        datas = {
            "repo": repo,
            "name": item.get("name", "New Release"),
            "version": item.get("tag_name", "Unknown Version"),
            "details": item.get("body", "No description provided."),
            "url": item.get("html_url", "No URL"),
            "time": item.get("published_at", "Unknown time"),
        }
    else:
        return "Unknown data type."

    return config_template.get(
        data_type, default_sending_templates.get(data_type, "")
    ).format(**datas)


async def check_repo_updates() -> None:
    """Check for new commits, issues, PRs, and releases for all repos and notify groups."""
    global api_cache
    api_cache = {}
    try:
        bot: Bot = get_bot()
        last_processed = load_last_processed()
        group_repo_dict = data_set.get("group_repo_dict")
    # pylint: disable=broad-exception-caught
    except Exception:
        return

    # Reset disables at the start of each hour
    reset_temp_disabled_configs()

    for group_id, repo_configs in group_repo_dict.items():
        group_id = int(group_id)
        for repo_config in repo_configs:
            repo = repo_config["repo"]
            for data_type, endpoint in [("commit", "commits"), ("issue", "issues"), ("pull_req", "pulls"), ("release", "releases")]:
                if repo_config.get(data_type, False) and not temp_disabled.get((group_id, repo, data_type)):
                    # Fetch data (use cache if available)
                    data = await fetch_github_data(repo, endpoint)
                    if data and "falt" not in data:
                        await notify(
                            bot=bot,
                            group_id=group_id,
                            repo=repo,
                            data=data,
                            data_type=data_type,
                            last_processed=last_processed,
                        )
                    elif data and "falt" in data:
                        logger.error(data.get("falt", "Unknown error"))
                        if config.github_send_faliure_group:
                            try:
                                if any('403' in x for x in data.get("errors", [])):
                                    await notify_qq(
                                        bot, group_id=group_id, message=Message(
                                            MessageSegment.text(
                                                data.get('falt','Unknown error') + "\nGitHub API rate limit exceeded.\nProbably caused by invalid / no token."
                                            )
                                        )
                                    )
                                else:
                                    html = '<p>GitHub API Error:</p>'
                                    html += "".join(
                                        (
                                            "<p style='white-space=pre-wrap'>"
                                            + x.replace("\n", "<br>")
                                            + "</p>"
                                        )
                                        for x in data["errors"]
                                    )
                                    pic = await html_to_pic(html)
                                    await notify_qq(bot, group_id=group_id, message=Message(
                                        MessageSegment.image(pic)
                                    ))
                            # pylint: disable=broad-exception-caught
                            except Exception as e:
                                logger.error(
                                        f"Failed to notify group {group_id} "
                                        f"about the error: {e}"
                                )
                        if config.github_send_faliure_superuser:
                            for users in superusers:
                                try:
                                    if any('403' in x for x in data["errors"]):
                                        await notify_qq(
                                            bot, user_id=users, message=Message(
                                                MessageSegment.text(
                                                    data['falt'] + "\nGitHub API rate limit exceeded.\nProbably caused by invalid / no token."
                                                )
                                            )
                                        )
                                    else:
                                        html = '<p>GitHub API Error:</p>'
                                        html += "".join(
                                            "<p style='white-space=pre-wrap'>"
                                            + x.replace("\n", "<br>")
                                            + "</p>"
                                            for x in data["errors"]
                                        )
                                        pic = await html_to_pic(html)
                                        await notify_qq(
                                            bot, user_id=users, message=Message(
                                                MessageSegment.image(pic)
                                            )
                                        )
                                # pylint: disable=broad-exception-caught
                                except Exception as e:
                                    logger.error(
                                        "Failed to notify the superuser "
                                        "about the error: "
                                        f"{e}"
                                    )
                        if (
                            config.github_disable_when_fail
                            and any('SSL' in x for x in data["errors"])
                            and any('403' in x for x in data["errors"])
                        ):
                            repo_config[data_type] = False
                            change_group_repo_cfg(
                                group_id, repo, data_type, False
                            )
                        if any('403' in x for x in data['errors']) and config.github_disable_when_fail:
                            # Temporarily disable for this hour
                            logger.debug(
                                f"Temporarily disabling {data_type} notifications "
                                f"for {repo} in group {group_id} due to rate limit."
                            )
                            temp_disabled[(group_id, repo, data_type)] = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

    save_last_processed(last_processed)

def reset_temp_disabled_configs() -> None:
    """Reset configs to True if a new hour has started."""
    current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    to_reset = []
    for key, hour in temp_disabled.items():
        if hour < current_hour:
            to_reset.append(key)
    # Remove reset entries
    for key in to_reset:
        del temp_disabled[key]
