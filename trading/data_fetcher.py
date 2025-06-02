import akshare as ak
import pandas as pd
from trading.contracts import contract_multipliers, exchanges
import re


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


def get_main_contracts_data(df: pd.DataFrame, end_date: str) -> pd.DataFrame:
    """
    对fetch_raw_data的返回结果进行进一步筛选，获取指定日期的主力合约数据

    参数:
    df (pd.DataFrame): fetch_raw_data函数返回的原始时序数据框
    end_date (str): 目标日期，格式为YYYYMMDD，只处理该日期的数据

    返回:
    pd.DataFrame: 清洗后的主力合约数据框

    处理逻辑:
    1. 筛选出date等于end_date的数据
    2. 筛选出variety在contract_multipliers字典中的数据
    3. 按品种分组，每个品种只保留volume和open_interest都最大的记录
    """

    if df.empty:
        print("输入数据框为空，返回空数据框")
        return pd.DataFrame()

    # 确保必要的列存在
    required_columns = ['date', 'variety', 'volume', 'open_interest']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"数据框缺少必要的列: {missing_columns}")

    print(f"原始数据共 {len(df)} 条记录")

    # 第一步：筛选出date等于end_date的数据
    # 确保date列为字符串格式进行比较
    df_copy = df.copy()
    df_copy['date'] = df_copy['date'].astype(str)

    end_date_data = df_copy[df_copy['date'] == end_date].copy()
    print(f"筛选日期 {end_date} 的数据后，剩余 {len(end_date_data)} 条记录")

    if end_date_data.empty:
        print(f"指定日期 {end_date} 无数据，返回空数据框")
        return pd.DataFrame()

    # 第二步：筛选出variety在contract_multipliers字典中的数据
    filtered_df = end_date_data[end_date_data['variety'].isin(contract_multipliers.keys())].copy()
    print(f"筛选contracts字典中的品种后，剩余 {len(filtered_df)} 条记录")

    if filtered_df.empty:
        print("筛选后无数据，返回空数据框")
        return pd.DataFrame()

    # 数据类型转换：将volume和open_interest转换为数值类型
    try:
        filtered_df['volume'] = pd.to_numeric(filtered_df['volume'], errors='coerce')
        filtered_df['open_interest'] = pd.to_numeric(filtered_df['open_interest'], errors='coerce')

        # 删除转换失败的行（NaN值）
        filtered_df = filtered_df.dropna(subset=['volume', 'open_interest'])
        print(f"数据类型转换后，剩余 {len(filtered_df)} 条记录")

    except Exception as e:
        print(f"数据类型转换失败: {e}")
        return pd.DataFrame()

    if filtered_df.empty:
        print("数据类型转换后无有效数据，返回空数据框")
        return pd.DataFrame()

    # 第三步：按variety分组，选择每个品种volume和open_interest都最大的记录
    main_contracts = []

    for variety in filtered_df['variety'].unique():
        variety_data = filtered_df[filtered_df['variety'] == variety]

        # 找到volume和open_interest都最大的记录
        # 先按volume降序排列，再按open_interest降序排列，取第一条
        main_contract = variety_data.nlargest(1, ['volume', 'open_interest'])

        if not main_contract.empty:
            main_contracts.append(main_contract)
            print(
                f"品种 {variety}: 选择主力合约，volume={main_contract['volume'].iloc[0]}, open_interest={main_contract['open_interest'].iloc[0]}")

    # 合并所有主力合约数据
    if main_contracts:
        result_df = pd.concat(main_contracts, ignore_index=True)
        print(f"日期 {end_date} 的主力合约数据共 {len(result_df)} 条记录，涵盖 {result_df['variety'].nunique()} 个品种")
        return result_df
    else:
        print("未找到任何主力合约数据，返回空数据框")
        return pd.DataFrame()

