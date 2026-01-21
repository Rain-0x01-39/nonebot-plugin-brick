from nonebot import get_driver, get_plugin_config, logger
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="砖",
    description="功夫再好，一砖撂倒。烧制砖头来拍群友吧，拍好了禁言他，没拍好被禁言！",
    usage="{插件用法}",
    type="application",
    homepage="https://github.com/SZ2528/nonebot-plugin-brick",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

driver = get_driver()
config = get_plugin_config(Config)
