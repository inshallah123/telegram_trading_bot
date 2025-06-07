import logging
from datetime import datetime
import re

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 用户状态枚举
class UserState:
    WAITING_NET_ASSET = "waiting_net_asset"
    WAITING_SIGNAL_DATE = "waiting_signal_date"
    WAITING_BOLLINGER_PERIOD = "waiting_bollinger_period"
    COMPLETED = "completed"


# 存储用户状态和数据
user_sessions = {}


class UserSession:
    """用户会话数据"""

    def __init__(self, user_id):
        self.user_id = user_id
        self.state = UserState.WAITING_NET_ASSET
        self.net_asset = None
        self.signal_date = None
        self.bollinger_period = None
        self.created_at = datetime.now()


async def start_command(update, context):
    """处理 /start 命令"""
    _ = context  # 明确标记未使用的参数
    user_id = update.effective_user.id
    user_sessions[user_id] = UserSession(user_id)

    welcome_msg = (
        "你好！欢迎使用期货交易信号助手 ✨\n\n"
        "我需要收集一些信息来为你提供个性化服务：\n"
        "📊 净资产\n"
        "📅 信号日期\n"
        "📈 布林带周期\n\n"
        "让我们开始吧！请输入你的净资产金额（单位：元）："
    )

    await update.message.reply_text(welcome_msg)


async def handle_net_asset(update, context):
    """处理净资产输入"""
    _ = context  # 明确标记未使用的参数
    user_id = update.effective_user.id
    text = update.message.text.strip()

    try:
        # 移除可能的逗号和空格
        cleaned_text = re.sub(r'[,\s]', '', text)
        net_asset = float(cleaned_text)

        if net_asset <= 0:
            await update.message.reply_text("净资产必须大于0，请重新输入：")
            return

        # 保存数据并进入下一状态
        user_sessions[user_id].net_asset = net_asset
        user_sessions[user_id].state = UserState.WAITING_SIGNAL_DATE

        await update.message.reply_text(
            f"净资产已记录：¥{net_asset:,.2f}\n\n"
            "请输入信号日期（格式：YYYYMMDD，如：20250607）："
        )

    except ValueError:
        await update.message.reply_text(
            "输入格式不正确，请输入有效的数字金额："
        )


async def handle_signal_date(update, context):
    """处理信号日期输入"""
    _ = context  # 明确标记未使用的参数
    user_id = update.effective_user.id
    text = update.message.text.strip()

    try:
        # 验证日期格式
        if not re.match(r'^\d{8}$', text):
            raise ValueError("日期格式不正确")

        # 验证日期有效性
        datetime.strptime(text, '%Y%m%d')

        # 保存数据并进入下一状态
        user_sessions[user_id].signal_date = text
        user_sessions[user_id].state = UserState.WAITING_BOLLINGER_PERIOD

        await update.message.reply_text(
            f"信号日期已记录：{text}\n\n"
            "请输入布林带周期（建议范围：10-50）："
        )

    except ValueError:
        await update.message.reply_text(
            "日期格式不正确！请输入8位数字格式（YYYYMMDD），如：20250607"
        )


async def handle_bollinger_period(update, context):
    """处理布林带周期输入"""
    _ = context  # 明确标记未使用的参数
    user_id = update.effective_user.id
    text = update.message.text.strip()

    try:
        period = int(text)

        if not (5 <= period <= 250):
            await update.message.reply_text(
                "布林带周期太大或太小，请重新输入："
            )
            return

        # 保存数据并完成收集
        session = user_sessions[user_id]
        session.bollinger_period = period
        session.state = UserState.COMPLETED

        # 显示汇总信息
        summary_msg = (
            "✅ 信息收集完成！\n\n"
            f"📊 净资产：¥{session.net_asset:,.2f}\n"
            f"📅 信号日期：{session.signal_date}\n"
            f"📈 布林带周期：{session.bollinger_period}天\n\n"
            "现在你可以使用其他功能了！\n"
            "输入 /help 查看可用命令。"
        )

        await update.message.reply_text(summary_msg)

    except ValueError:
        await update.message.reply_text(
            "请输入有效的整数作为布林带周期："
        )


async def handle_message(update, context):
    """处理普通消息"""
    user_id = update.effective_user.id

    # 检查用户是否有活跃会话
    if user_id not in user_sessions:
        await update.message.reply_text(
            "请先输入 /start 开始使用。"
        )
        return

    session = user_sessions[user_id]

    # 根据当前状态处理消息
    if session.state == UserState.WAITING_NET_ASSET:
        await handle_net_asset(update, context)
    elif session.state == UserState.WAITING_SIGNAL_DATE:
        await handle_signal_date(update, context)
    elif session.state == UserState.WAITING_BOLLINGER_PERIOD:
        await handle_bollinger_period(update, context)
    elif session.state == UserState.COMPLETED:
        await update.message.reply_text(
            "信息已收集完成。输入 /help 查看可用命令，或 /restart 重新设置。"
        )


async def help_command(update, context):
    """处理 /help 命令"""
    _ = context  # 明确标记未使用的参数
    help_text = (
        "🤖 期货交易信号助手使用指南\n\n"
        "📋 可用命令：\n"
        "/start - 开始设置个人信息\n"
        "/help - 显示此帮助信息\n"
        "/status - 查看当前设置\n"
        "/restart - 重新设置信息\n\n"
        "❓ 如有问题，请联系管理员。"
    )
    await update.message.reply_text(help_text)


async def status_command(update, context):
    """处理 /status 命令"""
    _ = context  # 明确标记未使用的参数
    user_id = update.effective_user.id

    if user_id not in user_sessions:
        await update.message.reply_text("请先输入 /start 开始设置。")
        return

    session = user_sessions[user_id]

    if session.state == UserState.COMPLETED:
        status_msg = (
            "📊 当前设置信息：\n\n"
            f"💰 净资产：¥{session.net_asset:,.2f}\n"
            f"📅 信号日期：{session.signal_date}\n"
            f"📈 布林带周期：{session.bollinger_period}天\n"
            f"🕐 设置时间：{session.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
    else:
        status_msg = "⚠️ 信息设置未完成，请继续输入所需信息。"

    await update.message.reply_text(status_msg)


async def restart_command(update, context):
    """处理 /restart 命令"""
    _ = context  # 明确标记未使用的参数
    user_id = update.effective_user.id
    user_sessions[user_id] = UserSession(user_id)

    await update.message.reply_text(
        "🔄 已重置设置，请输入你的净资产金额（单位：元）："
    )


def get_user_data(user_id):
    """获取用户数据（供其他模块调用）"""
    if user_id in user_sessions and user_sessions[user_id].state == UserState.COMPLETED:
        session = user_sessions[user_id]
        return {
            'net_asset': session.net_asset,
            'signal_date': session.signal_date,
            'bollinger_period': session.bollinger_period
        }
    return None


async def error_handler(update, context):
    """全局错误处理"""
    logger.error(f"更新 {update} 引起异常：{context.error}")

    if update and update.message:
        await update.message.reply_text(
            "抱歉，处理你的请求时出现了错误。请稍后重试或联系管理员。"
        )