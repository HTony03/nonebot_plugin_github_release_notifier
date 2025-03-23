from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    github_database_dir: str = "github_db.db"
    """
    The path to the SQLite database.
    """

    github_token: str = ""
    """
    GitHub token for accessing the GitHub API.
    Any token, either classic or fine-grained access token, is accepted.
    """

    github_notify_group: dict = {}
    """
    Group-to-repo mapping.
    Format: {group_id: [{repo: str (, commit: bool)(, issue: bool)
    (, pull_req: bool)(, release: bool)}]}
    """

    github_validate_retries: int = 3
    """
    The maximum number of retries for validating the GitHub token.
    """

    github_validate_delay: int = 5
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


config = get_plugin_config(Config)
