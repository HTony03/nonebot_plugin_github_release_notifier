# import aiohttp
from nonebot import CommandGroup, on_command
from nonebot.adapters.onebot.v11 import Bot
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
    load_groups,
    change_group_repo_cfg,
)
from .permission import permission_check
from .pic_process import text_to_pic


GITHUB_TOKEN = config.github_token


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
    permission=SUPERUSER | permission_check,
    priority=5
)


@on_command(
    'add_group_repo',
    aliases={'add_repo'},
    permission=SUPERUSER | permission_check
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
    permission=SUPERUSER | permission_check
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

    groups_repo = load_groups()
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
    permission=SUPERUSER | permission_check
).handle()
@repo_group.command("config").handle()
async def change_repo(
    bot: Bot, event: MessageEvent, args: Message = CommandArg()
):
    """Change repository configuration."""
    command_args = args.extract_plain_text().split()
    if len(command_args) < 3:
        await bot.send(event, "Usage: repo change <repo> <config> <value>")
        return

    repo = link_to_repo_name(command_args[0])
    config_key = command_args[1]
    config_value = command_args[2].lower() in ("true", "1", "yes", "t")

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

    groups_repo = load_groups()
    if group_id not in groups_repo or repo not in map(
        lambda x: x["repo"], groups_repo[group_id]
    ):
        await bot.send(
            event, f"Repository {repo} not found in group {group_id}."
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
    permission=SUPERUSER | permission_check
).handle()
@repo_group.command("show").handle()
async def show_repo(bot: Bot, event: MessageEvent):
    """Show repository mappings."""
    group_id = (
        str(event.group_id)
        if isinstance(event, GroupMessageEvent)
        else None
    )

    groups_repo = load_groups()
    if group_id and group_id in groups_repo:
        repos = groups_repo[group_id]
        output = ""
        for repo in repos:
            repo_info = f"- {repo['repo']}:\n"
            repo_info += "".join([
                f"{types}:{str(repo.get(types, 'False'))}\n"
                .replace('0', 'False').replace('1', 'True')
                for types in ['commit', 'issue', 'pull_req', 'release']
            ])
            repo_info += "\n"
            output += repo_info
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
        message = MessageSegment.image(await text_to_pic(html_lines))
 
    await bot.send(event, message)


@on_command(
    'refresh_group_repo',
    aliases={'refresh_repo'},
    permission=SUPERUSER | permission_check
).handle()
@repo_group.command("refresh").handle()
async def refresh_repo(bot: Bot, event: MessageEvent):
    """Refresh repository data."""
    from . import check_repo_updates
    await bot.send(event, "Refreshing repository data...")
    await check_repo_updates()
    # await bot.send(event, "Repository data refreshed.")


# TODO: repo.info command
