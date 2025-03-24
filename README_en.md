# Nonebot_plugin_github_release_notifier

A plugin for monitoring GitHub repository releases and sending notifications.

## Features
- Monitor multiple GitHub repositories.
- Notify users of new releases through qq bots.
- Customizable notification formats.

## Write at the beginning
This plugin uses aiohttp to obtain GitHub API data, but it is currently unable to stably connect to GitHub API in China

If there are connection issues, please try using a proxy or other tool

## Installation

### Install via nb-cli
```nb-cli install nonebot-plugin-github-release-notifier```

### Install via pip
```pip install nonebot-plugin-github-release-notifier```

### Clone Repository Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/HTony03/nonebot_plugin_github_release_notifier.git
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Place the plugin in your `plugins` folder.

## Usage
#### using by `pyproject.toml`
add thr following contents to your `pyproject.toml` file
```toml
[tool.nonebot]
plugins = ["nonebot_plugin_github_release_notifier"]
```
#### using by editing `bot.py`
```python title="bot.py"
import nonebot
from nonebot.adapters.onebot.v11 import Adapter

nonebot.init(_env_file=".env")

driver = nonebot.get_driver()
driver.register_adapter(Adapter)

nonebot.load_builtin_plugins()

# load other plugins


nonebot.load_plugin("nonebot_plugin_apscheduler")
nonebot.load_plugin("nonebot_plugin_github_release_notifier")

nonebot.run()
```

### Configuration
The relevant `.env` configuration items are as follows:

All configuration items are optional. Groups can add configurations via commands.

Before use, ensure that the `SUPERUSERS` configuration item in NoneBot is properly set.

```properties
# Wheter to send the failure message when failed
GITHUB_SEND_FAILURE_GROUP=True
GITHUB_SEND_FALIURE_SUPERUSER=False

# GitHub Token for accessing the GitHub API
# Accepts any token, whether classic token or fine-grained access token
GITHUB_TOKEN=""

# Mapping of groups to repositories (automatically added to the database, with the database as the primary data source)
# Format: {group_id: [{repo: str (, commit: bool)(, issue: bool)(, pull_req: bool)(, release: bool)}]}
GITHUB_NOTIFY_GROUP={}

# Maximum retry attempts for validating the GitHub Token
GITHUB_VALIDATE_RETRIES=3

# Delay between each validation retry (in seconds)
GITHUB_VALIDATE_DELAY=5

# Delete group-repository mappings (used to remove database configurations)
# Format: {group_id: ['repo']}
GITHUB_DEL_GROUP_REPO={}

# Disable configuration when repository data retrieval fails
GITHUB_DISABLE_WHEN_FAIL=True

# Bot sending templates
# Format: {"commit": <your_template>, "issue": <your_template>, "pull_req": <your_template>, "release": <your_template>}
# Available parameters:
# commit: repo, message, author, url
# issue: repo, title, author, url
# pull_req: repo, title, author, url
# release: repo, name, version, details, url
# Usage: '{<parameter>}' (implemented using Python's format functionality)
# Defaults to the standard template if not set
GITHUB_SENDING_TEMPLATES={}

# Default settings when adding a repository to a group chat
GITHUB_DEFAULT_CONFIG_SETTING=True
```

### Commands
(Repository names in this section can use repository links or .git links as substitutes)

#### **1. Add Group-Repository Mapping**
**Command**: `/add_group_repo` or `/add_repo`  
**Permission**: SUPERUSERS or group chat administrators/owners  
**Description**: Add a new mapping between a group and a repository.

- **Group Message**:
  - **Format**: `/add_group_repo <repository_name>`
  - **Example**: `/add_group_repo <user>/<repo>`
- **Private Message**:
  - **Format**: `/add_group_repo <repository_name> <group_id>`
  - **Example**: `/add_group_repo <user>/<repo> 123456`

---

#### **2. Delete Group-Repository Mapping**
**Command**: `/del_group_repo` or `/del_repo`  
**Permission**: SUPERUSERS or group chat administrators/owners  
**Description**: Delete a mapping between a group and a repository.

- **Group Message**:
  - **Format**: `/del_group_repo <repository_name>`
  - **Example**: `/del_group_repo <user>/<repo>`
- **Private Message**:
  - **Format**: `/del_group_repo <repository_name> <group_id>`
  - **Example**: `/del_group_repo <user>/<repo> 123456`

---

#### **3. Modify Repository Configuration**
**Command**: `/change_repo_config` or `/repo_cfg`  
**Permission**: SUPERUSERS or group chat administrators/owners  
**Description**: Modify the configuration of a group-repository mapping.

- **Group Message**:
  - **Format**: `/change_repo_config <repository_name> <config_item> <value>`
  - **Example**: `/change_repo_config <user>/<repo> issue False`
- **Private Message**:
  - **Format**: `/change_repo_config <repository_name> <group_id> <config_item> <value>`
  - **Example**: `/change_repo_config <user>/<repo> 123456 issue False`
- **Supported Configuration Items**:
  - `commit` (commit notifications)
  - `issue` (issue notifications)
  - `pull_req` (pull request notifications)
  - `release` (release notifications)

---

#### **4. View Group-Repository Mapping**
**Command**: `/show_group_repo` or `/group_repo`  
**Permission**: SUPERUSERS or group chat administrators/owners  
**Description**: View the repository mappings and their configurations for the current group or all groups.

- **Group Message**:
  - **Format**: `/show_group_repo`
  - **Example**: `/show_group_repo`
- **Private Message**:
  - **Format**: `/show_group_repo`
  - **Example**: `/show_group_repo`

---

#### **5. Refresh GitHub Status**
**Command**: `/refresh_github_stat`  
**Permission**: SUPERUSERS or group chat administrators/owners  
**Description**: Manually refresh the status of GitHub repositories.

- **Format**: `/refresh_github_stat`
- **Example**: `/refresh_github_stat`

---

#### **6. Reload Database**
**Command**: `/reload_database` or `/reload_db`  
**Permission**: SUPERUSERS or group chat administrators/owners  
**Description**: Reload the group and repository mappings from the database.

- **Format**: `/reload_database`
- **Example**: `/reload_database`

---

### Examples
1. Add a repository mapping:
   ```
   /add_group_repo <user>/<repo>
   ```
2. Delete a repository mapping:
   ```
   /del_group_repo <user>/<repo>
   ```
3. Modify repository configuration:
   ```
   /change_repo_config <user>/<repo> issue False
   ```
4. View the repository mappings for the current group:
   ```
   /show_group_repo
   ```
5. Refresh GitHub status:
   ```
   /refresh_github_stat
   ```
6. Reload the database:
   ```
   /reload_database
   ```

### TODOS

- [x] Customizable message formats
- [ ] add help
- [ ] Reset database structure

## LICENSE
This plugin is distributed under the MIT License.

## Release
`V0.1.2` prepare for upload and release

`V0.1.0` finish main program and funca