import requests
from bs4 import BeautifulSoup


def inspect_login_form(url):
    """
    探测指定URL的登录表单字段特征。

    参数:
    url (str): 需要探测的网页URL。
    """
    try:
        # 发送GET请求，设置User-Agent模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 如果请求失败 (状态码 4xx 或 5xx), 则抛出异常

        soup = BeautifulSoup(response.text, 'html.parser')

        print(f"Inspecting form elements on: {url}")
        print("-" * 50)

        # 查找所有表单 (forms)
        forms = soup.find_all('form')
        if not forms:
            print("No <form> elements found on the page.")
        else:
            for i, form in enumerate(forms):
                print(f"\n[Form #{i + 1}]")
                form_id = form.get('id', 'N/A')
                form_action = form.get('action', 'N/A')
                form_method = form.get('method', 'GET (default)')
                print(f"  ID: {form_id}")
                print(f"  Action: {form_action}")
                print(f"  Method: {form_method.upper()}")
                print("  Input Fields in this form:")

                # 查找表单内的所有输入字段
                input_fields = form.find_all('input')
                if input_fields:
                    for field in input_fields:
                        field_type = field.get('type', 'N/A')
                        field_name = field.get('name', 'N/A')
                        field_id = field.get('id', 'N/A')
                        field_value = field.get('value', 'N/A')
                        field_placeholder = field.get('placeholder', 'N/A')
                        print(
                            f"    Type: {field_type:<10} Name: {field_name:<20} ID: {field_id:<20} Placeholder: {field_placeholder:<20} Value: {field_value}")
                else:
                    print("    No <input> fields found in this form.")

        print("-" * 50)
        print("\n[All Input Fields on Page (regardless of form)]")
        all_input_fields = soup.find_all('input')
        if all_input_fields:
            for field in all_input_fields:
                field_type = field.get('type', 'N/A')
                field_name = field.get('name', 'N/A')
                field_id = field.get('id', 'N/A')
                field_placeholder = field.get('placeholder', 'N/A')
                print(
                    f"  Type: {field_type:<10} Name: {field_name:<20} ID: {field_id:<20} Placeholder: {field_placeholder}")
        else:
            print("  No <input> fields found on the page.")

        print("-" * 50)
        print("\n[Potential Captcha Images]")
        img_tags = soup.find_all('img')
        if img_tags:
            found_captcha_image_hint = False
            for img in img_tags:
                img_src = img.get('src', 'N/A')
                img_alt = img.get('alt', 'N/A')
                img_id = img.get('id', 'N/A')

                # 简单的启发式方法判断是否为验证码图片
                # 你可能需要根据实际情况调整这些关键词
                captcha_keywords = ['captcha', 'code', 'verify', 'vcode', 'validate', 'securitycode', 'authcode']
                is_potential_captcha = False
                for keyword in captcha_keywords:
                    if keyword in img_src.lower() or keyword in img_alt.lower() or keyword in img_id.lower():
                        is_potential_captcha = True
                        break

                if is_potential_captcha:
                    print(f"  Potential Captcha: Src: {img_src}, Alt: {img_alt}, ID: {img_id}")
                    found_captcha_image_hint = True

            if not found_captcha_image_hint:
                print("  No obvious captcha image found based on common keywords in src, alt, or id.")
                print("  Listing all images for manual inspection:")
                for img in img_tags:
                    print(
                        f"  Image: Src: {img.get('src', 'N/A')}, Alt: {img.get('alt', 'N/A')}, ID: {img.get('id', 'N/A')}")
        else:
            print("  No <img> tags found on the page.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
        if response.status_code == 403:
            print(
                "Access Forbidden (403). The site might be blocking automated requests. Try changing User-Agent or using proxies.")
        elif response.status_code == 401:
            print("Unauthorized (401). Access denied.")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred during the request: {req_err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# 指定你要探测的URL
target_url = "https://investorservice.cfmmc.com/"
inspect_login_form(target_url)