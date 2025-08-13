"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:45:25
@LastEditors    : HTony03
@LastEditTime   : 2025-08-13 17:12:30
@Description    : GitHub image renderer
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from hashlib import sha256

from pydantic_core import to_json
from nonebot import require
require("nonebot_plugin_htmlrender")
from githubkit.versions.latest import models
from nonebot_plugin_htmlrender import html_to_pic
from githubkit.typing import Missing

from ..config import config
# from src.plugins.github.cache.rendered_image import (
#     get_rendered_image,
#     save_rendered_image,
# )

from .context import (
    IssueContext,
    ReadmeContext,
    IssueClosedContext,
    IssueOpenedContext,
    IssueCommentedContext,
)
from .render import (
    issue_to_html,
    readme_to_html,
    issue_closed_to_html,
    issue_opened_to_html,
    issue_commented_to_html,
)

WIDTH = 800
HEIGHT = 30


async def _github_html_to_image(html: str, context_url: str | None = None) -> bytes:
    return await html_to_pic(
        html,
        viewport={"width": WIDTH, "height": HEIGHT},
        base_url=context_url,
    )


def _context_hash(
        context: (
                ReadmeContext
                | IssueContext
                | IssueOpenedContext
                | IssueCommentedContext
                | IssueClosedContext
        ),
) -> str:
    context_json = to_json(context)
    return sha256(context_json).hexdigest()


'''
async def readme_to_image(
    repo: models.FullRepository, readme: str
) -> bytes:
    """Render a github issue/pr timeline to image"""
    context = await ReadmeContext.from_repo_readme(repo, readme)
    # context_hash = _context_hash(context)
    # if cached_image := await get_rendered_image("readme", context_hash):
    #     return cached_image

    html = await readme_to_html(context, theme=config.github_theme)
    image = await _github_html_to_image(
        html,
        f"https://raw.githubusercontent.com/{repo.owner.login}/{repo.name}/{repo.default_branch}/",
    )
    # await save_rendered_image("readme", context_hash, image)
    return image
'''


async def issue_to_image(
    issue: models.Issue, highlight_comment: int | None = None
) -> bytes:
    """Render a github issue/pr timeline to image"""
    context = await IssueContext.from_issue(issue, highlight_comment)
    # context_hash = _context_hash(context)
    # if cached_image := await get_rendered_image("issue", context_hash):
    #     return cached_image

    html = await issue_to_html(context, theme=config.github_theme)
    image = await _github_html_to_image(html)
    # await save_rendered_image("issue", context_hash, image)
    return image


async def issue_opened_to_image(
    repo: Missing[models.Repository],
    issue: models.Issue,
) -> bytes:
    """Render webhook event issue/opened to image"""
    from .utils import get_repo_from_issue
    if not repo:
        repo = await get_repo_from_issue(issue)
    context = await IssueOpenedContext.from_issue(repo, issue)
    # context_hash = _context_hash(context)
    # if cached_image := await get_rendered_image("issue_opened", context_hash):
    #     return cached_image

    html = await issue_opened_to_html(context, theme=config.github_theme)
    image = await _github_html_to_image(html)
    # await save_rendered_image("issue_opened", context_hash, image)
    return image


async def issue_commented_to_image(
    repo: Missing[models.Repository],
    issue: models.Issue,
    comment: models.IssueComment,
) -> bytes:
    """Render webhook event issue_comment/created to image"""
    from .utils import get_repo_from_issue
    if not repo:
        repo = await get_repo_from_issue(issue)
    context = await IssueCommentedContext.from_issue_comment(repo, issue, comment)
    # context_hash = _context_hash(context)
    # if cached_image := await get_rendered_image("issue_commented", context_hash):
    #     return cached_image

    html = await issue_commented_to_html(context, theme=config.github_theme)
    image = await _github_html_to_image(html)
    # await save_rendered_image("issue_commented", context_hash, image)
    return image


async def issue_closed_to_image(
    repo: models.Repository,
    issue: models.Issue,
    sender: models.SimpleUser,
) -> bytes:
    """Render webhook event issue/closed to image"""
    context = await IssueClosedContext.from_issue(repo, issue, sender)
    # context_hash = _context_hash(context)
    # if cached_image := await get_rendered_image("issue_closed", context_hash):
    #     return cached_image

    html = await issue_closed_to_html(context, theme=config.github_theme)
    image = await _github_html_to_image(html)
    # await save_rendered_image("issue_closed", context_hash, image)
    return image
