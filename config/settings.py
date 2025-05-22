import os
from dotenv import load_dotenv
import logging # 推荐加入日志记录

# 配置日志，方便调试
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 获取项目根目录的绝对路径
# __file__ 是当前文件 (settings.py) 的路径
# os.path.dirname(__file__) 是 config 目录的路径
# os.path.dirname(os.path.dirname(__file__)) 是项目根目录的路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 构建 .env 文件的完整路径
DOTENV_PATH = os.path.join(BASE_DIR, '.env')

# 加载 .env 文件中的环境变量
# 如果 .env 文件存在，则加载其中的变量到环境变量中
if os.path.exists(DOTENV_PATH):
    load_dotenv(dotenv_path=DOTENV_PATH)
    logger.info(f".env file loaded from: {DOTENV_PATH}")
else:
    logger.warning(f".env file not found at: {DOTENV_PATH}. Make sure it exists and contains your environment variables.")

# 从环境变量中获取 TELEGRAM_BOT_TOKEN
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 检查 Token 是否成功加载
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not found in environment variables. "
                   "Please ensure it is set in your .env file or system environment.")
    # 在这里你可以选择是抛出异常使程序停止，还是允许程序继续运行（但不推荐用于核心配置）
    # raise ValueError("TELEGRAM_BOT_TOKEN is not set!")
else:
    # 为了安全，不要在生产日志中打印完整的Token，这里只打印一部分或确认已加载
    logger.info("TELEGRAM_BOT_TOKEN loaded successfully.")
    # logger.info(f"Loaded TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:10]}...") # 仅显示前10位

# 你可以在这里添加其他的配置变量，例如：
# API_KEY = os.getenv("CHOICE_API_KEY")
# API_SECRET = os.getenv("CHOICE_API_SECRET")
# DEFAULT_ASSET = "IF2406.CFE" # 示例：默认关注的期货合约

# 也可以设置一些默认值，如果环境变量中没有的话
# LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

if __name__ == '__main__':
    # 这个部分用于直接运行 settings.py 时进行测试，查看配置是否加载正确
    print(f"Project Base Directory: {BASE_DIR}")
    print(f"Path to .env file: {DOTENV_PATH}")
    if TELEGRAM_BOT_TOKEN:
        print(f"Telegram Bot Token (first 10 chars): {TELEGRAM_BOT_TOKEN[:10]}...")
    else:
        print("Telegram Bot Token: Not Found")
    # print(f"Default Asset: {DEFAULT_ASSET}")
    # print(f"Log Level: {LOG_LEVEL}")