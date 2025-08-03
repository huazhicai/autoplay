# -*- coding:utf-8 -*-
import time
import logging

from typing import Optional
from playwright.sync_api import Page, Frame, TimeoutError, expect

log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


class Course:
    def __init__(self, course_id: str, course_name: str):
        self.id = course_id
        self.name = course_name

    @staticmethod
    def time_to_seconds(t: str) -> int:
        """将时间字符串 'HH:MM:SS' 转换为秒数"""
        try:
            h, m, s = map(int, t.strip().split(":"))
            return h * 3600 + m * 60 + s
        except Exception as e:
            log.warning(f"时间解析失败: {t}, 错误: {e}")
            return 0

    @staticmethod
    def is_paused(frame) -> bool:
        """检查播放是否暂停"""
        try:
            display = frame.locator("#toPause").evaluate(
                "el => getComputedStyle(el).display"
            )
            # display = display.json_value()
            return display == "none"
        except Exception as e:
            log.debug(f"无法获取暂停状态: {e}")
            return True  # 默认视为暂停（安全策略）

    @staticmethod
    def get_current_time(frame) -> Optional[str]:
        """获取当前播放时间"""
        try:
            text = frame.locator("#currentTimeLabel").inner_text(timeout=3000)
            return text.strip()
        except TimeoutError:
            log.debug("获取当前时间超时")
            return None

    @staticmethod
    def get_total_time(frame) -> Optional[str]:
        """获取总时长"""
        try:
            text = frame.locator("#totalTimeLabel").inner_text(timeout=3000)
            return text.strip()
        except TimeoutError:
            log.debug("获取总时长超时")
            return None

    def play(self, page: Page):
        url = f"https://learning.hzrs.hangzhou.gov.cn/#/class?courseId={self.id}&coursetitle={self.name}"
        log.info(url)
        page.goto(url)
        page.on("dialog", lambda dialog: dialog.accept())  # 自动接受所有弹窗

        try:
            page.wait_for_load_state('networkidle', timeout=5000)
        except TimeoutError:
            log.warning("页面加载超时，但仍继续执行...")

        # 判断是否包含 iframe（区分版本 15.1 / 15.2.3）
        if page.locator('#hls_html5_api').count()>0:
            self.monitor_15_1(page)
        else:
            self.monitor_15_2_3(page)

        page.close()

    def monitor_15_1(self, page: Page):
        log.debug("🔍 检测到模式 15.1：无 iframe 结构")

        # 尝试点击“继续学习”弹窗
        self._handle_dialog_button(page, "确定", timeout=2000)

        # 尝试点击 Play Video 按钮
        try:
            play_button = page.get_by_role("button", name="Play Video")
            expect(play_button).to_be_visible(timeout=2000)
            play_button.click()
            log.info("▶️ 已点击播放按钮")
        except TimeoutError:
            log.warning("⚠️ 未找到播放按钮，可能已自动播放")

        # 播放控制按钮（VJS 播放器）
        play_control = page.locator('button.vjs-play-control')

        total_watch_time = 70 * 60 * 1000
        start_time = time.time() * 1000

        while (time.time() * 1000 - start_time) < total_watch_time:
            try:
                # 处理中途弹窗
                self._handle_dialog_button(page, "确定", timeout=3000)

                # 获取播放按钮 title
                title = play_control.get_attribute("title", timeout=2000)
                if title == "Play":
                    log.info("⏸️ 检测到暂停，点击继续播放")
                    play_control.click(force=True)
                elif title == "Replay":
                    log.info("✅ 视频播放完毕，退出循环")
                    break
            except Exception as e:
                log.debug(f"监控播放状态异常: {str(e)}")

    def monitor_15_2_3(self, page: Page):
        log.debug("🔍 检测到模式 15.2.3：嵌套 iframe 结构")
        # try:
        frame = page.frame_locator('iframe').frame_locator('iframe[name="course"]')
        frame.locator('#mediaMask').click()  # 恢复秩序
        frame.locator('#mediaMask').click()  # 开始播放
        # except Exception as e:
        #     log.error(f"❌ 获取嵌套 iframe 失败: {e}")
        #     return

        total_watch_time = 60 * 60 * 1000  # 60分钟
        check_interval = 1000
        start_time = time.time() * 1000

        max_seen_time = 0
        end_threshold = 9  # 允许误差 9 秒

        log.debug("⏳ 开始监控播放进度...")

        while (time.time() * 1000 - start_time) < total_watch_time:
            try:
                # 处理中途弹窗
                self._handle_dialog_button(page, "确定", timeout=2000)

                current_time_str = self.get_current_time(frame)
                total_time_str = self.get_total_time(frame)

                if not current_time_str or not total_time_str:
                    log.debug("⏳ 时间信息未就绪，重试...")
                    page.wait_for_timeout(check_interval)
                    continue

                current_sec = self.time_to_seconds(current_time_str)
                total_sec = self.time_to_seconds(total_time_str)

                if total_sec == 0:
                    log.warning("⚠️ 总时长为0，跳过本次检查")
                    page.wait_for_timeout(check_interval)
                    continue

                paused = self.is_paused(frame)

                log.debug(
                    f"📊 当前: {current_time_str}({current_sec}s), "
                    f"最大: {max_seen_time}s, 总: {total_time_str}({total_sec}s), "
                    f"暂停: {paused}"
                )

                # 更新最大播放进度
                if current_sec > max_seen_time:
                    max_seen_time = current_sec
                    log.debug(f"📈 更新最大播放进度: {max_seen_time}s")

                # ✅ 判断是否播放完成（暂停 + 接近结尾）
                if paused and max_seen_time >= total_sec - end_threshold:
                    log.info(f"🎉 检测到播放完成（{max_seen_time}/{total_sec}s），退出")
                    break

                # ⏯️如果暂停且未播完，点击播放
                if paused and current_sec < total_sec - end_threshold:
                    log.info(f"▶️ 检测到暂停，尝试恢复播放（{current_time_str}）")
                    try:
                        frame.locator("#toPlay").click(timeout=3000)
                    except TimeoutError:
                        log.warning("⚠️ #toPlay 按钮点击失败")

            except Exception as e:
                log.error(f"❌ 监控过程中发生异常: {str(e)}")

            # 使用更智能的等待（避免 busy-wait）
            page.wait_for_timeout(check_interval)

    def _handle_dialog_button(self, page, button_text: str, timeout: int = 3000):
        """通用处理弹窗按钮"""
        try:
            button = page.get_by_role("button", name=button_text)
            expect(button).to_be_visible(timeout=timeout)
            button.click(force=True)
            log.info(f"✅ 已点击弹窗按钮: '{button_text}'")
        except TimeoutError:
            log.debug(f"📭 未出现 '{button_text}' 弹窗，跳过")
        except Exception as e:
            log.debug(f"⚠️ 点击 '{button_text}' 时出错: {e}")
