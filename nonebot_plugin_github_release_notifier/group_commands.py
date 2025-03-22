import httpx
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageSegment
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from .config import Config
from .db_action import *
from .permission import permission_check

# Load GitHub token from the configuration
config = Config()
GITHUB_TOKEN = config.github_token



def link_to_repo_name(link:str):
    lin = link.replace('https://','').replace('http://','')
    if len(lin.split('/')) == 2:
        return lin
    return '/'.join(lin.split('/')[1:3])
    
# Command to check remaining GitHub API usage
check_api_usage = on_command("check_api_usage", aliases={"api_usage", "github_usage"}, priority=5)

@check_api_usage.handle()
async def handle_check_api_usage(bot: Bot,event:MessageEvent):
    """Fetch and send the remaining GitHub API usage limits."""
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    api_url = "https://api.github.com/rate_limit"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Extract rate limit information
            rate_limit = data.get("rate", {})
            remaining = rate_limit.get("remaining", "Unknown")
            limit = rate_limit.get("limit", "Unknown")
            reset_time = rate_limit.get("reset", "Unknown")

            # Format the reset time if available
            if reset_time != "Unknown":
                from datetime import datetime
                reset_time = datetime.fromtimestamp(reset_time).strftime("%Y-%m-%d %H:%M:%S")

            message = (
                f"**GitHub API Usage**\n"
                f"Remaining: {remaining}\n"
                f"Limit: {limit}\n"
                f"Reset Time: {reset_time}"
            )
            await bot.send(event,message=MessageSegment.text(message))
            logger.info("Sent GitHub API usage information.")
    except httpx.HTTPStatusError as e:
        error_message = f"Failed to fetch GitHub API usage: {e.response.status_code} - {e.response.text}"
        logger.error(error_message)
        await bot.send(event,message=MessageSegment.text(error_message))
    except Exception as e:
        fatal_message = f"Fatal error while fetching GitHub API usage: {e}"
        logger.error(fatal_message)
        await bot.send(event,message=MessageSegment.text(fatal_message))
        
        
        
        
add_group_repo = on_command("add_group_repo", aliases={"add_repo"}, priority=5,\
    permission= SUPERUSER | permission_check)

@add_group_repo.handle()
async def handle_add_group_repo(bot: Bot,event:GroupMessageEvent, args:Message = CommandArg()):
    """Add a new group-repo mapping to the configuration."""
    
    group_id = str(event.group_id)
    if not (repo := args.extract_plain_text()):
        await bot.send(event,'no repo given')
        return
    repo_f = link_to_repo_name(repo.split(' ')[0])
    
    add_group_repo_data(group_id, repo_f)
    from . import refresh_data_from_db
    refresh_data_from_db()
    await bot.send(event,f"Added group-repo mapping: {group_id} -> {repo_f}")
    logger.info(f"Added group-repo mapping: {group_id} -> {repo_f}")

@add_group_repo.handle()
async def handle_add_group_repo(bot: Bot,event:PrivateMessageEvent, args:Message = CommandArg()):
    """Add a new group-repo mapping to the configuration."""
    
    if not (repo := args.extract_plain_text()):
        await bot.send(event,'no repo given')
        return
    if len(repo.split(' ')) < 2:
        await bot.send(event,'no repo given')
        return
    repo_f = repo.split(' ')[0]
    group_id = repo.split(' ')[1]
    if repo_f.isdigit():
        repo_f,group_id = group_id,repo_f
    
    add_group_repo_data(group_id, repo_f)
    from . import refresh_data_from_db
    refresh_data_from_db()
    await bot.send(event,f"Added group-repo mapping: {group_id} -> {repo_f}")
    logger.info(f"Added group-repo mapping: {group_id} -> {repo_f}")
    
    
    
    
del_group_repo = on_command("del_group_repo", aliases={"del_repo"}, priority=5,\
    permission= SUPERUSER | permission_check)

