import os
import time
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
# 访问网页、启动OCR
crawler.get('https://investorservice.cfmmc.com')
ocr = ddddocr.DdddOcr()
# 获取输入框对象
user_id = crawler.ele('@name=userID') #用户名
password = crawler.ele('@name=password') #密码
vericode = crawler.ele('@name=vericode') #验证码输入框
veri_img = crawler.ele('@id=imgVeriCode') #验证码图片
veri_img_src = veri_img.src() #获取字节码
ocr_result = ocr.classification(veri_img_src) #获取OCR结果
print(ocr_result)
# 自动化录入信息
user_id.input(username) #账户
password.input(password_value) #密码
vericode.input(ocr_result) #验证码
submit = crawler.ele('@type=submit') #提交按钮
submit.click() #提交
#refresh_btn = crawler.ele('.login-form-refresh-captcha-btn') 验证码刷新按钮
#refresh_btn.click()  # 点击刷新验证码

# 启动下载
download = crawler.ele('#myDownload')
download.click()
time.sleep(3)
crawler.close() #关闭标签页
browser.quit() #关闭浏览器
# 健壮性模块构建

#<input type="text" name="tradeDate" maxlength="10" size="10" value=""> #交易日期框元素，点三下全选
#<input type="submit" value="提交" class="button"> #提交框元素

