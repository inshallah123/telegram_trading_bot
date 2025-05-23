"""
Choice API接口模块
专门处理非中金所期货品种的行情数据查询
"""

import logging
from typing import Optional, Dict, Any
from config import config
from trading.contracts import contract_manager, is_cffex_contract

try:
    from EmQuantAPI import *
except ImportError as e:
    logging.error(f"无法导入EmQuantAPI: {e}")
    logging.error("请确保已正确安装Choice API SDK")
    raise

logger = logging.getLogger(__name__)


class ChoiceAPI:
    """Choice API接口类"""

    def __init__(self):
        """初始化Choice API"""
        self.is_connected = False
        self.login_result = None

    def connect(self) -> bool:
        """
        连接Choice API

        Returns:
            bool: 连接是否成功
        """
        try:
            # 检查配置
            if not config.CHOICE_USERNAME or not config.CHOICE_PASSWORD:
                logger.error("Choice API用户名或密码未配置")
                return False

            logger.info("正在连接Choice API...")

            # 使用账密登录
            login_options = f"UserName={config.CHOICE_USERNAME},PassWord={config.CHOICE_PASSWORD}"
            self.login_result = c.start(login_options)

            # 检查登录结果
            if self.login_result.ErrorCode != 0:
                logger.error(f"Choice API登录失败: {self.login_result.ErrorMsg}")
                return False

            self.is_connected = True
            logger.info("Choice API连接成功")
            return True

        except Exception as e:
            logger.error(f"连接Choice API时发生异常: {e}")
            return False

    def disconnect(self) -> bool:
        """
        断开Choice API连接

        Returns:
            bool: 断开是否成功
        """
        try:
            if self.is_connected:
                logout_result = c.stop()
                if logout_result.ErrorCode != 0:
                    logger.warning(f"断开连接时出现警告: {logout_result.ErrorMsg}")
                else:
                    logger.info("Choice API连接已断开")

                self.is_connected = False
                return True

            return True

        except Exception as e:
            logger.error(f"断开Choice API连接时发生异常: {e}")
            return False

    def get_latest_price(self, contract_code: str) -> Optional[Dict[str, Any]]:
        """
        获取合约最新价格数据

        Args:
            contract_code: 合约代码，如 "RB2501"

        Returns:
            dict: 包含价格信息的字典，失败时返回None
        """
        if not self.is_connected:
            logger.error("Choice API未连接，请先调用connect()")
            return None

        # 检查是否为中金所品种
        if is_cffex_contract(contract_code):
            logger.warning(f"合约 {contract_code} 为中金所品种，Choice API不支持，请使用其他数据源")
            return None

        try:
            # 获取万得代码
            wind_code = contract_manager.get_wind_code(contract_code)
            if not wind_code:
                logger.error(f"无法获取合约 {contract_code} 的万得代码")
                return None

            logger.info(f"查询合约 {contract_code} ({wind_code}) 的最新价格")

            # 查询实时价格数据
            indicators = "CLOSE,LATEST,CHANGE,CHANGEPCT,HIGH,LOW,OPEN,VOLUME"

            data = c.css(wind_code, indicators)

            # 检查查询结果
            if data.ErrorCode != 0:
                logger.error(f"查询价格失败: {data.ErrorMsg}")
                return None

            # 解析返回数据
            if not data.Codes or wind_code not in data.Data:
                logger.warning(f"未找到合约 {wind_code} 的数据")
                return None

            # 提取价格数据
            price_data = data.Data[wind_code]

            # 构建返回数据
            result = {
                'contract': contract_code,
                'wind_code': wind_code,
                'timestamp': data.Dates[0] if data.Dates else None,
                'data_source': 'Choice'
            }

            # 映射指标数据
            indicator_mapping = {
                'CLOSE': 'close',
                'LATEST': 'latest',
                'CHANGE': 'change',
                'CHANGEPCT': 'change_pct',
                'HIGH': 'high',
                'LOW': 'low',
                'OPEN': 'open',
                'VOLUME': 'volume'
            }

            for i, indicator in enumerate(data.Indicators):
                if indicator in indicator_mapping:
                    result[indicator_mapping[indicator]] = price_data[i]

            logger.info(f"成功获取 {contract_code} 价格数据: 最新价={result.get('latest', 'N/A')}")
            return result

        except Exception as e:
            logger.error(f"查询价格时发生异常: {e}")
            return None

    def get_historical_data(self, contract_code: str, period: int = 20) -> Optional[Dict[str, Any]]:
        """
        获取历史价格数据（用于布林带计算）

        Args:
            contract_code: 合约代码
            period: 数据周期（天数）

        Returns:
            dict: 历史价格数据
        """
        if not self.is_connected:
            logger.error("Choice API未连接，请先调用connect()")
            return None

        if is_cffex_contract(contract_code):
            logger.warning(f"合约 {contract_code} 为中金所品种，Choice API不支持")
            return None

        try:
            wind_code = contract_manager.get_wind_code(contract_code)
            if not wind_code:
                logger.error(f"无法获取合约 {contract_code} 的万得代码")
                return None

            logger.info(f"查询合约 {contract_code} 最近{period}天的历史数据")

            # 查询历史数据
            data = c.csd(wind_code, "CLOSE,HIGH,LOW,OPEN,VOLUME", f"-{period}TD", "0TD")

            if data.ErrorCode != 0:
                logger.error(f"查询历史数据失败: {data.ErrorMsg}")
                return None

            # 构建返回数据
            result = {
                'contract': contract_code,
                'wind_code': wind_code,
                'data_source': 'Choice',
                'dates': data.Dates,
                'close': data.Data[wind_code][0] if data.Data[wind_code] else [],
                'high': data.Data[wind_code][1] if len(data.Data[wind_code]) > 1 else [],
                'low': data.Data[wind_code][2] if len(data.Data[wind_code]) > 2 else [],
                'open': data.Data[wind_code][3] if len(data.Data[wind_code]) > 3 else [],
                'volume': data.Data[wind_code][4] if len(data.Data[wind_code]) > 4 else []
            }

            logger.info(f"成功获取 {contract_code} 历史数据，共{len(result['dates'])}个交易日")
            return result

        except Exception as e:
            logger.error(f"查询历史数据时发生异常: {e}")
            return None

    def test_connection(self) -> bool:
        """
        测试API连接和查询功能

        Returns:
            bool: 测试是否成功
        """
        logger.info("开始测试Choice API连接...")

        # 测试连接
        if not self.connect():
            return False

        # 测试查询非中金所品种
        test_contract = "MA2509"  # 甲醇2509合约

        logger.info(f"测试查询 {test_contract}...")
        price_data = self.get_latest_price(test_contract)

        if price_data:
            logger.info(f"✅ {test_contract} 查询成功: 最新价={price_data.get('latest', 'N/A')}")
            return True
        else:
            logger.warning(f"❌ {test_contract} 查询失败")
            return False

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()


