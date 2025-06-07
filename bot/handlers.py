import logging
from datetime import datetime, timedelta
import re
import asyncio
import os
from dotenv import load_dotenv


# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 用户状态枚举
class UserState:
    WAITING_NET_ASSET = "waiting_net_asset"
    WAITING_SIGNAL_DATE = "waiting_signal_date"
    WAITING_BOLLINGER_CHOICE = "waiting_bollinger_choice"
    WAITING_BOLLINGER_PERIOD = "waiting_bollinger_period"
    WAITING_CFMMC_CHOICE = "waiting_cfmmc_choice"
    WAITING_CFMMC_USERNAME = "waiting_cfmmc_username"
    WAITING_CFMMC_PASSWORD = "waiting_cfmmc_password"
    COMPLETED = "completed"


class UserSession:
    """用户会话数据"""

    def __init__(self, user_id):
        self.user_id = user_id
        self.state = UserState.WAITING_NET_ASSET
        self.net_asset = None
        self.signal_date = None
        self.use_custom_bollinger = None
        self.bollinger_period = 19  # 默认值
        self.bollinger_std = 2  # 默认值
        self.use_custom_cfmmc = None
        self.cfmmc_username = None
        self.cfmmc_password = None
        self.created_at = datetime.now()


class UserDataManager:
    """用户数据管理器 - 封装所有数据存储和访问"""

    def __init__(self):
        self._sessions = {}  # 私有存储
        self._last_activity = {}

    # ========== 会话管理方法 ==========

    def create_session(self, user_id):
        """创建新会话"""
        self._sessions[user_id] = UserSession(user_id)
        self._last_activity[user_id] = datetime.now()
        return self._sessions[user_id]

    def get_session(self, user_id):
        """获取会话（内部使用）"""
        return self._sessions.get(user_id)

    def has_session(self, user_id):
        """检查用户是否有会话"""
        return user_id in self._sessions

    def delete_session(self, user_id):
        """删除会话"""
        self._sessions.pop(user_id, None)
        self._last_activity.pop(user_id, None)

    def update_activity(self, user_id):
        """更新活动时间"""
        self._last_activity[user_id] = datetime.now()

    # ========== 状态更新方法 ==========

    def update_state(self, user_id, new_state):
        """更新会话状态"""
        if user_id in self._sessions:
            self._sessions[user_id].state = new_state

    def update_net_asset(self, user_id, net_asset):
        """更新净资产"""
        if user_id in self._sessions:
            self._sessions[user_id].net_asset = net_asset

    def update_signal_date(self, user_id, signal_date):
        """更新信号日期"""
        if user_id in self._sessions:
            self._sessions[user_id].signal_date = signal_date

    def update_bollinger_choice(self, user_id, use_custom):
        """更新布林带选择"""
        if user_id in self._sessions:
            self._sessions[user_id].use_custom_bollinger = use_custom

    def update_bollinger_period(self, user_id, period):
        """更新布林带周期"""
        if user_id in self._sessions:
            self._sessions[user_id].bollinger_period = period

    def update_cfmmc_choice(self, user_id, use_custom):
        """更新CFMMC选择"""
        if user_id in self._sessions:
            self._sessions[user_id].use_custom_cfmmc = use_custom

    def update_cfmmc_credentials(self, user_id, username, password):
        """更新CFMMC凭据"""
        if user_id in self._sessions:
            self._sessions[user_id].cfmmc_username = username
            self._sessions[user_id].cfmmc_password = password

    # ========== 数据获取方法（对外接口）==========

    def get_complete_data(self, user_id):
        """获取完整用户数据"""
        if not self.is_setup_complete(user_id):
            return None

        session = self._sessions[user_id]
        return {
            'net_asset': session.net_asset,
            'signal_date': session.signal_date,
            'use_custom_bollinger': session.use_custom_bollinger,
            'bollinger_period': session.bollinger_period,
            'bollinger_std': session.bollinger_std,
            'use_custom_cfmmc': session.use_custom_cfmmc,
            'cfmmc_username': session.cfmmc_username,
            'cfmmc_password': session.cfmmc_password
        }

    def get_user_state(self, user_id):
        """获取用户当前状态"""
        session = self._sessions.get(user_id)
        return session.state if session else None

    def is_setup_complete(self, user_id):
        """检查用户是否完成设置"""
        session = self._sessions.get(user_id)
        return session and session.state == UserState.COMPLETED

    def get_bollinger_params(self, user_id):
        """获取布林带参数 (period, std)"""
        session = self._sessions.get(user_id)
        if session and session.state == UserState.COMPLETED:
            return session.bollinger_period, session.bollinger_std
        return 19, 2  # 默认值

    def get_cfmmc_credentials(self, user_id):
        """获取CFMMC凭据"""
        session = self._sessions.get(user_id)
        if (session and
                session.state == UserState.COMPLETED and
                session.use_custom_cfmmc):
            return {
                'username': session.cfmmc_username,
                'password': session.cfmmc_password
            }
        return {
            'username': os.getenv('CFMMC_USER_NAME'),
            'password': os.getenv('CFMMC_PASSWORD')
        }

    def get_net_asset(self, user_id):
        """获取净资产"""
        session = self._sessions.get(user_id)
        if session and session.state == UserState.COMPLETED:
            return session.net_asset
        return None

    def get_signal_date(self, user_id):
        """获取信号日期"""
        session = self._sessions.get(user_id)
        if session and session.state == UserState.COMPLETED:
            return session.signal_date
        return None

    # ========== 清理和维护方法 ==========

    def cleanup_inactive_sessions(self, inactive_hours=2, completed_hours=24):
        """清理不活跃会话，返回清理的数量"""
        now = datetime.now()
        to_remove = []

        for user_id, last_time in list(self._last_activity.items()):
            if user_id not in self._sessions:
                to_remove.append(user_id)
                continue

            session = self._sessions[user_id]

            # 根据状态使用不同的超时时间
            if session.state == UserState.COMPLETED:
                timeout = timedelta(hours=completed_hours)
            else:
                timeout = timedelta(hours=inactive_hours)

            if now - last_time > timeout:
                to_remove.append(user_id)

        # 执行清理
        for user_id in to_remove:
            self.delete_session(user_id)

        return len(to_remove)

    def get_active_users_count(self):
        """获取活跃用户数量"""
        return len(self._sessions)

    def get_all_user_ids(self):
        """获取所有用户ID"""
        return list(self._sessions.keys())


