# -*- coding:utf-8 -*-
"""
进入chrome.exe 目录，打开cmd, 执行一下命令
chrome.exe --remote-debugging-port=9222 --user-data-dir="E:\Projects\autoplay\automationprofile" --profile-directory="Profile 1"
登录你要访问的网页后，再执行脚本获取登录的cookies ,复制cookies，供你的代码使用备用

chrome_options.add_argument('--user-agent=""')  # 设置请求头的User-Agent
chrome_options.add_argument('--window-size=1280x1024')  # 设置浏览器分辨率（窗口大小）
chrome_options.add_argument('--start-maximized')  # 最大化运行（全屏窗口）,不设置，取元素会报错
chrome_options.add_argument('--disable-infobars')  # 禁用浏览器正在被自动化程序控制的提示
chrome_options.add_argument('--incognito')  # 隐身模式（无痕模式）
chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
chrome_options.add_argument('--disable-javascript')  # 禁用javascript
chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面
chrome_options.add_argument('--ignore-certificate-errors')  # 禁用扩展插件并实现窗口最大化
chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
chrome_options.add_argument('--disable-software-rasterizer')  # 禁用 3D 软件光栅化器
chrome_options.add_argument('--disable-extensions')  # 禁用扩展
chrome_options.add_argument('--start-maximized')  # 启动浏览器最大化

"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
# chrome_options.add_argument(
#     '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"')
chrome_options.add_argument("--on-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_experimental_option(
    "excludeSwitches",
    ["enable-automation", "ignore-certificate-errors", "enable-logging"]
)
prefs = {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--start-maximized")

# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
# chrome_options.add_argument("--user-data-dir=E:\\Projects\\autoplay\\automationprofile")

driver = webdriver.Chrome(options=chrome_options)


def get_cookies(url):
    # input("随便输入")
    driver.get(url)
    print(driver.get_cookies())


cookies_variable = [
    {'domain': '.openai.com', 'expiry': 1698050670, 'httpOnly': False, 'name': 'intercom-session-dgkjq2bp', 'path': '/',
     'sameSite': 'Lax', 'secure': False,
     'value': 'TVJJdGk4cm0xR1I3ZGJrTk1pMmxMQ1ZOWG9taTkwUXFSMWk0S0cxVTlnSElmek9uSEJsa2VBcmladnZYVjgzNy0tbjFXYTZjNjdONDgvL25nSjZ1Q0JLZz09--19b8b7d9e94b1fd8e734d43940d28e551d67d9c2'},
    {'domain': '.openai.com', 'expiry': 1728981865, 'httpOnly': False, 'name': 'ajs_anonymous_id', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': 'a17e0153-cec5-4a39-83bc-4246a25fc37d'},
    {'domain': '.openai.com', 'expiry': 1728981865, 'httpOnly': False, 'name': 'ajs_user_id', 'path': '/',
     'sameSite': 'Lax', 'secure': False, 'value': 'user-ZfY0xwZxiC59jVVOWfqX7ZNF'},
    {'domain': '.chat.openai.com', 'expiry': 1728981791, 'httpOnly': True, 'name': 'cf_clearance', 'path': '/',
     'sameSite': 'None', 'secure': True,
     'value': '2StIVi67Nm6sTtN8M5Rm2w5NP4kN5ozwKmz3GO9v0mg-1697445791-0-1-6474d71d.5f09653b.337588fd-0.2.1697445791'},
    {'domain': 'chat.openai.com', 'expiry': 1697446861, 'httpOnly': False, 'name': '_dd_s', 'path': '/',
     'sameSite': 'Strict', 'secure': False, 'value': 'rum=0&expire=1697446861159'},
    {'domain': '.openai.com', 'expiry': 1720775870, 'httpOnly': False, 'name': 'intercom-device-id-dgkjq2bp',
     'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '837a7cda-09c0-46dc-a966-2a60746e5361'},
    {'domain': '.chat.openai.com', 'httpOnly': True, 'name': '_cfuvid', 'path': '/', 'sameSite': 'None', 'secure': True,
     'value': 'OSgYPTuvWY7VWILQmIWc6vkvCjN6L0PmXkP_HCbS2B8-1697445489447-0-604800000'},
    {'domain': 'chat.openai.com', 'httpOnly': True, 'name': '__Secure-next-auth.callback-url', 'path': '/',
     'sameSite': 'Lax', 'secure': True, 'value': 'https%3A%2F%2Fchat.openai.com%2F'},
    {'domain': 'chat.openai.com', 'expiry': 1705221960, 'httpOnly': True, 'name': '__Secure-next-auth.session-token',
     'path': '/', 'sameSite': 'Lax', 'secure': True,
     'value': 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..zz7uf3HxUe7kVocU.f_XnMYenkdplMgri74SxdnO3m6_QrTgqtD3hmjQYk9HbyV11h4-h9s5WpPKOOa30imwro5uK6iRFsDX6-jaQC0TChLc9Rk7R7x2yiZXKIdGJxs8MFGJF6wH-dbYDU94Djs_A35KcRkeI-GgqtePQhXa2lxWsPf-EJMPg-wx5QinrjeGuk-d73MKRXSnUnBwIEKw4YzO5Ih80DXSNWavapPoCBNvYgk9aPzKuv2qKX5xsgYlWjsQKkFgRpe8ga4w1O8t59vK5xRbkJ1he7qtb8H1__-Yoy1y5uhAUn10Cdsvj1DeWHnjDQvdc04NIOVWr-3dHOpoO1oBpQU_ppeBlBGdVixy-jRHpHcKNM0zx9bB1vLQUrufs1NNkxbfNSMeWj6XZTH9PXLRziZt1Nd-OmWcNRK0mkk315_ReLQUDf9SPeD6SJxIm1eNmZUp6yExROqPE_YDL8k2tfu8qsShiDf9EwhUpjYpxXoKJgrhmB7js4s6IX5FfF5j5kH99h-DMt6bvM3x9g7V3Vqy2aHVMlEw6vUav711PGRNMlN6aqXLi0cb6GCqDLKQXN5PrpvkhzoJJLooSr7n7PkLKgL4Gg1xjbxsP8WcqpjpLxdaAeSTirsx3O2lTsw5GOmPNEajVVXOBy1agQ457RJpcW9yi_ICgHlYmMQLGpiTbCk_rEpEFpIxM_rB115C8VwURhzMEKdOJChkyTMdLc-zxAmLgQjs2-_wog2-sJaNYG76BwBWo0XPTx4Mf4618fjO1PERtf3o_IoLsyye7eXoGXlkegu_jVfBQk0FlnomyCowF3AGAYkJbb4ewmhtUBdE4_-3BOXpXe4DilqusH9hIXCENa8v3e3UMhT02f3QV1B0ZFpY9a5UhewxrHgKGibotlk0QVkA0q2bCmGENnqhTlxXDyrw528D4KjHoNzmwes15lvDGUEmnLGj4nYWi1k2uL1wAC8B9ufgAKlOokku3vvHI_n4AznS2_Mppotf2W7d3kSO5-ZI3E6vlHAzuh55O0S0kU2PVf7ASIxHDL4JE6DgEAj7xG9nNkb2mW-cIV68r7wzIgfvupdb08eVN_XLo9BBdj9SfZ0x3tSKTVWiFOoO4VC1mvTZsqa3z9-ZvgM84cX71njXLIGzk-cdSH0iV9stR3FVJqqfR_VSGTiqb5E8mKv9ECc5KG9KIg_oRRCZJ38xyRVE-f60AEYQ3in4lhZ9u5xwbHgOdEriKkBMgfO4RMyE6MJzp7L3qNsgof7-sPTdZbkx_AjIu0DQWl1ARFUdS0pcIAjBC3bcnWcCTQt_egTSFvXrnpJ7N-jc5_VfNUMqsE2BDfc8OZ5YB9mcxcjq8ypsNAtc54IyeDAo6EU_QBSgzAHHLr7mICl3lmY-xTUevxM-ezABotR979UyWXY1vu3t4HOJuOtIYvkOGJ4p5OW4bhKXk9BulhZGlHAiWtlTNZPOeIbZG4NbPG7kDvjY9FBhortLMAcBI0DbQplVh30nDMAng6br8Enj5ue3Hi8dJupj-N3OUl03dpI1BX429bvWS0Z5ypVJqLtFaPEsbpyTR2aQVOq9a6EAFmMPvGAkE8yLAzmrQvsuD8rMFZGQUvCNr22oB3GRGg9W8azwvM2ePHsEF9TFUPUTNvbhPIKZggjUq5xyjgOOuNCJtLC6AF1mB2zZ1b8zy3fk0agS9VOeugqS1KHaYT2bQD_vujAyMhsLwxROcPzt1S2rZAjk7UpdiMuWno227MOsp72qkzzxmIsXLV2FjQRZAr44xWxGpeP0VdBloQwUXpKHEecuX3GORjShS2gpFvzX0PrbYrqUwuwE-6A0WtF4NVbeiN9XR9Peo3nXL3fgZDEbTzpcl_eckhkExreiOPpsVVA_wlZk24TyaH8IhTU06CQmRVfbWOh10h0ibIZxfNoKjL-X5k535eZgn7HTOnycsu5Zs_3q2tCmn82VbgTkt7Nq92vrOvRcjZuWC5zVwBNcvyzurSchdxWnmUnfV9nTV-lpE-6D4rb_qPv8m6CkjwuxmoWuBERAnj8K2rNV9oORp8EcVl7y6dMIOKHEwQmeI4BmojwkqmqHRccYvWacIXJp1mO4xJkY-PTvhOCUWL8nuQIakUOSJ10FvPu0yCvJMA1zZpmEs7opfF0Uc-9GRKk3bH3y5xbvxeBjU_wdQt28yJGQ2Ynv7eNgRY7UGRHUjC5sGfdv2sFhqvrSq507SdBjv-2kDXLeFrck3cSG5xXP2y-ARx4iqz8QPfZ8UWADUtDTzs1m0tPtt3PXfmAPr8i2rncnWEbI6Cl-AHSaHbzip1mKJEMSjPPEqsTkluZRe9Kv0j4Qil0AVBpT_8qTPbPPMjhdbNAqjzaKDVqiEjskQNCm-oG6GauODyDMmCCX2YBAsZy8-RjbQE4pvtFTRAbcyEd_PgFGZ62Up-PIXFhzW3M0ABsxH1zo4DwTYhzM0MJZWaDheI23j1CgeuGaGFb2zGjPO8I0BmHGrGhQpr7VcuqCScDMzolq-7wLVVYfXQZJ5uJMMCPuv-exzaIjtDC1FCgwrE6HaQ_Sbdwm62FwA53L1WvuKFXgCJVmyScODkUNTgXCrrz_aGL7m_yoHlVrpwcz1lSv3_ofPto7YGDbQwojONDO5KMJBkDRoB8m2ODgjkMLlnPahtoQLni56oknybIaI2fwN6KHTsFOXbickJALuwrm13MuMZGfOQ2e69FUejuSxzKnOXpos1BXgS1a1LXghTiSC1O_OMpdwC6sjInmwPoivyGCXJh5F3LzLIbu__iSganDVKKLbHNhN3CvTZ9SMAw.KE0C5E84-YS8IG4Yr3plVg'},
    {'domain': '.chat.openai.com', 'expiry': 1697447289, 'httpOnly': True, 'name': '__cf_bm', 'path': '/',
     'sameSite': 'None', 'secure': True,
     'value': 'Fq12GZsJyazTVn6GPAhN.YPbCAjmwrijYWJ4CSquyB8-1697445489-0-AbRm8Q3qKVyxhsjVWpovgtdvQxtYZsoOV5vjjrK7nKSPNQ71gJNUP4HTf4O37n6PoLHmk66L4yrC3Jv6CToSRUc='},
    {'domain': 'chat.openai.com', 'httpOnly': True, 'name': '__Host-next-auth.csrf-token', 'path': '/',
     'sameSite': 'Lax', 'secure': True,
     'value': '75a618bb76a08f970aab6070f1d8cc05f1b482aad248780025296589278bd2cd%7C4c9c24a1fad1c9fdc1102fee27aebd437291ee5100d54c4ad7d8cccfd874f47c'}]


def set_cookies(url, cookies_variable):
    driver.get(url)
    # driver.delete_all_cookies()
    for cookie in cookies_variable:
        driver.add_cookie(cookie)
    driver.get(url)


if __name__ == '__main__':
    url = 'https://chat.openai.com/'
    # get_cookies('https://chat.openai.com/')
    set_cookies(url, cookies_variable)
