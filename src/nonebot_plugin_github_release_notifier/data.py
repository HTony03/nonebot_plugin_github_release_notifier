from typing import Any


class Data:
    data: dict[str, Any] = {}

    @classmethod
    def get(cls, key, default=None):  # -> Any | None
        """Get the value associated with the key."""
        return cls.data.get(key, default)

    @classmethod
    def set(cls, key, value) -> None:
        """Set the value for the key."""
        cls.data[key] = value


data_set = Data()


class Folder:
    folder_id: str = ''
    folder_name: str = ''

    def __init__(self, data: dict) -> None:
        """Initialize Folder with data."""
        self.folder_id = data.get('folder_id', '')
        self.folder_name = data.get('folder_name', '')


class File:
    file_id: str = ''
    file_name: str = ''
    busid: int = 0

    def __init__(self, data: dict) -> None:
        """Initialize Folder with data."""
        self.file_id = data.get('file_id', '')
        self.file_name = data.get('file_name', '')
        self.busid = data.get('busid', 0)


class User:
    id: str = ''
    name: str = ''

class Comment:
    comment_id: str = ''
    message: str = ''
    user: str = ''

class Issue:
    issue_id: str = ''
    title: str = ''
    latest_comment: str = ''
    uploader: str = ''
    labels: list[dict[str, str]] = []
    stat: bool = True # True for open, False for closed



class PullRequest:
    pr_id: str = ''
    title: str = ''
    latest_comment: str = ''
    comments: list[Comment] = []
    uploader: str = ''
    tags: list[dict[str,str]] = []
    assigner: list[User]
    stat: bool = 1 # 1 for open, 0 for merged, -1 for aborted

