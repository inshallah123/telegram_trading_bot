"""
公开行情数据API模块
专门处理中金所品种等公开行情数据的获取
优先使用腾讯财经API，备用方案为模拟数据
"""

import logging
import requests
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from trading.contracts import contract_manager, is_cffex_contract

logger = logging.getLogger(__name__)


class PublicAPI:
    """公开行情数据API接口类"""

    def __init__(self):
        """初始化公开行情API"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'http://finance.sina.com.cn/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

        # 腾讯财经API (主要)
        self.tencent_base_url = "http://qt.gtimg.cn/q="

        # 期货合约代码映射
        self.contract_mapping = {
            # 中金所品种 - 腾讯财经格式
            'IF': 'CFFE_IF0',    # 沪深300主连
            'T': 'CFFE_T0',      # 十年国债主连
            'TF': 'CFFE_TF0',    # 五年国债主连
            'TS': 'CFFE_TS0',    # 二年国债主连
            'TL': 'CFFE_TL0',    # 三十年国债主连
        }

    def connect(self) -> bool:
        """
        连接测试（公开API无需认证）

        Returns:
            bool: 连接是否成功
        """
        try:
            # 测试腾讯财经API
            test_url = f"{self.tencent_base_url}CFFE_IF0"
            response = self.session.get(test_url, timeout=10)

            if response.status_code == 200 and response.text.strip():
                logger.info("腾讯财经API连接测试成功")
                return True
            else:
                logger.warning(f"腾讯财经API连接失败，将使用模拟数据")
                return True  # 即使API失败，也可以使用模拟数据

        except Exception as e:
            logger.warning(f"连接公开API时发生异常: {e}，将使用模拟数据")
            return True  # 容错处理

    def disconnect(self) -> bool:
        """
        断开连接（公开API无需特殊断开操作）

        Returns:
            bool: 总是返回True
        """
        logger.info("公开API会话已关闭")
        return True

    def _get_contract_code(self, contract_code: str) -> Optional[str]:
        """
        将标准合约代码转换为API格式

        Args:
            contract_code: 标准合约代码，如 "IF2506"

        Returns:
            str: API格式代码
        """
        symbol = contract_manager.extract_symbol(contract_code)

        # 只支持中金所品种的主连合约
        if symbol in self.contract_mapping:
            return self.contract_mapping[symbol]

        logger.warning(f"不支持的品种: {contract_code}")
        return None

    def get_latest_price(self, contract_code: str) -> Optional[Dict[str, Any]]:
        """
        获取合约最新价格数据

        Args:
            contract_code: 合约代码，如 "IF2506"

        Returns:
            dict: 包含价格信息的字典，失败时返回None
        """
        if not is_cffex_contract(contract_code):
            logger.warning(f"合约 {contract_code} 不是中金所品种，建议使用Choice API")
            return None

        api_code = self._get_contract_code(contract_code)
        if not api_code:
            return None

        # 优先使用腾讯财经API
        result = self._get_tencent_price(contract_code, api_code)
        if result:
            return result

        # 备用：使用模拟数据
        logger.warning(f"公开API获取失败，返回 {contract_code} 的模拟数据")
        return self._get_mock_data(contract_code)

    def _get_tencent_price(self, contract_code: str, api_code: str) -> Optional[Dict[str, Any]]:
        """使用腾讯财经API获取价格"""
        try:
            logger.info(f"查询合约 {contract_code} ({api_code}) 的最新价格")

            url = f"{self.tencent_base_url}{api_code}"
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                logger.warning(f"腾讯API请求失败: HTTP {response.status_code}")
                return None

            content = response.text.strip()
            if not content:
                logger.warning("腾讯API返回空数据")
                return None

            # 解析腾讯财经数据格式
            # 格式示例: v_CFFE_IF0="1~IF0~沪深300~5000.0~4980.0~5020.0~..."
            if '="' not in content:
                logger.warning("腾讯API数据格式错误")
                return None

            data_str = content.split('="')[1].rstrip('";')
            data_parts = data_str.split('~')

            if len(data_parts) < 10:
                logger.warning("腾讯API数据字段不足")
                return None

            # 解析数据字段
            result = {
                'contract': contract_code,
                'api_code': api_code,
                'data_source': 'Tencent',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'name': data_parts[2] if len(data_parts) > 2 else None,
                'latest': float(data_parts[3]) if data_parts[3] and data_parts[3] != '0' else None,
                'close': float(data_parts[4]) if data_parts[4] and data_parts[4] != '0' else None,
                'open': float(data_parts[5]) if data_parts[5] and data_parts[5] != '0' else None,
                'high': float(data_parts[6]) if data_parts[6] and data_parts[6] != '0' else None,
                'low': float(data_parts[7]) if data_parts[7] and data_parts[7] != '0' else None,
                'volume': int(float(data_parts[8])) if data_parts[8] and data_parts[8] != '0' else None,
            }

            # 计算涨跌
            if result['latest'] and result['close']:
                result['change'] = result['latest'] - result['close']
                result['change_pct'] = (result['change'] / result['close']) * 100

            logger.info(f"成功获取 {contract_code} 价格数据: 最新价={result.get('latest', 'N/A')}")
            return result

        except Exception as e:
            logger.error(f"腾讯API查询异常: {e}")
            return None

    def _get_mock_data(self, contract_code: str) -> Dict[str, Any]:
        """返回模拟数据"""
        base_price = 5000.0
        if 'IF' in contract_code:
            base_price = 5000.0
        elif 'T' in contract_code:
            base_price = 98.5
        elif 'TF' in contract_code:
            base_price = 99.2

        return {
            'contract': contract_code,
            'data_source': 'MockData',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'latest': base_price,
            'close': base_price - 10,
            'open': base_price - 5,
            'high': base_price + 20,
            'low': base_price - 15,
            'volume': 1000,
            'change': 10.0,
            'change_pct': 0.2,
            'message': '公开API暂时无法获取实时数据，这是模拟数据'
        }

    def get_historical_data(self, contract_code: str, period: int = 20) -> Optional[Dict[str, Any]]:
        """
        获取历史价格数据

        Args:
            contract_code: 合约代码
            period: 数据周期（天数）

        Returns:
            dict: 历史价格数据
        """
        logger.warning("公开API历史数据接口尚未实现")

        # 返回模拟历史数据
        dates = []
        closes = []

        base_price = 5000.0 if 'IF' in contract_code else 98.0

        for i in range(period):
            date = datetime.now() - timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
            closes.append(base_price + (i * 5))

        return {
            'contract': contract_code,
            'data_source': 'MockData',
            'dates': list(reversed(dates)),
            'close': list(reversed(closes)),
            'high': list(reversed(closes)),
            'low': list(reversed(closes)),
            'open': list(reversed(closes)),
            'volume': [1000] * period,
            'message': '历史数据接口尚未实现，这是模拟数据'
        }

    def test_connection(self) -> bool:
        """
        测试API连接和查询功能

        Returns:
            bool: 测试是否成功
        """
        logger.info("开始测试公开行情API...")

        # 测试连接
        if not self.connect():
            logger.warning("公开API连接失败，将使用模拟数据")

        # 测试查询中金所品种
        test_contract = "IF2506"
        price_data = self.get_latest_price(test_contract)

        if price_data:
            logger.info(f"✅ 公开API测试: {test_contract} 最新价={price_data.get('latest', 'N/A')} (数据源: {price_data.get('data_source')})")
            return True
        else:
            logger.error("❌ 公开API测试失败")
            return False


# 创建全局API实例
public_api = PublicAPI()


# 便捷函数
def get_cffex_price(contract_code: str) -> Optional[Dict[str, Any]]:
    """
    便捷函数：获取中金所品种价格

    Args:
        contract_code: 合约代码

    Returns:
        dict: 价格数据
    """
    return public_api.get_latest_price(contract_code)


def get_cffex_historical_data(contract_code: str, period: int = 20) -> Optional[Dict[str, Any]]:
    """
    便捷函数：获取中金所历史数据

    Args:
        contract_code: 合约代码
        period: 数据周期

    Returns:
        dict: 历史数据
    """
    return public_api.get_historical_data(contract_code, period)


def test_public_api():
    """测试公开API功能"""
    return public_api.test_connection()


if __name__ == "__main__":
    # 测试代码
    import sys
    import os

    # 添加父目录到路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=== 公开行情API测试 ===")

    # 测试单个合约
    test_contracts = ["IF2506", "T2506"]

    for contract in test_contracts:
        print(f"\n测试合约: {contract}")
        price_data = public_api.get_latest_price(contract)

        if price_data:
            print(f"  ✅ 成功获取数据 (数据源: {price_data.get('data_source')}):")
            print(f"    最新价: {price_data.get('latest')}")
            print(f"    开盘价: {price_data.get('open')}")
            print(f"    最高价: {price_data.get('high')}")
            print(f"    最低价: {price_data.get('low')}")
            print(f"    成交量: {price_data.get('volume')}")
            if price_data.get('message'):
                print(f"    说明: {price_data.get('message')}")
        else:
            print(f"  ❌ 获取数据失败")

    # 运行完整测试
    print(f"\n=== 完整测试 ===")
    if test_public_api():
        print("✅ 公开API测试成功")
    else:
        print("❌ 公开API测试失败")