# 创建全局API实例
choice_api = ChoiceAPI()


# 便捷函数
def get_price(contract_code: str) -> Optional[Dict[str, Any]]:
    """
    便捷函数：获取合约价格（仅支持非中金所品种）

    Args:
        contract_code: 合约代码

    Returns:
        dict: 价格数据
    """
    if is_cffex_contract(contract_code):
        logger.warning(f"合约 {contract_code} 为中金所品种，请使用其他数据源")
        return None

    if not choice_api.is_connected:
        if not choice_api.connect():
            return None

    return choice_api.get_latest_price(contract_code)


def get_historical_data(contract_code: str, period: int = 20) -> Optional[Dict[str, Any]]:
    """
    便捷函数：获取历史数据

    Args:
        contract_code: 合约代码
        period: 数据周期

    Returns:
        dict: 历史数据
    """
    if is_cffex_contract(contract_code):
        logger.warning(f"合约 {contract_code} 为中金所品种，请使用其他数据源")
        return None

    if not choice_api.is_connected:
        if not choice_api.connect():
            return None

    return choice_api.get_historical_data(contract_code, period)


def test_api():
    """测试API功能"""
    return choice_api.test_connection()


if __name__ == "__main__":
    # 测试代码
    import sys
    import os

    # 添加父目录到路径以导入config
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 运行测试
    if test_api():
        print("✅ Choice API测试成功")
    else:
        print("❌ Choice API测试失败")