from .repo_activity import validate_github_token

async def post_plugin_setup() -> None:
    await validate_github_token()
