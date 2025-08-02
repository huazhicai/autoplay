import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth2.json")
    page = context.new_page()
    page.goto("https://learning.hzrs.hangzhou.gov.cn/#/")
    page.get_by_text("网络课程").first.click()
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
