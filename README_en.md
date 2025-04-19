
<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-github-release-notifier

_✨ NoneBot GitHub Release Notifier ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/HTony03/nonebot_plugin_github_release_notifier.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-github-release-notifier">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-github-release-notifier.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

This is a plugin for monitoring GitHub repository releases and sending notifications.

## 📖 Introduction

This plugin can monitor multiple GitHub repositories, notify users of new updates via QQ Bot, and supports customizable notification formats.

## 💿 Installation

<details open>
<summary>Install via nb-cli</summary>
Open the command line in the root directory of your NoneBot2 project and enter the following command to install:

    nb plugin install nonebot-plugin-github-release-notifier

</details>

<details>
<summary>Install via package manager</summary>
Open the command line in the plugin directory of your NoneBot2 project and enter the corresponding installation command based on your package manager:

<details>
<summary>pip</summary>

    pip install nonebot-plugin-github-release-notifier
</details>

Open the `pyproject.toml` file in the root directory of your NoneBot2 project and add the following to the `[tool.nonebot]` section:

    plugins = ["nonebot-plugin-github-release-notifier"]

</details>

## ⚙️ Configuration

Before use, ensure that the `SUPERUSERS` configuration item in NoneBot is properly set.

Add the following optional configuration items to the `.env` file in your NoneBot2 project:

| Configuration Item | Required | Default Value | Description |
|:------------------:|:--------:|:-------------:|:-----------:|
| GITHUB_TOKEN | No | Empty string | Token for accessing the GitHub API |
| GITHUB_RETRIES | No | 3 | Maximum retry attempts for refreshing |
| GITHUB_RETRY_DELAY | No | 5 | Delay between each refresh retry (in seconds) |
| GITHUB_NOTIFY_GROUP | No | Empty dictionary | Mapping of groups to repositories |
| GITHUB_DEL_GROUP_REPO | No | Empty dictionary | Delete group-repository mappings |
| GITHUB_DISABLE_WHEN_FAIL | No | False | Disable configuration when repository data retrieval fails |
| GITHUB_SENDING_TEMPLATES | No | Default template | Customizable notification formats (see below) |

### Customizable Notification Formats

The `GITHUB_SENDING_TEMPLATES` configuration item allows users to customize the notification formats for GitHub events. The format is as follows:

```dotenv
# Format: {"commit": <your_template>, "issue": <your_template>, "pull_req": <your_template>, "release": <your_template>}
# Available parameters:
# commit: repo, message, author, url, time
# issue: repo, title, author, url, time
# pull_req: repo, title, author, url, time
# release: repo, name, version, details, url, time
# Usage: '{<parameter>}' (implemented using Python's format functionality)
# Defaults to the standard template if not set
github_sending_templates={}
```

## 🎉 Usage

### Command Table

| Command | Permission | Requires @ | Scope | Description |
|:-------:|:----------:|:----------:|:-----:|:-----------:|
| /add_group_repo or /repo.add | SUPERUSERS or Admins | No | Private & Group | Add group-repository mapping |
| /del_group_repo or /repo.delete | SUPERUSERS or Admins | No | Private & Group | Delete group-repository mapping |
| /change_repo_config or /repo.config | SUPERUSERS or Admins | No | Private & Group | Modify repository configuration |
| /show_group_repo or /repo.show | SUPERUSERS or Admins | No | Private & Group | View group-repository mapping |
| /refresh_group_repo or /repo.refresh | SUPERUSERS or Admins | No | Private & Group | Refresh GitHub status |
| /repo_info or /repo.info | SUPERUSERS or Admins | No | Private & Group | View repository details |
| /check_api_usage | Everyone | No | Private & Group | View GitHub API usage |

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
   /refresh_group_repo
   ```
6. View repository details:
   ```
   /repo.info <user>/<repo>
   ```
7. View GitHub API usage:
   ```
   /check_api_usage
   ```

### TODOS

- [x] Customizable notification formats
- [ ] Add help documentation
- [ ] Reset database structure

## LICENSE
This plugin is distributed under the MIT License.

## Releases
`V0.1.2` Updated release information

`V0.1.0`-`V0.1.1` Completed main program and functionality, prepared for release