@del_group_repo.handle()
async def handle_del_group_repo(bot: Bot,event:GroupMessageEvent, args:Message = CommandArg()):
    """Delete a group-repo mapping from the configuration."""
    
    group_id = str(event.group_id)
    if not (repo := args.extract_plain_text()):
        await bot.send(event,'no repo given')
        return
    repo_f = link_to_repo_name(repo.split(' ')[0])
    
    groups_repo = load_groups()
    for group_id, repo in {group_id:repo}.items():
        if group_id in groups_repo:
            if repo_f in map(lambda x:x['repo'], groups_repo[group_id]):
                break
            else:
                logger.error(f"Repo {repo} not found in group {group_id}")
                await bot.send(event,f"Repo {repo} not found in group {group_id}")
                return
        else:
            logger.error(f"Group {group_id} not found")
            await bot.send(event,f"Group {group_id} not found")
            return
    
    remove_group_repo_data(group_id, repo_f)
    await bot.send(event,f"Deleted group-repo mapping: {group_id} -> {repo_f}")
    from . import refresh_data_from_db
    refresh_data_from_db()
    logger.info(f"Deleted group-repo mapping: {group_id} -> {repo_f}")


@del_group_repo.handle()
async def handle_del_group_repo(bot: Bot,event:PrivateMessageEvent, args:Message = CommandArg()):
    """Delete a group-repo mapping from the configuration."""
    
    if not (repo := args.extract_plain_text()):
        await bot.send(event,'no repo given')
        return
    if len(repo.split(' ')) < 2:
        await bot.send(event,'no repo given')
        return
    repo_f = repo.split(' ')[0]
    group_id = repo.split(' ')[1]
    if repo_f.isdigit():
        repo_f,group_id = group_id,repo_f
    repo_f = link_to_repo_name(repo_f)
    
    groups_repo = load_groups()
    for group_id, repo in {group_id:repo}.items():
        if group_id in groups_repo:
            if repo_f in map(lambda x:x['repo'], groups_repo[group_id]):
                break
            else:
                logger.error(f"Repo {repo} not found in group {group_id}")
                await bot.send(event,f"Repo {repo} not found in group {group_id}")
                return
        else:
            logger.error(f"Group {group_id} not found")
            await bot.send(event,f"Group {group_id} not found")
            return
    
    remove_group_repo_data(group_id, repo_f)
    await bot.send(event,f"Deleted group-repo mapping: {group_id} -> {repo_f}")
    from . import refresh_data_from_db
    refresh_data_from_db()
    logger.info(f"Deleted group-repo mapping: {group_id} -> {repo_f}")



change_group_repo_config = on_command("change_repo_config", aliases={"repo_cfg"}, priority=5,\
    permission= SUPERUSER | permission_check)

@change_group_repo_config.handle()
async def handle_del_group_repo(bot: Bot,event:GroupMessageEvent, args:Message = CommandArg()):
    """Delete a group-repo mapping from the configuration."""
    
    group_id = str(event.group_id)
    if not (repo := args.extract_plain_text()):
        await bot.send(event,'no repo given')
        return
    if len(repo.split(' ')) < 3:
        await bot.send(event,'no enough param given')
        return
    repo_f = link_to_repo_name(repo.split(' ')[0])
    data = repo.split(' ')[1]
    if data not in ['commit','issue','pull_req','release',\
        'commits','issues','prs','releases']:
        await bot.send(event,"incorrect config, support:['commit','issue','pull_req','release','commits','issues','prs','releases']")
        return
    val = True if repo.split(' ')[2] in ('True','true','TRUE','T','t','1') else False
    
    groups_repo = load_groups()
    for group_id, repo in {group_id:repo_f}.items():
        if group_id in groups_repo:
            if repo_f in map(lambda x:x['repo'], groups_repo[group_id]):
                change_group_repo_cfg(group_id,repo_f,data,val)
                await bot.send(event,f'changed config for {repo_f}({data}) to {val}')
                from . import refresh_data_from_db
                refresh_data_from_db()
            else:
                logger.error(f"Repo {repo_f} not found in group {group_id}")
                await bot.send(event,f"Repo {repo_f} not found in group {group_id}")
        else:
            logger.error(f"Group {group_id} not found")
            await bot.send(event,f"Group {group_id} not found")

