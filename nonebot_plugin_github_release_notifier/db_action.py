import sqlite3
from nonebot.log import logger
from .config import DATA_DIR

DB_FILE = DATA_DIR / "github_release_notifier.db"
group_data = {}


# Initialize the database
def init_database() -> None:
    """Initialize the SQLite database and create
    the necessary table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS last_processed (
            repo TEXT PRIMARY KEY,
            commits TEXT,
            issues TEXT,
            prs TEXT,
            releases TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_config (
            groupid TEXT,
            repo TEXT,
            commits BOOLEAN,
            issues BOOLEAN,
            prs BOOLEAN,
            releases BOOLEAN,
            release_folder TEXT,
            send_release BOOLEAN,
            PRIMARY KEY (groupid, repo)
        )
    """)
    # Check if 'release_folder' column exists, add if not
    cursor.execute("PRAGMA table_info(group_config)")
    columns = [row[1] for row in cursor.fetchall()]
    if "release_folder" not in columns:
        cursor.execute("ALTER TABLE group_config ADD COLUMN release_folder TEXT")
    if "send_release" not in columns:
        cursor.execute("ALTER TABLE group_config ADD COLUMN send_release BOOLEAN")
    conn.commit()
    conn.close()


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


def load_group_configs(fast=True) -> dict:
    """Load the group configurations from the SQLite database."""
    global group_data
    if fast:
        return group_data
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM group_config")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a dictionary
    group_data = {}
    for row in rows:
        groupid, repo, commits, prs, issues, releases, send_folder, send_release= row
        if groupid not in group_data:
            data = []
        else:
            data: list = group_data[groupid]
        data.append({
            "repo": repo,
            "commit": commits if commits else False,
            "issue": issues if issues else False,
            "pull_req": prs if prs else False,
            "release": releases if releases else False,
            "send_release": send_release if send_release else False,
            "release_folder": send_folder if send_folder else None,
        })
        group_data[groupid] = data
    return group_data


def add_group_repo_data(
    group_id: int | str,
    repo: str,
    commits: bool = False,
    issues: bool = False,
    prs: bool = False,
    releases: bool = False,
    release_folder: str | None = None,
    send_release: bool = False
) -> None:
    """Add or update a group's repository
    configuration in the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    group_id = int(group_id)

    cursor.execute("""
        INSERT INTO group_config (groupid, repo, commits,
issues, prs, releases)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(groupid, repo) DO UPDATE SET
            commits=excluded.commits,
            issues=excluded.issues,
            prs=excluded.prs,
            releases=excluded.releases,
            release_folder=excluded.release_folder,
            send_release=excluded.send_release
    """, (group_id, repo, commits, issues, prs, releases, release_folder, send_release))

    conn.commit()
    conn.close()


def change_group_repo_cfg(group_id: int | str, repo: str,
                          config_type: str, value: bool | str) -> None:
    """Change a group's repository configuration in the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    group_id = int(group_id)

    # Map type to database column
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
    }
    if config_type not in column_mapping:
        logger.error(
            f"Error: Invalid type format '{config_type}'. "
            f"Must be one of {list(column_mapping.keys())}."
        )
        conn.close()
        raise ValueError(
            f"Invalid type format '{config_type}'. "
            f"Must be one of {list(column_mapping.keys())}."
        )

    # Get the correct column name
    column = column_mapping[config_type]

    cursor.execute(f"""
        UPDATE group_config
        SET {column}=?
        WHERE groupid=? AND repo=?
    """, (value, group_id, repo))

    # Commit changes and close the connection
    conn.commit()
    conn.close()


def remove_group_repo_data(group_id: int | str, repo: str) -> None:
    """Remove a group's repository configuration from the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    group_id = int(group_id)
    cursor.execute("""
        DELETE FROM group_config
        WHERE groupid=? AND repo=?
    """, (group_id, repo))

    conn.commit()
    conn.close()
