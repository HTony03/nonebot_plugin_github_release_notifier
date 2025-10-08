import sqlite3
from nonebot.log import logger
from .config import DATA_DIR

DB_FILE = DATA_DIR / "github_release_notifier.db"
group_data = {}


def init_database() -> None:
    """
    Initialize the SQLite database and create necessary tables.

    This function creates all required tables and ensures they have
    the correct schema by adding any missing columns.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Create all required tables
        _create_tables(cursor)
        # Update schema for existing installations
        _update_table_schema(cursor)
        conn.commit()
    finally:
        conn.close()


def _create_tables(cursor: sqlite3.Cursor) -> None:
    """
    Create all required database tables.

    Args:
        cursor: SQLite database cursor
    """
    # Create last_processed table for tracking repository updates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS last_processed (
            repo TEXT PRIMARY KEY,
            commits TEXT,
            issues TEXT,
            prs TEXT,
            releases TEXT
        )
    """)

    # Create group_config table for group-repository configurations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_config (
            group_id TEXT,
            repo TEXT,
            commits BOOLEAN,
            issues BOOLEAN,
            prs BOOLEAN,
            releases BOOLEAN,
            release_folder TEXT,
            send_release BOOLEAN DEFAULT FALSE,
            send_issue_comment BOOLEAN DEFAULT FALSE,
            send_pr_comment BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (group_id, repo)
        )
    """)

    # Create tables for tracking issue and PR commit hashes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prs (
            repo TEXT,
            id INT,
            latest_commit_hash TEXT,
            PRIMARY KEY (id, repo)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            repo TEXT,
            id INT,
            latest_commit_hash TEXT,
            PRIMARY KEY (id, repo)
        )
    """)


def _update_table_schema(cursor: sqlite3.Cursor) -> None:
    """
    Update table schema for backward compatibility.
    
    Adds missing columns to existing tables and handles column renames.
    
    Args:
        cursor: SQLite database cursor
    """
    # Check existing columns in group_config table
    cursor.execute("PRAGMA table_info(group_config)")
    columns = [row[1] for row in cursor.fetchall()]

    # Add missing columns if they don't exist
    missing_columns = [
        ("release_folder", "TEXT"),
        ("send_release", "BOOLEAN"),
        ("send_issue_comment", "BOOLEAN"),
        ("send_pr_comment", "BOOLEAN")
    ]

    for column_name, column_type in missing_columns:
        if column_name not in columns:
            cursor.execute(f"ALTER TABLE group_config ADD COLUMN {column_name} {column_type}")

    # Handle legacy column rename
    if "groupid" in columns:
        cursor.execute('ALTER TABLE group_config RENAME COLUMN groupid TO group_id;')


def load_last_processed() -> dict:
    """Load the last processed timestamps from the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM last_processed")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a dictionary
    last_processed = {}
    for row in rows:
        repo, commits, issues, prs, releases = row
        last_processed[repo] = {
            "commit": commits,
            "issue": issues,
            "pull_req": prs,
            "release": releases,
        }
    return last_processed


def save_last_processed(data: dict) -> None:
    """Save the last processed timestamps to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for repo, timestamps in data.items():
        cursor.execute("""
            INSERT INTO last_processed (repo, commits, issues, prs, releases)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(repo) DO UPDATE SET
                commits=excluded.commits,
                issues=excluded.issues,
                prs=excluded.prs,
                releases=excluded.releases
        """, (
            repo,
            timestamps.get("commit"),
            timestamps.get("issue"),
            timestamps.get("pull_req"),
            timestamps.get("release"),
        ))

    conn.commit()
    conn.close()


def load_group_configs(fast=False) -> dict:
    """
    Load the group configurations from the SQLite database.
    
    Args:
        fast (bool): If True, return cached data without database query
        
    Returns:
        dict: Dictionary mapping group_id to list of repository configurations
    """
    global group_data

    # Return cached data if fast mode is enabled
    if fast:
        return group_data

    # Fetch data from database
    rows = _fetch_group_config_rows()

    # Convert database rows to structured dictionary
    group_data = _convert_rows_to_group_data(rows)

    return group_data


