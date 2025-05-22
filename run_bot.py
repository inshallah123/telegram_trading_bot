# run_bot.py (在项目根目录 D:\QT\trading bot\)
import logging
from config import settings # 从 config 包导入 settings
from bot import main as bot_module # 从 bot 包导入 main 模块

# 配置基础日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler() # 输出到控制台
        # 如果需要，可以添加 logging.FileHandler("bot.log") 输出到文件
    ]
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("尝试启动 Trading Bot...")
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error(
            "错误: Telegram Bot Token 未配置。 "
            "请检查你的 .env 文件和 config/settings.py。"
        )
    else:
        logger.info("配置加载成功。正在启动 Bot 核心模块...")
        try:
            bot_module.run_bot() # 调用 bot/main.py 中的 run_bot 函数
        except Exception as e:
            logger.critical(f"Bot 启动或运行时发生严重错误: {e}", exc_info=True)
        finally:
            logger.info("Trading Bot 进程结束。")