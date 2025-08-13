# pylint: disable=missing-module-docstring
import os
import shutil

import aiohttp
from aiohttp import ClientConnectorError
from githubkit import Response
from githubkit.rest import FullRepository
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
from packaging.version import Version
# noinspection PyPackageRequirements
from nonebot import logger

from .repo_activity_new import validate_github_token
from .db_action import init_database, DB_FILE, load_group_configs, remove_group_repo_data
from .config import config, DATA_DIR


__pypi_package_name__ = "nonebot-plugin-github-release-notifier"


async def check_plugin_version() -> None:
    """Check the plugin version against the latest release on GitHub."""
    from . import __version__
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://pypi.org/pypi/{__pypi_package_name__}/json"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    latest_version = data.get('info', {}).get('version', '0.0.0')
                else:
                    logger.warning(
                        "\n"
                        "Failed to fetch the latest version from PyPI. \n"
                        "Please check your network connection."
                    )
                    return
        if Version(latest_version) > Version(__version__):
            logger.opt(colors=True).warning(
                f"\n"
                f"A new release of plugin available: <red>{__version__}</red> -> <green>{latest_version}</green>\n"
                f"To update, run: <green>pip install --upgrade {__pypi_package_name__}</green>"
            )
    except ClientConnectorError:
        logger.warning("Failed to get the latest version data from pypi")


# Initialize the database and load group configurations
def pre_plugin_setup() -> None:
    """Pre-plugin setup."""
    init_database()
    shutil.copyfile(DB_FILE, DB_FILE.with_suffix(".bak"))


async def post_plugin_setup() -> None:
    """Post plugin setup function."""
    await validate_github_token(config.github_retries, config.github_retry_delay)
    await test_config_exists()
    await check_plugin_version()


# test if all configs exist in the previous database
async def test_config_exists() -> None:
    """Test if all configs exist in the previous database."""
    from .repo_activity_new import github
    if not os.path.exists(DATA_DIR / "checked.lock"):
        logger.warning("Reading data and check availability from database, would spend some time to verify...")
        cfgs = load_group_configs(False)

        @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
        async def fetch_repo(repo: str) -> Response[FullRepository]:
            return await github.rest.repos.async_get(
                owner=repo.split('/')[0], repo=repo.split('/')[1]
            )
        for cfg, repos in cfgs.items():
            for repo in repos:
                try:
                    repo = await fetch_repo(repo.get('repo'))
                except RetryError:
                    logger.warning(f'Failed to fetch repo "{repo.get("repo")}" for group config {cfg} after retries')
                    logger.warning("auto removing related config....")
                    remove_group_repo_data(cfg, repo.get('repo'))
        with open(DATA_DIR / "checked.lock", "w", encoding="utf-8") as f:
            f.write("passed")
        logger.success("Repository config checking success, would skip the process afterwards")
    logger.info("if you want to re-check the config from database, please delete "
                f"the checked.lock file in location: {DATA_DIR / 'checked.lock'}")
