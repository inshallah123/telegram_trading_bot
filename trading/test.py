import requests
from bs4 import BeautifulSoup
import time


def scrape_example_website():
    """
    完整的网页爬取示例 - 爬取httpbin.org的测试页面
    这是一个专门用于测试HTTP请求的网站，很适合练习
    """

    # 目标网站 - httpbin.org是一个测试网站，允许爬取
    url = "https://investorservice.cfmmc.com/"

    # 设置请求头，模拟真实浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # 发送GET请求
        print("正在发送请求...")
        response = requests.get(url, headers=headers, timeout=10)

        # 检查请求是否成功
        if response.status_code == 200:
            print(f"✅ 请求成功！状态码：{response.status_code}")
        else:
            print(f"❌ 请求失败！状态码：{response.status_code}")
            return

        # 解析HTML内容
        soup = BeautifulSoup(response.content, 'html.parser')

        # 提取并显示网页标题
        title = soup.find('title')
        if title:
            print(f"网页标题：{title.text}")

        # 提取所有的h1标签
        h1_tags = soup.find_all('h1')
        print(f"\n找到 {len(h1_tags)} 个h1标签：")
        for i, h1 in enumerate(h1_tags, 1):
            print(f"  {i}. {h1.text.strip()}")

        # 提取所有段落
        paragraphs = soup.find_all('p')
        print(f"\n找到 {len(paragraphs)} 个段落：")
        for i, p in enumerate(paragraphs, 1):
            print(f"  段落{i}：{p.text.strip()}")

        # 提取所有链接
        links = soup.find_all('a')
        print(f"\n找到 {len(links)} 个链接：")
        for i, link in enumerate(links, 1):
            href = link.get('href', '没有链接')
            text = link.text.strip() or '没有文本'
            print(f"  {i}. 文本：{text} | 链接：{href}")

        # 显示原始HTML（前500个字符）
        print(f"\n原始HTML内容（前500字符）：")
        print("-" * 50)
        print(response.text[:500])
        print("-" * 50)

    except requests.exceptions.Timeout:
        print("❌ 请求超时！")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误！请检查网络连接。")
    except Exception as e:
        print(f"❌ 发生错误：{e}")

    # 礼貌地等待
    time.sleep(1)