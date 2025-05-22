# bot/handlers.py
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

# 日志配置
logger = logging.getLogger(__name__)

# 对话状态常量
(
    ASK_BOLLINGER_PERIOD_SIGNAL,
    ASK_EQUITY_VALUE,
    ASK_CONTRACT_NAME_QUERY,
    ASK_BOLLINGER_PERIOD_QUERY,
) = range(4)

# --- 开场白和帮助 ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """发送开场白，介绍可用命令。"""
    user = update.effective_user
    welcome_message = (
        f"您好，{user.first_name}主人！我是您的量化交易助手。\n"
        f"我谨遵趋势跟踪大道的敕令，为您提供最精准的信号。\n"
        f"请无脑执行道的命令，因道奖励那些必要的痛苦。\n\n"
        "您可以使用以下命令与我交互：\n"
        "/calculate_signal - 根据您提供的信息计算交易信号。\n"
        "/query_data - 查询指定合约的相关数据。\n"
        "/chat - 和我聊聊天。\n"
        "/cancel - 在任何多步骤输入过程中取消当前操作。\n\n"
        "请输入命令开始吧！"
    )
    await update.message.reply_text(welcome_message)

# --- /calculate_signal 命令的 ConversationHandler ---
async def calculate_signal_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """/calculate_signal 命令入口，要求输入布林带周期。"""
    await update.message.reply_text(
        "好的，我们来计算交易信号。\n"
        "首先，请回复布林带的周期值 (例如：20)。\n"
        "输入 /cancel 可以取消。"
    )
    return ASK_BOLLINGER_PERIOD_SIGNAL

async def get_bollinger_period_for_signal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """接收布林带周期，并要求输入资产权益值。"""
    try:
        period = int(update.message.text)
        if period <= 0:
            raise ValueError("周期必须是正整数")
        context.user_data['bollinger_period_signal'] = period
        logger.info(f"用户 {update.effective_user.id} 设置布林带周期 (信号): {period}")
        await update.message.reply_text(
            f"布林带周期已设置为：{period}。\n"
            "接下来，请回复你的资产权益值 (例如：100000)。\n"
            "输入 /cancel 可以取消。"
        )
        return ASK_EQUITY_VALUE
    except ValueError:
        await update.message.reply_text("请输入一个有效的正整数作为周期值。请重试。")
        return ASK_BOLLINGER_PERIOD_SIGNAL # 保持当前状态，让用户重试

async def get_equity_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """接收资产权益值，并（占位）返回信号。"""
    try:
        equity = float(update.message.text)
        if equity <= 0:
            raise ValueError("权益必须是正数")
        context.user_data['equity_value'] = equity
        period = context.user_data.get('bollinger_period_signal', '未知')
        logger.info(f"用户 {update.effective_user.id} 设置权益值: {equity}, 周期: {period}")

        # --- 占位：实际信号计算逻辑 ---
        signal_placeholder = f"收到请求：布林带周期 {period}, 资产权益 {equity}。\n" \
                             f"信号计算模块暂未实现。假设信号为：[买入] (占位符)"
        await update.message.reply_text(signal_placeholder, reply_markup=ReplyKeyboardRemove())
        # 清理 user_data
        context.user_data.clear()
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("请输入一个有效的正数作为资产权益值。请重试。")
        return ASK_EQUITY_VALUE # 保持当前状态

# --- /query_data 命令的 ConversationHandler ---
async def query_data_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """/query_data 命令入口，要求输入期货合约名称。"""
    await update.message.reply_text(
        "好的，我们来查询数据。\n"
        "首先，请回复期货合约的标准名称 (例如：IF2409.CFE)。\n"
        "输入 /cancel 可以取消。"
    )
    return ASK_CONTRACT_NAME_QUERY

async def get_contract_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """接收合约名称，并要求输入布林带周期。"""
    contract_name = update.message.text.strip().upper() # 简单处理，转大写去空格
    if not contract_name: # 简单校验
        await update.message.reply_text("合约名称不能为空，请重新输入。")
        return ASK_CONTRACT_NAME_QUERY

    context.user_data['contract_name_query'] = contract_name
    logger.info(f"用户 {update.effective_user.id} 设置查询合约: {contract_name}")
    await update.message.reply_text(
        f"查询合约已设置为：{contract_name}。\n"
        "接下来，请回复布林带的周期值 (例如：20)。\n"
        "输入 /cancel 可以取消。"
    )
    return ASK_BOLLINGER_PERIOD_QUERY

async def get_bollinger_period_for_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """接收布林带周期，并（占位）返回查询结果。"""
    try:
        period = int(update.message.text)
        if period <= 0:
            raise ValueError("周期必须是正整数")
        context.user_data['bollinger_period_query'] = period
        contract = context.user_data.get('contract_name_query', '未知合约')
        logger.info(f"用户 {update.effective_user.id} 设置查询周期: {period} for {contract}")

        # --- 占位：实际数据查询逻辑 ---
        query_result_placeholder = (
            f"收到请求：查询合约 {contract}, 布林带周期 {period}。\n"
            "数据查询模块暂未实现。假设结果为：\n"
            "收盘价: 3500.5 (占位)\n"
            "布林带上轨: 3550.2 (占位)\n"
            "布林带中轨: 3500.0 (占位)\n"
            "布林带下轨: 3450.8 (占位)"
        )
        await update.message.reply_text(query_result_placeholder, reply_markup=ReplyKeyboardRemove())
        # 清理 user_data
        context.user_data.clear()
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("请输入一个有效的正整数作为周期值。请重试。")
        return ASK_BOLLINGER_PERIOD_QUERY

# --- /chat 命令 ---
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """简单的闲聊回复。"""
    chat_replies = [
        "今天天气不错，适合量化交易！",
        "你觉得下一个风口是什么？",
        "我正在学习新的交易策略呢！",
        "有什么有趣的交易想法吗？",
        "风险控制很重要哦！",
    ]
    import random
    await update.message.reply_text(random.choice(chat_replies))

# --- 取消操作 ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """取消当前操作并结束对话。"""
    user = update.effective_user
    logger.info(f"用户 {user.id} 取消了当前操作。")
    await update.message.reply_text(
        "好的，当前操作已取消。", reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear() # 清理可能存在的对话数据
    return ConversationHandler.END

# --- 错误处理 (可选，但推荐) ---
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """记录错误并向用户发送错误消息。"""
    logger.error("Update '%s' caused error '%s'", update, context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text("抱歉，处理您的请求时发生了一个内部错误。请稍后再试。")


# 构建 ConversationHandler 实例
calculate_signal_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("calculate_signal", calculate_signal_entry)],
    states={
        ASK_BOLLINGER_PERIOD_SIGNAL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_bollinger_period_for_signal)
        ],
        ASK_EQUITY_VALUE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_equity_value)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    # per_user=True, per_chat=True # 默认值，通常够用
)

query_data_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("query_data", query_data_entry)],
    states={
        ASK_CONTRACT_NAME_QUERY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_contract_name)
        ],
        ASK_BOLLINGER_PERIOD_QUERY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_bollinger_period_for_query)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)