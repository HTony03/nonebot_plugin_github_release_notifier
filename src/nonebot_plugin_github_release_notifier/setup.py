# pylint: disable=missing-module-docstring
from .repo_activity import validate_github_token
from .db_action import init_database, DB_FILE
import shutil


# Initialize the database and load group configurations
def pre_plugin_setup() -> None:
    """Pre-plugin setup to initialize the database."""
    init_database()
    shutil.copyfile(DB_FILE, DB_FILE.with_suffix(".bak"))

async def post_plugin_setup() -> None:
    """Post plugin setup function to validate GitHub token."""
    await validate_github_token()
