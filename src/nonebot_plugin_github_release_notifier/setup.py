# pylint: disable=missing-module-docstring
import shutil
import aiohttp
from packaging.version import Version
# noinspection PyPackageRequirements
from nonebot import logger

from .repo_act import validate_github_token
from .db_action import init_database, DB_FILE

__pypi_package_name__ = "nonebot-plugin-github-release-notifier"


async def check_plugin_version() -> None:
    """Check the plugin version against the latest release on GitHub."""
    from . import __version__
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


# Initialize the database and load group configurations
def pre_plugin_setup() -> None:
    """Pre-plugin setup."""
    init_database()
    shutil.copyfile(DB_FILE, DB_FILE.with_suffix(".bak"))


async def post_plugin_setup() -> None:
    """Post plugin setup function."""
    await validate_github_token()
    await check_plugin_version()
