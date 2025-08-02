# -*- coding:utf-8 -*-
from playwright.sync_api import sync_playwright
import re
from playwright.sync_api import sync_playwright
from playwright.sync_api import sync_playwright


COURSE_TYPE = {'所有': 'all', '专业课程': 15, '行业公需': 16, '一般公需': 17}
pages = 33

# current_page = 7



def write_url(urls):
    with open('urls.txt', 'w') as f:
        f.write('\n'.join(urls))


def on_response(response):
    print(response.url)
    if response.status == 200 and 'SelectCourse' in response.url:
        urls = []
        print(response.json())
        for item in response.json()['course']['data']:
            courseid, coursename = item['courseid'], item['coursename']
            url = f"https://learning.hzrs.hangzhou.gov.cn/#/class?courseId={courseid}&coursetitle={coursename}"
            print(url)
            if url not in urls:
                urls.append(url)
        write_url(urls)


def get_current_page_urls(page_obj, current_page):
    page.on('response', on_response)


def play_course(page, title):

    with page.expect_popup() as page1_info:
        page.get_by_text(title).click()
    page1 = page1_info.value
    with page1.expect_popup() as page2_info:
        page1.get_by_role("button", name="立即学习").click()
    page2 = page2_info.value

    page2.get_by_role("button", name="Play Video").click()


with sync_playwright() as p:
    browser = p.webkit.launch(args=["--start-fullscreen"], headless=False, slow_mo=500)
    context = browser.new_context(storage_state="auth2.json", viewport={"width": 1920, "height": 1080})  # 加载已保存的状态
    page = context.new_page()
    page.goto("https://learning.hzrs.hangzhou.gov.cn/#/")       # 已是登录态

    page.get_by_text("网络课程").first.click()

    page.click("div.el-select__placeholder:has-text('--所有--')")
    page.wait_for_timeout(500)  # 等待0.5秒
    page.click("li:has-text('行业公需')")

    # old_titles = page.locator(".el-only-child__content").all_text_contents()
    page.get_by_role("button", name="查询").click()
    old_titles = page.locator(".el-only-child__content").all_text_contents()

    for _ in range(99):
        new_titles = page.locator(".el-only-child__content").all_text_contents()
        if new_titles != old_titles:
            break
        page.wait_for_timeout(100)
    else:
        raise Exception("查询结果未更新")

    total_page = 10

    for title in new_titles:
        play_course(page, title)
        break

    # current_page = 1
    # while current_page < total_page:
    #     page.wait_for_timeout(500)
    #     page.get_by_role("listitem", name=f"第 {current_page} 页").click()
        # page.on('response', on_response)
        # page.wait_for_load_state('networkidle')


    input('anything....')
    browser.close()

