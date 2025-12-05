# pylint: disable=missing-module-docstring
from nonebot import get_plugin_config
from nonebot import logger, require
from nonebot.compat import model_validator
# pylint: disable=no-name-in-module
from pydantic import BaseModel
from typing import Literal, Any, Self
from pathlib import Path
from githubkit import GitHub, UnauthAuthStrategy, TokenAuthStrategy, Response
from githubkit.exception import (
    PrimaryRateLimitExceeded, RequestFailed, RequestError,
    RequestTimeout, RateLimitExceeded
)

from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
import json

require("nonebot_plugin_localstore")
# pylint: disable=wrong-import-position
import nonebot_plugin_localstore as store  # noqa: E402

DATA_DIR = store.get_plugin_data_dir()
CACHE_DIR = store.get_plugin_cache_dir()

logger.info(f"data folder ->  {DATA_DIR}")


def _get_validator_data(data: Any, field: str) -> Any:
    """
    Helper function to safely extract field data from validator input.
    
    Handles both model instances (with attributes) and dictionaries,
    which can occur in different validation contexts in Pydantic v2.
    
    :param data: The validation data (either model instance or dict)
    :param field: The field name to extract
    :return: The field value or None if not found
    """
    if hasattr(data, field):
        return getattr(data, field)
    elif isinstance(data, dict) and field in data:
        return data[field]
    else:
        return None


class Config(BaseModel):  # pylint: disable=missing-class-docstring
    github_dbg: bool = False  # ignore when writing in the readme

    github_token: str = ""  # validate
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

    github_language: str = "en_us"  # validate
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
    - release
    """

    github_comment_check_amount: int = 20
    """
    The amount of issues/prs to check for comment each time when refresh.
    due to GitHub REST API limitations, the pull requests would also being got when fetching issues.
    the actual amount of issues fetched would be less than this value.
    
    Meanwhile, the larger the value is, the longer it would take to refresh every repo issue/pull comments.
    the smaller the value is, the less amount of issue/pr comments would be checked each time,
    amount of time would spent (estimated) = (value + 1) * 5 (seconds)
    """

    # github_upload_remove_older_ver: bool = True

    github_theme: Literal['light', 'dark'] = "dark"  # validate


    @model_validator(mode="after")
    @classmethod
    def model_validate_ints(cls, data: Any):
        """Validate integer configuration values are non-negative."""
        if _get_validator_data(data, 'github_retries') < 0:
            logger.warning(
                f"Invalid github_retries '{data.github_retries}', "
                "using default 3"
            )
            data.github_retries = 3
        if _get_validator_data(data, 'github_retry_delay') < 0:
            logger.warning(
                f"Invalid github_retry_delay '{data.github_retry_delay}', "
                "using default 5"
            )
            data.github_retry_delay = 5
        if _get_validator_data(data, 'github_comment_check_amount') < 0:
            logger.warning(
                f"Invalid github_comment_check_amount "
                f"'{data.github_comment_check_amount}', using default 20"
            )
            data.github_comment_check_amount = 20
        return data

    @model_validator(mode="after")
    @classmethod
    def model_validate_lang(cls, data: Any):
        """Validate language configuration is supported."""
        supported_langs = {"en_us", "zh_cn"}
        if _get_validator_data(data, 'github_language') not in supported_langs:
            logger.warning(
                f"Unsupported language '{data.github_language}', "
                "using default 'en_us'"
            )
            data.github_language = "en_us"
        return data

    @model_validator(mode="after")
    @classmethod
    def model_validate_theme(cls, data: Any):
        """Validate theme configuration is supported."""
        supported_themes = {"light", "dark"}
        if _get_validator_data(data, 'github_theme') not in supported_themes:
            logger.warning(
                f"Unsupported theme '{data.github_theme}', "
                "using default 'dark'"
            )
            data.github_theme = "dark"
        return data

    @model_validator(mode="after")
    @classmethod
    def model_validate_token(cls, data: Any):
        if not isinstance(_get_validator_data(data, 'github_token'), str):
            logger.warning("GitHub token must be a string, using empty token")
            data.github_token = ""
            return data

        # Github(auto_retry=False) to ignore built-in retries leading to uncatchable tracebacks
        token: str | None = _get_validator_data(data, 'github_token')
        if not token:
            logger.warning(
                "No GitHub token provided. Proceeding without authentication."
            )
            return data

        auth_github = GitHub(TokenAuthStrategy(token), auto_retry=False)

        @retry(stop=stop_after_attempt(_get_validator_data(data, 'github_retries')),
               wait=wait_fixed(_get_validator_data(data, 'github_retry_delay')))
        def token_valid() -> None:
            try:
                auth_github.rest.repos.get(
                    owner="HTony03",
                    repo="nonebot_plugin_github_release_notifier"
                )
                logger.info("GitHub token is valid.")
            except (RequestFailed, RateLimitExceeded, RequestError):
                logger.error(
                    "Invalid GitHub token received. "
                    "Proceed without authentication."
                )
                data.github_token = ''
                return

        try:
            token_valid()
        except RetryError as e:
            logger.error(
                "GitHub token validation failed after multiple attempts. "
                "Proceed without authentication."
            )
            logger.error(
                f"exception: {e.last_attempt.__class__.__name__}: "
                f"{e.last_attempt.exception()}"
            )
            data.github_token = ''
        return data


def get_translation() -> dict:
    # if language is None:
    #     language = config.github_language
    #
    # translation_file = Path(__file__).parent / "lang" / f"{language}.json"
    #
    # if not translation_file.exists():
    #     logger.error(f"Failed to fetch translation file for lang: {language}, using default(en_us)")
    translation_file = Path(__file__).parent / "lang" / (config.github_language + ".json")

    try:
        with open(translation_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


config: Config = get_plugin_config(Config)
t = get_translation()
