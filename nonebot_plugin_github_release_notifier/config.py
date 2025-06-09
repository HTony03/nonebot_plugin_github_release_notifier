# pylint: disable=missing-module-docstring
from nonebot import get_plugin_config
from nonebot import logger, require
# pylint: disable=no-name-in-module
from pydantic import BaseModel

require("nonebot_plugin_localstore")
# pylint: disable=wrong-import-position
import nonebot_plugin_localstore as store  # noqa: E402

DATA_DIR = store.get_plugin_data_dir()
CACHE_DIR = store.get_plugin_cache_dir()

logger.info(f"data folder ->  {DATA_DIR}")


class Config(BaseModel):  # pylint: disable=missing-class-docstring
    github_token: str = ""
    """
    GitHub token for accessing the GitHub API.
    Any token, either classic or fine-grained access token, is accepted.
    """
    github_send_faliure_group: bool = True
    github_send_faliure_superuser: bool = False
    """
    Send failure messages to the group and superuser.
    """

    github_retries: int = 3
    """
    The maximum number of retries for validating the GitHub token.
    """

    github_retry_delay: int = 5
    """
    The delay (in seconds) between each validation retry.
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

    github_send_in_markdown: bool = False
    """
    Send messages in Markdown pics.
    """
    github_send_detail_in_markdown: bool = True
    """
    Send detailed messages in Markdown pics.
    influenced types:
    - pr
    - issue
    - release
    """
    github_send_in_markdown: bool = False

    github_upload_remove_older_ver: bool = True


try:
    config = get_plugin_config(Config)
except (ValueError, TypeError) as e:
    logger.error(f"read config failed: {e}, using default config")
    config = Config()