def _fetch_group_config_rows() -> list:
    """
    Fetch all group configuration rows from database.
    
    Returns:
        list: List of tuples containing group configuration data
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM group_config")
    rows = cursor.fetchall()
    conn.close()
    return rows


def _convert_rows_to_group_data(rows: list) -> dict:
    """
    Convert database rows to structured group configuration dictionary.
    
    Args:
        rows (list): List of database row tuples
        
    Returns:
        dict: Structured group configuration data
    """
    group_data = {}

    for row in rows:
        group_id, config_data = _parse_config_row(row)

        # Initialize group data if not exists
        if group_id not in group_data:
            group_data[group_id] = []

        group_data[group_id].append(config_data)
    
    return group_data


def _parse_config_row(row: tuple) -> tuple[str, dict]:
    """
    Parse a single database row into group_id and configuration data.
    
    Args:
        row (tuple): Database row containing configuration data
        
    Returns:
        tuple: (group_id, config_dict)
    """
    (
        group_id, repo, commits, prs, issues, releases,
        send_folder, send_release, send_issue_comment, send_pr_comment
    ) = row

    config_data = {
        "repo": repo,
        "commit": bool(commits),
        "issue": bool(issues),
        "pull_req": bool(prs),
        "release": bool(releases),
        "send_release": bool(send_release),
        "release_folder": send_folder,
        "send_issue_comment": bool(send_issue_comment),
        "send_pr_comment": bool(send_pr_comment),
    }

    return group_id, config_data


def add_group_repo_data(
        group_id: int | str,
        repo: str,
        commits: bool = False,
        issues: bool = False,
        prs: bool = False,
        releases: bool = False,
        release_folder: str | None = None,
        send_release: bool = False,
        send_issue_comment: bool = False,
        send_pr_comment: bool = False,
) -> None:
    """Add or update a group's repository
    configuration in the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    group_id = int(group_id)

    cursor.execute("""
        INSERT INTO group_config (group_id, repo, commits,
issues, prs, releases, release_folder, send_release, send_issue_comment, send_pr_comment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(group_id, repo) DO UPDATE SET
            commits=excluded.commits,
            issues=excluded.issues,
            prs=excluded.prs,
            releases=excluded.releases,
            release_folder=excluded.release_folder,
            send_release=excluded.send_release,
            send_issue_comment=excluded.send_issue_comment,
            send_pr_comment=excluded.send_pr_comment
    """, (group_id, repo, commits, issues, prs, releases,
          release_folder, send_release, send_issue_comment, send_pr_comment))

    conn.commit()
    conn.close()


def change_group_repo_cfg(group_id: int | str, repo: str,
                          config_type: str, value: bool | str) -> None:
    """
    Change a group's repository configuration in the SQLite database.
    
    Args:
        group_id: The group identifier
        repo: Repository name in format "owner/repo"
        config_type: Configuration type to change
        value: New value for the configuration
        
    Raises:
        ValueError: If config_type is invalid
    """
    # Validate and map configuration type to database column
    column = _validate_and_map_config_type(config_type)

    # Update database
    _update_group_config_in_db(group_id, repo, column, value)


def _validate_and_map_config_type(config_type: str) -> str:
    """
    Validate configuration type and map to database column name.
    
    Args:
        config_type: Configuration type to validate
        
    Returns:
        str: Corresponding database column name
        
    Raises:
        ValueError: If config_type is invalid
    """
    column_mapping = {
        "commit": "commits",
        "issue": "issues",
        "pull_req": "prs",
        "release": "releases",
        "commits": "commits",
        "issues": "issues",
        "prs": "prs",
        "releases": "releases",
        "release_folder": "release_folder",
        "send_release": "send_release",
        "send_issue_comment": "send_issue_comment",
        "send_pr_comment": "send_pr_comment",
    }

    if config_type not in column_mapping:
        error_msg = (
            f"Invalid type format '{config_type}'. "
            f"Must be one of {list(column_mapping.keys())}."
        )
        logger.error(f"Error: {error_msg}")
        raise ValueError(error_msg)

    return column_mapping[config_type]


def _update_group_config_in_db(group_id: int | str, repo: str,
                               column: str, value: bool | str) -> None:
    """
    Update group configuration in database.
    
    Args:
        group_id: The group identifier
        repo: Repository name
        column: Database column name to update
        value: New value for the column
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    group_id = int(group_id)

    try:
        cursor.execute(f"""
            UPDATE group_config
            SET {column}=?
            WHERE group_id=? AND repo=?
        """, (value, group_id, repo))

        conn.commit()
    finally:
        conn.close()


def remove_group_repo_data(group_id: int | str, repo: str) -> None:
    """
    Remove a group's repository configuration from the SQLite database.

    :param group_id: Group id to remove
    :param repo: the repo to remove
    :return None
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    group_id = int(group_id)
    cursor.execute("""
        DELETE FROM group_config
        WHERE group_id=? AND repo=?
    """, (group_id, repo))

    conn.commit()
    conn.close()


def save_commit_data(repo: str, commit_hash: str, id_: int, type_: str) -> None:
    """Save commit data to the database."""
    if type_ not in ["issues", "prs"]:
        raise ValueError(f"Invalid type '{type_}'. Must be 'issues' or 'prs'.")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO {type_} (repo, id, latest_commit_hash)
        VALUES (?, ?, ?)
        ON CONFLICT(repo, id) DO UPDATE SET
            latest_commit_hash=excluded.latest_commit_hash
    """, (repo, id_, commit_hash))
    conn.commit()
    conn.close()


def get_commit_data(repo: str, id_: int, type_: str) -> str | None:
    """Get the latest commit hash for a specific issue or pull request."""
    if type_ not in ["issues", "prs"]:
        raise ValueError(f"Invalid type '{type_}'. Must be 'issues' or 'prs'.")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT latest_commit_hash FROM {type_}
        WHERE repo=? AND id=?
    """, (repo, id_))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
