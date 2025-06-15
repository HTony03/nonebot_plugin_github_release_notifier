from datetime import datetime  # Standard library imports
import aiohttp  # Third-party imports

from nonebot import CommandGroup, on_command
from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER, Bot
from nonebot.adapters.onebot.v11.helpers import Cooldown
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
    MessageSegment,
)
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from .config import config
from .db_action import (
    add_group_repo_data,
    remove_group_repo_data,
    load_group_configs,
    change_group_repo_cfg,
)
from .pic_process import html_to_pic, md_to_pic


@on_command(
    "check_api_usage", aliases={"api_usage", "github_usage"}, priority=5
).handle(parameterless=[Cooldown(15, prompt="调用过快")])
async def handle_check_api_usage(bot: Bot, event: MessageEvent) -> None:
    """Fetch and send the remaining GitHub API usage limits."""
    headers = {}
    from .repo_activity import GITHUB_TOKEN
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    api_url = "https://api.github.com/rate_limit"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()

                # Extract rate limit information
                rate_limit = data.get("rate", {})
                remaining = rate_limit.get("remaining", "Unknown")
                limit = rate_limit.get("limit", "Unknown")
                reset_time = rate_limit.get("reset", "Unknown")

                # Format the reset time if available
                if reset_time != "Unknown":
                    reset_time = datetime.fromtimestamp(reset_time).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                message = (
                    f"**GitHub API Usage**\n"
                    f"Remaining: {remaining}\n"
                    f"Limit: {limit}\n"
                    f"Reset Time: {reset_time}"
                )
                await bot.send(event, message=MessageSegment.text(message))
    except aiohttp.ClientResponseError as e:
        error_message = (
            f"Failed to fetch GitHub API usage: {e.status} - {e.message}"
        )
        logger.error(error_message)
        await bot.send(event, message=MessageSegment.text(error_message))
    except Exception as e:  # pylint: disable=broad-exception-caught
        fatal_message = f"Fatal error while fetching GitHub API usage: {e}"
        logger.error(fatal_message)
        await bot.send(event, message=MessageSegment.text(fatal_message))


def link_to_repo_name(link: str) -> str:
    """Convert a repository link to its name."""
    repo = link.replace("https://", "") \
        .replace("http://", "") \
        .replace(".git", "")
    if len(repo.split("/")) == 2:
        return repo
    return "/".join(repo.split("/")[1:3])


# Create a command group for repository management
repo_group = CommandGroup(
    "repo",
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=5
)


@on_command(
    'add_group_repo',
    aliases={'add_repo'},
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER
).handle()
@repo_group.command("add").handle()
async def add_repo(
        bot: Bot, event: MessageEvent, args: Message = CommandArg()
):
    """Add a new repository mapping."""
    command_args = args.extract_plain_text().split()
    if len(command_args) < 1:
        await bot.send(event, "Usage: repo add <repo> [group_id]")
        return

    repo = link_to_repo_name(command_args[0])
    group_id = (
        str(event.group_id)
        if isinstance(event, GroupMessageEvent)
        else command_args[1]
        if len(command_args) > 1
        else None
    )

    if not group_id:
        await bot.send(event, "Group ID is required for private messages.")
        return

    add_group_repo_data(group_id, repo,
                        config.github_default_config_setting,
                        config.github_default_config_setting,
                        config.github_default_config_setting,
                        config.github_default_config_setting)
    from . import (
        refresh_data_from_db,
    )
    refresh_data_from_db()
    await bot.send(event, f"Added repository mapping: {group_id} -> {repo}")
    logger.info(f"Added repository mapping: {group_id} -> {repo}")


