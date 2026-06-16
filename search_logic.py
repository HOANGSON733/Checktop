"""
search_logic.py
Chứa các hàm/tầng logic tìm kiếm, thao tác với Selenium, xử lý proxy, Google Sheets.
"""

import threading
import random
import time
import requests
import sys
import concurrent.futures
import json
import math
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QMimeData, QUrl
import logging
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import uuid
from pathlib import Path
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup
import zipfile
import tempfile
import os
import shutil
from utils import resource_path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def find_local_chrome_binary() -> str:
    """Tìm chrome.exe theo thứ tự ưu tiên: bundled tools -> system PATH -> common install paths."""
    candidate_paths = [
        resource_path("tools/chrome-win64/chrome.exe"),
        get_resource_path("tools/chrome-win64/chrome.exe", external=True),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]

    for path in candidate_paths:
        try:
            if path and Path(path).exists():
                return path
        except Exception:
            continue

    return "chrome.exe"


def find_local_chromedriver_path() -> str:
    """Tìm chromedriver.exe theo thứ tự ưu tiên: bundled tools -> PATH."""
    candidate_paths = [
        get_resource_path("tools/chromedriver.exe", external=True),
        resource_path("tools/chromedriver.exe"),
        "chromedriver.exe",
    ]

    for path in candidate_paths:
        try:
            if path and Path(path).exists():
                return path
        except Exception:
            continue

    return "chromedriver.exe"


window_slots = []
slot_lock = threading.Lock()
proxy_slot_lock = threading.Lock()
proxy_slot_counter = 0
proxy_rotation_attempts = {}
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1040
DEFAULT_WINDOW_SIZE = (600, 800)
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

USER_AGENTS = {
    "Windows Chrome": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    ],
    "Windows Edge": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    ],
    "macOS": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    ],
    "Android": [
        "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    ],
    "iPhone": [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    ],
}


ALL_USER_AGENTS = [ua for uas in USER_AGENTS.values() for ua in uas]


