import httpx
from nonebot import get_bot
from nonebot.log import logger
from nonebot import get_plugin_config
from nonebot.adapters.onebot.v11 import MessageSegment, Bot
from datetime import datetime
import requests
import time
import ssl
from .config import Config
from .db_action import *

config = get_plugin_config(Config)

# Load GitHub token from environment variables
GITHUB_TOKEN: str | None = config.github_token
max_retries: int = config.github_validate_retries
delay: int = config.github_validate_delay

default_sending_templates = {
    "commit": "📜 New Commit in {repo}\n\nMessage: {message}\nAuthor: {author}\nURL: {url}",
    "issue": "🐛 **New Issue in {repo}!**\n\nTitle: {title}\nAuthor: {author}\nURL: {url}",
    "pull_req": "🔀 **New Pull Request in {repo}!**\n\nTitle: {title}\nAuthor: {author}\nURL: {url}",
    "release": "🚀 **New Release for {repo}!**\n\n**Name:** {name}\nVersion: {version}\nDetails:\n {details}\nURL: {url}",
}
config_template = config.github_sending_templates


def validate_github_token(retries=3, delay=5) -> bool:
    """Validate the GitHub token by making a test request, with retries on SSL errors."""
    global GITHUB_TOKEN
    if not GITHUB_TOKEN:
        logger.warning("No GitHub token provided. Proceeding without authentication.")
        return False

    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    for attempt in range(retries):
        try:
            response = httpx.get("https://api.github.com/user", headers=headers)
            if response.status_code == 200:
                logger.info("GitHub token is valid.")
                return True
            else:
                logger.error(f"GitHub token validation failed: {response.status_code} - {response.text}")
                GITHUB_TOKEN = None
                return False
        except ssl.SSLError as e:
            logger.error(f"SSL error during GitHub token validation: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            logger.error(f"Error validating GitHub token: {e}")

    logger.error("GitHub token validation failed after multiple attempts.")
    GITHUB_TOKEN = None
    return False


async def fetch_github_data(repo: str, endpoint: str) -> dict | None:
    """Fetch data from the GitHub API for a specific repo and endpoint."""
    api_url = f"https://api.github.com/repos/{repo}/{endpoint}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e2:
            logger.error(f"Failed to fetch GitHub {endpoint} for {repo}: \n\
                         {str(e).replace('url','repo').replace(api_url,repo)}\n{str(e2).replace('url','repo').replace(api_url,repo)}")
            return {"falt": f"Failed to fetch GitHub {endpoint} for {repo}:\n\
                {str(e).replace('url','repo').replace(api_url,repo)}\n{str(e2).replace('url','repo').replace(api_url,repo)}"}


async def notify(bot: Bot, group_id: int, repo: str, data: list, data_type: str, last_processed: dict):
    """Send notifications for new data (commits, issues, PRs, releases)."""
    latest_data = data[:3]  # Process only the latest 3 items
    for item in latest_data:
        if 'created_at' in item:
            times = item['created_at'].replace("Z", "+00:00")
        elif 'published_at' in item:
            times = item['published_at'].replace("Z", "+00:00")
        else:
            times = item['commit']['committer']['date'].replace("Z", "+00:00")
        item_time = datetime.fromisoformat(times)
        last_time = load_last_processed().get(repo, {}).get(data_type)
        # logger.info(f'comparing {item_time}(current) and {last_time}')
        if not last_time or item_time > datetime.fromisoformat(last_time.replace("Z", "+00:00")):
            message = format_message(repo, item, data_type)
            try:
                await bot.send_group_msg(group_id=group_id, message=MessageSegment.text(message))
                # logger.info(f"Notified group {group_id} about new {data_type} in {repo}.")
            except Exception as e:
                logger.error(f"Failed to notify group {group_id} about {data_type} in {repo}: {e}")

    if 'created_at' in item:
        times = latest_data[0]['created_at'].replace("Z", "+00:00")
    elif 'published_at' in item:
         times = latest_data[0]['published_at'].replace("Z", "+00:00")
    else:
       times = latest_data[0]['commit']['committer']['date'].replace("Z", "+00:00")
        
    # Update the last processed time
    last_processed.setdefault(repo, {})[data_type] = times


def format_message(repo: str, item: dict, data_type: str) -> str:
    """Format the notification message based on the data type."""
    if data_type == "commit":
        datas = {
            "repo": repo,
            "message": item['commit']['message'],
            "author": item['commit']['committer']['name'],
            "url": item['html_url']
        }
        return config_template.get(data_type, 
                                       default_sending_templates
                                       .get(data_type, '')).format(**datas)
        
    elif data_type == "issue":
        datas = {
            "repo": repo,
            "title": item['title'],
            "author": item['user']['login'],
            "url": item['html_url']
        }
        return config_template.get(data_type, 
                                       default_sending_templates
                                       .get(data_type, '')).format(**datas)
    elif data_type == "pull_req":
        datas = {
            "repo": repo,
            "title": item['title'],
            "author": item['user']['login'],
            "url": item['html_url']
        }
        return config_template.get(data_type, 
                                       default_sending_templates
                                       .get(data_type, '')).format(**datas)
    elif data_type == "release":
        datas = {
            "repo": repo,
            "name": item.get('name', 'New Release'),
            "version": item.get('tag_name', 'Unknown Version'),
            "details": item.get('body', 'No description provided.'),
            "url": item.get('html_url', 'No URL')
        }
        return config_template.get(data_type, 
                                       default_sending_templates
                                       .get(data_type, '')).format(**datas)
    return "Unknown data type."


async def check_and_notify_updates():
    """Check for new commits, issues, PRs, and releases for all repos and notify groups."""
    bot: Bot = get_bot()
    last_processed = load_last_processed()
    group_repo_dict = load_groups()
    for group_id, repo_configs in group_repo_dict.items():
        group_id = int(group_id)
        for repo_config in repo_configs:
            repo = repo_config["repo"]
            for data_type, endpoint in [("commit", "commits"), ("issue", "issues"), ("pull_req", "pulls"), ("release", "releases/latest")]:
                if repo_config.get(data_type, False):
                    data = await fetch_github_data(repo, endpoint)
                    if "falt" not in data and data:
                        await notify(bot, group_id, repo, data if isinstance(data,list) else [data], data_type, last_processed)
                    elif "falt" in data:
                        logger.error(data["falt"])
                        await bot.send_group_msg(group_id=group_id, message=data["falt"])
                        if config.github_disable_when_fail and 'SSL' not in data["falt"]:
                            # TODO get fail times, >3 disable,or with 404 disable
                            repo_config[data_type] = False  # Disable further notifications for this type
                            change_group_repo_cfg(group_id, repo, data_type, False)

    # Save the updated processed timestamps after processing all groups
    save_last_processed(last_processed)

# Initialize the database at startup
init_database()

# Validate the GitHub token at startup
validate_github_token(max_retries, delay)
