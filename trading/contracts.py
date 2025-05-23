"""
期货品种信息配置模块
基于真实品种信息表数据，包含品种基本信息、交易所映射等
"""

from typing import Dict, Optional, List, Set
from dataclasses import dataclass


@dataclass
class ContractInfo:
    """合约信息数据类"""
    name: str  # 品种中文名
    symbol: str  # 品种英文代码
    exchange: str  # 交易所代码
    multiplier: int  # 合约乘数

    def __str__(self) -> str:
        return f"{self.name}({self.symbol}) - {self.exchange} - 乘数:{self.multiplier}"

    @property
    def wind_code(self) -> str:
        """万得主连代码"""
        return f"{self.symbol}.{self.exchange}"


# 期货品种信息字典 - 基于真实品种信息表（共66个品种）
CONTRACTS_DATA: Dict[str, ContractInfo] = {
    # 郑商所 (CZC) - 18个品种
    "RM": ContractInfo("菜粕", "RM", "CZC", 10),
    "AP": ContractInfo("苹果", "AP", "CZC", 10),
    "SF": ContractInfo("硅铁", "SF", "CZC", 5),
    "UR": ContractInfo("尿素", "UR", "CZC", 20),
    "SA": ContractInfo("纯碱", "SA", "CZC", 20),
    "SR": ContractInfo("白糖", "SR", "CZC", 10),
    "PF": ContractInfo("短纤", "PF", "CZC", 5),
    "OI": ContractInfo("菜油", "OI", "CZC", 10),
    "SM": ContractInfo("锰硅", "SM", "CZC", 5),
    "PK": ContractInfo("花生", "PK", "CZC", 5),
    "TA": ContractInfo("PTA", "TA", "CZC", 5),
    "CF": ContractInfo("棉花", "CF", "CZC", 5),
    "PR": ContractInfo("瓶片", "PR", "CZC", 15),
    "PX": ContractInfo("对二甲苯", "PX", "CZC", 5),
    "FG": ContractInfo("玻璃", "FG", "CZC", 20),
    "SH": ContractInfo("烧碱", "SH", "CZC", 30),
    "MA": ContractInfo("甲醇", "MA", "CZC", 10),
    "CJ": ContractInfo("红枣", "CJ", "CZC", 5),

    # 大商所 (DCE) - 19个品种
    "C": ContractInfo("玉米", "C", "DCE", 10),
    "CS": ContractInfo("玉米淀粉", "CS", "DCE", 10),
    "A": ContractInfo("豆一", "A", "DCE", 10),
    "LH": ContractInfo("生猪", "LH", "DCE", 16),
    "JD": ContractInfo("鸡蛋", "JD", "DCE", 10),
    "V": ContractInfo("PVC", "V", "DCE", 5),
    "M": ContractInfo("豆粕", "M", "DCE", 10),
    "L": ContractInfo("塑料", "L", "DCE", 5),
    "B": ContractInfo("豆二", "B", "DCE", 10),
    "Y": ContractInfo("豆油", "Y", "DCE", 10),
    "P": ContractInfo("棕榈油", "P", "DCE", 10),
    "PP": ContractInfo("聚丙烯", "PP", "DCE", 5),
    "I": ContractInfo("铁矿石", "I", "DCE", 100),
    "EB": ContractInfo("苯乙烯", "EB", "DCE", 5),
    "PG": ContractInfo("LPG", "PG", "DCE", 20),
    "EG": ContractInfo("乙二醇", "EG", "DCE", 10),
    "J": ContractInfo("焦炭", "J", "DCE", 100),
    "JM": ContractInfo("焦煤", "JM", "DCE", 60),
    "LG": ContractInfo("原木", "LG", "DCE", 90),

    # 上期所 (SHF) - 17个品种
    "AO": ContractInfo("氧化铝", "AO", "SHF", 20),
    "ZN": ContractInfo("沪锌", "ZN", "SHF", 5),
    "AU": ContractInfo("沪金", "AU", "SHF", 1000),
    "AL": ContractInfo("沪铝", "AL", "SHF", 5),
    "PB": ContractInfo("沪铅", "PB", "SHF", 5),
    "SS": ContractInfo("不锈钢", "SS", "SHF", 5),
    "BR": ContractInfo("合成橡胶", "BR", "SHF", 5),
    "RB": ContractInfo("螺纹钢", "RB", "SHF", 10),
    "RU": ContractInfo("橡胶", "RU", "SHF", 10),
    "HC": ContractInfo("热卷", "HC", "SHF", 10),
    "CU": ContractInfo("沪铜", "CU", "SHF", 5),
    "BU": ContractInfo("沥青", "BU", "SHF", 10),
    "AG": ContractInfo("沪银", "AG", "SHF", 15),
    "NI": ContractInfo("沪镍", "NI", "SHF", 1),
    "SN": ContractInfo("沪锡", "SN", "SHF", 1),
    "SP": ContractInfo("纸浆", "SP", "SHF", 10),
    "FU": ContractInfo("燃油", "FU", "SHF", 10),

    # 中金所 (CFE) - 5个品种
    "TL": ContractInfo("三十年国债", "TL", "CFE", 10000),
    "T": ContractInfo("十年国债", "T", "CFE", 10000),
    "TF": ContractInfo("五年国债", "TF", "CFE", 10000),
    "TS": ContractInfo("二年国债", "TS", "CFE", 20000),
    "IF": ContractInfo("沪深300", "IF", "CFE", 300),

    # 广期所 (GFE) - 2个品种
    "SI": ContractInfo("工业硅", "SI", "GFE", 5),
    "LC": ContractInfo("碳酸锂", "LC", "GFE", 1),

    # 上海国际能源交易中心 (INE) - 5个品种
    "NR": ContractInfo("20号胶", "NR", "INE", 10),
    "BC": ContractInfo("国际铜", "BC", "INE", 5),
    "LU": ContractInfo("低硫燃油", "LU", "INE", 10),
    "SC": ContractInfo("原油", "SC", "INE", 1000),
    "EC": ContractInfo("欧线集运", "EC", "INE", 50),
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
    def get_exchange(symbol: str) -> Optional[str]:
        """获取品种所属交易所"""
        contract = ContractManager.get_contract(symbol)
        return contract.exchange if contract else None

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
    def get_wind_code(contract_code: str) -> Optional[str]:
        """获取万得主连代码"""
        contract = ContractManager.get_contract_info(contract_code)
        return contract.wind_code if contract else None

    @staticmethod
    def list_all_symbols() -> List[str]:
        """获取所有支持的品种代码列表"""
        return list(CONTRACTS_DATA.keys())

    @staticmethod
    def list_by_exchange(exchange: str) -> List[ContractInfo]:
        """获取指定交易所的所有品种"""
        return [contract for contract in CONTRACTS_DATA.values()
                if contract.exchange == exchange.upper()]

    @staticmethod
    def get_cffex_symbols() -> Set[str]:
        """获取中金所品种代码集合"""
        return {symbol for symbol, contract in CONTRACTS_DATA.items()
                if contract.exchange == 'CFE'}

    @staticmethod
    def is_cffex_symbol(symbol: str) -> bool:
        """判断是否为中金所品种"""
        contract = ContractManager.get_contract(symbol)
        return contract.exchange == 'CFE' if contract else False

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


def get_exchange(contract_code: str) -> Optional[str]:
    """便捷函数：获取合约所属交易所"""
    return contract_manager.get_exchange(
        contract_manager.extract_symbol(contract_code)
    )


def is_cffex_contract(contract_code: str) -> bool:
    """便捷函数：判断是否为中金所品种"""
    symbol = contract_manager.extract_symbol(contract_code)
    return contract_manager.is_cffex_symbol(symbol)


def get_wind_code(contract_code: str) -> Optional[str]:
    """便捷函数：获取万得主连代码"""
    return contract_manager.get_wind_code(contract_code)


if __name__ == "__main__":
    # 测试代码
    test_contracts = ["IF2506", "RB2501", "M2501"]

    print("=== 合约信息测试 ===")
    for contract in test_contracts:
        info = get_contract_info(contract)
        if info:
            print(f"{contract}: {info}")
            print(f"  交易所: {get_exchange(contract)}")
            print(f"  万得代码: {get_wind_code(contract)}")
            print(f"  是否中金所: {is_cffex_contract(contract)}")
        else:
            print(f"{contract}: 未找到品种信息")
        print()

    print("=== 中金所品种列表 ===")
    cffex_symbols = contract_manager.get_cffex_symbols()
    print(f"中金所品种: {', '.join(cffex_symbols)}")

    print("\n=== 交易所品种统计 ===")
    exchanges = ['CZC', 'DCE', 'SHF', 'CFE', 'GFE', 'INE']
    for exchange in exchanges:
        contracts = contract_manager.list_by_exchange(exchange)
        symbols = [c.symbol for c in contracts]
        print(f"{exchange}: {len(contracts)}个品种 - {', '.join(symbols)}")