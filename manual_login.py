# -*- coding:utf-8 -*-
from playwright.sync_api import sync_playwright

# 临时代码：运行一次保存登录态
with sync_playwright() as p:
    browser = p.firefox.launch(headless=False)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    # 手动登录...
    page.goto("https://learning.hzrs.hangzhou.gov.cn/#/")
    input("登录完成后按回车...")
    context.storage_state(path="auth.json")
    browser.close()
