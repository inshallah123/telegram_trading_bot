import pandas as pd


def calculate_bollinger_bands(df, period=19, std=2):
    """
    计算布林带指标
    
    参数:
    df: pandas.DataFrame 或 pandas.Series - 包含价格数据的时间序列
    period: int - 移动平均线周期，默认19
    std: float - 标准差倍数，默认2
    
    返回:
    pandas.DataFrame - 包含上轨、中轨、下轨的数据框
    """
    # 如果输入是Series，转换为DataFrame
    if isinstance(df, pd.Series):
        prices = df
    elif isinstance(df, pd.DataFrame):
        # 假设价格列名为'close'，如果不是可以调整
        if 'close' in df.columns:
            prices = df['close']
        elif 'Close' in df.columns:
            prices = df['Close']
        else:
            # 如果没有明确的价格列，使用第一列
            prices = df.iloc[:, 0]
    else:
        raise ValueError("输入数据必须是pandas DataFrame或Series")
    
    # 计算中轨（简单移动平均线）
    middle_band = prices.rolling(window=period).mean()
    
    # 计算标准差
    rolling_std = prices.rolling(window=period).std()
    
    # 计算上轨和下轨
    upper_band = middle_band + (rolling_std * std)
    lower_band = middle_band - (rolling_std * std)
    
    # 创建结果DataFrame
    result = pd.DataFrame({
        'upper_band': upper_band,
        'middle_band': middle_band,
        'lower_band': lower_band
    }, index=prices.index)
    
    return result


def calculate_bollinger_signals(price_t, price_t_minus_1, holdings, bollinger_bands):
    """
    计算布林带交易信号
    
    参数:
    price_t: float - 今日价格
    price_t_minus_1: float - 上一交易日价格
    holdings: dict - 持仓信息，格式如：{'position': 'long'/'short'/'none', 'contract': '合约代码'}
    bollinger_bands: dict - 布林带数据，格式如：{
        'upper_band_t': float,# 今日上轨
        'middle_band_t': float, # 今日中轨
        'lower_band_t': float, # 今日下轨
        'upper_band_t_minus_1': float, # 昨日上轨
        'middle_band_t_minus_1': float,# 昨日中轨
        'lower_band_t_minus_1': float # 昨日下轨
    }
    
    返回:
    dict - 交易信号，格式如：{
        'signal_type': str, # 'open_long', 'open_short', 'close_long', 'close_short', 'change_contract', 'hold'
        'action': str, # 具体操作描述
        'price': float, # 当前价格
        'reason': str # 信号原因
    }
    """
    
    # 获取布林带数据
    upper_band_t = bollinger_bands['upper_band_t']
    middle_band_t = bollinger_bands['middle_band_t']
    lower_band_t = bollinger_bands['lower_band_t']
    middle_band_t_minus_1 = bollinger_bands['middle_band_t_minus_1']
    
    # 获取当前持仓状态
    current_position = holdings.get('position', 'none')
    current_contract = holdings.get('contract', '')
    is_main_contract = holdings.get('is_main_contract', True)
    
    # 检查是否需要换仓
    if current_position != 'none' and not is_main_contract:
        return {
            'signal_type': 'change_contract',
            'action': f'换仓提示：当前持仓合约 {current_contract} 已不是主力合约',
            'price': price_t,
            'reason': '持仓合约不再是主力合约'
        }
    
    # 平仓信号检查
    # 平空：当price_t >= 中轨 且 price_t-1 < 昨日中轨，且Holdings为空头
    if (current_position == 'short' and 
        price_t >= middle_band_t and 
        price_t_minus_1 < middle_band_t_minus_1):
        return {
            'signal_type': 'close_short',
            'action': '平空仓',
            'price': price_t,
            'reason': f'价格突破中轨向上：当前价格{price_t:.2f} >= 中轨{middle_band_t:.2f}，且昨日价格{price_t_minus_1:.2f} < 昨日中轨{middle_band_t_minus_1:.2f}'
        }
    
    # 平多：当price_t <= 中轨 且 price_t-1 > 昨日中轨，且Holdings为多头
    if (current_position == 'long' and 
        price_t <= middle_band_t and 
        price_t_minus_1 > middle_band_t_minus_1):
        return {
            'signal_type': 'close_long',
            'action': '平多仓',
            'price': price_t,
            'reason': f'价格跌破中轨向下：当前价格{price_t:.2f} <= 中轨{middle_band_t:.2f}，且昨日价格{price_t_minus_1:.2f} > 昨日中轨{middle_band_t_minus_1:.2f}'
        }
    
    # 开仓信号检查（只有在无持仓时才考虑开仓）
    if current_position == 'none':
        # 开多：当price_t > 上轨
        if price_t > upper_band_t:
            return {
                'signal_type': 'open_long',
                'action': '开多仓',
                'price': price_t,
                'reason': f'价格突破上轨：当前价格{price_t:.2f} > 上轨{upper_band_t:.2f}'
            }
        
        # 开空：当price_t < 下轨
        if price_t < lower_band_t:
            return {
                'signal_type': 'open_short',
                'action': '开空仓',
                'price': price_t,
                'reason': f'价格跌破下轨：当前价格{price_t:.2f} < 下轨{lower_band_t:.2f}'
            }
    
    # 无信号，持有当前状态
    return {
        'signal_type': 'hold',
        'action': '持有',
        'price': price_t,
        'reason': '无交易信号'
    }

