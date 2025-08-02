import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth2.json", viewport={"width":1920,"height":1080})
    page = context.new_page()
    page.goto("https://learning.hzrs.hangzhou.gov.cn/#/")

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