# 创建全局数据管理器实例
user_data_manager = UserDataManager()


async def cleanup_task():
    """定期清理任务"""
    while True:
        try:
            await asyncio.sleep(1800)  # 30分钟检查一次

            # 使用数据管理器的清理方法
            removed_count = user_data_manager.cleanup_inactive_sessions()

            if removed_count > 0:
                logger.info(f"清理了 {removed_count} 个超时会话")
                logger.info(f"当前活跃会话数: {user_data_manager.get_active_users_count()}")

        except Exception as e:
            logger.error(f"清理会话时出错: {e}")


async def start_command(update, context):
    """处理 /start 命令"""
    _ = context
    user_id = update.effective_user.id

    # 更新活动时间
    user_data_manager.update_activity(user_id)

    # 检查是否已有会话
    if user_data_manager.has_session(user_id):
        session = user_data_manager.get_session(user_id)

        if session.state == UserState.COMPLETED:
            # 已完成设置
            await update.message.reply_text(
                "你好！看起来你已经完成了设置 ✨\n\n"
                "输入 /status 查看当前设置\n"
                "输入 /restart 重新设置\n"
                "输入 /help 查看所有命令"
            )
            return
        else:
            # 设置未完成，询问是否继续
            await update.message.reply_text(
                "检测到你有未完成的设置，是否继续之前的设置？\n\n"
                "回复 '继续' 接着之前的步骤\n"
                "回复 '重新开始' 清空重新设置\n"
                "或者直接输入 /restart 重新开始"
            )
            return

    # 新用户，开始设置
    user_data_manager.create_session(user_id)

    welcome_msg = (
        "你好！欢迎使用期货交易信号助手 ✨\n\n"
        "我需要收集一些信息来为你提供个性化服务：\n"
        "📊 净资产\n"
        "📅 信号日期\n"
        "📈 布林带参数\n"
        "👤 CFMMC账户信息\n\n"
        "让我们开始吧！请输入你的净资产金额（单位：元）："
    )

    await update.message.reply_text(welcome_msg)


