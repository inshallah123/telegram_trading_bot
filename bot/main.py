import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from handlers import (
    start_command, help_command, status_command, restart_command,
    handle_message, error_handler, cleanup_inactive_sessions
)

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(_application: Application
) -> None:
    """Bot启动后的初始化"""
    # 创建清理任务
    asyncio.create_task(cleanup_inactive_sessions())
    logger.info("会话清理任务已启动")


def main():
    """启动Bot"""
    # 获取Token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("未找到TELEGRAM_BOT_TOKEN，请检查.env文件")
        return

    # 创建应用
    application = Application.builder().token(token).post_init(post_init).build()

    # 注册命令处理器
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("restart", restart_command))

    # 注册消息处理器
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 注册错误处理器
    application.add_error_handler(error_handler)

    # 启动Bot
    logger.info("Bot启动中...")
    try:
        application.run_polling(allowed_updates=['message'])
    except KeyboardInterrupt:
        logger.info("Bot已停止")
    except Exception as e:
        logger.error(f"Bot运行时出错：{e}")


if __name__ == '__main__':
    main()