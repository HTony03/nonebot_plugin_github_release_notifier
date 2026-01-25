<div align="center">
    <a href="https://v2.nonebot.dev/store">
    <img src="https://raw.githubusercontent.com/fllesser/nonebot-plugin-template/refs/heads/resource/.docs/NoneBotPlugin.svg" width="310" alt="logo"></a>

  <em>✨ NoneBot GitHub Release Notifier ✨</em>
</div>

<p align="center">
  <a href="https://github.com/HTony03/nonebot_plugin_github_release_notifier/LICENSE">
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

本插件用于监控 GitHub 仓库发布并发送通知。

**本项目为纯GitHub REST API实现，非webhook，不依赖相关服务**

其他语言 | Other languages: [English](https://github.com/HTony03/nonebot_plugin_github_release_notifier/blob/main/README_en.md)

## 📖 介绍

本插件可以监控多个 GitHub 仓库，通过 QQ Bot 通知用户新动态，并支持自定义通知格式。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行，输入以下指令即可安装：

    nb plugin install nonebot-plugin-github-release-notifier

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下，打开命令行，根据你使用的包管理器，输入相应的安装命令：

<details>
<summary>pip</summary>

    pip install nonebot-plugin-github-release-notifier
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件，在 `[tool.nonebot]` 部分追加写入：

    plugins = ["nonebot-plugin-github-release-notifier"]

</details>

## ⚙️ 配置

使用前请确保 nonebot2 的 SUPERUSERS 配置项已配置。

在 nonebot2 项目的 `.env` 文件中添加下表中的必填配置：

| 配置项 | 必填 |   默认值   |                          说明                           |
|:-----:|:----:|:-------:|:-----------------------------------------------------:|
| GITHUB_TOKEN | 否 |  空字符串   |                用于访问 GitHub API 的 Token                |
| GITHUB_RETRIES | 否 |    3    |                       刷新最大重试次数                        |
| GITHUB_RETRY_DELAY | 否 |    5    |                    每次刷新重试之间的延迟（秒）                     |
| GITHUB_LANGUAGE | 否 | "en_us" |                        发送的模板语言                        |
| GITHUB_SEND_FALIURE_GROUP | 否 |  True   |                       失败时是否通知群聊                       |
| GITHUB_SEND_FALIURE_SUPERUSER | 否 |  False  |                      失败时是否通知超级用户                      |
| GITHUB_DEFAULT_CONFIG_SETTING | 否 |  True   |                     添加仓库时默认监控所有事件                     |
| GITHUB_SEND_IN_MARKDOWN | 否 |  False  |                 是否以 Markdown 图片方式发送消息                 |
| GITHUB_SEND_DETAIL_IN_MARKDOWN | 否 |  True   |       是否以 Markdown 图片方式发送详细信息（pr/issue/release）       |
| GITHUB_SEND_PREV_DETAILS | 否 |  False  |                    是否发送添加repo前的数据                     |
| GITHUB_UPLOAD_REMOVE_OLDER_VER | 否 |  True   |        上传 release 文件时是否移除旧版本( in development)         |
| GITHUB_THEME | 否 | "dark"  | （针对issue/pull request comment）渲染页面风格 ["light","dark"] | 

`v0.1.9` 删除了对于`.env`添加群组repo的适配, 请使用指令使用相关功能

`v0.1.10` 删除了使用自定义模板输出格式，请使用`github_language`配置相关模板


## 🎉 使用

### 指令表

本插件所有**非仅管理员或SUPERUSEES**指令均设有15s Cooldown

私聊使用command请将配置群号放在指令最后，如`/repo.add <user>/<repo> <group_id>`

| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| /add_group_repo 或 /repo.add | SUPERUSERS 或管理员 | 否 | 私聊&群聊 | 添加群组仓库映射 |
| /del_group_repo 或 /repo.delete 或 /repo.del | SUPERUSERS 或管理员 | 否 | 私聊&群聊 | 删除群组仓库映射 |
| /change_group_repo_cfg 或 /repo.config 或 /repo.cfg | SUPERUSERS 或管理员 | 否 | 私聊&群聊 | 修改仓库配置（支持布尔型和字符串型配置，详见下方说明） |
| /show_group_repo 或 /repo.show | SUPERUSERS 或管理员 | 否 | 私聊&群聊 | 查看群组仓库映射 |
| /refresh_group_repo 或 /repo.refresh | SUPERUSERS 或管理员 | 否 | 私聊&群聊 | 刷新 GitHub 状态 |
| /repo_info 或 /repo.info | 所有人 | 否 | 私聊&群聊 | 查看仓库详细信息 |
| /check_api_usage | 所有人 | 否 | 私聊&群聊 | 查看 GitHub API 使用情况 |


### TODOS

- [x] 自定义发送信息格式
- [ ] 添加help
- [ ] 数据库结构重置
- [x] markdown 信息支持
- [x] markdown 转图片展示
- [ ] issue/pr 详细信息支持
- [x] 转发issue/pr comments
- [x] 渲染gh页面展示pr/issue

## LICENCE

本插件按照MIT协议传播，相关LICENCE见[此处](https://github.com/HTony03/nonebot_plugin_github_release_notifier/LICENSE)

## Releases

`v0.1.10` 添加issue comment转发支持，使用[`cscs181/QQ-GitHub-Bot`](https://github.com/cscs181/QQ-GitHub-Bot)渲染新页面

`v0.1.9` 删除了对于`.env`添加群组repo, 请使用指令使用相关功能

`v0.1.8` 已知问题修复，readme更新

`v0.1.3`-`v0.1.7` bug修复，发布至nonebot

`V0.1.2` 修改发布信息

`V0.1.0`-`V0.1.1` 主程序完成，功能适配， 准备发布
</br>
</br>
</br>
#### 免责申明（叠甲（bushi））
插件**部分**代码来自/启发自 [`cscs181/QQ-GitHub-Bot`](https://github.com/cscs181/QQ-GitHub-Bot)，以MIT协议传播，详细可见 [此处](https://github.com/cscs181/QQ-GitHub-Bot/blob/master/LICENSE)。

