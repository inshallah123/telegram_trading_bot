import os
from typing import Dict, Optional
from datetime import datetime, timedelta
from EmQuantAPI import *
from dotenv import load_dotenv

# 加载.env中的账号密码
load_dotenv()
CHOICE_USERNAME = os.getenv("CHOICE_USERNAME")
CHOICE_PASSWORD = os.getenv("CHOICE_PASSWORD")


class ChoiceAPI:
    """Choice量化接口封装类"""

    def __init__(self):
        self.logged_in = False

    def login(self) -> bool:
        """
        登录Choice接口

        Returns:
            bool: 登录是否成功
        """
        try:
            # Eastmoney支持直接传用户名密码登录
            options = f"UserName={CHOICE_USERNAME},PassWord={CHOICE_PASSWORD},ForceLogin=1"
            result = c.start(options)
            if result.ErrorCode == 0:
                self.logged_in = True
                print("Choice API登录成功!")
                return True
            else:
                print(f"Choice API登录失败: {result.ErrorMsg}")
                return False
        except Exception as e:
            print(f"登录异常: {e}")
            return False

    def logout(self) -> None:
        """登出Choice接口"""
        try:
            c.stop()
            self.logged_in = False
            print("Choice API已登出")
        except Exception as e:
            print(f"登出异常: {e}")

    def _check_cffex_contract(self, code: str) -> bool:
        """
        检查是否为中金所合约

        Args:
            code: 合约代码，如 "IF2506.CFE"

        Returns:
            bool: True表示是中金所合约，False表示不是
        """
        return code.upper().endswith('.CFE')

    def _validate_contract_code(self, code: str) -> bool:
        """
        验证合约代码格式是否正确

        Args:
            code: 合约代码

        Returns:
            bool: 代码格式是否正确
        """
        if not code or '.' not in code:
            return False

        parts = code.split('.')
        if len(parts) != 2:
            return False

        symbol_part, exchange_part = parts
        # 检查交易所部分
        valid_exchanges = ['CZC', 'DCE', 'SHF', 'GFE', 'INE', 'CFE']
        return exchange_part.upper() in valid_exchanges

    def get_cross_section_data(self, codes: str, end_date: Optional[str] = None) -> Optional[Dict]:
        """
        查询截面数据：指定日期的收盘价、成交量、持仓量

        Args:
            codes: 合约代码，支持单个或多个（逗号分隔），如 "MA2509.CZC" 或 "MA2509.CZC,RM2509.CZC"
            end_date: 查询日期，格式 "YYYY-MM-DD" 或 "YYYYMMDD"，默认为None（查询最新交易日）

        Returns:
            Dict: 包含收盘价、成交量、持仓量的字典，格式为：
            {
                'MA2509.CZC': {
                    'close': 2850.0,
                    'volume': 125463,
                    'open_interest': 89234,
                    'date': '2025-05-23'  # 实际查询的日期
                }
            }
            查询失败返回None
        """
        if not self.logged_in:
            print("请先登录Choice API")
            return None

        # 处理多个合约代码
        code_list = [code.strip() for code in codes.split(',')]

        # 检查中金所合约
        for code in code_list:
            if not self._validate_contract_code(code):
                print(f"无效的合约代码格式: {code}")
                return None

            if self._check_cffex_contract(code):
                print(f"不支持中金所合约: {code}")
                return None

        try:
            # 确定查询日期描述
            query_date_display = end_date if end_date else "最新交易日"
            # 构建查询参数
            indicators = "CLOSE,VOLUME,OI"
            options = "Ispandas=0"

            # 如果指定了日期，添加到options中
            if end_date:
                # 验证并格式化日期
                try:
                    if len(end_date) == 10 and '-' in end_date:  # YYYY-MM-DD格式
                        formatted_date = end_date.replace('-', '')  # 转换为YYYYMMDD
                    elif len(end_date) == 8 and end_date.isdigit():  # YYYYMMDD格式
                        formatted_date = end_date
                        # 验证日期有效性
                        datetime.strptime(end_date, "%Y%m%d")
                    else:
                        print("日期格式错误，请使用 YYYY-MM-DD 或 YYYYMMDD 格式")
                        return None

                    options += f",enddate={formatted_date}"
                    print(f"查询日期: {end_date}")

                except ValueError:
                    print("无效的日期格式")
                    return None

            data = c.css(codes, indicators, options)

            if data.ErrorCode != 0:
                print(f"查询截面数据失败: {data.ErrorMsg}")
                return None

            # 解析返回数据
            result = {}
            for code in data.Codes:
                try:
                    close_price = data.Data[code][0]  # 收盘价
                    volume = data.Data[code][1]  # 成交量
                    open_interest = data.Data[code][2]  # 持仓量

                    result[code] = {
                        'close': close_price,  # ✅ 改为实际值
                        'volume': volume,  # ✅ 改为实际值
                        'open_interest': open_interest,  # ✅ 改为实际值
                        'date': query_date_display
                    }

                    print(f"{code} - 收盘价: {close_price}, 成交量: {volume}, 持仓量: {open_interest}")

                except (IndexError, KeyError) as e:
                    print(f"解析{code}数据失败: {e}")
                    result[code] = {
                        'close': None,
                        'volume': None,
                        'open_interest': None,
                        'date': query_date_display
                    }

            return result
        except Exception as e:
            print(f"查询截面数据异常: {e}")
            return None


    def get_time_series_data(self, codes: str, start_date: str, end_date: str) -> Optional[Dict]:
        """
        查询时序数据：给定周期内的所有收盘价

        Args:
            codes: 合约代码，支持单个或多个（逗号分隔）
            start_date: 开始日期，格式 "YYYY-MM-DD"
            end_date: 结束日期，格式 "YYYY-MM-DD"

        Returns:
            Dict: 包含时序收盘价数据的字典，格式为：
            {
                'MA2509.CZC': {
                    'dates': ['2025-05-20', '2025-05-21', ...],
                    'close_prices': [2850.0, 2855.0, ...]
                }
            }
            查询失败返回None
        """
        if not self.logged_in:
            print("请先登录Choice API")
            return None

        # 处理多个合约代码
        code_list = [code.strip() for code in codes.split(',')]

        # 检查中金所合约
        for code in code_list:
            if not self._validate_contract_code(code):
                print(f"无效的合约代码格式: {code}")
                return None

            if self._check_cffex_contract(code):
                print(f"不支持中金所合约: {code}")
                return None

        try:
            # 验证日期格式
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                print("日期格式错误，请使用 YYYY-MM-DD 格式")
                return None

            # 查询收盘价时序数据
            indicators = "CLOSE"
            options = "Ispandas=0"

            data = c.csd(codes, indicators, start_date, end_date, options)

            if data.ErrorCode != 0:
                print(f"查询时序数据失败: {data.ErrorMsg}")
                return None

            # 解析返回数据
            result = {}
            for code in data.Codes:
                try:
                    # 获取该合约的收盘价数据
                    close_prices = data.Data[code][0]  # 第一个指标（CLOSE）的数据
                    dates = data.Dates

                    # 格式化日期
                    formatted_dates = []
                    for date in dates:
                        if isinstance(date, str):
                            # 如果是字符串，转换格式
                            try:
                                if len(date) == 8:  # YYYYMMDD格式
                                    formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
                                else:
                                    formatted_date = date
                            except:
                                formatted_date = str(date)
                        else:
                            formatted_date = str(date)
                        formatted_dates.append(formatted_date)

                    result[code] = {
                        'dates': formatted_dates,
                        'close_prices': close_prices
                    }

                    print(f"{code} - 查询到 {len(close_prices)} 个交易日数据")
                    print(
                        f"  日期范围: {formatted_dates[0] if formatted_dates else 'N/A'} ~ {formatted_dates[-1] if formatted_dates else 'N/A'}")
                    print(
                        f"  价格范围: {min(close_prices) if close_prices else 'N/A'} ~ {max(close_prices) if close_prices else 'N/A'}")

                except (IndexError, KeyError) as e:
                    print(f"解析{code}数据失败: {e}")
                    result[code] = {
                        'dates': [],
                        'close_prices': []
                    }

            return result
        except Exception as e:
            print(f"查询时序数据异常: {e}")
            return None

    def get_historical_cross_section_data(self, codes: str, target_date: str) -> Optional[Dict]:
        """
        获取历史截面数据的替代方案
        通过时序查询获取指定日期的截面数据

        Args:
            codes: 合约代码，支持单个或多个（逗号分隔）
            target_date: 目标日期，格式 "YYYY-MM-DD"

        Returns:
            Dict: 包含指定日期的收盘价等数据，格式为：
            {
                'MA2509.CZC': {
                    'close': 2365.0,
                    'date': '2025-05-14'
                }
            }
            查询失败返回None
        """
        if not self.logged_in:
            print("请先登录Choice API")
            return None

        # 处理多个合约代码
        code_list = [code.strip() for code in codes.split(',')]

        # 检查中金所合约
        for code in code_list:
            if not self._validate_contract_code(code):
                print(f"无效的合约代码格式: {code}")
                return None

            if self._check_cffex_contract(code):
                print(f"不支持中金所合约: {code}")
                return None

        try:
            # 验证日期格式
            try:
                datetime.strptime(target_date, "%Y-%m-%d")
            except ValueError:
                print("日期格式错误，请使用 YYYY-MM-DD 格式")
                return None

            # 使用时序查询获取单日数据（查询目标日期前后几天）
            start_date = (datetime.strptime(target_date, "%Y-%m-%d") - timedelta(days=5)).strftime("%Y-%m-%d")
            end_date = (datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=5)).strftime("%Y-%m-%d")

            time_data = self.get_time_series_data(codes, start_date, end_date)

            if not time_data:
                print(f"无法获取 {target_date} 的历史数据")
                return None

            result = {}

            for code in code_list:
                if code not in time_data:
                    result[code] = {
                        'close': None,
                        'date': target_date
                    }
                    continue

                dates = time_data[code]['dates']
                prices = time_data[code]['close_prices']

                # 查找目标日期的数据
                target_price = None
                actual_date = target_date

                # 格式化目标日期进行匹配
                target_formatted = target_date

                for i, date in enumerate(dates):
                    # 将日期统一格式化为 YYYY-MM-DD
                    if '/' in date:
                        parts = date.split('/')
                        formatted_date = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                    else:
                        formatted_date = date

                    if formatted_date == target_formatted:
                        target_price = prices[i]
                        actual_date = formatted_date
                        break

                result[code] = {
                    'close': target_price,
                    'date': actual_date
                }

                if target_price is not None:
                    print(f"{code} ({actual_date}) - 历史收盘价: {target_price}")
                else:
                    print(f"{code} - {target_date} 无交易数据")

            return result

        except Exception as e:
            print(f"获取历史截面数据异常: {e}")
            return None