async def handle_net_asset(update, context):
    """处理净资产输入"""
    _ = context
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
        user_data_manager.update_net_asset(user_id, net_asset)
        user_data_manager.update_state(user_id, UserState.WAITING_SIGNAL_DATE)

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
    _ = context
    user_id = update.effective_user.id
    text = update.message.text.strip()

    try:
        # 验证日期格式
        if not re.match(r'^\d{8}$', text):
            raise ValueError("日期格式不正确")

        # 验证日期有效性
        datetime.strptime(text, '%Y%m%d')

        # 保存数据并进入布林带选择状态
        user_data_manager.update_signal_date(user_id, text)
        user_data_manager.update_state(user_id, UserState.WAITING_BOLLINGER_CHOICE)

        await update.message.reply_text(
            f"信号日期已记录：{text}\n\n"
            "是否需要自定义布林带周期参数？\n"
            "回复 '是' 进行自定义设置\n"
            "回复 '否' 使用默认参数 (19, 2)"
        )

    except ValueError:
        await update.message.reply_text(
            "日期格式不正确！请输入8位数字格式（YYYYMMDD），如：20250607"
        )


async def handle_bollinger_choice(update, context):
    """处理布林带参数选择"""
    _ = context
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    if text in ['是', 'yes', 'y', '1']:
        user_data_manager.update_bollinger_choice(user_id, True)
        user_data_manager.update_state(user_id, UserState.WAITING_BOLLINGER_PERIOD)

        await update.message.reply_text(
            "请输入布林带周期（建议范围：10-50）："
        )
    elif text in ['否', 'no', 'n', '0']:
        user_data_manager.update_bollinger_choice(user_id, False)
        user_data_manager.update_state(user_id, UserState.WAITING_CFMMC_CHOICE)

        await update.message.reply_text(
            "已设置使用默认布林带参数 (19, 2)\n\n"
            "是否需要录入CFMMC账户密码信息？\n"
            "回复 '是' 进行账户设置\n"
            "回复 '否' 使用 yyh's 检查持仓状态"
        )
    else:
        await update.message.reply_text(
            "请回复 '是' 或 '否'："
        )


async def handle_bollinger_period(update, context):
    """处理布林带周期输入"""
    _ = context
    user_id = update.effective_user.id
    text = update.message.text.strip()

    try:
        period = int(text)

        if not (5 <= period <= 250):
            await update.message.reply_text(
                "布林带周期建议在5-250之间，请重新输入："
            )
            return

        # 保存数据并进入CFMMC选择状态
        user_data_manager.update_bollinger_period(user_id, period)
        user_data_manager.update_state(user_id, UserState.WAITING_CFMMC_CHOICE)

        await update.message.reply_text(
            f"布林带周期已设置为：{period}天\n\n"
            "是否需要录入CFMMC账户密码信息？\n"
            "回复 '是' 进行账户设置\n"
            "回复 '否' 使用 yyh's 检查持仓状态"
        )

    except ValueError:
        await update.message.reply_text(
            "请输入有效的整数作为布林带周期："
        )


async def handle_cfmmc_choice(update, context):
    """处理CFMMC账户选择"""
    _ = context
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    if text in ['是', 'yes', 'y', '1']:
        user_data_manager.update_cfmmc_choice(user_id, True)
        user_data_manager.update_state(user_id, UserState.WAITING_CFMMC_USERNAME)

        await update.message.reply_text(
            "请输入CFMMC用户名："
        )
    elif text in ['否', 'no', 'n', '0']:
        user_data_manager.update_cfmmc_choice(user_id, False)
        user_data_manager.update_state(user_id, UserState.COMPLETED)

        session = user_data_manager.get_session(user_id)
        summary_msg = (
            "✅ 信息收集完成！\n\n"
            f"📊 净资产：¥{session.net_asset:,.2f}\n"
            f"📅 信号日期：{session.signal_date}\n"
            f"📈 布林带参数：({session.bollinger_period}, {session.bollinger_std})\n"
            f"👤 持仓检查：使用 yyh's 状态\n\n"
            "现在你可以使用其他功能了！\n"
            "输入 /help 查看可用命令。"
        )

        await update.message.reply_text(summary_msg)
    else:
        await update.message.reply_text(
            "请回复 '是' 或 '否'："
        )