@on_command(
    'delete_group_repo',
    aliases={'del_repo'},
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER
).handle()
@repo_group.command("delete").handle()
@repo_group.command("del").handle()
async def delete_repo(
        bot: Bot, event: MessageEvent, args: Message = CommandArg()
):
    """Delete a repository mapping."""
    command_args = args.extract_plain_text().split()
    if len(command_args) < 1:
        await bot.send(event, "Usage: repo delete <repo> [group_id]")
        return

    repo = link_to_repo_name(command_args[0])
    group_id = (
        str(event.group_id)
        if isinstance(event, GroupMessageEvent)
        else command_args[1]
        if len(command_args) > 1
        else None
    )

    if not group_id:
        await bot.send(event, "Group ID is required for private messages.")
        return

    groups_repo = load_group_configs()
    if group_id not in groups_repo or repo not in map(
            lambda x: x["repo"], groups_repo[group_id]
    ):
        await bot.send(
            event, f"Repository {repo} not found in group {group_id}."
        )
        return

    remove_group_repo_data(group_id, repo)
    from . import refresh_data_from_db
    refresh_data_from_db()
    await bot.send(event, f"Deleted repository mapping: {group_id} -> {repo}")
    logger.info(f"Deleted repository mapping: {group_id} -> {repo}")


@on_command(
    'change_group_repo_cfg',
    aliases={'change_repo'},
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER
).handle()
@repo_group.command("config").handle()
@repo_group.command('cfg').handle()
async def change_repo(
        bot: Bot, event: MessageEvent, args: Message = CommandArg()
):
    """Change repository configuration."""
    command_args = args.extract_plain_text().split()
    if len(command_args) < 3:
        await bot.send(
            event,
            "Usage: repo change <repo> <config> <value>\n"
            "Config types:\n"
            "- commit/issue/pull_req/release/commits/issues/prs/releases/send_release: bool (True/False)\n"
            "- release_folder: string (folder path)"
        )
        return

    repo = link_to_repo_name(command_args[0])
    config_key = command_args[1]
    config_value = command_args[2].lower() in ("true", "1", "yes", "t")
    if config_key == 'release_folder':
        config_value = command_args[2]  # Keep as string for folder path

    group_id = (
        str(event.group_id)
        if isinstance(event, GroupMessageEvent)
        else command_args[3]
        if len(command_args) > 3
        else None
    )

    if not group_id:
        await bot.send(event, "Group ID is required for private messages.")
        return

    groups_repo = load_group_configs()
    if group_id not in groups_repo or repo not in map(
            lambda x: x["repo"], groups_repo[group_id]
    ):
        await bot.send(
            event, f"Repository {repo} not found in group {group_id}."
        )
        return
    if config_key not in [
        "commit", "issue", "pull_req", "release",
        "commits", "issues", "prs", "releases", 'release_folder',
        'send_release'
    ]:
        await bot.send(
            event,
            f"Invalid configuration key: {config_key}.\n"
            "Config types:\n"
            "- commit/issue/pull_req/release/commits/issues/prs/releases/send_release: bool (True/False)\n"
            "- release_folder: string (folder path)"
        )
        return

    change_group_repo_cfg(group_id, repo, config_key, config_value)
    from . import refresh_data_from_db
    refresh_data_from_db()
    await bot.send(
        event,
        f"Changed configuration for {repo} ({config_key}) to {config_value}."
    )
    logger.info(
        f"Changed configuration for {repo} ({config_key}) to {config_value}."
    )