def get_window_slot(window_width, window_height, max_cols=4):
    """Lấy slot trống và tính toán vị trí cửa sổ Chrome"""
    with slot_lock:
        spacing_x = 24
        spacing_y = 28

        # Tính số cột/hàng có thể fit trên màn hình
        cols = min(max_cols, max(1, SCREEN_WIDTH // (window_width + spacing_x)))
        grid_width = cols * window_width + (cols - 1) * spacing_x
        start_x = max(0, (SCREEN_WIDTH - grid_width) // 2)

        # Tìm slot trống
        for i, slot in enumerate(window_slots):
            if not slot["occupied"]:
                window_slots[i]["occupied"] = True
                return i, slot["x"], slot["y"]

        # Tạo slot mới
        slot_index = len(window_slots)
        row = slot_index // cols
        col = slot_index % cols

        x = start_x + col * (window_width + spacing_x)
        y = row * (window_height + spacing_y)

        # Clamp vào màn hình
        x = min(x, SCREEN_WIDTH - window_width)
        y = min(y, SCREEN_HEIGHT - window_height)
        x = max(0, x)
        y = max(0, y)

        window_slots.append({"x": x, "y": y, "occupied": True})
        return slot_index, x, y


def release_window_slot(slot_index):
    """Giải phóng slot khi Chrome đóng"""
    with slot_lock:
        if slot_index is not None and slot_index < len(window_slots):
            window_slots[slot_index]["occupied"] = False


def get_next_proxy_key(proxy_list):
    """Cấp proxy key theo toàn bộ luồng đang chạy của app, không reset theo từng job."""
    global proxy_slot_counter

    cleaned_proxy_list = [str(key).strip() for key in (proxy_list or []) if str(key).strip()]
    if not cleaned_proxy_list:
        return None, None

    with proxy_slot_lock:
        key_index = proxy_slot_counter % len(cleaned_proxy_list)
        proxy_slot_counter += 1
        return cleaned_proxy_list[key_index], key_index


def build_proxyxoay_url(api_key, nhamang="random", tinhthanh="0", whitelist=""):
    """Build URL lấy proxy xoay từ key."""
    base_url = "https://proxyxoay.shop/api/get.php"
    params = {
        "key": api_key,
        "nhamang": nhamang,
        "tinhthanh": tinhthanh,
        "whitelist": whitelist,
    }
    return f"{base_url}?{urlencode(params)}"


def parse_proxyxoay_response(response_text):
    """Parse response từ API proxy xoay và trả về ip:port."""
    text = (response_text or "").strip()
    if not text:
        return None, "Phản hồi rỗng"

    # API của bạn trả plain text: ip:port hoặc http://ip:port::
    if text.startswith("http://") or text.startswith("https://"):
        text = text.split("//", 1)[-1]
    text = text.rstrip(":")

    # Nếu đã là ip:port thì trả luôn
    if text.count(":") == 1 and all(part.strip() for part in text.split(":")):
        return text, None

    try:
        data = json.loads(text)
    except Exception:
        return None, f"Không parse được phản hồi: {text[:120]}"

    if isinstance(data, dict):
        if data.get("status") not in (100, "100", True, None):
            return None, data.get("message", "API proxy xoay trả về lỗi")

        proxy_http = data.get("proxyhttp") or data.get("proxy") or data.get("data")
        if not proxy_http:
            return None, "Không tìm thấy proxy trong phản hồi"
        return str(proxy_http).strip(), None

    return None, "Định dạng phản hồi không hỗ trợ"


def simulateUserBehavior(page, options):
    """Mô phỏng hành vi người dùng trên trang sau khi click vào website.

    Sau khi vào site, trang sẽ được cuộn mượt mà, con trỏ chuột di chuyển ngẫu nhiên
    và có thể click thêm một số link nội bộ nếu được bật. Không tự động click sang link khác ngoài ý muốn.
    """
    if not options or not options.get("enabled"):
        return

    min_time = int(options.get("minTime", 20))
    max_time = int(options.get("maxTime", 60))
    if min_time > max_time:
        min_time, max_time = max_time, min_time

    end_time = time.time() + random.randint(min_time, max_time)

    try:
        smooth_scroll_script = """
        window.smoothScroll = function(distance, duration) {
            const start = window.pageYOffset;
            const startTime = performance.now();

            function easeInOutQuad(t) {
                return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
            }

            function step(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const ease = easeInOutQuad(progress);
                window.scrollTo(0, start + distance * ease);
                if (progress < 1) {
                    requestAnimationFrame(step);
                }
            }

            requestAnimationFrame(step);
        };
        """
        page.execute_script(smooth_scroll_script)
    except Exception:
        pass

    def move_mouse_randomly():
        try:
            from selenium.webdriver.common.action_chains import ActionChains

            size = page.get_window_size()
            width = max(300, int(size.get("width", 800)) - 30)
            height = max(300, int(size.get("height", 600)) - 80)
            x = random.randint(20, width)
            y = random.randint(20, height)
            ActionChains(page).move_by_offset(x, y).perform()
        except Exception:
            try:
                page.execute_script(
                    "window.dispatchEvent(new MouseEvent('mousemove', {clientX: arguments[0], clientY: arguments[1], bubbles: true}));",
                    random.randint(20, 500),
                    random.randint(20, 500),
                )
            except Exception:
                pass

    def click_internal_link():
        try:
            links = page.find_elements(By.CSS_SELECTOR, "a[href]")
            candidates = []
            for link in links:
                try:
                    href = (link.get_attribute("href") or "").strip()
                    text = (link.text or "").strip()
                    if not href or not text:
                        continue
                    if href.startswith(("javascript:", "#")):
                        continue
                    if any(x in href.lower() for x in ["/login", "/signup", "/cart", "/checkout"]):
                        continue
                    candidates.append(link)
                except Exception:
                    continue
            if candidates:
                target = random.choice(candidates[: min(len(candidates), 8)])
                try:
                    page.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
                    time.sleep(random.uniform(0.3, 0.8))
                except Exception:
                    pass
                try:
                    target.click()
                except Exception:
                    try:
                        page.execute_script("arguments[0].click();", target)
                    except Exception:
                        pass
                return True
        except Exception:
            pass
        return False

    extra_clicks_remaining = int(options.get("extraClicks", 0))

    while time.time() < end_time:
        try:
            move_mouse_randomly()

            distance = random.randint(220, 520)
            duration = random.randint(700, 1400)
            if random.random() < 0.75:
                page.execute_script(f"window.smoothScroll({distance}, {duration});")
            else:
                page.execute_script(f"window.smoothScroll(-{random.randint(80, 180)}, {random.randint(500, 900)});")

            time.sleep((duration / 1000) + random.uniform(0.4, 1.2))

            if random.random() < 0.35:
                move_mouse_randomly()
                page.execute_script(f"window.smoothScroll(-{random.randint(60, 140)}, {random.randint(400, 800)});")
                time.sleep(random.uniform(0.4, 1.0))

            if random.random() < 0.25:
                move_mouse_randomly()

            if options.get("extraClicksEnabled") and extra_clicks_remaining > 0 and random.random() < 0.35:
                if click_internal_link():
                    extra_clicks_remaining -= 1
                    time.sleep(random.uniform(1.0, 2.5))

            time.sleep(random.uniform(0.6, 1.6))
        except Exception:
            break


# Optional: Xóa slot nếu nó ở cuối danh sách để tránh tích tụ slot rỗng
def get_resource_path(relative_path: str, external: bool = False) -> str:
    """Get the absolute path to a resource, handling both development and packaged environments."""
    if getattr(sys, "frozen", False):
        base_path = Path(sys.executable).resolve().parent if external else Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return str(Path(base_path) / relative_path)


def setup_chrome_options(
    extension_path: str = None,
    chrome_exe_path: str = None,
    headless: bool = False,
    window_size: tuple = DEFAULT_WINDOW_SIZE,
    window_position: tuple = (0, 0),
    user_agent: str = None,
    profile_path: str = None,
    proxy: str = None,
) -> webdriver.ChromeOptions:
    """Set up Chrome options for the driver."""
    options = webdriver.ChromeOptions()

    # Add extension if provided (avoid loading it in headless mode to reduce startup crashes)
    if extension_path and Path(extension_path).exists() and not headless:
        options.add_argument(f"--load-extension={extension_path}")
        options.add_argument(f"--disable-extensions-except={extension_path}")

    # Set binary location if provided
    if chrome_exe_path and Path(chrome_exe_path).exists():
        options.binary_location = chrome_exe_path

    # Window settings
    options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
    options.add_argument(f"--window-position={window_position[0]},{window_position[1]}")
    options.add_argument("--force-device-scale-factor=1")

    # Other arguments
    options.add_argument("--lang=vi-VN,en-US,en")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--remote-allow-origins=*")
    options.add_argument("--remote-debugging-port=0")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--allow-running-insecure-content")

    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")
    if proxy:
        proxy_arg = str(proxy).strip()
        if not proxy_arg.startswith(("http://", "https://", "socks4://", "socks5://")):
            proxy_arg = f"http://{proxy_arg}"
        options.add_argument(f"--proxy-server={proxy_arg}")
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-extensions")
    if profile_path:
        options.add_argument(f"--user-data-dir={profile_path}")

    if os.name == "nt":
        options.add_argument("--disable-features=RendererCodeIntegrity")
        options.add_argument("--disable-breakpad")
        options.add_argument("--disable-crash-reporter")

    return options


def create_chrome_driver(
    proxy: str = None,
    headless_mode: bool = False,
    window_position: tuple = (0, 0),
    user_agent: str = None,
    width: int = 600,
    height: int = 800,
    thread_name: str = None,
    delete_profile: bool = False,
) -> webdriver.Chrome:
    """Create and configure a Chrome WebDriver instance.

    Args:
        proxy: Proxy server address (not implemented yet)
        headless_mode: Run browser in headless mode
        window_position: Tuple of (x, y) coordinates for window position
        user_agent: Custom user agent string
        width: Browser window width
        height: Browser window height
        thread_name: Name of the thread for profile isolation

    Returns:
        Configured Chrome WebDriver instance or None if initialization fails
    """
    if not thread_name:
        thread_name = threading.current_thread().name

    # Validate parameters
    if width <= 0 or height <= 0:
        logging.error(
            f"Thread {thread_name} - Invalid window dimensions: {width}x{height}"
        )
        return None

    try:
        # Setup paths
        driver_path = find_local_chromedriver_path()
        chrome_exe_path = find_local_chrome_binary()
        extension_path = resource_path("tools/RektCaptcha_Extension")
        logging.info(f"Thread {thread_name} - Using Chrome binary: {chrome_exe_path}")
        logging.info(f"Thread {thread_name} - Using extension path: {extension_path}")

        # Create profile path - ưu tiên path từ tham số truyền vào, fallback sang thư mục mặc định
        profile_root = None
        try:
            profile_root = getattr(create_chrome_driver, "profile_root", None)
        except Exception:
            profile_root = None

        if profile_root:
            profile_base = Path(profile_root)
        else:
            app_data_path = os.getenv("LOCALAPPDATA", str(Path.home()))
            profile_base = Path(app_data_path) / "TSEO_Profiles"

        profile_path = profile_base / f"Profile_{thread_name}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        profile_path.mkdir(parents=True, exist_ok=True)

        # Ensure each thread gets a clean, isolated profile to avoid startup crashes
        try:
            if delete_profile and profile_path.exists():
                shutil.rmtree(profile_path, ignore_errors=True)
                profile_path.mkdir(parents=True, exist_ok=True)
        except Exception as profile_cleanup_err:
            logging.warning(
                f"Thread {thread_name} - Could not reset profile directory: {profile_cleanup_err}"
            )

        # Setup options
        options = setup_chrome_options(
            chrome_exe_path=chrome_exe_path,
            extension_path=extension_path,
            headless=headless_mode,
            window_size=(width, height),
            window_position=window_position,
            user_agent=user_agent or DEFAULT_USER_AGENT,
            profile_path=str(profile_path),
            proxy=proxy,
        )

        # Initialize driver
        if Path(driver_path).exists():
            service = Service(executable_path=driver_path)
        else:
            service = Service()

        driver = None
        launch_errors = []
        attempts = [options]

        # Retry once with a safer fallback configuration if Chrome crashes on startup
        fallback_profile_path = profile_path.parent / f"fallback_{profile_path.name}"
        try:
            fallback_profile_path.mkdir(parents=True, exist_ok=True)
        except Exception:
            fallback_profile_path = profile_path

        fallback_options = setup_chrome_options(
            chrome_exe_path=chrome_exe_path,
            extension_path=None,
            headless=headless_mode,
            window_size=(width, height),
            window_position=window_position,
            user_agent=user_agent or DEFAULT_USER_AGENT,
            profile_path=str(fallback_profile_path),
            proxy=proxy,
        )
        fallback_options.add_argument("--disable-extensions")
        fallback_options.add_argument("--disable-features=AutomationControlled")
        fallback_options.add_argument("--remote-debugging-port=0")
        fallback_options.add_argument("--no-sandbox")
        fallback_options.add_argument("--disable-dev-shm-usage")
        attempts.append(fallback_options)

        for attempt_index, attempt_options in enumerate(attempts, start=1):
            try:
                driver = webdriver.Chrome(service=service, options=attempt_options)
                break
            except Exception as driver_err:
                launch_errors.append(str(driver_err))
                logging.warning(
                    f"Thread {thread_name} - Chrome launch attempt {attempt_index} failed: {driver_err}"
                )
                driver = None

        if driver is None:
            try:
                shutil.rmtree(profile_path, ignore_errors=True)
                if fallback_profile_path != profile_path:
                    shutil.rmtree(fallback_profile_path, ignore_errors=True)
            except Exception:
                pass
            raise RuntimeError("Chrome launch failed after retries: " + " | ".join(launch_errors[-2:]))

        # Set window properties
        if not headless_mode:
            try:
                driver.set_window_rect(
                    x=window_position[0],
                    y=window_position[1],
                    width=width,
                    height=height,
                )
            except Exception as e:
                logging.warning(
                    f"Thread {thread_name} - Could not set window rect: {e}"
                )
                try:
                    driver.set_window_size(width, height)
                    driver.set_window_position(*window_position)
                except Exception as e2:
                    logging.warning(
                        f"Thread {thread_name} - Could not set window size/position: {e2}"
                    )

        # Custom quit method
        original_quit = driver.quit

        def custom_quit():
            logging.info(f"Thread {thread_name} - Closing driver...")
            try:
                original_quit()
            except Exception as e:
                logging.error(f"Thread {thread_name} - Error during driver quit: {e}")
            finally:
                try:
                    if delete_profile and profile_path.exists():
                        shutil.rmtree(profile_path, ignore_errors=True)
                        logging.info(f"Thread {thread_name} - Deleted profile path: {profile_path}")
                    if delete_profile and fallback_profile_path.exists() and fallback_profile_path != profile_path:
                        shutil.rmtree(fallback_profile_path, ignore_errors=True)
                        logging.info(f"Thread {thread_name} - Deleted fallback profile path: {fallback_profile_path}")
                except Exception as cleanup_err:
                    logging.error(f"Thread {thread_name} - Failed to delete profile path: {cleanup_err}")

        driver.quit = custom_quit

        logging.info(f"Thread {thread_name} - Chrome driver initialized successfully")
        return driver

    except Exception as e:
        logging.error(f"Thread {thread_name} - Failed to initialize Chrome driver: {e}")
        return None


class SearchThread(QThread):
    """Thread để chạy tìm kiếm không block UI"""

    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, config, credentials_file, thread_index=0):
        super().__init__()
        self.config = config
        self.credentials_file = credentials_file
        self.thread_index = thread_index  # Để lấy proxy tương ứng
        self.is_running = True
        self.driver = None  # Để theo dõi driver
        self.slot_index = None  # Để theo dõi slot đang sử dụng
        self.proxy_dict = None
        self.proxy_failures = 0

    def stop(self):
        """Dừng thread"""
        self.is_running = False
        # Dừng Chrome driver ngay lập tức nếu đang chạy
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        # Hủy tất cả futures đang chạy
        if hasattr(self, "executor") and self.executor:
            self.executor.shutdown(wait=False)
            self.log("⏸ Đã hủy tất cả các task đang chạy")

    def log(self, message):
        """Ghi log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_signal.emit(f"[{timestamp}] {message}")

    def get_page_title(self, url):
        """Lấy title của trang web"""
        try:
            headers = {"User-Agent": random.choice(ALL_USER_AGENTS)}
            # Sử dụng proxy nếu có
            proxies = getattr(self, "proxy_dict", None)
            response = requests.get(url, headers=headers, timeout=5, proxies=proxies)
            soup = BeautifulSoup(response.content, "html.parser")
            title = soup.find("title")
            return title.string if title else "N/A"
        except:
            return "N/A"

    def refresh_proxy(self):
        """Lấy lại proxy mới nếu proxy hiện tại bị lỗi."""
        proxy_enabled = self.config.get("proxy_enabled", False)
        proxy_list = self.config.get("proxy_list", [])
        if not proxy_enabled or not proxy_list:
            self.proxy_dict = None
            return None

        max_attempts = max(1, min(len(proxy_list), 5))
        last_error = None
        for _ in range(max_attempts):
            proxy_key, key_index = get_next_proxy_key(proxy_list)
            if not proxy_key:
                break
            try:
                api_url = build_proxyxoay_url(proxy_key)
                self.log(f"🔄 Luồng {self.thread_index + 1} đổi proxy key #{key_index + 1}...")
                api_resp = requests.get(api_url, timeout=10)
                proxy_http, proxy_error = parse_proxyxoay_response(api_resp.text)
                if not proxy_http:
                    last_error = proxy_error
                    continue

                proxy_hostport = proxy_http.strip().rstrip(":")
                proxy_scheme = self.config.get("proxy_type", "http")
                proxy_url = f"{proxy_scheme}://{proxy_hostport}"
                test_proxy = {"http": proxy_url, "https": proxy_url}
                try:
                    test_resp = requests.get(
                        "https://api.ipify.org?format=json",
                        proxies=test_proxy,
                        timeout=10,
                    )
                    self.proxy_dict = test_proxy
                    self.proxy_failures = 0
                    self.log(f"🔗 Luồng {self.thread_index + 1} proxy OK: {proxy_hostport}")
                    self.log(f"🌍 IP qua proxy: {test_resp.text}")
                    return self.proxy_dict
                except Exception as proxy_test_err:
                    last_error = str(proxy_test_err)
                    self.log(f"⚠ Proxy test failed: {proxy_test_err}")
            except Exception as e:
                last_error = str(e)
                self.log(f"⚠ Lỗi lấy proxy mới: {e}")

        self.proxy_dict = None
        self.proxy_failures += 1
        self.log(f"⚠ Không lấy được proxy mới sau nhiều lần thử: {last_error}")
        return None

    def create_proxy_auth_extension(self, username, password):
        """Tạo Chrome extension để authenticate proxy"""
        import zipfile
        import tempfile
        import os

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Proxy Auth",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            }
        }
        """

        background_js = f"""
        var config = {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{self.config.get('proxy_host', '')}",
                    port: parseInt({self.config.get('proxy_port', '')})
                }},
                bypassList: ["localhost"]
            }}
        }};

        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{username}",
                    password: "{password}"
                }}
            }};
        }};

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
        );
        """

        temp_dir = tempfile.mkdtemp()
        manifest_path = os.path.join(temp_dir, "manifest.json")
        background_path = os.path.join(temp_dir, "background.js")
        with open(manifest_path, "w") as f:
            f.write(manifest_json)
        with open(background_path, "w") as f:
            f.write(background_js)

        zip_path = os.path.join(temp_dir, "proxy_auth.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.write(manifest_path, "manifest.json")
            zf.write(background_path, "background.js")
        return zip_path

    def _click_link_with_retry(self, driver, link, url, retries=3):
        """Thử click link nhiều lần, fallback sang JS click."""
        for attempt in range(1, retries + 1):
            try:
                self.log(f"🖱️ Click thử lần {attempt}/{retries}: {url[:60]}...")
                try:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        link,
                    )
                    time.sleep(random.uniform(0.3, 0.8))
                except Exception:
                    pass

                try:
                    link.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", link)

                time.sleep(random.uniform(1.0, 2.0))
                return True
            except Exception as e:
                self.log(f"⚠ Click thất bại lần {attempt}/{retries}: {e}")
                time.sleep(random.uniform(0.8, 1.5))
        return False

    def _recover_driver(self, driver, x_pos, y_pos, window_width, window_height, ua, headless):
        """Tự mở lại driver khi session bị lỗi."""
        try:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
        except Exception:
            pass

        try:
            if getattr(self, "config", {}).get("profile_path", ""):
                create_chrome_driver.profile_root = self.config.get("profile_path", "")
            else:
                create_chrome_driver.profile_root = None

            new_driver = create_chrome_driver(
                proxy=(self.proxy_dict.get("http") if self.proxy_dict else None),
                headless_mode=headless,
                window_position=(x_pos, y_pos),
                user_agent=ua,
                width=window_width,
                height=window_height,
                thread_name=f"search_{self.thread_index}_recovered",
                delete_profile=bool(getattr(self, "config", {}).get("delete_profile", False)),
            )
            self.driver = new_driver
            return new_driver
        except Exception as e:
            self.log(f"⚠ Không thể khôi phục driver: {e}")
            return None

    def _is_driver_session_error(self, exc):
        msg = str(exc).lower()
        keywords = [
            "winerror 10061",
            "connection refused",
            "invalid session id",
            "session not created",
            "session deleted",
            "disconnected",
            "chrome not reachable",
            "/session/",
        ]
        return any(k in msg for k in keywords)

    def _visit_and_interact(self, driver, keyword, url, title, results, ip_address, min_time, max_time, extra_clicks=False):
        """Vào thẳng domain và tương tác; lỗi thì chỉ log."""
        try:
            self.log(f"🌐 Đang vào domain: {url}")
            try:
                driver.get(url)
                WebDriverWait(driver, 15).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except Exception as e:
                if self._is_driver_session_error(e):
                    raise
                pass

            extra_click_range = self.config.get("extra_click_range", "1-3")
            extra_click_count = 0
            if extra_clicks and self.config.get("extra_clicks_enabled", False):
                try:
                    if isinstance(extra_click_range, str) and "-" in extra_click_range:
                        parts = [p.strip() for p in extra_click_range.split("-") if p.strip()]
                        if len(parts) == 2:
                            extra_click_count = random.randint(int(parts[0]), int(parts[1]))
                    elif isinstance(extra_click_range, (list, tuple)) and len(extra_click_range) == 2:
                        extra_click_count = random.randint(int(extra_click_range[0]), int(extra_click_range[1]))
                except Exception:
                    extra_click_count = random.randint(1, 3)

            simulateUserBehavior(
                driver,
                {
                    "enabled": True,
                    "minTime": min_time,
                    "maxTime": max_time,
                    "extraClicksEnabled": self.config.get("extra_clicks_enabled", False),
                    "extraClicks": extra_click_count,
                },
            )

            onsite_elapsed = max(0, int(random.uniform(min_time, max_time)))
            current_url = url
            try:
                current_url = driver.current_url
            except Exception:
                pass

            if results:
                results[-1]["onsite_time"] = f"{onsite_elapsed}s"
                results[-1]["ip_address"] = ip_address
                results[-1]["link_click"] = current_url
            self.log("✅ Đã tương tác xong trên site")
            return True
        except Exception as e:
            self.log(f"⚠ Domain fallback thất bại, bỏ qua: {e}")
            return False

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Proxy Auth",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            }
        }
        """

        background_js = f"""
        var config = {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{self.config.get('proxy_host', '')}",
                    port: parseInt({self.config.get('proxy_port', '')})
                }},
                bypassList: ["localhost"]
            }}
        }};

        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{username}",
                    password: "{password}"
                }}
            }};
        }}

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
        );
        """

        # Tạo temporary directory
        temp_dir = tempfile.mkdtemp()
        manifest_path = os.path.join(temp_dir, "manifest.json")
        background_path = os.path.join(temp_dir, "background.js")

        # Ghi files
        with open(manifest_path, "w") as f:
            f.write(manifest_json)
        with open(background_path, "w") as f:
            f.write(background_js)

        # Tạo zip file
        zip_path = os.path.join(temp_dir, "proxy_auth.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.write(manifest_path, "manifest.json")
            zf.write(background_path, "background.js")

        return zip_path

    def scroll_like_human(self, driver):
        """Scroll như người thật để load thêm kết quả - MƯỢT MÀ NHƯ NGƯỜI THẬT"""
        try:
            self.log("📜 Đang scroll mượt mà để load thêm kết quả...")

            # Inject smooth scroll JavaScript
            smooth_scroll_script = """
            window.smoothScroll = function(distance, duration) {
                const start = window.pageYOffset;
                const target = start + distance;
                const startTime = performance.now();

                function easeInOutQuad(t) {
                    return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
                }

                function scroll(currentTime) {
                    const elapsed = currentTime - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    const ease = easeInOutQuad(progress);
                    window.scrollTo(0, start + distance * ease);

                    if (progress < 1) {
                        requestAnimationFrame(scroll);
                    }
                }

                requestAnimationFrame(scroll);
            };
            """
            driver.execute_script(smooth_scroll_script)
            time.sleep(1)  # Đợi script được inject
            # Lấy chiều cao trang
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            current_scroll = 0
            scroll_distance = random.randint(300, 500)  # Random scroll distance

            # Scroll từ từ xuống dưới với smooth scroll
            scroll_duration = random.randint(800, 1500)  # 0.8-1.5 giây mỗi lần scroll

            while (
                current_scroll < scroll_height * 0.8 and self.is_running
            ):  # Scroll đến 80% chiều cao
                # Smooth scroll - inject function first then execute
                # self.inject_smooth_scroll_and_execute(driver, scroll_distance, scroll_duration)
                driver.execute_script(
                    f"window.smoothScroll({scroll_distance}, {scroll_duration});"
                )
                current_scroll += scroll_distance

                # Đợi smooth scroll hoàn thành + pause ngẫu nhiên như người đọc
                wait_time = (scroll_duration / 1000) + random.uniform(0.8, 2.0)
                time.sleep(wait_time)

                # Cập nhật chiều cao mới (trong trường hợp trang load thêm nội dung)
                new_scroll_height = driver.execute_script(
                    "return document.body.scrollHeight"
                )
                if new_scroll_height > scroll_height:
                    scroll_height = new_scroll_height

                # Tỷ lệ scroll hiện tại
                current_position = driver.execute_script("return window.pageYOffset")
                scroll_percent = int((current_position / scroll_height) * 100)
                self.log(f"   ↓ Đã scroll {scroll_percent}%")

            if not self.is_running:
                return

            # Scroll lên một chút rồi xuống lại (hành vi người thật khi đọc xong)
            self.log("   ↑ Scroll lên một chút...")
            driver.execute_script("window.smoothScroll(-150, 600);")
            time.sleep(1.0)

            if not self.is_running:
                return

            self.log("   ↓ Scroll xuống để xem thêm...")
            driver.execute_script("window.smoothScroll(200, 700);")
            time.sleep(random.uniform(0.8, 1.5))

            self.log("✅ Hoàn thành scroll mượt mà")

        except Exception as e:
            self.log(f"⚠ Lỗi khi scroll: {str(e)}")

    def search_keyword(
        self,
        keyword,
        num_results,
        target_domain=None,
        thread_index=0,
        window_position=None,
    ):
        """Tìm kiếm từ khóa - Nhập từ khóa chậm + Tự động giải CAPTCHA"""
        results = []
        try:
            # Cập nhật thread_index cho instance hiện tại
            self.thread_index = thread_index

            results = []
            thread_name = threading.current_thread().name
            self.log(f"🚀 [{thread_name}] Bắt đầu tìm kiếm từ khóa: '{keyword}'")

            # Validate keyword
            if not keyword or not keyword.strip():
                self.log(f"⚠ Từ khóa rỗng, bỏ qua")
                return results

            # Normalize target domain if provided
            normalized_target = None
            if target_domain:
                parsed_target = urlparse(
                    target_domain
                    if "://" in target_domain
                    else f"http://{target_domain}"
                )
                normalized_target = parsed_target.netloc.lower().replace("www.", "")

            # Get Chrome config from self.config
            ua_category = self.config.get("ua_category", "Windows Chrome")
            ua_specific = self.config.get("ua_specific", "")
            window_width = self.config.get("window_width", 375)
            window_height = self.config.get("window_height", 812)
            headless = self.config.get("headless", False)

            # Select User-Agent
            if ua_specific:
                ua = ua_specific
            else:
                ua = random.choice(
                    USER_AGENTS.get(ua_category, USER_AGENTS["Windows Chrome"])
                )

            # Setup Chrome options - CHE DẤU AUTOMATION TỐI ĐA
            chrome_options = Options()
            # chrome_options.binary_location = r"D:\Salon\GG Sea\chrome-win64\chrome.exe"
            chrome_options.binary_location = find_local_chrome_binary()

            # Load extension
            # enxtensio_path = r"D:\Salon\GG Sea\RektCaptcha_Extension"
            extension_path = resource_path("tools/RektCaptcha_Extension")
            if Path(extension_path).exists():
                chrome_options.add_argument(f"--load-extension={extension_path}")
                chrome_options.add_argument(
                    f"--disable-extensions-except={extension_path}"
                )
                self.log(f"✓ Đã load extension: {extension_path}")
            else:
                self.log(f"⚠️ Extension không tìm thấy tại: {extension_path}")

            # Các tùy chọn cơ bản
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")

            chrome_options.add_argument("--remote-debugging-port=0")

            # Window size from config
            chrome_options.add_argument(f"--window-size={window_width},{window_height}")

            # Headless mode from config
            if headless:
                chrome_options.add_argument("--headless")

            # QUAN TRỌNG: Che dấu automation
            chrome_options.add_experimental_option(
                "excludeSwitches", ["enable-automation"]
            )
            chrome_options.add_experimental_option("useAutomationExtension", False)

            # Logging
            chrome_options.add_argument("--log-level=3")

            # User-Agent thực tế
            chrome_options.add_argument(f"--user-agent={ua}")

            # Thêm prefs
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
            }
            chrome_options.add_experimental_option("prefs", prefs)

            # Cấu hình Proxy xoay theo key nếu được bật
            proxy_enabled = self.config.get("proxy_enabled", False)
            proxy_list = self.config.get("proxy_list", [])
            self.proxy_dict = None

            if proxy_enabled and proxy_list and len(proxy_list) > 0:
                self.refresh_proxy()

            driver = None
            self.log(f"🔍 Tìm kiếm: {keyword}")
            self.log(f"🌐 Đang mở trình duyệt Chrome...")

            # Sắp xếp slot trước khi khởi tạo driver để truyền vị trí ngay vào driver
            # Lấy slot và vị trí cửa sổ
            slot_index, x_pos, y_pos = get_window_slot(window_width, window_height)
            self.log(f"📐 Slot #{slot_index} → vị trí ({x_pos}, {y_pos})")

            # Khởi tạo driver bằng helper create_chrome_driver (từ test.py)
            driver = None
            try:
                if getattr(self, "config", {}).get("profile_path", ""):
                    create_chrome_driver.profile_root = self.config.get("profile_path", "")
                else:
                    create_chrome_driver.profile_root = None

                driver = create_chrome_driver(
                    proxy=(self.proxy_dict.get("http") if self.proxy_dict else None),
                    headless_mode=headless,
                    window_position=(x_pos, y_pos),
                    user_agent=ua,
                    width=window_width,
                    height=window_height,
                    thread_name=f"search_{self.thread_index}",
                    delete_profile=bool(getattr(self, "config", {}).get("delete_profile", False)),
                )
            except Exception as e:
                import traceback as _tb

                self.log(f"⚠ Exception from create_chrome_driver: {e}")
                self.log("\n".join(_tb.format_exception_only(type(e), e)))
                driver = None

            if not driver:
                self.log("⚠ create_chrome_driver failed, retrying with a clean temporary profile")
                try:
                    temp_profile_dir = Path(tempfile.mkdtemp(prefix=f"chrome_profile_{self.thread_index}_"))
                    retry_options = setup_chrome_options(
                        chrome_exe_path=find_local_chrome_binary(),
                        extension_path=None,
                        headless=headless,
                        window_size=(window_width, window_height),
                        window_position=(x_pos, y_pos),
                        user_agent=ua,
                        profile_path=str(temp_profile_dir),
                        proxy=(self.proxy_dict.get("http") if self.proxy_dict else None),
                    )
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=retry_options)
                    self.driver = driver
                    try:
                        driver.set_window_position(x_pos, y_pos)
                        driver.set_window_size(window_width, window_height)
                    except Exception:
                        pass
                except Exception as e:
                    import traceback as _tb

                    self.log(f"❌ Retry with clean profile failed: {e}")
                    self.log("\n".join(_tb.format_exception_only(type(e), e)))
                    driver = None

            # If helper failed, try fallback to webdriver.Chrome with webdriver_manager
            if not driver:
                self.log(
                    "⚠ create_chrome_driver failed or returned None, attempting fallback with webdriver.Chrome"
                )
                try:
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    self.driver = driver
                    try:
                        # try to set position/size
                        driver.set_window_position(x_pos, y_pos)
                        driver.set_window_size(window_width, window_height)
                    except Exception:
                        try:
                            driver.set_window_rect(
                                x=x_pos,
                                y=y_pos,
                                width=window_width,
                                height=window_height,
                            )
                        except Exception:
                            pass
                    try:
                        driver.set_page_load_timeout(30)
                    except Exception:
                        pass
                except Exception as e:
                    import traceback as _tb

                    self.log(f"❌ Fallback webdriver.Chrome failed: {e}")
                    self.log("\n".join(_tb.format_exception_only(type(e), e)))
                    return results

            # Delay trước khi bắt đầu điều hướng để khớp với tab Chrome
            delay_seconds = float(self.config.get("delay_seconds", 2) or 0)
            if delay_seconds > 0:
                self.log(f"⏳ Chờ {delay_seconds}s trước khi mở Google")
                time.sleep(delay_seconds)

            # Bổ sung anti-detection scripts via CDP (nếu cần)
            try:
                driver.execute_cdp_cmd(
                    "Network.setUserAgentOverride", {"userAgent": ua}
                )
                driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
                driver.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument",
                    {
                        "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                        Object.defineProperty(navigator, 'plugins', {
                            get: () => [1, 2, 3, 4, 5]
                        });
                        Object.defineProperty(navigator, 'languages', {
                            get: () => ['en-US', 'en', 'vi']
                        });
                    """
                    },
                )
            except Exception:
                # Non-critical if CDP commands fail
                pass

            # Log thông tin trình duyệt
            try:
                self.log(f"📊 Thông tin trình duyệt:")
                self.log(f"   • User-Agent: {ua[:80]}...")
                self.log(f"   • Window: {window_width}x{window_height}")
                self.log(f"   • Position: ({x_pos}, {y_pos})")
                self.log(f"   • Headless: {'✓ Có' if headless else '✗ Không'}")
            except Exception:
                pass

            # Navigate to Google with retry logic
            self.log("🌐 Đang truy cập Google...")
            max_retries = 3
            retry_count = 0

            while retry_count < max_retries and self.is_running:
                try:
                    driver.get("https://www.google.com")
                    if not self.is_running:
                        break
                    time.sleep(random.uniform(2, 4))  # Random delay
                    break  # Successfully navigated
                except Exception as e:
                    retry_count += 1
                    if self._is_driver_session_error(e):
                        self.log(f"⚠ Driver session bị ngắt, khởi tạo lại: {str(e)}")
                        driver = self._recover_driver(driver, x_pos, y_pos, window_width, window_height, ua, headless)
                        if not driver:
                            return results
                        retry_count = 0
                        continue
                    if retry_count >= max_retries:
                        self.log(
                            f"❌ Không thể truy cập Google sau {max_retries} lần thử: {str(e)}"
                        )
                        self.log("⚠️ Kiểm tra kết nối internet hoặc thử lại sau.")
                        if driver:
                            try:
                                driver.quit()
                            except:
                                pass
                        return results
                    else:
                        wait_time = 5 * retry_count
                        self.log(
                            f"⚠️ Lỗi kết nối (lần {retry_count}/{max_retries}): {str(e)}"
                        )
                        self.log(f"⏳ Đợi {wait_time} giây trước khi thử lại...")
                        time.sleep(wait_time)

            # Kiểm tra và xử lý CAPTCHA
            def check_and_solve_captcha(wait_after_success=True):
                time.sleep(2)

                def _reload_page_once():
                    try:
                        self.log("🔄 Reload trang để extension tiếp tục giải CAPTCHA...")
                        driver.refresh()
                        time.sleep(3)
                        return True
                    except Exception as reload_err:
                        self.log(f"⚠ Không reload được trang: {reload_err}")
                        return False

                try:
                    current_url = driver.current_url
                    page_source = driver.page_source.lower()
                except:
                    return True

                if "sorry/index" in current_url or "recaptcha" in page_source:
                    self.log("⚠️ Phát hiện CAPTCHA/Checkpoint!")
                    self.log("🔄 Reload ngay để extension tiếp tục giải CAPTCHA...")
                    if not _reload_page_once():
                        return False
                    self.log("⏳ Chờ extension tự giải (tối đa 120 giây)...")

                    for i in range(120):
                        if not self.is_running:
                            self.log("⏸ Đã dừng trong lúc chờ giải CAPTCHA")
                            return False

                        time.sleep(1)

                        try:
                            current_url = driver.current_url
                            page_source = driver.page_source.lower()
                        except:
                            return False

                        if (
                            "sorry/index" not in current_url
                            and "recaptcha" not in page_source
                        ):
                            self.log(f"✅ Extension đã giải xong sau {i+1} giây!")
                            if wait_after_success:
                                self.log("⏳ Đợi trang ổn định...")
                                for _ in range(int(random.uniform(5, 8) * 10)):
                                    if not self.is_running:
                                        return False
                                    time.sleep(0.1)
                            return True

                        if (i + 1) % 20 == 0:
                            if not _reload_page_once():
                                return False

                        if i % 5 == 0:
                            self.log(f"   ⏳ Đang chờ extension... ({i+1}/120s)")

                    self.log("❌ Hết 120 giây, extension không giải được CAPTCHA")
                    return False

                return True

            # Kiểm tra CAPTCHA ngay từ đầu
            if not check_and_solve_captcha():
                self.log("⚠️ CAPTCHA phát hiện ngay từ đầu, dừng tìm kiếm từ khóa này")
                return results

            # Xử lý cookie consent
            try:
                cookie_buttons = [
                    "//button[contains(., 'Accept')]",
                    "//button[contains(., 'Chấp nhận')]",
                    "//button[contains(., 'Đồng ý')]",
                    "//button[@id='L2AGLb']",
                    "//div[text()='Accept all']",
                    "//button[text()='Reject all']",
                ]
                for xpath in cookie_buttons:
                    try:
                        cookie_button = WebDriverWait(driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        cookie_button.click()
                        self.log("✓ Đã đóng popup cookie")
                        time.sleep(1)
                        break
                    except:
                        continue
            except:
                pass

            # Tìm ô search
            try:
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "q"))
                )
            except TimeoutException:
                self.log("❌ Không tìm thấy ô tìm kiếm")
                return results
            except Exception as e:
                if self._is_driver_session_error(e):
                    self.log(f"⚠ Driver session bị ngắt khi chờ ô tìm kiếm: {e}")
                    driver = self._recover_driver(driver, x_pos, y_pos, window_width, window_height, ua, headless)
                    if not driver:
                        return results
                    return self.search_keyword(keyword, num_results, target_domain, thread_index, window_position)
                raise

            # NHẬP TỪ KHÓA TỪ TỪ (GIỐNG NGƯỜI THẬT)
            self.log(f"⌨️ Đang nhập từ khóa từ từ: '{keyword}'")
            search_box.clear()
            time.sleep(random.uniform(0.3, 0.7))  # Đợi sau khi clear

            # Nhập từng ký tự với delay dài hơn
            for i, char in enumerate(keyword):
                search_box.send_keys(char)
                # Delay ngẫu nhiên từ 0.1 đến 0.3 giây giữa các ký tự
                delay = random.uniform(0.15, 0.35)
                time.sleep(delay)

                # Log progress mỗi 5 ký tự
                if (i + 1) % 5 == 0:
                    self.log(f"   ⌨️ Đã nhập: '{keyword[:i+1]}'...")

            self.log(f"✓ Đã nhập xong từ khóa")

            # Đợi trước khi submit (giống người suy nghĩ)
            time.sleep(random.uniform(0.8, 1.5))

            # Try to click search button first, fallback to submit
            try:
                search_box = driver.find_element(By.NAME, "q")
                search_box.submit()
                self.log("🔍 Đã submit form")
            except Exception:
                try:
                    # Fallback: nhấn Enter bằng keyboard
                    from selenium.webdriver.common.keys import Keys

                    search_box = driver.find_element(By.NAME, "q")
                    search_box.send_keys(Keys.RETURN)
                    self.log("🔍 Đã nhấn Enter")
                except Exception as e:
                    self.log(f"⚠ Lỗi submit: {e}")
            # Chờ kết quả load - tăng delay để tránh CAPTCHA
            for _ in range(int(random.uniform(5, 8) * 10)):
                if not self.is_running:
                    break
                time.sleep(0.1)

            if not self.is_running:
                return results

            # Scroll like a real person to load more results
            self.scroll_like_human(driver)

            if not self.is_running:
                return results

            # Kiểm tra CAPTCHA sau khi submit
            if not check_and_solve_captcha():
                return results

            ip_address = "N/A"
            try:
                if self.proxy_dict:
                    ip_resp = requests.get(
                        "https://api.ipify.org?format=json",
                        proxies=self.proxy_dict,
                        timeout=8,
                    )
                else:
                    ip_resp = requests.get("https://api.ipify.org?format=json", timeout=8)
                ip_address = ip_resp.json().get("ip", "N/A")
            except Exception as e:
                self.log(f"⚠ Không kiểm tra được IP hiện tại: {e}")
                if self.config.get("proxy_enabled", False):
                    self.log("🔄 Thử lấy proxy mới vì IP check thất bại...")
                    self.refresh_proxy()
                    try:
                        if self.proxy_dict:
                            ip_resp = requests.get(
                                "https://api.ipify.org?format=json",
                                proxies=self.proxy_dict,
                                timeout=8,
                            )
                            ip_address = ip_resp.json().get("ip", "N/A")
                    except Exception:
                        pass

            found_position = None
            current_rank = 0
            num_pages = (num_results + 9) // 10

            onsite_enabled = self.config.get("onsite_interaction_enabled", False)
            onsite_time_range = self.config.get("onsite_time_range", "20-60")
            min_time, max_time = 20, 60
            try:
                if isinstance(onsite_time_range, str) and "-" in onsite_time_range:
                    parts = [p.strip() for p in onsite_time_range.split("-") if p.strip()]
                    if len(parts) == 2:
                        min_time = int(parts[0])
                        max_time = int(parts[1])
                elif isinstance(onsite_time_range, (list, tuple)) and len(onsite_time_range) == 2:
                    min_time = int(onsite_time_range[0])
                    max_time = int(onsite_time_range[1])
            except Exception:
                min_time, max_time = 20, 60

            for page in range(num_pages):
                if not self.is_running:
                    break

                self.log(f"📄 Đang xử lý trang {page + 1}/{num_pages}")

                # Wait for results với retry logic
                result_loaded = False
                retry_count = 0
                max_retries = 3

                while retry_count < max_retries and not result_loaded:
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "search"))
                        )
                        result_loaded = True
                        self.log(f"✓ Kết quả trang {page + 1} đã load")
                    except TimeoutException:
                        retry_count += 1
                        if retry_count < max_retries:
                            self.log(
                                f"⚠ Timeout kết quả trang {page + 1} (lần {retry_count}/{max_retries}), thử lại..."
                            )
                            time.sleep(2)
                        else:
                            self.log(
                                f"⚠ Bỏ qua trang {page + 1} (timeout sau {max_retries} lần thử)"
                            )

                # Nếu không load được, skip trang này và tiếp tục trang tiếp theo
                if not result_loaded:
                    continue

                # Scroll mượt giống hệt trang đầu
                try:
                    self.scroll_like_human(driver)
                except Exception:
                    pass

                # Find result links - Comprehensive selectors for desktop and mobile
                result_links = []
                selectors = [
                    # Desktop selectors
                    "div.g a[href]",  # Traditional Google results
                    "div.yuRUbf a[href]",  # Modern Google results
                    "a[jsname='UWckNb']",  # Another variant
                    "h3 a[href]",  # Direct title links
                    "div[data-ved] a[href]",  # Data attribute based
                    "div.MjjYud a[href]",  # Another common class
                    "div[data-snf] a[href]",  # Snippet based
                    # Mobile selectors
                    "div[data-ved] a",  # Mobile result links
                    "a[data-ved]",  # Mobile link variant
                    "div.ZINbbc a[href]",  # Mobile result container
                    "div.kCrYT a[href]",  # Mobile title links
                    "div.BNeawe a[href]",  # Mobile text links
                    "div[data-hveid] a[href]",  # Mobile data attribute
                    "div.uUPGi a[href]",  # Mobile specific class
                    # General fallback
                    "a[href*='http']",  # Any link with http
                    "a[href^='http']",  # Links starting with http
                ]

                for selector in selectors:
                    try:
                        links = driver.find_elements(By.CSS_SELECTOR, selector)
                        if links:
                            # Filter out non-result links
                            filtered_links = []
                            for link in links:
                                href = link.get_attribute("href")
                                if href and not any(
                                    x in href
                                    for x in [
                                        "javascript:",
                                        "#",
                                        "/search?",
                                        "google.com/search",
                                        "webcache",
                                        "google.com/preferences",
                                        "google.com/advanced_search",
                                    ]
                                ):
                                    # Check if it's a result link by looking at parent elements
                                    try:
                                        parent_classes = (
                                            link.find_element(
                                                By.XPATH, ".."
                                            ).get_attribute("class")
                                            or ""
                                        )
                                        grandparent_classes = (
                                            link.find_element(
                                                By.XPATH, "../.."
                                            ).get_attribute("class")
                                            or ""
                                        )

                                        # Skip if it's a navigation or footer link
                                        if any(
                                            skip_class
                                            in parent_classes + grandparent_classes
                                            for skip_class in [
                                                "nav",
                                                "footer",
                                                "header",
                                                "menu",
                                                "sidebar",
                                            ]
                                        ):
                                            continue

                                        filtered_links.append(link)
                                    except:
                                        # If we can't check parent, include it
                                        filtered_links.append(link)

                            if filtered_links:
                                result_links = filtered_links
                                self.log(
                                    f"✓ Tìm thấy {len(filtered_links)} links hợp lệ với selector: {selector}"
                                )
                                break
                    except Exception as e:
                        self.log(f"⚠ Lỗi với selector {selector}: {str(e)}")
                        continue

                if not result_links:
                    self.log(f"⚠ Không tìm thấy kết quả ở trang {page + 1}")
                    break

                self.log(f"✓ Tìm thấy {len(result_links)} links")

                for link_idx, link in enumerate(result_links):
                    if not self.is_running:
                        break

                    if current_rank >= num_results:
                        self.log(
                            f"ℹ Đã đạt số lượng kết quả tối đa ({num_results}), dừng tìm kiếm"
                        )
                        break

                    try:
                        url = link.get_attribute("href")
                        if (
                            not url
                            or url.startswith("javascript:")
                            or url.startswith("#")
                        ):
                            continue

                        if any(
                            x in url
                            for x in ["/search?", "google.com/search", "webcache"]
                        ):
                            continue

                        current_rank += 1
                        current_page = (current_rank - 1) // 10 + 1
                        position = (current_rank - 1) % 10 + 1

                        # Check target domain
                        is_target = False
                        if normalized_target:
                            parsed_url = urlparse(url)
                            normalized_url_domain = parsed_url.netloc.lower().replace(
                                "www.", ""
                            )

                            if normalized_target == normalized_url_domain:
                                is_target = True
                                if not found_position:
                                    found_position = current_rank
                                    self.log(
                                        f"🎯 Tìm thấy '{normalized_target}' ở vị trí #{current_rank}"
                                    )
                                    try:
                                        driver.execute_script(
                                            "arguments[0].scrollIntoView({block: 'center'});",
                                            link,
                                        )
                                        time.sleep(random.uniform(0.8, 1.5))
                                    except Exception:
                                        pass
                        else:
                            # Nếu không có domain mục tiêu, tính is_target = True cho tất cả
                            is_target = True

                        # Chỉ lấy kết quả có is_target = True (từ domain mục tiêu)
                        if not is_target:
                            continue

                        # Get title
                        title = "N/A"
                        try:
                            h3_elements = link.find_elements(By.CSS_SELECTOR, "h3")
                            if h3_elements:
                                title = h3_elements[0].text
                        except:
                            pass

                        onsite_start_time = datetime.now()
                        ip_address = "N/A"
                        try:
                            ip_resp = requests.get(
                                "https://api.ipify.org?format=json",
                                proxies=getattr(self, "proxy_dict", None),
                                timeout=8,
                            )
                            if ip_resp.ok:
                                ip_address = ip_resp.json().get("ip", "N/A")
                        except Exception:
                            pass

                        results.append(
                            {
                                "keyword": keyword,
                                "rank": current_rank,
                                "page": current_page,
                                "position": position,
                                "url": url,
                                "title": title,
                                "is_target": "Có",
                                "ip_address": ip_address,
                                "link_click": url,
                                "onsite_time": "",
                                "search_date": onsite_start_time.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                            }
                        )

                        self.log(f"🎯 #{current_rank}: {url[:60]}...")

                        if onsite_enabled and is_target:
                            try:
                                if self._click_link_with_retry(driver, link, url):
                                    self._visit_and_interact(driver, keyword, url, title, results, ip_address, min_time, max_time, extra_clicks=True)
                                else:
                                    self.log(f"⚠ Không click được link, sẽ vào thẳng domain: {url}")
                                    self._visit_and_interact(driver, keyword, url, title, results, ip_address, min_time, max_time, extra_clicks=True)
                            except Exception as behavior_error:
                                if self._is_driver_session_error(behavior_error):
                                    self.log(f"⚠ Driver session chết khi tương tác site: {behavior_error}")
                                    driver = self._recover_driver(driver, x_pos, y_pos, window_width, window_height, ua, headless)
                                    if driver:
                                        continue
                                self.log(f"⚠ Lỗi tương tác trên site: {behavior_error}")

                    except Exception as e:
                        continue

                # Stop searching further pages if target domain is found
                if found_position and normalized_target:
                    self.log(
                        f"✅ Đã tìm thấy domain mục tiêu '{normalized_target}', dừng tìm kiếm thêm trang"
                    )
                    break

                # Stop searching if we have enough results
                if current_rank >= num_results:
                    self.log(f"✅ Đã tìm đủ {num_results} kết quả, dừng tìm kiếm")
                    break

                # Next page
                if current_rank < num_results and page < num_pages - 1:
                    self.log(
                        f"📄 Đang chuẩn bị chuyển sang trang {page + 2}/{num_pages} (tìm được {current_rank}/{num_results} kết quả)"
                    )
                    try:
                        # Scroll xuống cuối (giống người thật)
                        driver.execute_script(
                            "window.scrollTo(0, document.body.scrollHeight);"
                        )
                        time.sleep(random.uniform(1.5, 2.5))

                        # Thử nhiều selector để tìm nút "Trang tiếp theo"
                        next_button = None
                        selectors = [
                            (By.ID, "pnnext"),  # Google tiêu chuẩn
                            (By.CSS_SELECTOR, "a#pnnext"),  # ID selector alternative
                            (By.XPATH, "//a[@id='pnnext']"),  # XPath ID
                            (
                                By.XPATH,
                                "//a[contains(text(), 'Next')]",
                            ),  # English "Next"
                            (
                                By.XPATH,
                                "//a[contains(@aria-label, 'Next')]",
                            ),  # aria-label Next
                            (
                                By.CSS_SELECTOR,
                                "a[href*='start=']",
                            ),  # Links with pagination
                            (By.XPATH, "//a[@rel='next']"),  # rel=next attribute
                        ]

                        for selector_type, selector_value in selectors:
                            try:
                                elements = driver.find_elements(
                                    selector_type, selector_value
                                )
                                if elements:
                                    # Lấy element cuối cùng (thường là nút Next)
                                    candidate = elements[-1]
                                    try:
                                        if candidate.is_displayed():
                                            next_button = candidate
                                            self.log(
                                                f"✓ Tìm thấy nút Next bằng: {selector_type}={selector_value[:40]}"
                                            )
                                            break
                                    except:
                                        pass
                            except Exception as e:
                                continue

                        if next_button is None:
                            self.log(f"⚠ Không tìm thấy nút 'Trang tiếp theo' để click")
                            self.log(f"ℹ Dừng tìm kiếm sau trang {page + 1}")
                            break

                        # Scroll để nó hiển thị trên màn hình
                        driver.execute_script(
                            "arguments[0].scrollIntoView(true);", next_button
                        )
                        time.sleep(0.5)

                        self.log(f"🖱️ Đang click nút Next...")
                        next_button.click()
                        self.log("→ Đã chuyển sang trang tiếp theo, đang chờ tải...")
                        time.sleep(random.uniform(3, 5))

                        # Kiểm tra CAPTCHA sau khi chuyển trang
                        if not check_and_solve_captcha():
                            break

                    except TimeoutException:
                        self.log("⚠ Hết trang kết quả hoặc timeout")
                        break
                    except Exception as e:
                        if self._is_driver_session_error(e):
                            self.log(f"⚠ Driver session bị ngắt khi chuyển trang: {str(e)}")
                            driver = self._recover_driver(driver, x_pos, y_pos, window_width, window_height, ua, headless)
                            if driver:
                                continue
                        self.log(f"⚠ Lỗi chuyển trang: {str(e)}")
                        break

            if normalized_target and not found_position and self.is_running:
                self.log(f"⚠ Không thấy '{normalized_target}' trong Google, sẽ vào thẳng domain để tương tác")
                fallback_url = target_domain if "://" in target_domain else f"https://{target_domain}"
                try:
                    fallback_ok = self._visit_and_interact(driver, keyword, fallback_url, target_domain, results, ip_address, min_time, max_time, extra_clicks=True)
                    if fallback_ok:
                        results.append(
                            {
                                "keyword": keyword,
                                "rank": "N/A",
                                "page": "N/A",
                                "position": "N/A",
                                "url": fallback_url,
                                "title": target_domain,
                                "is_target": "Có",
                                "ip_address": ip_address,
                                "link_click": fallback_url,
                                "onsite_time": f"{random.randint(min_time, max_time)}s",
                                "search_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            }
                        )
                    else:
                        self.log("⚠ Domain fallback thất bại, bỏ qua job này và tiếp tục")
                except Exception as fallback_error:
                    if self._is_driver_session_error(fallback_error):
                        self.log(f"⚠ Driver session chết ở fallback domain: {fallback_error}")
                        driver = self._recover_driver(driver, x_pos, y_pos, window_width, window_height, ua, headless)
                        if driver:
                            try:
                                fallback_ok = self._visit_and_interact(driver, keyword, fallback_url, target_domain, results, ip_address, min_time, max_time, extra_clicks=True)
                                if fallback_ok:
                                    results.append(
                                        {
                                            "keyword": keyword,
                                            "rank": "N/A",
                                            "page": "N/A",
                                            "position": "N/A",
                                            "url": fallback_url,
                                            "title": target_domain,
                                            "is_target": "Có",
                                            "ip_address": ip_address,
                                            "link_click": fallback_url,
                                            "onsite_time": f"{random.randint(min_time, max_time)}s",
                                            "search_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        }
                                    )
                                    return results
                            except Exception:
                                pass
                    self.log(f"⚠ Domain fallback lỗi: {fallback_error}")


        except Exception as e:
            self.log(f"❌ Lỗi: {str(e)}")
            import traceback

            self.log(f"Chi tiết:\n{traceback.format_exc()}")
        finally:
            if driver:
                try:
                    self.log("🔒 Đang đóng trình duyệt...")
                    driver.quit()
                    self.driver = None
                except:
                    self.driver = None
            # Giải phóng slot để tái sử dụng
            release_window_slot(slot_index if "slot_index" in locals() else None)
        return results

    def write_to_sheet(self, sheet_id, results):
        """Ghi kết quả lên Google Sheets"""
        try:
            self.log("📊 Đang kết nối Google Sheets...")

            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]

            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, scope
            )
            client = gspread.authorize(creds)

            sheet = client.open_by_key(sheet_id)
            worksheet_name = f"Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            self.log(f"📝 Tạo worksheet: {worksheet_name}")
            worksheet = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=10)

            # Header
            headers = [
                "Từ khóa",
                "Thứ hạng",
                "Trang",
                "Vị trí",
                "URL",
                "Tiêu đề",
                "Domain mục tiêu",
                "Địa chỉ IP",
                "Link click",
                "Thời gian onsite",
                "Ngày tìm kiếm",
            ]
            worksheet.append_row(headers)

            # Format header
            worksheet.format(
                "A1:K1",
                {
                    "textFormat": {"bold": True, "fontSize": 11},
                    "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.86},
                    "horizontalAlignment": "CENTER",
                },
            )

            # Ghi dữ liệu
            self.log(f"💾 Đang ghi {len(results)} kết quả...")
            for i, result in enumerate(results):
                if not self.is_running:
                    break

                row = [
                    result["keyword"],
                    result["rank"],
                    result["page"],
                    result["position"],
                    result["url"],
                    result["title"],
                    result["is_target"],
                    result.get("ip_address", "N/A"),
                    result.get("link_click", result.get("url", "N/A")),
                    result.get("onsite_time", "N/A"),
                    result["search_date"],
                ]
                worksheet.append_row(row)
                self.progress_signal.emit(i + 1, len(results))

            self.log(f"✅ Hoàn thành! Đã ghi {len(results)} kết quả")
            self.log(f"🔗 Sheet URL: {sheet.url}")

            return True

        except Exception as e:
            self.log(f"❌ Lỗi khi ghi Google Sheets: {str(e)}")
            return False

    def write_results_to_sheet(self, sheet_id, results, worksheet_name):
        """Ghi kết quả lên Google Sheets - Ghi từng từ khóa một"""
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]

            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, scope
            )
            client = gspread.authorize(creds)

            sheet = client.open_by_key(sheet_id)

            # Kiểm tra xem worksheet đã tồn tại chưa
            try:
                worksheet = sheet.worksheet(worksheet_name)
                # Nếu worksheet đã tồn tại, lấy số dòng hiện tại
                self.log(f"✓ Sử dụng worksheet hiện có: {worksheet_name}")
            except:
                # Nếu chưa tồn tại, tạo mới
                worksheet = sheet.add_worksheet(
                    title=worksheet_name, rows=5000, cols=11
                )

                # Header
                headers = [
                    "Từ khóa",
                    "Thứ hạng",
                    "Trang",
                    "Vị trí",
                    "URL",
                    "Tiêu đề",
                    "Domain mục tiêu",
                    "Địa chỉ IP",
                    "Link click",
                    "Thời gian onsite",
                    "Ngày tìm kiếm",
                ]
                worksheet.append_row(headers)

                # Format header
                worksheet.format(
                    "A1:K1",
                    {
                        "textFormat": {"bold": True, "fontSize": 11},
                        "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.86},
                        "horizontalAlignment": "CENTER",
                    },
                )
                self.log(f"✓ Tạo worksheet mới: {worksheet_name}")

            # Ghi dữ liệu
            self.log(
                f"💾 Đang ghi {len(results)} kết quả của '{results[0]['keyword']}'..."
            )
            for i, result in enumerate(results):
                if not self.is_running:
                    break

                row = [
                    result["keyword"],
                    result["rank"],
                    result["page"],
                    result["position"],
                    result["url"],
                    result["title"],
                    result["is_target"],
                    result.get("ip_address", "N/A"),
                    result.get("link_click", result.get("url", "N/A")),
                    result.get("onsite_time", "N/A"),
                    result["search_date"],
                ]
                worksheet.append_row(row)
                self.progress_signal.emit(i + 1, len(results))

            self.log(f"✅ Đã ghi xong {len(results)} kết quả")

            return True

        except Exception as e:
            self.log(f"❌ Lỗi khi ghi Google Sheets: {str(e)}")
            return False

    def run(self):
        """Chạy tìm kiếm với đa luồng"""
        try:
            # Kiểm tra kết nối internet trước
            self.log("🔌 Đang kiểm tra kết nối internet...")
            try:
                # Thử kết nối đến Google
                response = requests.head("https://www.google.com", timeout=5)
                self.log("✓ Kết nối internet bình thường")
            except requests.exceptions.ConnectionError:
                self.log("❌ LỖI: Không thể kết nối internet!")
                self.log("⚠️ Vui lòng kiểm tra:")
                self.log("   • Đảm bảo bạn có kết nối Internet ổn định")
                self.log("   • Tắt VPN/Proxy nếu có (hoặc cấu hình đúng)")
                self.log("   • Kiểm tra Firewall hoặc antivirus")
                self.finished_signal.emit(False, "Không có kết nối internet")
                return
            except requests.exceptions.Timeout:
                self.log("⚠️ Cảnh báo: Kết nối chậm, nhưng sẽ tiếp tục thử")

            keywords = [
                k.strip() for k in self.config["keywords"].split("\n") if k.strip()
            ]
            num_results = self.config["num_pages"] * 10
            target_domain = self.config["target_domain"].strip()

            self.log("=" * 50)
            self.log("🚀 BẮT ĐẦU TÌM KIẾM")
            self.log(f"📝 Số từ khóa: {len(keywords)}")
            self.log(f"📄 Số trang: {self.config['num_pages']}")
            if target_domain:
                self.log(f"🎯 Domain mục tiêu: {target_domain}")
            self.log("=" * 50)

            all_results = []
            today = datetime.now()
            # worksheet_name = f"Results_{datetime.now().strftime('%Y%m%d')}"
            worksheet_name = f"Ngày_{today.day:02d}_{today.month:02d}_{today.year}"
            worksheet_initialized = False

            # Sử dụng ThreadPoolExecutor để chạy đa luồng
            max_workers = min(len(keywords), self.config.get("max_threads", 5))
            if max_workers < 1:
                max_workers = 1
            self.log(f"🧵 max_workers = {max_workers}, len(keywords) = {len(keywords)}")
            self.log(f"🧵 Sử dụng {max_workers} thread để xử lý")

            delay_seconds = self.config.get("delay_seconds", 2)
            if delay_seconds > 0:
                self.log(f"⏳ Delay {delay_seconds}s giữa các từ khóa")

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers
            ) as executor:
                # Submit các task tìm kiếm
                future_to_keyword = {}

                for i, keyword in enumerate(keywords):
                    thread_index = i % max_workers
                    future_to_keyword[
                        executor.submit(
                            self.search_keyword,
                            keyword,
                            num_results,
                            target_domain,
                            thread_index,
                        )
                    ] = keyword

                    # Stagger: đợi delay_seconds trước khi mở từ khóa tiếp theo
                    if i < len(keywords) - 1:  # Không delay sau keyword cuối
                        delay_seconds = float(self.config.get("delay_seconds", 2) or 0)
                        if delay_seconds > 0:
                            self.log(f"⏳ Đợi {delay_seconds}s trước từ khóa tiếp theo")
                            time.sleep(delay_seconds)
                # Thu thập kết quả từ các thread
                completed_keywords = 0  # ← THÊM DÒNG NÀY
                for future in concurrent.futures.as_completed(future_to_keyword):
                    if not self.is_running:
                        self.log("⏸ Đã dừng tìm kiếm")
                        executor.shutdown(wait=False)
                        break

                    keyword = future_to_keyword[future]
                    try:
                        results = future.result() or []
                        self.log(f"✓ Tìm thấy {len(results)} kết quả cho '{keyword}'")

                        # Ghi kết quả lên Google Sheet ngay sau khi tìm xong từ khóa
                        # Dù có hay không có kết quả đều ghi lên sheet
                        if not worksheet_initialized:
                            # Initialize worksheet lần đầu
                            self.log(f"📝 Tạo worksheet: {worksheet_name}")
                            worksheet_initialized = True

                        if len(results) > 0:
                            self.log(
                                f"💾 Đang ghi kết quả của '{keyword}' lên Google Sheets..."
                            )
                            self.write_results_to_sheet(
                                self.config["sheet_id"], results, worksheet_name
                            )
                        else:
                            # Tạo hàng thông báo không có kết quả
                            no_result = {
                                "keyword": keyword,
                                "rank": "N/A",
                                "page": "N/A",
                                "position": "N/A",
                                "url": "Không có kết quả",
                                "title": "Không tìm thấy từ khóa này",
                                "is_target": "Không",
                                "search_date": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                            }
                            self.log(
                                f"💾 Ghi thông báo không có kết quả cho '{keyword}'..."
                            )
                            self.write_results_to_sheet(
                                self.config["sheet_id"], [no_result], worksheet_name
                            )

                        completed_keywords += 1
                        self.progress_signal.emit(
                            completed_keywords, len(keywords)
                        )
                        all_results.extend(results)
                        if self.config.get("proxy_enabled", False):
                            self.log(f"🔄 Đổi proxy sau khi xử lý '{keyword}'")
                            self.refresh_proxy()
                    except Exception as exc:
                        self.log(f"❌ Từ khóa '{keyword}' gặp lỗi: {exc}")

            if self.is_running:
                self.log("\n" + "=" * 50)
                if all_results:
                    self.finished_signal.emit(
                        True, f"Hoàn thành! Đã ghi {len(all_results)} kết quả"
                    )
                else:
                    self.finished_signal.emit(
                        True, "Hoàn thành tìm kiếm (không có kết quả)"
                    )
            else:
                self.finished_signal.emit(
                    False,
                    f"Đã dừng tìm kiếm. Đã tìm thấy {len(all_results)} kết quả (đã ghi lên sheet)",
                )

        except Exception as e:
            self.log(f"❌ Lỗi nghiêm trọng: {str(e)}")
            self.finished_signal.emit(False, str(e))


def run_headless():
    """Run search in headless mode without GUI"""
    config_file = "config.json"

    # Load config
    if not os.path.exists(config_file):
        print("Error: config.json not found")
        return

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    # Validate config
    if not config.get("sheet_id"):
        print("Error: Google Sheet ID is required")
        return

    if not config.get("keywords", "").strip():
        print("Error: Keywords are required")
        return

    credentials_file = config.get("credentials_file", "credentials.json")
    if not os.path.exists(credentials_file):
        print("Error: Credentials file not found")
        return

    # Prepare config
    search_config = {
        "sheet_id": config["sheet_id"],
        "num_pages": config.get("num_pages", 3),
        "target_domain": config.get("target_domain", ""),
        "keywords": config["keywords"],
    }

    # Run search thread
    search_thread = SearchThread(search_config, credentials_file)
    search_thread.log_signal.connect(lambda msg: print(msg))
    search_thread.finished_signal.connect(
        lambda success, msg: print(f"Finished: {msg}")
    )

    search_thread.start()
    search_thread.wait()  # Wait for completion
