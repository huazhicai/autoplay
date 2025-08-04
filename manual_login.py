# -*- coding:utf-8 -*-
from playwright.sync_api import sync_playwright

username = '18701943997'
password = ''

# 临时代码：运行一次保存登录态
with sync_playwright() as p:
    browser = p.firefox.launch(headless=False)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    # 手动登录...
    page.goto("https://learning.hzrs.hangzhou.gov.cn/#/")
    page.get_by_role("button", name="学员登录").click()

    if username and password:
        user_btn = page.get_by_role("textbox", name="请输入手机号/用户名/居民身份证号")
        user_btn.click()
        user_btn.fill(username)
        passwd_btn = page.get_by_role("textbox", name="请输入登录密码")
        passwd_btn.click()
        passwd_btn.fill(password)
        page.get_by_role("textbox", name="请输入图片验证码").click()

    input("登录完成后按回车...")
    context.storage_state(path="auth.json")
    browser.close()
