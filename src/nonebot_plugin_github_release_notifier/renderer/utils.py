from colorsys import rgb_to_hls

from githubkit.versions.latest import models


async def get_repo_from_issue(issue: models.Issue) -> models.FullRepository:
    """Get repository from issue"""
    from ..repo_activity_new import github
    if issue.repository:
        owner, repo = issue.repository.full_name.split("/", 1)
        return (await github.rest.repos.async_get(owner=owner, repo=repo)).parsed_data
    if issue.repository_url:
        owner, repo = issue.repository_url.split("/")[-2::]
        return (await github.rest.repos.async_get(owner=owner, repo=repo)).parsed_data
    raise ValueError("Issue has no repository")

async def get_pull_request_from_issue(
        issue: models.Issue,
) -> models.PullRequest | None:
    """Get pull request from issue"""
    from ..repo_activity_new import github
    if issue.pull_request:
        if issue.repository:
            owner, repo = issue.repository.full_name.split("/", 1)
        else:
            owner, repo = issue.repository_url.split("/")[-2::]
        return (
            await github.rest.pulls.async_get(
                owner=owner, repo=repo, pull_number=issue.number
            )
        ).parsed_data
    return None


REACTION_EMOJIS = {
    "plus_one": "👍",
    "minus_one": "👎",
    "laugh": "😄",
    "confused": "😕",
    "hooray": "🎉",
    "heart": "❤️",
    "rocket": "🚀",
    "eyes": "👀",
}
"""Issue comment reaction emoji mapping"""


def get_comment_reactions(
        reactions: (
                models.ReactionRollup
                | models.WebhookIssuesOpenedPropIssuePropReactions
                | models.WebhookIssuesClosedPropIssueMergedReactions
                | models.WebhookIssueCommentCreatedPropIssueMergedReactions
                | models.WebhookIssueCommentEditedPropIssueMergedReactions
                | models.WebhookIssueCommentCreatedPropCommentPropReactions
                | models.WebhooksIssueCommentPropReactions
        ),
) -> dict[str, int]:
    """Parse the reactions of the issue comment"""
    result: dict[str, int] = {}
    for reaction, emoji in REACTION_EMOJIS.items():
        if count := getattr(reactions, reaction, None):
            result[emoji] = count
    return result


def get_issue_label_color(color: str) -> tuple[int, int, int, int, int, int]:
    """Get the color of the issue label in RGB and HLS"""
    color = color.removeprefix("#")
    r = int(color[:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    h, l, s = rgb_to_hls(r / 255, g / 255, b / 255)  # noqa: E741
    return r, g, b, int(h * 360), int(l * 100), int(s * 100)
