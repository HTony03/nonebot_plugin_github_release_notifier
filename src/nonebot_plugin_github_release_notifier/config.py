# pylint: disable=missing-module-docstring
from nonebot import get_driver, get_plugin_config
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
import os

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


# Backwards compatibility for the misspelled configuration names shipped before v0.1.11:
# GITHUB_SEND_FALIURE_GROUP / GITHUB_SEND_FALIURE_SUPERUSER -> GITHUB_SEND_FAILURE_...
# NoneBot lowercases every key read from `.env` files, so the legacy names are lowercase here.
_LEGACY_CONFIG_ALIASES: dict[str, str] = {
    "github_send_faliure_group": "github_send_failure_group",
    "github_send_faliure_superuser": "github_send_failure_superuser",
}


def _is_configured(value: Any) -> bool:
    """
    Check whether a configuration value should override the field default.

    Empty values (``None`` or blank strings) are treated as unset, matching the
    lenient behaviour the misspelled options had before the names were corrected.

    :param value: The raw configuration value
    :return: Whether the value is usable
    """
    return value is not None and (not isinstance(value, str) or value.strip() != "")


def _get_legacy_value(data: Any, legacy_name: str) -> Any:
    """
    Extract a value configured under a deprecated (misspelled) option name.

    Values are looked up following NoneBot's precedence order: the data passed to
    the validator (which already contains the values merged from `.env` files),
    the process environment, and finally NoneBot's global configuration.

    :param data: The validation data (either model instance or dict)
    :param legacy_name: The lowercase legacy option name to look up
    :return: The legacy value or None if it is not configured
    """
    value = _get_validator_data(data, legacy_name)
    if value is not None:
        return value

    for env_name, env_value in os.environ.items():
        if env_name.lower() == legacy_name:
            return env_value

    try:
        global_config = get_driver().config
    except Exception:
        # NoneBot is not initialized (e.g. standalone unit tests), nothing to read
        return None
    return _get_validator_data(global_config, legacy_name)


class Config(BaseModel):  # pylint: disable=missing-class-docstring
    github_dbg: bool = False  # ignore when writing in the readme

    github_token: str = ""  # validate
    """
    GitHub token for accessing the GitHub API.
    Any token, either classic or fine-grained access token, is accepted.
    """
    github_send_failure_group: bool = True
    github_send_failure_superuser: bool = False
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

    github_send_prev_details: bool = False
    """
    Whether send previous details when adding a new repository. 
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


    @model_validator(mode="before")
    @classmethod
    def model_apply_legacy_names(cls, data: Any) -> Any:
        """
        Keep the misspelled legacy option names working.

        ``GITHUB_SEND_FALIURE_GROUP`` and ``GITHUB_SEND_FALIURE_SUPERUSER``
        (typos of ``..._FAILURE_...``) were shipped before v0.1.11, so values
        configured under those names in existing `.env` files are applied to the
        corrected fields. The correctly spelled names always take precedence.
        """
        for legacy_name, field_name in _LEGACY_CONFIG_ALIASES.items():
            if _is_configured(_get_validator_data(data, field_name)):
                # the correctly spelled option is configured, it wins
                continue

            legacy_value = _get_legacy_value(data, legacy_name)
            if not _is_configured(legacy_value):
                continue

            logger.warning(
                f"Deprecated config name '{legacy_name.upper()}' detected, "
                f"please rename it to '{field_name.upper()}' in your .env file. "
                "The misspelled name is still applied for now."
            )
            if isinstance(data, dict):
                data[field_name] = legacy_value
            else:
                setattr(data, field_name, legacy_value)
        return data

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
    translation_file = Path(__file__).parent / "lang" / (config.github_language + ".json")
    try:
        with open(translation_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


config: Config = get_plugin_config(Config)
t = get_translation()
