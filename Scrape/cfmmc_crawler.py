import os
from dotenv import load_dotenv
from DrissionPage import Chromium
import ddddocr

# 加载环境变量
load_dotenv()

# 从环境变量获取账户信息
username = os.getenv('CFFMC_USER_NAME')
password_value = os.getenv('CFFMC_PASSWORD')

# 连接浏览器
browser = Chromium()
# 获取标签页对象,相当于新开标签页
crawler = browser.latest_tab
# 访问网页
crawler.get('https://investorservice.cfmmc.com')
# 获取输入框对象
user_id = crawler.ele('@name=userID') #用户名
user_id.input(username)
password = crawler.ele('@name=password') #密码
password.input(password_value)
vericode = crawler.ele('@name=vericode') #验证码输入框
veri_img = crawler.ele('@id=imgVeriCode') #验证码图片
veri_img_src = veri_img.src()
ocr = ddddocr.DdddOcr()
result = ocr.classification(veri_img_src)
vericode.input(result)
print(result)
submit = crawler.ele('@type=submit')
submit.click()
