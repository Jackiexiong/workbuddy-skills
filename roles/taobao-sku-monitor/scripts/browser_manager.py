import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, BrowserContext, Page


class BrowserManager:
    def __init__(self, user_data_dir: str = None, headless: bool = False):
        if user_data_dir is None:
            user_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_data")
        self.user_data_dir = Path(user_data_dir)
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.playwright = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.session_file = self.user_data_dir / "session.json"

    def start(self):
        self.playwright = sync_playwright().start()
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
            viewport={"width": 1440, "height": 900},
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
            ],
        )
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        return self.page

    def _check_cookies_logged_in(self) -> bool:
        try:
            cookies = self.context.cookies()
            cookie_names = [c["name"] for c in cookies]
            has_tb_token = "_tb_token_" in cookie_names
            has_cookie2 = "cookie2" in cookie_names
            return has_tb_token and has_cookie2
        except Exception:
            return False

    def _check_current_page_logged_in(self) -> bool:
        try:
            current_url = self.page.url
            if "login.taobao.com" not in current_url and "login.tmall.com" not in current_url:
                if "taobao.com" in current_url or "tmall.com" in current_url:
                    login_indicators = [
                        ".site-nav-login-info-nick",
                        ".nick-name",
                        "[class*='nickName']",
                        "[class*='userName']",
                        ".site-nav-menu .site-nav-mt-menu",
                        "a[href*='i.taobao.com']",
                        "a[href*='home.taobao.com']",
                    ]
                    for selector in login_indicators:
                        try:
                            el = self.page.query_selector(selector)
                            if el and el.is_visible():
                                text = el.text_content().strip()
                                if text and "登录" not in text and "注册" not in text and len(text) > 0:
                                    return True
                        except Exception:
                            continue
            return False
        except Exception:
            return False

    def is_logged_in(self) -> bool:
        try:
            import time
            if self._check_cookies_logged_in():
                return True
            if self._check_current_page_logged_in():
                return True
            try:
                self.page.goto("https://www.taobao.com", timeout=30000, wait_until="domcontentloaded")
                try:
                    self.page.wait_for_load_state("load", timeout=10000)
                except Exception:
                    pass
                time.sleep(2)
            except Exception:
                pass
            if self._check_cookies_logged_in():
                return True
            if self._check_current_page_logged_in():
                return True
            login_btn_selectors = [
                "a[href*='login.taobao.com']",
                ".J_Login",
                "a:has-text('登录')",
                "[class*='login-btn']",
            ]
            for selector in login_btn_selectors:
                try:
                    login_btn = self.page.query_selector(selector)
                    if login_btn and login_btn.is_visible():
                        btn_text = login_btn.text_content().strip() if login_btn.text_content() else ""
                        if "登录" in btn_text or "亲，请" in btn_text:
                            return False
                except Exception:
                    continue
            return self._check_cookies_logged_in()
        except Exception:
            return False

    def wait_for_login(self, timeout: int = 600):
        print("=" * 60)
        print("请在打开的浏览器中完成淘宝登录（扫码或账号密码）")
        print(f"登录成功后程序会自动继续（最长等待：{timeout // 60}分钟）")
        print("=" * 60)
        try:
            self.page.goto("https://login.taobao.com", timeout=30000, wait_until="domcontentloaded")
        except Exception:
            pass
        import time
        start_time = time.time()
        last_print = 0
        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            try:
                current_url = self.page.url
                if "login.taobao.com" not in current_url and "login.tmall.com" not in current_url:
                    if "taobao.com" in current_url or "tmall.com" in current_url:
                        if self._check_cookies_logged_in() or self._check_current_page_logged_in():
                            print("\n✓ 检测到登录成功！")
                            time.sleep(2)
                            return True
            except Exception:
                pass
            if self._check_cookies_logged_in():
                print("\n✓ 检测到登录成功（Cookie验证）！")
                time.sleep(1)
                return True
            if remaining <= 0:
                break
            if elapsed - last_print >= 30:
                mins = remaining // 60
                secs = remaining % 60
                print(f"  等待登录中... 剩余 {mins}分{secs:02d}秒 (按Ctrl+C可退出)", flush=True)
                last_print = elapsed
            time.sleep(2)
        print(f"\n× 登录等待超时（{timeout}秒）")
        return False

    def ensure_login(self):
        if self.is_logged_in():
            print("✓ 已检测到登录会话，无需重新登录")
            return True
        print("未检测到登录状态，请登录...")
        result = self.wait_for_login()
        if result:
            self.save_session()
        return result

    def go_to_product(self, url: str):
        import time
        self.page.goto(url, timeout=60000, wait_until="domcontentloaded")
        try:
            self.page.wait_for_load_state("load", timeout=20000)
        except Exception:
            pass
        time.sleep(3)
        selectors = [
            "h1",
            "[class*='mainTitle']",
            "[class*='ItemTitle']",
            "#J_Title",
            ".tb-main-title",
            "[class*='skuWrapper']",
            "[class*='SkuWrapper']",
            "[class*='priceText']",
            ".tm-price",
            ".tb-rmb-num",
            "#J_PromoPrice",
        ]
        for selector in selectors:
            try:
                self.page.wait_for_selector(selector, timeout=8000)
                break
            except Exception:
                continue

    def save_session(self):
        """保存登录会话到本地文件"""
        try:
            cookies = self.context.cookies()
            localStorage = self.page.evaluate("""() => {
                let data = {};
                for (let i = 0; i < localStorage.length; i++) {
                    let key = localStorage.key(i);
                    data[key] = localStorage.getItem(key);
                }
                return data;
            }""")
            session_data = {
                "cookies": cookies,
                "localStorage": localStorage
            }
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False)
            print(f"✓ 登录会话已保存到: {self.session_file}")
            return True
        except Exception as e:
            print(f"× 保存会话失败: {e}")
            return False

    def load_session(self) -> bool:
        """从本地文件恢复登录会话"""
        if not self.session_file.exists():
            return False
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # 恢复 cookies
            cookies = session_data.get("cookies", [])
            if cookies:
                self.context.add_cookies(cookies)
            
            # 恢复 localStorage
            localStorage = session_data.get("localStorage", {})
            if localStorage:
                self.page.evaluate("""(data) => {
                    for (let key in data) {
                        localStorage.setItem(key, data[key]);
                    }
                }""", localStorage)
            
            print(f"✓ 已从本地恢复登录会话")
            return True
        except Exception as e:
            print(f"× 恢复会话失败: {e}")
            return False

    def close(self):
        if self.page and not self.page.is_closed():
            pass
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()

    def __enter__(self):
        self.start()
        # 先加载保存的会话（如果有）
        if self.session_file.exists():
            self.load_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