async def handle_cfmmc_username(update, context):
    """处理CFMMC用户名输入"""
    _ = context
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if len(text) < 3:
        await update.message.reply_text(
            "用户名长度太短，请重新输入："
        )
        return

    # 临时保存用户名，等待密码一起更新
    session = user_data_manager.get_session(user_id)
    if session:
        session.cfmmc_username = text  # 临时保存

    user_data_manager.update_state(user_id, UserState.WAITING_CFMMC_PASSWORD)

    await update.message.reply_text(
        f"用户名已记录\n\n"
        "请输入CFMMC密码："
    )


async def handle_cfmmc_password(update, context):
    """处理CFMMC密码输入"""
    _ = context
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if len(text) < 6:
        await update.message.reply_text(
            "密码长度太短，请重新输入："
        )
        return

    # 获取临时保存的用户名
    session = user_data_manager.get_session(user_id)
    if session and session.cfmmc_username:
        # 保存密码并完成设置
        user_data_manager.update_cfmmc_credentials(user_id, session.cfmmc_username, text)
        user_data_manager.update_state(user_id, UserState.COMPLETED)

        summary_msg = (
            "✅ 信息收集完成！\n\n"
            f"📊 净资产：¥{session.net_asset:,.2f}\n"
            f"📅 信号日期：{session.signal_date}\n"
            f"📈 布林带参数：({session.bollinger_period}, {session.bollinger_std})\n"
            f"👤 CFMMC账户：已设置\n\n"
            "现在你可以使用其他功能了！\n"
            "输入 /help 查看可用命令。"
        )

        await update.message.reply_text(summary_msg)
    else:
        await update.message.reply_text(
            "出现错误，请使用 /restart 重新开始设置。"
        )


async def handle_message(update, context):
    """处理普通消息"""
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # 更新活动时间
    user_data_manager.update_activity(user_id)

    if not user_data_manager.has_session(user_id):
        await update.message.reply_text(
            "请先输入 /start 开始使用。"
        )
        return

    session = user_data_manager.get_session(user_id)

    # 处理继续/重新开始的选择（当用户在start命令后回复时）
    if text in ['继续', '重新开始'] and session.state != UserState.COMPLETED:
        if text == '重新开始':
            # 重置会话
            user_data_manager.create_session(user_id)
            await update.message.reply_text(
                "已重置设置，请输入你的净资产金额（单位：元）："
            )
            return
        elif text == '继续':
            # 继续之前的状态，根据当前状态提示用户
            state_prompts = {
                UserState.WAITING_NET_ASSET: "请输入你的净资产金额（单位：元）：",
                UserState.WAITING_SIGNAL_DATE: "请输入信号日期（格式：YYYYMMDD）：",
                UserState.WAITING_BOLLINGER_CHOICE: "是否需要自定义布林带周期参数？回复 '是' 或 '否'：",
                UserState.WAITING_BOLLINGER_PERIOD: "请输入布林带周期（建议范围：10-50）：",
                UserState.WAITING_CFMMC_CHOICE: "是否需要录入CFMMC账户密码信息？回复 '是' 或 '否'：",
                UserState.WAITING_CFMMC_USERNAME: "请输入CFMMC用户名：",
                UserState.WAITING_CFMMC_PASSWORD: "请输入CFMMC密码："
            }
            prompt = state_prompts.get(session.state, "请继续之前的输入：")
            await update.message.reply_text(f"好的，让我们继续~\n{prompt}")
            return

    # 根据当前状态处理消息
    if session.state == UserState.WAITING_NET_ASSET:
        await handle_net_asset(update, context)
    elif session.state == UserState.WAITING_SIGNAL_DATE:
        await handle_signal_date(update, context)
    elif session.state == UserState.WAITING_BOLLINGER_CHOICE:
        await handle_bollinger_choice(update, context)
    elif session.state == UserState.WAITING_BOLLINGER_PERIOD:
        await handle_bollinger_period(update, context)
    elif session.state == UserState.WAITING_CFMMC_CHOICE:
        await handle_cfmmc_choice(update, context)
    elif session.state == UserState.WAITING_CFMMC_USERNAME:
        await handle_cfmmc_username(update, context)
    elif session.state == UserState.WAITING_CFMMC_PASSWORD:
        await handle_cfmmc_password(update, context)
    elif session.state == UserState.COMPLETED:
        await update.message.reply_text(
            "信息已收集完成。输入 /help 查看可用命令，或 /restart 重新设置。"
        )


