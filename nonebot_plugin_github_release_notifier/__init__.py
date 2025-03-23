from nonebot import require
from nonebot.log import logger
from .repo_activity import *
from nonebot import get_plugin_config
from .config import Config
from .group_commands import *
from .db_action import init_database, load_groups

__version__ = "0.1.0"

from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name = "github_release_notifier",
    description="A plugin for nonebot & onebot to notify group members of new commits, issues, and PRs in GitHub repos.",
    usage="github repo events auto forward|自动转发github repo事件",
    config = Config,
    extra={},
)

# Scheduler for periodic tasks
scheduler = require("nonebot_plugin_apscheduler").scheduler
config = get_plugin_config(Config)

# Parse the group-to-repo mapping from the config
group_repo_dict = config.github_notify_group

# Initialize the database and load group configurations
init_database()
del_groups = config.github_del_group_repo

groups_repo = load_groups()
for group_id, repos in del_groups.items():
    if group_id in groups_repo:
        for repo in repos:
            if repo in map(lambda x:x['repo'], groups_repo[group_id]):
                remove_group_repo_data(group_id, repo)
                logger.info(f"Repo {repo} removed from group {group_id}(del)")
            else:
                logger.error(f"Repo {repo} not found in group {group_id}(del)")
    else:
        logger.error(f"Group {group_id} not found(del)")
groups_repo = load_groups()
for group in group_repo_dict:
    if group not in groups_repo:
        for repo in group_repo_dict[group]:
            add_group_repo_data(group, repo['repo'],repo.get("commit", False), repo.get("issue", False), repo.get("pull_req", False), repo.get("release", False))
    else:
        for repo in group_repo_dict[group]:
            if repo['repo'] not in map(lambda x:x['repo'], groups_repo[group]):
                add_group_repo_data(group, repo['repo'],repo.get("commit", False), repo.get("issue", False), repo.get("pull_req", False), repo.get("release", False))
group_repo_dict = load_groups()
logger.debug(f'read from db: {group_repo_dict}')


# TODO: reformat database

def refresh_data_from_db():
    global group_repo_dict
    group_repo_dict = load_groups()

@scheduler.scheduled_job("cron", minute="*/5")  # Trigger every 5 minutes (:00, :05, :10, ...)
async def _():
    """Check for new commits, issues, and PRs for all repos and notify groups."""
    await check_and_notify_updates()