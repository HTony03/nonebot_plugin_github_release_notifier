<div align="center">
    <a href="https://v2.nonebot.dev/store">
    <img src="https://raw.githubusercontent.com/fllesser/nonebot-plugin-template/refs/heads/resource/.docs/NoneBotPlugin.svg" width="310" alt="logo"></a>

  <em>✨ NoneBot GitHub Release Notifier ✨</em>
</div>

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

Before use, ensure that the `SUPERUSERS` configuration item in NoneBot2 is set.

Add the following required configuration items to the `.env` file in your NoneBot2 project:

| Config Item | Required | Default |                               Description                               |
|:-----------:|:--------:|:-------:|:-----------------------------------------------------------------------:|
| GITHUB_TOKEN |    No    | Empty string |                   Token for accessing the GitHub API                    |
| GITHUB_RETRIES |    No    | 3 |                  Maximum retry attempts for refreshing                  |
| GITHUB_RETRY_DELAY |    No    | 5 |               Delay between each refresh retry (seconds)                |
| GITHUB_LANGUAGE |    No    | "en_us" |                     Language for sending templates                      |
| GITHUB_SEND_FALIURE_GROUP |    No    | True |                         Notify group on failure                         |
| GITHUB_SEND_FALIURE_SUPERUSER |    No    | False |                       Notify superuser on failure                       |
| GITHUB_DEFAULT_CONFIG_SETTING |    No    | True |            Monitor all events by default when adding a repo             |
| GITHUB_SEND_IN_MARKDOWN |    No    | False |                    Send messages as Markdown images                     |
| GITHUB_SEND_DETAIL_IN_MARKDOWN |    No    | True |           Send details (pr/issue/release) as Markdown images            |
| GITHUB_SEND_PREV_DETAILS |    No    |  False  |       Whether send previous details when adding a new repository        |
| GITHUB_UPLOAD_REMOVE_OLDER_VER |    No    | True |    Remove old versions when uploading release files (in development)    |
| GITHUB_THEME |    No    | "dark" | (For issue/pull request comments) Page rendering style ["light","dark"] |

`v0.1.9` removed support for adding group repo via `.env`. Please use commands for related features.

`v0.1.10` removed custom template output format, please use `github_language` configuration for related templates.

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

### TODOS

- [x] Customizable notification formats
- [ ] Add help documentation
- [ ] Reset database structure
- [x] Markdown message support
- [x] Markdown to image rendering
- [ ] Issue/PR details support
- [x] Forward issue/PR comments
- [x] Render GitHub page for PR/issue display

## LICENSE

This plugin is distributed under the MIT License. See [here](./LICENSE) for details.

## Releases

`v0.1.10` Added issue comment forwarding support, using [`cscs181/QQ-GitHub-Bot`](https://github.com/cscs181/QQ-GitHub-Bot) to render new pages

`v0.1.9` Removed support for adding group repo via `.env`, please use commands for related features

`v0.1.8` Known issues fixed, readme updated

`v0.1.3`-`v0.1.7` Bug fixes, published to nonebot

`V0.1.2` Updated release information

`V0.1.0`-`V0.1.1` Main program completed, features adapted, ready for release
</br>
</br>
</br>
#### Disclaimer
**Some** of the plugin code is derived from/inspired by [`cscs181/QQ-GitHub-Bot`](https://github.com/cscs181/QQ-GitHub-Bot), distributed under the MIT License, details can be found [here](https://github.com/cscs181/QQ-GitHub-Bot/blob/master/LICENSE).