@on_command(
    'show_group_repo',
    aliases={'show_repo'},
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER
).handle()
@repo_group.command("show").handle()
async def show_repo(bot: Bot, event: MessageEvent):
    """Show repository mappings."""
    group_id = (
        str(event.group_id)
        if isinstance(event, GroupMessageEvent)
        else None
    )

    groups_repo = load_group_configs()
    if group_id and group_id in groups_repo:
        repos = groups_repo[group_id]
        output = ""
        for repo in repos:
            current_repo_info = f"- {repo['repo']}:\n"
            current_repo_info += "".join([
                f"{types}:{str(repo.get(types, 'False'))}\n"
                .replace('0', 'False').replace('1', 'True')
                for types in ['commit', 'issue', 'pull_req', 'release']
            ])
            current_repo_info += "\n"
            output += current_repo_info
        message = f"Group {group_id} Repositories:\n" + output
    elif isinstance(event, PrivateMessageEvent):
        groups = groups_repo.keys()
        message = ""
        for current_group_id in groups:
            repos = groups_repo[current_group_id]
            group_info = f"Group {current_group_id}:\n"
            for repo in repos:
                group_info += f"- {repo['repo']}\n"
                group_info += "".join([
                    f"{types}:{str(repo.get(types, 'False'))}\n"
                    .replace('0', 'False')
                    .replace('1', 'True')
                    for types in ['commit', 'issue', 'pull_req', 'release']])
                group_info += "\n"
            group_info += "\n"
            message += group_info
    else:
        message = f"Repository data not found in group {group_id}."

    if '\n' in message:
        html_lines = '<p>' + message.replace('\n', '<br />') + '</p>'
        message = MessageSegment.image(await html_to_pic(html_lines))

    await bot.send(event, message)


@on_command(
    'refresh_group_repo',
    aliases={'refresh_repo'},
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER
).handle()
@repo_group.command("refresh").handle()
async def refresh_repo(bot: Bot, event: MessageEvent):
    """Refresh repository data."""
    from . import check_repo_updates
    load_group_configs(fast=False)
    await bot.send(event, "Refreshing repository data...")
    await check_repo_updates()
    # await bot.send(event, "Repository data refreshed.")


@on_command(
    'repo_info',
    aliases={'repo.info'}
).handle(parameterless=[Cooldown(15, prompt="调用过快")])
async def repo_info(
        bot: Bot, event: MessageEvent, args: Message = CommandArg()
):
    """Show repository information."""
    command_args = args.extract_plain_text().split()
    if len(command_args) < 1:
        await bot.send(event, "Usage: repo info <repo>")
        return

    from .repo_activity import GITHUB_TOKEN
    repo = link_to_repo_name(command_args[0])

    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    api_url = "https://api.github.com/repos/" + repo

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                # Extract repository information
                repo_name = data.get("full_name", "Unknown")
                description = data.get("description", "No description")
                owner = data.get("owner", {}).get("login", "Unknown")
                url = data.get("html_url", "Unknown")
                licence = data.get("license", {}).get("name", "Unknown")
                language = data.get("language", "Unknown")
                homepage = data.get("homepage", "Unknown")
                default_branch = data.get("default_branch", "Unknown")

                stars = data.get("stargazers_count", 0)
                forks = data.get("forks", 0)

                issue_count = data.get("open_issues_count", 0)

                created = data.get("created_at", "Unknown")
                updated = data.get("updated_at", "Unknown")

                is_template = data.get("is_template", False)
                is_private = data.get("private", False)
                allow_fork = data.get("allow_forking", False)
                is_fork = data.get("fork", False)
                is_archived = data.get("archived", False)

                message = f'''**Repository Information**
- Name: {repo_name}
- Description: {description}
- Owner: {owner}
- URL: {url}
- License: {licence}
- Language: {language}
- Homepage: {homepage}
Default branch: {default_branch}

Repo data
Stars: {stars}
Forks: {forks}
Issue count: {issue_count}

Repo statics & status
Created time: {created}
Last updated: {updated}''' + \
                          ('The repo is a template\n' if is_template else '') + \
                          ('The repo is private repo\n' if is_private else '') + \
                          ('' if allow_fork else 'The repo does not allow forks\n') + \
                          ('The repo is a fork\n' if is_fork else '') + \
                          ('The repo is archived\n' if is_archived else '')

                re_text = message.replace('\n', '<br />')
                message = MessageSegment.image(
                    await html_to_pic(f'<p>{re_text}</p>'))
    except aiohttp.ClientResponseError as e:
        message = (
            f"Failed to fetch GitHub repo usage: {e.status} - {e.message}"
        )
        logger.error(message)
    except Exception as e:  # pylint: disable=broad-exception-caught
        message = f"Fatal error while fetching GitHub repo usage: {e}"
        logger.error(message)
    await bot.send(event, message)


