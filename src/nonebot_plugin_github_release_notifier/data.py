
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
