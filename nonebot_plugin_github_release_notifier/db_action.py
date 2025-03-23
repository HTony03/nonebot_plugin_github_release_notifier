import sqlite3
from nonebot.log import logger
from .config import DATA_DIR

DB_FILE = DATA_DIR / "github_release_notifier.db"


# Initialize the database
def init_database():
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
            PRIMARY KEY (groupid, repo)  -- Composite primary key
        )
    """)
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


def save_last_processed(data: dict):
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


def load_groups() -> dict:
    """Load the group configurations from the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM group_config")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a dictionary
    group_data = {}
    for row in rows:
        groupid, repo, commits, prs, issues, releases = row
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
):
    """Add or update a group's repository
    configuration in the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    group_id = int(group_id)

    cursor.execute("""
        INSERT INTO group_config (groupid, repo, commits,
issues, prs, releases)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(groupid, repo) DO UPDATE SET
            commits=excluded.commits,
            issues=excluded.issues,
            prs=excluded.prs,
            releases=excluded.releases
    """, (group_id, repo, commits, issues, prs, releases))

    conn.commit()
    conn.close()


def change_group_repo_cfg(group_id: int | str, repo: str,
                          type: str, value: bool):
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
    }
    if type not in column_mapping:
        logger.error(
            f"Error: Invalid type format '{type}'. "
            f"Must be one of {list(column_mapping.keys())}."
        )
        conn.close()
        return

    # Get the correct column name
    column = column_mapping[type]

    # Execute the update query
    logger.info(f"Updating group {group_id}, repo {repo}, "
                f"setting {column} to {value}")
    cursor.execute(f"""
        UPDATE group_config
        SET {column}=?
        WHERE groupid=? AND repo=?
    """, (value, group_id, repo))

    # Log the number of rows affected
    logger.info(f"Rows affected: {cursor.rowcount}")

    # Commit changes and close the connection
    conn.commit()
    conn.close()


def remove_group_repo_data(group_id: int | str, repo: str):
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