@change_group_repo_config.handle()
async def handle_del_group_repo(bot: Bot,event:PrivateMessageEvent, args:Message = CommandArg()):
    """Delete a group-repo mapping from the configuration."""
    
    if not (repo := args.extract_plain_text()):
        await bot.send(event,'no repo given')
        return
    if len(repo.split(' ')) < 4:
        await bot.send(event,'no enough param given')
        return
    repo_f = repo.split(' ')[0]
    group_id = repo.split(' ')[1]
    if repo_f.isdigit():
        repo_f,group_id = group_id,repo_f
    repo_f = link_to_repo_name(repo_f)
    data = repo.split(' ')[2]
    if data not in ['commit','issue','pull_req','release',\
        'commits','issues','prs','releases']:
        await bot.send(event,"incorrect config, support:['commit','issue','pull_req','release','commits','issues','prs','releases']")
        return
    val = True if repo.split(' ')[3] in ('True','true','TRUE','T','t','1') else False
    
    groups_repo = load_groups()
    for group_id, repo in {group_id:repo}.items():
        if group_id in groups_repo:
            if repo_f in map(lambda x:x['repo'], groups_repo[group_id]):
                change_group_repo_cfg(group_id,repo_f,data,val)
                await bot.send(event,f'changed config for {repo_f}({data}) to {val}')
                from . import refresh_data_from_db
                refresh_data_from_db()
            else:
                logger.error(f"Repo {repo_f} not found in group {group_id}")
                await bot.send(event,f"Repo {repo_f} not found in group {group_id}")
        else:
            logger.error(f"Group {group_id} not found")
            await bot.send(event,f"Group {group_id} not found")




show_group_repo = on_command("show_group_repo", aliases={"group_repo"}, priority=5,\
    permission= SUPERUSER | permission_check)

@show_group_repo.handle()
async def handle_del_group_repo(bot: Bot,event:GroupMessageEvent):
    """Delete a group-repo mapping from the configuration."""
    group_id: int = str(event.group_id)
    
    groups_repo = load_groups()
    final_str = '* Group Repos *'
    logger.info(f'{groups_repo}\n {group_id}({type(group_id)})')
    if group_id in groups_repo:
        for repo in groups_repo[group_id]:
            repo_name = repo.get("repo", "Unknown")
            repo_other = repo
            repo_other.pop('repo')
            config_str = ", ".join(f"\n{key}: {value}" for key, value in repo_other.items())
            final_str += f"\n- Repo: {repo_name}\n  Config: {config_str}"
    else:
        final_str += "\nNo repositories found for this group."

    await bot.send(event, final_str.replace(': 1',': True').replace(': 0',': False'))


@show_group_repo.handle()
async def handle_del_group_repo(bot: Bot,event:PrivateMessageEvent):
    """Delete a group-repo mapping from the configuration."""
    
    groups_repo = load_groups()
    final_str = ''
    for group_id, data in groups_repo.items():
        final_str += f'* Group {group_id} Repos *'
        logger.info(f'{groups_repo}\n {group_id}({type(group_id)})')
        if group_id in groups_repo:
            for repo in groups_repo[group_id]:
                repo_name = repo.get("repo", "Unknown")
                repo_other = repo
                repo_other.pop('repo')
                config_str = ", ".join(f"\n{key}: {value}" for key, value in repo_other.items())
                final_str += f"\n- Repo: {repo_name}\n  Config: {config_str}"
        else:
            final_str += "\nNo repositories found for this group."
        final_str += '\n'

    await bot.send(event, final_str.replace(': 1',': True').replace(': 0',': False'))




refresh = on_command("refresh_github_stat", priority=5,\
    permission= SUPERUSER | permission_check)
@refresh.handle()
async def handle_refresh(bot: Bot, event: MessageEvent):
    await bot.send(event,'refreshing github stats')
    from . import check_and_notify_updates
    await check_and_notify_updates()
    
reload = on_command("reload_database", aliases={'reload_db'}, priority=5,\
    permission= SUPERUSER | permission_check)
@reload.handle()
async def handle_reload(bot: Bot, event: MessageEvent):
    from . import refresh_data_from_db
    refresh_data_from_db()
    await bot.send(event,'reloaded database')
    logger.info('reloaded database')
    