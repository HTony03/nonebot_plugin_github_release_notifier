from datetime import datetime  # Standard library imports

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
from githubkit.rest import FullRepository
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
from githubkit import Response

from .config import config
from .db_action import (
    add_group_repo_data,
    remove_group_repo_data,
    load_group_configs,
    change_group_repo_cfg,
)
from .pic_process import html_to_pic, md_to_pic

async def send_message(bot:Bot, event:MessageEvent, message:MessageSegment | Message):
    """Send a message to the appropriate target based on the event type."""
    try:
        await bot.send(event, message)
    except Exception as e:
        logger.error(f"Failed to send message: {e.__class__.__name__}:{e}")


@on_command(
    "check_api_usage", aliases={"api_usage", "github_usage"}, priority=5
).handle(parameterless=[Cooldown(15, prompt="调用过快")])
async def handle_check_api_usage(bot: Bot, event: MessageEvent) -> None:
    """Fetch and send the remaining GitHub API usage limits."""
    from .repo_activity_new import github
    try:
        resp = github.rest.rate_limit.get()
        logger.info(resp)
        parsed = resp.parsed_data
        reset_time = datetime.fromtimestamp(parsed.rate.reset).strftime(
            "%Y-%m-%d %H:%M:%S"
        ) if parsed.rate.reset else "Unknown"

        message = (
            f"GitHub API Usage:\n"
            f"   - Remaining: {parsed.rate.remaining}\n"
            f"   - Limit: {parsed.rate.limit}\n"
            f"   - Reset Time: {reset_time}"
        )
        await send_message(bot, event, MessageSegment.text(message))
    except Exception:
        logger.opt(exception=True).error("Failed to fetch GitHub API usage")

    return


def link_to_repo_name(link: str) -> str:
    """Convert a repository link to its name."""
    repo = link.replace("https://", "") \
        .replace("http://", "")
        #.replace(".git", "")
    repo = repo if not repo[-4:] == '.git' else repo[:-4]
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
        bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()
):
    """Add a new repository mapping."""
    from .repo_activity_new import github
    command_args = args.extract_plain_text().split()
    if len(command_args) < 1:
        await bot.send(event, "Usage: repo add <repo> [group_id]")
        return

    repo = link_to_repo_name(command_args[0])
    group_id = event.group_id

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def fetch_repo(repo: str) -> Response[FullRepository]:
        return await github.rest.repos.async_get(
            owner=repo.split('/')[0], repo=repo.split('/')[1]
        )

    try:
        await fetch_repo(repo)
    except RetryError as e:
        logger.error(f"Failed to fetch repository for {repo}")
        await bot.send(event, f"Failed to fetch repository data for {repo}.")
        await bot.send(event, "Please check if the repository exists, whether it is public.")
        await bot.send(event, "To proceed with private repositories, please contact the bot "
                              "admin to generate a github token accessible to the repo.")
        await bot.send(event, f"error details: {e.last_attempt.__class__.__name__}: {e.last_attempt.exception()}")
        return

    add_group_repo_data(group_id, repo,
                        config.github_default_config_setting,
                        config.github_default_config_setting,
                        config.github_default_config_setting,
                        config.github_default_config_setting,
                        None,
                        False)
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
        'send_release', 'send_issue_comment', 'send_pr_comment'
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
    await bot.send(event, "Function fixing, please wait for further update")
    return


#     command_args = args.extract_plain_text().split()
#     if len(command_args) < 1:
#         await bot.send(event, "Usage: repo info <repo>")
#         return

#     from .repo_activity_new import github
#     repo = link_to_repo_name(command_args[0])

#     repo = await github.rest.repos.async_get(
#         owner=repo.split('/')[0], repo=repo.split('/')[1])


#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(api_url, headers=headers) as response:
#                 response.raise_for_status()
#                 data = await response.json()
#                 # Extract repository information
#                 repo_name = data.get("full_name", "Unknown")
#                 description = data.get("description", "No description")
#                 owner = data.get("owner", {}).get("login", "Unknown")
#                 url = data.get("html_url", "Unknown")
#                 licence = data.get("license", {}).get("name", "Unknown")
#                 language = data.get("language", "Unknown")
#                 homepage = data.get("homepage", "Unknown")
#                 default_branch = data.get("default_branch", "Unknown")

#                 stars = data.get("stargazers_count", 0)
#                 forks = data.get("forks", 0)

#                 issue_count = data.get("open_issues_count", 0)

#                 created = data.get("created_at", "Unknown")
#                 updated = data.get("updated_at", "Unknown")

#                 is_template = data.get("is_template", False)
#                 is_private = data.get("private", False)
#                 allow_fork = data.get("allow_forking", False)
#                 is_fork = data.get("fork", False)
#                 is_archived = data.get("archived", False)

#                 message = f'''**Repository Information**
# - Name: {repo_name}
# - Description: {description}
# - Owner: {owner}
# - URL: {url}
# - License: {licence}
# - Language: {language}
# - Homepage: {homepage}
# Default branch: {default_branch}

# Repo data
# Stars: {stars}
# Forks: {forks}
# Issue count: {issue_count}

# Repo statics & status
# Created time: {created}
# Last updated: {updated}''' + \
#                           ('The repo is a template\n' if is_template else '') + \
#                           ('The repo is private repo\n' if is_private else '') + \
#                           ('' if allow_fork else 'The repo does not allow forks\n') + \
#                           ('The repo is a fork\n' if is_fork else '') + \
#                           ('The repo is archived\n' if is_archived else '')
#                 message = MessageSegment.image(
#                     await md_to_pic(message))
#     except aiohttp.ClientResponseError as e:
#         message = (
#             f"Failed to fetch GitHub repo usage: {e.status} - {e.message}"
#         )
#         logger.error(message)
#     except Exception as e:  # pylint: disable=broad-exception-caught
#         message = f"Fatal error while fetching GitHub repo usage: {e}"
#         logger.error(message)
#     await bot.send(event, message)
