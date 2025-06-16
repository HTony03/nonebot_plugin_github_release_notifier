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
