from nonebot import get_plugin_config
from nonebot import logger, require
from pydantic import BaseModel

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store  # noqa: E402

DATA_DIR = store.get_plugin_data_dir()

logger.info(f"nonebot_plugin_github_release_notifier 数据文件夹 ->  {DATA_DIR}")


class Config(BaseModel):
    github_token: str = ""
    """
    GitHub token for accessing the GitHub API.
    Any token, either classic or fine-grained access token, is accepted.
    """
    github_send_faliure_group: bool = True
    github_send_faliure_superuser: bool = False

    github_notify_group: dict = {}
    """
    Group-to-repo mapping.
    Format: {group_id: [{repo: str (, commit: bool)(, issue: bool)
    (, pull_req: bool)(, release: bool)}]}
    """

    github_retries: int = 3
    """
    The maximum number of retries for validating the GitHub token.
    """

    github_retry_delay: int = 5
    """
    The delay (in seconds) between each validation retry.
    """

    github_del_group_repo: dict = {}
    """
    Delete group-repo mapping.
    Format: {group_id: ['repo']}
    """

    github_disable_when_fail: bool = False
    """
    Disable the configuration when failing to retrieve repository data.
    """

    github_sending_templates: dict = {}
    """
    Sending templates for different events.
    Format: {"commit": <your_template>, "issue": <your_template>,
    "pull_req": <your_template>, "release": <your_template>}
    Available parameters:
    - commit: repo, message, author, url
    - issue: repo, title, author, url
    - pull_req: repo, title, author, url
    - release: repo, name, version, details, url
    Usage: '{<parameter>}' (using Python's format function).
    Defaults to the standard template if not set.
    """

    github_default_config_setting: bool = True
    """
    Default settings for all repositories when adding a repository to groups.
    """


try:
    config = get_plugin_config(Config)
except Exception as e:
    logger.error(f"nonebot_plugin_github_release_notifier 配置读取失败: {e}")
    config = Config()
# logger.info('got configs: ' + str(config))