@on_command("latest_release", aliases={"repo_release", "get_release"}).handle(
    parameterless=[Cooldown(15, prompt="调用过快")])
async def latest_release(
        bot: Bot, event: MessageEvent, args: Message = CommandArg()
):
    """Get the latest release of a repository."""
    command_args = args.extract_plain_text().split()
    if len(command_args) < 1:
        await bot.send(event, "Usage: latest_release <repo>")
        return

    repo = link_to_repo_name(command_args[0])
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {}
    from .repo_activity import GITHUB_TOKEN
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 404:
                    await bot.send(event, f"No releases found for {repo}.")
                    return
                response.raise_for_status()
                data = await response.json()
                name = data.get("name", "No name")
                tag = data.get("tag_name", "No tag")
                url = data.get("html_url", "")
                body = data.get("body", "No description")
                published = data.get("published_at", "Unknown")
                message = (
                    f"**Latest Release for {repo}**\n"
                    f"Name: {name}\n"
                    f"Tag: {tag}\n"
                    f"Published: {published}\n"
                    f"URL: {url}\n"
                    f"Description:\n{body}"
                )
                if config.github_send_in_markdown:
                    message = MessageSegment.image(await md_to_pic(
                        f"### Latest Release for {repo}\n"
                        f"- Name: {name}\n"
                        f"- Tag: {tag}\n"
                        f"- Published: {published}\n"
                        f"- URL: {url}\n"
                        f"Details:\n"
                        f"{body}"
                    ))
                elif config.github_send_detail_in_markdown:
                    message = MessageSegment.text(
                        f"### Latest Release for {repo}\n"
                        f"- Name: {name}\n"
                        f"- Tag: {tag}\n"
                        f"- Published: {published}\n"
                        f"- URL: {url}"
                    ) + MessageSegment.image(await md_to_pic(body))
                else:
                    message = MessageSegment.text(message)
                await bot.send(event, message)
    except Exception as e:  # pylint: disable=broad-exception-caught
        await bot.send(event, f"Error fetching latest release: {e}")


@on_command("latest_commit", aliases={"repo_commit", "get_commit"}).handle(
    parameterless=[Cooldown(15, prompt="调用过快")])
async def latest_commit(
        bot: Bot, event: MessageEvent, args: Message = CommandArg()
):
    """Get the latest commit of a repository."""
    command_args = args.extract_plain_text().split()
    if len(command_args) < 1:
        await bot.send(event, "Usage: latest_commit <repo>")
        return

    repo = link_to_repo_name(command_args[0])
    api_url = f"https://api.github.com/repos/{repo}/commits"
    headers = {}
    from .repo_activity import GITHUB_TOKEN
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                if not data:
                    await bot.send(event, f"No commits found for {repo}.")
                    return
                commit = data[0]
                sha = commit.get("sha", "Unknown")
                author = commit.get("commit", {}).get("author", {}).get("name", "Unknown")
                date = commit.get("commit", {}).get("author", {}).get("date", "Unknown")
                message_text = commit.get("commit", {}).get("message", "No message")
                url = commit.get("html_url", "")
                message = (
                    f"**Latest Commit for {repo}**\n"
                    f"SHA: {sha}\n"
                    f"Author: {author}\n"
                    f"Date: {date}\n"
                    f"URL: {url}\n"
                    f"Message:\n{message_text}"
                )
                await bot.send(event, MessageSegment.text(message))
    except Exception as e:  # pylint: disable=broad-exception-caught
        await bot.send(event, f"Error fetching latest commit: {e}")
