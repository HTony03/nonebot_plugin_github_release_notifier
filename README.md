# GitHub 发布通知器

一个用于监控 GitHub 仓库发布并发送通知的插件。

## 功能
- 监控多个 GitHub 仓库。
- 通过指定渠道通知用户新发布。
- 可自定义通知格式。

## 安装
1. 克隆仓库：
    ```bash
    git clone https://github.com/your-repo/github_release_notifier.git
    ```
2. 安装依赖：
    ```bash
    pip install -r requirements.txt
    ```
3. 根据需要配置插件。

## 使用
```python title="bot.py"
import nonebot
from nonebot.adapters.onebot.v11 import Adapter

nonebot.init(_env_file=".env")

driver = nonebot.get_driver()
driver.register_adapter(Adapter)

nonebot.load_builtin_plugins()

# load other plugins

# bam need this to manage background tasks
nonebot.load_plugin("nonebot_plugin_apscheduler")
nonebot.load_plugin("github_release_notifier")

nonebot.run()

```
相关`.env`配置项如下

所有配置项均为可选参数 群组可通过command添加

使用前请确保nonebot的`SUPERUSERS`配置项已配置

```properties
# SQLite 数据库的路径
GITHUB_DATABASE_DIR="github_db.db"

# 用于访问 GitHub API 的 GitHub Token
# 接受任何 Token，无论是经典 Token full_grained access Token
GITHUB_TOKEN=""

# 群组到仓库的映射(自动添加到数据库，以数据库配置作为第一数据源)
# 格式: {group_id: [{repo: str (, commit: bool)(, issue: bool)(, pull_req: bool)(, release: bool)}]}
GITHUB_NOTIFY_GROUP={}

# 验证 GitHub Token 的最大重试次数
GITHUB_VALIDATE_RETRIES=3

# 每次验证重试之间的延迟（以秒为单位）
GITHUB_VALIDATE_DELAY=5

# 删除群组仓库(用于删除数据库配置)
# 格式: {group_id: ['repo']}
GITHUB_DEL_GROUP_REPO={}

# 在获取仓库数据失败时禁用配置
GITHUB_DISABLE_WHEN_FAIL=False
```

### 命令

#### **1. 添加群组仓库映射**
**命令**: `/add_group_repo` 或 `/add_repo`  
**权限**: SUPERUSERS或群聊管理员/群主  
**说明**: 添加一个新的群组到仓库的映射。

- **群组消息**:
  - **格式**: `/add_group_repo <仓库名>`
  - **示例**: `/add_group_repo <user>/<repo>`
- **私聊消息**:
  - **格式**: `/add_group_repo <仓库名> <群组ID>`
  - **示例**: `/add_group_repo <user>/<repo> 123456`

---

#### **2. 删除群组仓库映射**
**命令**: `/del_group_repo` 或 `/del_repo`  
**权限**: SUPERUSERS或群聊管理员/群主  
**说明**: 删除一个群组到仓库的映射。

- **群组消息**:
  - **格式**: `/del_group_repo <仓库名>`
  - **示例**: `/del_group_repo <user>/<repo>`
- **私聊消息**:
  - **格式**: `/del_group_repo <仓库名> <群组ID>`
  - **示例**: `/del_group_repo <user>/<repo> 123456`

---

#### **3. 修改仓库配置**
**命令**: `/change_repo_config` 或 `/repo_cfg`  
**权限**: SUPERUSERS或群聊管理员/群主  
**说明**: 修改群组仓库的配置项。

- **群组消息**:
  - **格式**: `/change_repo_config <仓库名> <配置项> <值>`
  - **示例**: `/change_repo_config <user>/<repo> issue False`
- **私聊消息**:
  - **格式**: `/change_repo_config <仓库名> <群组ID> <配置项> <值>`
  - **示例**: `/change_repo_config <user>/<repo> 123456 issue False`
- **支持的配置项**:
  - `commit` (提交通知)
  - `issue` (问题通知)
  - `pull_req` (拉取请求通知)
  - `release` (发布通知)

---

#### **4. 查看群组仓库映射**
**命令**: `/show_group_repo` 或 `/group_repo`  
**权限**: SUPERUSERS或群聊管理员/群主  
**说明**: 查看当前群组或所有群组的仓库映射及其配置。

- **群组消息**:
  - **格式**: `/show_group_repo`
  - **示例**: `/show_group_repo`
- **私聊消息**:
  - **格式**: `/show_group_repo`
  - **示例**: `/show_group_repo`

---

#### **5. 刷新 GitHub 状态**
**命令**: `/refresh_github_stat`  
**权限**: SUPERUSERS或群聊管理员/群主  
**说明**: 手动刷新 GitHub 仓库的状态。

- **格式**: `/refresh_github_stat`
- **示例**: `/refresh_github_stat`

---

#### **6. 重新加载数据库**
**命令**: `/reload_database` 或 `/reload_db`  
**权限**: SUPERUSERS或群聊管理员/群主  
**说明**: 重新加载数据库中的群组和仓库映射。

- **格式**: `/reload_database`
- **示例**: `/reload_database`

---

### 示例
1. 添加仓库映射：
   ```
   /add_group_repo <user>/<repo>
   ```
2. 删除仓库映射：
   ```
   /del_group_repo <user>/<repo>
   ```
3. 修改仓库配置：
   ```
   /change_repo_config <user>/<repo> issue False
   ```
4. 查看当前群组的仓库映射：
   ```
   /show_group_repo
   ```
5. 刷新 GitHub 状态：
   ```
   /refresh_github_stat
   ```
