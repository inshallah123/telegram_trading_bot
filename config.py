"""
配置管理模块
从环境变量和配置文件中读取应用配置
"""
import os
from typing import List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""

    # Telegram Bot配置
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # Choice API配置
    CHOICE_USERNAME: str = os.getenv("CHOICE_USERNAME", "")
    CHOICE_PASSWORD: str = os.getenv("CHOICE_PASSWORD", "")

    # 授权用户配置
    AUTHORIZED_USERS: List[int] = [
        int(user_id.strip())
        for user_id in os.getenv("AUTHORIZED_USERS", "").split(",")
        if user_id.strip()
    ]

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # 交易策略默认配置
    BOLLINGER_PERIOD: int = 19  # 布林带周期
    BOLLINGER_STD: float = 2.0  # 标准差倍数

    @classmethod
    def validate(cls) -> bool:
        """验证必要的配置是否存在"""
        required_configs = [
            "TELEGRAM_BOT_TOKEN",
            "CHOICE_USERNAME",
            "CHOICE_PASSWORD"
        ]

        missing_configs = []
        for config in required_configs:
            if not getattr(cls, config):
                missing_configs.append(config)

        if missing_configs:
            print(f"❌ 缺少必要配置: {', '.join(missing_configs)}")
            return False

        print("✅ 配置验证通过")
        return True

    @classmethod
    def is_authorized_user(cls, user_id: int) -> bool:
        """检查用户是否有权限"""
        return user_id in cls.AUTHORIZED_USERS

# 创建全局配置实例
config = Config()