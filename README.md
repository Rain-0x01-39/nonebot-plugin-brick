<div align="center">
    <a href="https://v2.nonebot.dev/store">
    <img src="https://raw.githubusercontent.com/fllesser/nonebot-plugin-template/refs/heads/resource/.docs/NoneBotPlugin.svg" width="310" alt="logo"></a>
</div>


<div align="center">

# nonebot-plugin-brick

_✨ 烧制砖块，然后拍晕群友！ ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/SZ2528/nonebot-plugin-brick.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-brick">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-brick.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>


## 📖 介绍

功夫再好，一砖撂倒。烧制砖头来拍群友吧，拍好了禁言他，没拍好被禁言！

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-brick

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-brick
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-brick
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-brick
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-brick
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_brick"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| BRICK__MAX_BRICK | 否 | 1 | 砖块最多持有量 |
| BRICK__COST | 否 | 10 | 多少条消息能烧好一块砖 |
| BRICK__COOLDOWN | 否 | 60 | 拍砖冷却时间（秒） |
| BRICK__MIN_MUTE_TIME | 否 | 10 | 最小禁言时间（秒） |
| BRICK__MAX_MUTE_TIME | 否 | 120 | 最大禁言时间（秒） |
| BRICK__REVERSE | 否 | 10 | 反被拍晕的默认概率（%） |
| BRICK__SPECIAL_USER | 否 | {} | 键为用户ID，值为被拍时的反击概率（%）<br/>不设置则使用默认概率 |
| BRICK__CHECKING | 否 | False | 是否开启每日签到（获取随机数量的砖头） |
| BRICK__MIN_GAIN | 否 | 1 | 最小获取数量 |
| BRICK__MAX_GAIN | 否 | 5 | 最大获取数量 |

## 🎉 使用
### 指令表
记得在前面加上命令消息的起始符（通常为`/`）
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 砖头 烧砖 | 群员 | 否 | 群聊 | 烧点砖头拍人 |
| 砖头 拍人 @someone | 群员 | 否 | 群聊 | 拍晕（禁言）对方随机时间，有概率被反将一军 |
| 砖头 随机拍人 | 群员 | 否 | 群聊 | 随机拍晕（禁言）某个群友随机时间，有概率被反将一军 |
| 砖头 查看 | 群员 | 否 | 群聊 | 看看自己在这个群有多少砖头 |
| 砖头 签到 | 群员 | 否 | 群聊 | 签到获取随机数量砖头 |
### 效果图
如果有效果图的话