6. 重新加载数据库：
   ```
   /reload_database
   ```

### TODOS

- [ ] 自定义发送信息格式
- [ ] 数据库结构重置


## LICENCE
本插件按照MIT协议传播

---

# GitHub Release Notifier

A plugin for monitoring GitHub repository releases and sending notifications.

## Features
- Monitor multiple GitHub repositories.
- Notify users of new releases via specified channels.
- Customizable notification formats.

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/github_release_notifier.git
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Configure the plugin as needed.

## Usage
```python title="bot.py"
import nonebot
from nonebot.adapters.onebot.v11 import Adapter

nonebot.init(_env_file=".env")

driver = nonebot.get_driver()
driver.register_adapter(Adapter)

nonebot.load_builtin_plugins()

# load other plugins

# bam need this to manage background tasks
nonebot.load_plugin("nonebot_plugin_apscheduler")
nonebot.load_plugin("github_release_notifier")

nonebot.run()

```
Relevant `.env` configuration:

All configuration items are optional. Groups can be added via commands.

Before using, make sure the `SUPERUSERS` configuration item in nonebot is set.

```properties
# Path to the SQLite database
GITHUB_DATABASE_DIR="github_db.db"

# GitHub token for accessing the GitHub API
# Accepts any token, whether classic or fine-grained access token
GITHUB_TOKEN=""

# Group-to-repo mapping (automatically added to the database, database configuration is the primary data source)
# Format: {group_id: [{repo: str (, commit: bool)(, issue: bool)(, pull_req: bool)(, release: bool)}]}
GITHUB_NOTIFY_GROUP={}

# Maximum number of retries for validating the GitHub token
GITHUB_VALIDATE_RETRIES=3

# Delay (in seconds) between each validation retry
GITHUB_VALIDATE_DELAY=5

# Delete group repo (used to delete database configurations)
# Format: {group_id: ['repo']}
GITHUB_DEL_GROUP_REPO={}

# Disable the configuration when failing to get repo data
GITHUB_DISABLE_WHEN_FAIL=False
```

### Commands

#### **1. Add Group-to-Repo Mapping**
**Command**: `/add_group_repo` or `/add_repo`  
**Permission**: SUPERUSERS or group chat admins/owners  
**Description**: Add a new group-to-repo mapping.

- **Group Message**:
  - **Format**: `/add_group_repo <repo>`
  - **Example**: `/add_group_repo <user>/<repo>`
- **Private Message**:
  - **Format**: `/add_group_repo <repo> <group_id>`
  - **Example**: `/add_group_repo <user>/<repo> 123456`

---

#### **2. Delete Group-to-Repo Mapping**
**Command**: `/del_group_repo` or `/del_repo`  
**Permission**: SUPERUSERS or group chat admins/owners  
**Description**: Delete a group-to-repo mapping.

- **Group Message**:
  - **Format**: `/del_group_repo <repo>`
  - **Example**: `/del_group_repo <user>/<repo>`
- **Private Message**:
  - **Format**: `/del_group_repo <repo> <group_id>`
  - **Example**: `/del_group_repo <user>/<repo> 123456`

---

#### **3. Modify Repo Configuration**
**Command**: `/change_repo_config` or `/repo_cfg`  
**Permission**: SUPERUSERS or group chat admins/owners  
**Description**: Modify the configuration of a group-to-repo mapping.

- **Group Message**:
  - **Format**: `/change_repo_config <repo> <config_item> <value>`
  - **Example**: `/change_repo_config <user>/<repo> issue False`
- **Private Message**:
  - **Format**: `/change_repo_config <repo> <group_id> <config_item> <value>`
  - **Example**: `/change_repo_config <user>/<repo> 123456 issue False`
- **Supported Config Items**:
  - `commit` (commit notifications)
  - `issue` (issue notifications)
  - `pull_req` (pull request notifications)
  - `release` (release notifications)

---

#### **4. View Group-to-Repo Mapping**
**Command**: `/show_group_repo` or `/group_repo`  
**Permission**: SUPERUSERS or group chat admins/owners  
**Description**: View the current group or all groups' repo mappings and their configurations.

- **Group Message**:
  - **Format**: `/show_group_repo`
  - **Example**: `/show_group_repo`
- **Private Message**:
  - **Format**: `/show_group_repo`
  - **Example**: `/show_group_repo`

---

#### **5. Refresh GitHub Status**
**Command**: `/refresh_github_stat`  
**Permission**: SUPERUSERS or group chat admins/owners  
**Description**: Manually refresh the status of GitHub repositories.

- **Format**: `/refresh_github_stat`
- **Example**: `/refresh_github_stat`

---

#### **6. Reload Database**
**Command**: `/reload_database` or `/reload_db`  
**Permission**: SUPERUSERS or group chat admins/owners  
**Description**: Reload the group and repo mappings from the database.

- **Format**: `/reload_database`
- **Example**: `/reload_database`

---

### Examples
1. Add a repo mapping:
   ```
   /add_group_repo <user>/<repo>
   ```
2. Delete a repo mapping:
   ```
   /del_group_repo <user>/<repo>
   ```
3. Modify repo configuration:
   ```
   /change_repo_config <user>/<repo> issue False
   ```
4. View current group repo mappings:
   ```
   /show_group_repo
   ```
5. Refresh GitHub status:
   ```
   /refresh_github_stat
   ```
6. Reload database:
   ```
   /reload_database
   ```

### TODOS

- [ ] Customize notification formats
- [ ] Reset database structure


## LICENSE
This plugin is distributed under the MIT License.