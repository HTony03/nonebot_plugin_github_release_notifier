# pylint: disable=missing-module-docstring
from nonebot import get_plugin_config
from nonebot import logger, require
# pylint: disable=no-name-in-module
from pydantic import BaseModel
from typing import Literal
from pathlib import Path
import json

require("nonebot_plugin_localstore")
# pylint: disable=wrong-import-position
import nonebot_plugin_localstore as store  # noqa: E402

DATA_DIR = store.get_plugin_data_dir()
CACHE_DIR = store.get_plugin_cache_dir()

logger.info(f"data folder ->  {DATA_DIR}")


class Config(BaseModel):  # pylint: disable=missing-class-docstring
    github_dbg: bool = False  # ignore when writing in the readme

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

    github_language: str = "en_us"
    """
    language for markdown sending templates
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

    github_upload_remove_older_ver: bool = True

    github_theme: Literal['light', 'dark'] = "dark"


# 加载翻译
def get_translation(language: str | None = None) -> dict:
    if language is None:
        language = config.github_language

    translation_file = Path(__file__).parent / "lang" / f"{language}.json"

    if not translation_file.exists():
        logger.error(f"Failed to fetch translation file for lang: {language}, using default(en_us)")
        translation_file = Path(__file__).parent / "lang" / "en_us.json"

    try:
        with open(translation_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


try:
    config: Config = get_plugin_config(Config)
    t = get_translation(config.github_language)
except (ValueError, TypeError) as e:
    logger.error(f"read config failed: {e}, using default config")
    config: Config = Config()
    t = get_translation("en_us")