async def help_command(update, context):
    """处理 /help 命令"""
    _ = context
    user_id = update.effective_user.id

    # 更新活动时间
    user_data_manager.update_activity(user_id)

    help_text = (
        "🤖 期货交易信号助手使用指南\n\n"
        "📋 可用命令：\n"
        "/start - 开始使用（智能检测状态）\n"
        "/help - 显示此帮助信息\n"
        "/status - 查看当前设置\n"
        "/restart - 重新设置所有信息\n\n"
        "❓ 如有问题，请联系管理员。"
    )
    await update.message.reply_text(help_text)


async def status_command(update, context):
    """处理 /status 命令"""
    _ = context
    user_id = update.effective_user.id

    # 更新活动时间
    user_data_manager.update_activity(user_id)

    if not user_data_manager.has_session(user_id):
        await update.message.reply_text("请先输入 /start 开始设置。")
        return

    session = user_data_manager.get_session(user_id)

    if session.state == UserState.COMPLETED:
        # 构建布林带参数显示
        if session.use_custom_bollinger:
            bollinger_info = f"自定义 ({session.bollinger_period}, {session.bollinger_std})"
        else:
            bollinger_info = f"默认 ({session.bollinger_period}, {session.bollinger_std})"

        # 构建CFMMC账户显示
        if session.use_custom_cfmmc:
            cfmmc_info = f"已设置 ({session.cfmmc_username})"
        else:
            cfmmc_info = "使用 yyh's 状态"

        status_msg = (
            "📊 当前设置信息：\n\n"
            f"💰 净资产：¥{session.net_asset:,.2f}\n"
            f"📅 信号日期：{session.signal_date}\n"
            f"📈 布林带参数：{bollinger_info}\n"
            f"👤 持仓检查：{cfmmc_info}\n"
            f"🕐 设置时间：{session.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
    else:
        # 根据当前状态显示进度
        progress_states = {
            UserState.WAITING_NET_ASSET: "等待净资产输入",
            UserState.WAITING_SIGNAL_DATE: "等待信号日期输入",
            UserState.WAITING_BOLLINGER_CHOICE: "等待布林带参数选择",
            UserState.WAITING_BOLLINGER_PERIOD: "等待布林带周期输入",
            UserState.WAITING_CFMMC_CHOICE: "等待CFMMC账户选择",
            UserState.WAITING_CFMMC_USERNAME: "等待CFMMC用户名输入",
            UserState.WAITING_CFMMC_PASSWORD: "等待CFMMC密码输入"
        }

        current_step = progress_states.get(session.state, "未知状态")
        status_msg = f"⚠️ 信息设置未完成\n当前步骤：{current_step}"

    await update.message.reply_text(status_msg)


async def restart_command(update, context):
    """处理 /restart 命令"""
    _ = context
    user_id = update.effective_user.id

    # 更新活动时间
    user_data_manager.update_activity(user_id)

    # 创建新会话
    user_data_manager.create_session(user_id)

    await update.message.reply_text(
        "🔄 已重置设置，请输入你的净资产金额（单位：元）："
    )


async def error_handler(update, context):
    """全局错误处理"""
    logger.error(f"更新 {update} 引起异常：{context.error}")

    if update and update.message:
        await update.message.reply_text(
            "抱歉，处理你的请求时出现了错误。请稍后重试或联系管理员。"
        )


# 导出清理任务函数
async def cleanup_inactive_sessions():
    """供main.py调用的清理任务"""
    await cleanup_task()