"""
期货品种信息配置模块
包含各品种的基本信息：中文名、英文代码、合约乘数等
用于信号计算、仓位计算、主力合约定位等
"""

from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class ContractInfo:
    """合约信息数据类"""
    name: str  # 品种中文名
    symbol: str  # 品种英文代码
    multiplier: int  # 合约乘数

    def __str__(self) -> str:
        return f"{self.name}({self.symbol}) - 乘数:{self.multiplier}"


# 期货品种信息字典 - 以英文代码为键
CONTRACTS_DATA: Dict[str, ContractInfo] = {
    "RM": ContractInfo("菜粕", "RM", 10),
    "C": ContractInfo("玉米", "C", 10),
    "SI": ContractInfo("工业硅", "SI", 5),
    "CS": ContractInfo("玉米淀粉", "CS", 10),
    "A": ContractInfo("豆一", "A", 10),
    "TL": ContractInfo("三十年国债", "TL", 10000),
    "AP": ContractInfo("苹果", "AP", 10),
    "T": ContractInfo("十年国债", "T", 10000),
    "AO": ContractInfo("氧化铝", "AO", 20),
    "TF": ContractInfo("五年国债", "TF", 10000),
    "TS": ContractInfo("二年国债", "TS", 20000),
    "SF": ContractInfo("硅铁", "SF", 5),
    "LH": ContractInfo("生猪", "LH", 16),
    "ZN": ContractInfo("沪锌", "ZN", 5),
    "IF": ContractInfo("沪深300", "IF", 300),
    "AU": ContractInfo("沪金", "AU", 1000),
    "JD": ContractInfo("鸡蛋", "JD", 10),
    "AL": ContractInfo("沪铝", "AL", 5),
    "PB": ContractInfo("沪铅", "PB", 5),
    "V": ContractInfo("PVC", "V", 5),
    "SS": ContractInfo("不锈钢", "SS", 5),
    "UR": ContractInfo("尿素", "UR", 20),
    "SA": ContractInfo("纯碱", "SA", 20),
    "BR": ContractInfo("合成橡胶", "BR", 5),
    "SR": ContractInfo("白糖", "SR", 10),
    "PF": ContractInfo("短纤", "PF", 5),
    "OI": ContractInfo("菜油", "OI", 10),
    "SM": ContractInfo("锰硅", "SM", 5),
    "M": ContractInfo("豆粕", "M", 10),
    "L": ContractInfo("塑料", "L", 5),
    "RB": ContractInfo("螺纹钢", "RB", 10),
    "PK": ContractInfo("花生", "PK", 5),
    "RU": ContractInfo("橡胶", "RU", 10),
    "HC": ContractInfo("热卷", "HC", 10),
    "TA": ContractInfo("PTA", "TA", 5),
    "NR": ContractInfo("20号胶", "NR", 10),
    "B": ContractInfo("豆二", "B", 10),
    "Y": ContractInfo("豆油", "Y", 10),
    "CF": ContractInfo("棉花", "CF", 5),
    "PR": ContractInfo("瓶片", "PR", 15),
    "P": ContractInfo("棕榈油", "P", 10),
    "BC": ContractInfo("国际铜", "BC", 5),
    "PP": ContractInfo("聚丙烯", "PP", 5),
    "PX": ContractInfo("对二甲苯", "PX", 5),
    "CU": ContractInfo("沪铜", "CU", 5),
    "FG": ContractInfo("玻璃", "FG", 20),
    "SH": ContractInfo("烧碱", "SH", 30),
    "LU": ContractInfo("低硫燃油", "LU", 10),
    "LC": ContractInfo("碳酸锂", "LC", 1),
    "I": ContractInfo("铁矿石", "I", 100),
    "BU": ContractInfo("沥青", "BU", 10),
    "AG": ContractInfo("沪银", "AG", 15),
    "MA": ContractInfo("甲醇", "MA", 10),
    "EB": ContractInfo("苯乙烯", "EB", 5),
    "NI": ContractInfo("沪镍", "NI", 1),
    "PG": ContractInfo("LPG", "PG", 20),
    "EG": ContractInfo("乙二醇", "EG", 10),
    "SN": ContractInfo("沪锡", "SN", 1),
    "CJ": ContractInfo("红枣", "CJ", 5),
    "J": ContractInfo("焦炭", "J", 100),
    "JM": ContractInfo("焦煤", "JM", 60),
    "SP": ContractInfo("纸浆", "SP", 10),
    "FU": ContractInfo("燃油", "FU", 10),
    "SC": ContractInfo("原油", "SC", 1000),
    "EC": ContractInfo("欧线集运", "EC", 50),
    "LG": ContractInfo("原木", "LG", 90),
}


class ContractManager:
    """合约信息管理器"""

    @staticmethod
    def get_contract(symbol: str) -> Optional[ContractInfo]:
        """根据品种代码获取合约信息"""
        return CONTRACTS_DATA.get(symbol.upper())

    @staticmethod
    def get_multiplier(symbol: str) -> Optional[int]:
        """获取品种乘数"""
        contract = ContractManager.get_contract(symbol)
        return contract.multiplier if contract else None

    @staticmethod
    def get_name(symbol: str) -> Optional[str]:
        """获取品种中文名"""
        contract = ContractManager.get_contract(symbol)
        return contract.name if contract else None

    @staticmethod
    def extract_symbol(contract_code: str) -> str:
        """从合约代码中提取品种代码"""
        # 例如: RB2501 -> RB, IF2412 -> IF
        import re
        match = re.match(r'^([A-Z]+)', contract_code.upper())
        return match.group(1) if match else contract_code

    @staticmethod
    def get_contract_info(contract_code: str) -> Optional[ContractInfo]:
        """根据合约代码获取品种信息"""
        symbol = ContractManager.extract_symbol(contract_code)
        return ContractManager.get_contract(symbol)

    @staticmethod
    def list_all_symbols() -> List[str]:
        """获取所有支持的品种代码列表"""
        return list(CONTRACTS_DATA.keys())

    @staticmethod
    def search_by_name(name: str) -> List[ContractInfo]:
        """根据中文名搜索品种"""
        return [contract for contract in CONTRACTS_DATA.values()
                if name in contract.name]

    @staticmethod
    def is_supported(symbol: str) -> bool:
        """检查是否支持该品种"""
        return symbol.upper() in CONTRACTS_DATA


# 创建全局实例
contract_manager = ContractManager()


# 便捷函数
def get_contract_info(contract_code: str) -> Optional[ContractInfo]:
    """便捷函数：获取合约信息"""
    return contract_manager.get_contract_info(contract_code)


def get_multiplier(contract_code: str) -> Optional[int]:
    """便捷函数：获取合约乘数"""
    return contract_manager.get_multiplier(
        contract_manager.extract_symbol(contract_code)
    )