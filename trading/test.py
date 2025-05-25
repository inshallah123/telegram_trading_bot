#国泰君安查询乘数信息
import akshare as ak
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


futures_comm_info_df = ak.futures_comm_info(symbol="所有")
main_contracts_df = futures_comm_info_df[futures_comm_info_df["备注"] == "主力合约"]

#
ak.futures_hist_table_em()
futures_hist_em_df = ak.futures_hist_em(symbol="热卷主连", period="daily")
print(futures_hist_em_df)