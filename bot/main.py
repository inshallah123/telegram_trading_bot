# bot/main.py
import logging
from telegram.ext import Application, CommandHandler

# 从同级目录导入 handlers 模块中的处理函数和对话处理器
from . import handlers
# 从项目根目录的 config 包导入 settings 模块
from config import settings # 确保 PYTHONPATH 或 IDE 正确设置

# 日志配置 (也可以在 settings.py 中统一配置，这里为了模块独立性再次配置)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def run_bot() -> None:
    """启动 Bot."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN 未在配置中找到！Bot 无法启动。")
        return

    # 创建 Application 实例
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # 注册命令处理器
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("chat", handlers.chat))
    # 注意：/cancel 命令主要在 ConversationHandler 内部使用，但也可以全局注册一个以防万一
    application.add_handler(CommandHandler("cancel", handlers.cancel))


    # 注册 ConversationHandler
    application.add_handler(handlers.calculate_signal_conv_handler)
    application.add_handler(handlers.query_data_conv_handler)

    # 注册错误处理器 (可选，但推荐)
    application.add_error_handler(handlers.error_handler)

    logger.info("Bot 正在启动...")
    # 启动 Bot (开始轮询)
    application.run_polling()
    logger.info("Bot 已停止。")


if __name__ == "__main__":
    # 这个部分使得你可以直接运行 python bot/main.py 来启动机器人
    # 但我们推荐使用项目根目录的 run_bot.py
    logger.warning("正在直接从 bot/main.py 运行。推荐使用项目根目录的 run_bot.py。")
    run_bot()