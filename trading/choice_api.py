import os
from EmQuantAPI import *
from dotenv import load_dotenv

# 加载.env中的账号密码
load_dotenv()
CHOICE_USERNAME = os.getenv("CHOICE_USERNAME")
CHOICE_PASSWORD = os.getenv("CHOICE_PASSWORD")

class ChoiceAPI:
    def __init__(self):
        self.logged_in = False

    def login(self):
        # Eastmoney支持直接传用户名密码登录
        options = f"UserName={CHOICE_USERNAME},PassWord={CHOICE_PASSWORD},ForceLogin=1"
        result = c.start(options)
        if result.ErrorCode == 0:
            self.logged_in = True
            print("Login Success!")
        else:
            print("Login Failed:", result.ErrorMsg)
        return result.ErrorCode == 0

    def logout(self):
        c.stop()
        self.logged_in = False
        print("Logout.")

    def get_close_price(self, code="MA2509.CZC"):
        # 查询最近一个交易日的收盘价
        # indicators参数用 "CLOSE"（收盘价）
        # MA2509.CZC 是郑商所2509合约
        # options参数用 "Ispandas=0" 表示返回非pandas格式
        data = c.css(code, "CLOSE", "Ispandas=0")
        if data.ErrorCode != 0:
            print("request css Error,", data.ErrorMsg)
            return None
        # 通常返回 data.Data[code][0] 为收盘价
        try:
            close = data.Data[code][0]
            print(f"{code} 最新收盘价：{close}")
            return close
        except Exception as e:
            print("Data Parse Error:", e)
            return None

if __name__ == "__main__":
    # 测试主函数
    api = ChoiceAPI()
    if api.login():
        api.get_close_price("MA2509.CZC")
        api.logout()
