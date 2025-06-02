import akshare as ak
import pandas as pd
from trading.contracts import contract_multipliers, exchanges
import re


# 从ak接口获得原始数据
def fetch_raw_data(start_date: str, end_date: str, market: str = None) -> pd.DataFrame:
    """
    获取期货日线数据

    参数:
    start_date (str): 开始日期，格式为YYYYMMDD
    end_date (str): 结束日期，格式为YYYYMMDD
    market (str, optional): 指定交易所，如果为None则获取所有交易所数据

    返回:
    pd.DataFrame: 拼接后的完整数据框

    异常:
    ValueError: 当日期格式不正确时抛出
    """

    # 严格校验日期格式为YYYYMMDD八位数字
    date_pattern = r'^\d{8}$'
    if not re.match(date_pattern, start_date):
        raise ValueError(f"开始日期格式错误，应为YYYYMMDD格式的八位数字，当前输入: {start_date}")
    if not re.match(date_pattern, end_date):
        raise ValueError(f"结束日期格式错误，应为YYYYMMDD格式的八位数字，当前输入: {end_date}")

    # 验证日期的有效性
    try:
        pd.to_datetime(start_date, format='%Y%m%d')
        pd.to_datetime(end_date, format='%Y%m%d')
    except ValueError as e:
        raise ValueError(f"日期无效: {e}")

    # 确定要查询的交易所列表
    if market is not None:
        if market not in exchanges:
            raise ValueError(f"指定的交易所 '{market}' 不在支持的交易所列表中: {exchanges}")
        markets_to_query = [market]
    else:
        markets_to_query = exchanges

    # 存储所有数据的列表
    all_data = []

    # 遍历每个交易所获取数据
    for exchange in markets_to_query:
        try:
            print(f"正在获取 {exchange} 交易所数据...")

            # 调用akshare接口获取期货日线数据
            df = ak.get_futures_daily(
                start_date=start_date,
                end_date=end_date,
                market=exchange
            )

            if df is not None and not df.empty:
                # 添加交易所标识列
                df['exchange'] = exchange
                all_data.append(df)
                print(f"成功获取 {exchange} 数据，共 {len(df)} 条记录")
            else:
                print(f"警告: {exchange} 交易所在指定日期范围内无数据")

        except Exception as e:
            print(f"获取 {exchange} 交易所数据时出现错误: {str(e)}")
            continue

    # 拼接所有数据
    if all_data:
        result_df = pd.concat(all_data, ignore_index=True)
        print(f"数据获取完成，总共 {len(result_df)} 条记录")
        return result_df
    else:
        print("警告: 未能获取到任何数据")
        return pd.DataFrame()


