# Telegram Trading Bot

一个基于Telegram的期货量化交易机器人，实现布林带趋势跟踪策略，通过Choice API获取实时行情数据。

## 功能特性

- 🤖 Telegram Bot交互界面
- 📈 布林带趋势跟踪策略
- 📊 Choice API实时行情数据
- 📱 手机端随时查看交易信号
- ⚡ 一次性信号生成，无需数据存储

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 环境配置

创建 `.env` 文件并配置以下参数：

```env
# Telegram Bot Token
TELEGRAM_BOT_TOKEN="your_bot_token_here"

# Choice API登录配置
CHOICE_USERNAME="your_choice_username"
CHOICE_PASSWORD="your_choice_password"

# 授权用户ID
AUTHORIZED_USERS="123456789,987654321"

# 日志级别
LOG_LEVEL="INFO"
```

### 运行Bot

```bash
python main.py
```

## 项目结构

```
telegram_trading_bot/
├── main.py                 # 主入口文件
├── config.py              # 配置管理
├── requirements.txt       # 依赖包
├── .env                   # 环境变量
├── bot/                   # Telegram Bot模块
│   ├── handlers.py        # 消息处理器
│   ├── commands.py        # 命令处理
│   └── keyboards.py       # 键盘布局
├── trading/               # 交易模块
│   ├── choice_api.py      # Choice API接口
│   ├── bollinger.py       # 布林带策略
│   └── signals.py         # 信号计算与管理
```

## Bot命令

- `/start` - 启动机器人
- `/help` - 帮助信息
- `/signal` - 获取交易信号
- `/config` - 配置交易参数
- `/status` - 查看状态

## 开发说明

本项目遵循最小够用原则，适合小范围亲友使用。后续可根据需要扩展功能。

## 注意事项

- 仅供学习和个人使用
- 交易有风险，投资需谨慎
- 请妥善保管API密钥

## License

MIT License