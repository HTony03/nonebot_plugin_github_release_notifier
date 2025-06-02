<p align="center">
  <a href="https://v2.nonebot.dev/store">
    <img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo">
  </a>
</p>
<p align="center">
  <img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText">
</p>

<p align="center">
  <em>✨ NoneBot GitHub Release Notifier ✨</em>
</p>

<p align="center">
  <a href="./LICENSE">
    <img src="https://img.shields.io/github/license/HTony03/nonebot_plugin_github_release_notifier.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-github-release-notifier">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-github-release-notifier.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg?style=social" alt="python">
  <a href="https://wakatime.com/badge/github/HTony03/nonebot_plugin_github_release_notifier">
    <img src="https://wakatime.com/badge/github/HTony03/nonebot_plugin_github_release_notifier.svg?style=social" alt="wakatime">
  </a>
</p>

This is a plugin for monitoring GitHub repository releases and sending notifications.

Other languages: [中文](./README.md)

## 📖 Introduction

This plugin can monitor multiple GitHub repositories, notify users of new updates via QQ Bot, and supports customizable notification formats.

## 💿 Installation

<details open>
<summary>Install via nb-cli</summary>
Open the command line in the root directory of your NoneBot2 project and enter:

    nb plugin install nonebot-plugin-github-release-notifier

</details>

<details>
<summary>Install via package manager</summary>
Open the command line in the plugin directory of your NoneBot2 project and enter the corresponding command for your package manager:

<details>
<summary>pip</summary>

    pip install nonebot-plugin-github-release-notifier
</details>

Open the `pyproject.toml` file in the root directory of your NoneBot2 project and add the following to the `[tool.nonebot]` section:

    plugins = ["nonebot-plugin-github-release-notifier"]

</details>

## ⚙️ Configuration

Before use, ensure that the `SUPERUSERS` configuration item in NoneBot is set.

Add the following configuration items to the `.env` file in your NoneBot2 project:

| Config Item | Required | Default | Description |
|:-----------:|:--------:|:-------:|:-----------:|
| GITHUB_TOKEN | No | Empty string | Token for accessing the GitHub API |
| GITHUB_RETRIES | No | 3 | Maximum retry attempts for refreshing |
| GITHUB_RETRY_DELAY | No | 5 | Delay between each refresh retry (seconds) |
| GITHUB_DISABLE_WHEN_FAIL | No | False | Disable configuration when repository data retrieval fails |
| GITHUB_SENDING_TEMPLATES | No | Default template | Customizable notification formats (see below) |
| GITHUB_SEND_FALIURE_GROUP | No | True | Notify group on failure |
| GITHUB_SEND_FALIURE_SUPERUSER | No | False | Notify superuser on failure |
| GITHUB_DEFAULT_CONFIG_SETTING | No | True | Monitor all events by default when adding a repo |
| GITHUB_SEND_IN_MARKDOWN | No | False | Send messages as Markdown images |
| GITHUB_SEND_DETAIL_IN_MARKDOWN | No | True | Send details (pr/issue/release) as Markdown images |
| GITHUB_UPLOAD_REMOVE_OLDER_VER | No | True | Remove old versions when uploading release files (in development) |

`v0.1.9` removed support for adding group repo via `.env`. Please use commands for related features.

### Customizable Notification Formats

The `GITHUB_SENDING_TEMPLATES` config allows users to customize the notification format for GitHub events. Format:

```dotenv
# Format: {"commit": <your_template>, "issue": <your_template>, "pull_req": <your_template>, "release": <your_template>}
# Available parameters:
# commit: repo, message, author, url, time
# issue: repo, title, author, url, time
# pull_req: repo, title, author, url, time
# release: repo, name, version, details, url, time
# Usage: '{<parameter>}' (uses Python format)
# Defaults to the standard template if not set
github_sending_templates={}
```

## 🎉 Usage

### Command Table

All commands **not restricted to admins or SUPERUSERS** have a 15s cooldown.

For private messages, add the group ID at the end of the command, e.g. `/repo.add <user>/<repo> <group_id>`

| Command | Permission | Requires @ | Scope | Description |
|:-------:|:----------:|:----------:|:-----:|:-----------:|
| /add_group_repo or /repo.add | SUPERUSERS or Admins | No | Private & Group | Add group-repository mapping |
| /del_group_repo or /repo.delete or /repo.del | SUPERUSERS or Admins | No | Private & Group | Delete group-repository mapping |
| /change_group_repo_cfg or /repo.config or /repo.cfg | SUPERUSERS or Admins | No | Private & Group | Modify repository configuration (supports boolean and string configs, see below) |
| /show_group_repo or /repo.show | SUPERUSERS or Admins | No | Private & Group | View group-repository mapping |
| /refresh_group_repo or /repo.refresh | SUPERUSERS or Admins | No | Private & Group | Refresh GitHub status |
| /repo_info or /repo.info | Everyone | No | Private & Group | View repository details |
| /check_api_usage | Everyone | No | Private & Group | View GitHub API usage |
| /latest_release | Everyone | No | Private & Group | Get latest release of a repository |
| /latest_commit | Everyone | No | Private & Group | Get latest commit of a repository |

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
   /change_group_repo_cfg <user>/<repo> <config> <value>
   ```

   - `<config>` options and types:
     - `commit`/`issue`/`pull_req`/`release`/`commits`/`issues`/`prs`/`releases`/`send_release`: boolean (True/False)
     - `release_folder`: string

   For example:

   ```
   /change_group_repo_cfg <user>/<repo> issue False
   /change_group_repo_cfg <user>/<repo> release_folder <folder_name>
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
   /repo_info <user>/<repo>
   ```

7. View API usage:

   ```
   /check_api_usage
   ```

8. Get latest release:

   ```
   /latest_release <user>/<repo>
   ```

9. Get latest commit:

   ```
   /latest_commit <user>/<repo>
   ```

### TODOS

- [x] Customizable notification formats
- [ ] Add help documentation
- [ ] Reset database structure
- [x] Markdown message support
- [x] Markdown to image rendering
- [ ] Issue/PR details support
- [ ] Forward issue/PR comments
- [ ] Render GitHub page for PR/issue display

## LICENSE

This plugin is distributed under the MIT License. See [here](./LICENSE) for details.

## Releases

`v0.1.9` Removed support for adding group repo via `.env`, please use commands for related features

`v0.1.8` Bug fixes, readme update

`v0.1.3`-`v0.1.7` Bug fixes, published to nonebot

`V0.1.2` Updated release information

`V0.1.0`-`V0.1.1` Main program completed, features adapted, ready for 
