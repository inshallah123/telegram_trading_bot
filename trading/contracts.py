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

