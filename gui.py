"""
gui.py
Chứa class giao diện chính (KeywordSearchGUI) và các widget liên quan.
"""

import requests
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QSpinBox,
    QGroupBox,
    QMessageBox,
    QFileDialog,
    QProgressBar,
    QTabWidget,
    QCheckBox,
    QComboBox,
    QDialog,
    QInputDialog,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QScrollArea,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QMimeData, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from search_logic import SearchThread, parse_proxyxoay_response
from config_utils import *
from db import UserManager

from login import LoginDialog

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


class PlainTextEdit(QTextEdit):
    """QTextEdit that strips formatting on paste"""

    def insertFromMimeData(self, source):
        """Override paste to strip formatting"""
        if source.hasText():
            # Get plain text only
            plain_text = source.text()
            # Insert as plain text
            self.insertPlainText(plain_text)


# Để sử dụng: from gui import KeywordSearchGUI
class KeywordSearchGUI(QMainWindow):
    """Giao diện chính"""

    # Dịch ngôn ngữ
    TRANSLATIONS = {
        "vi": {
            "title": "Công cụ Tìm kiếm Từ khóa - SEA DRAGON TECHOLOGY - v1.6",
            "config_tab": "⚙️ Cấu hình",
            "chrome_tab": "🌐 Chrome",
            "log_tab": "📋 Log",
            "browser_tab": "🌐 Chrome Browser",
            "User": "Người dùng",
            "admin_tab": "🛡️ Quản trị Admin",
            "admin_group": "🛡️ Quản lý tài khoản",
            "admin_refresh_users": "🔄 Tải danh sách",
            "admin_user_list": "Danh sách tài khoản",
            "admin_selected_user": "Tài khoản đã chọn:",
            "admin_current_role": "Quyền hiện tại:",
            "admin_new_role": "Quyền mới:",
            "admin_update_role": "💾 Cập nhật quyền",
            "admin_clear_machine": "🧹 Xóa machine info",
            "admin_no_user_selected": "Vui lòng chọn tài khoản để thao tác.",
            "admin_update_role_success": "Đã cập nhật quyền cho tài khoản '{}'.",
            "admin_clear_machine_success": "Đã xóa machine info cho tài khoản '{}'.",
            "admin_cannot_manage_self": "Không thể tự hạ quyền tài khoản admin đang đăng nhập.",
            "admin_user_info": "User: {} | Role: {} | Expired: {} | Machine: {}",
            "admin_machine_exists": "Có",
            "admin_machine_missing": "Không",
            "admin_expired_none": "Không có",
            "admin_load_failed": "Không thể tải danh sách tài khoản: {}",
            "sheets": "📊 Google Sheets",
            "sheet_id": "📋 Sheet ID:",
            "credentials": "🔑 Credentials:",
            "select_btn": "📁 Chọn",
            "search_config": "🔍 Cấu hình Tìm kiếm",
            "pages": "📄 Số trang:",
            "threads": "🧵 Số luồng:",
            "domain": "🎯 Tên miền:",
            "domain_placeholder": "VD: example.com (không bắt buộc)",
            "keywords": "🔑 Danh sách từ khóa",
            "keywords_placeholder": "Nhập mỗi từ khóa trên một dòng...\nVD:\nmarketing online\nseo tips\ndigital marketing",
            "keywords_count": "Số từ khóa: {}",
            "start_btn": "▶️ Bắt đầu",
            "stop_btn": "⏸️ Dừng",
            "save_btn": "💾 Lưu",
            "edit_btn": "✏️ Sửa",
            "open_sheet_btn": "📊 Mở Sheet",
            "logout_btn": "🚪 Đăng xuất",
            "ua_config": "👤 Cấu hình User-Agent",
            "ua_category": "📋 Danh mục User-Agent:",
            "ua_specific": "🎯 User-Agent cụ thể:",
            "window_config": "🪟 Cấu hình Cửa sổ",
            "window_size": "📐 Kích thước cửa sổ:",
            "headless": "🙈 Chạy headless (không hiển thị cửa sổ)",
            "save_chrome_btn": "💾 Lưu cấu hình Chrome",
            "reset_chrome_btn": "🔄 Tải mặc định",
            "log_label": "📋 Log",
            "ready": "Sẵn sàng",
            "searching": "Đang tìm kiếm...",
            "completed": "Hoàn thành!",
            "error": "Có lỗi xảy ra",
            "warning": "Cảnh báo",
            "not_found": "Chưa chọn file",
            "select_credentials": "Chọn file credentials.json",
            "json_files": "JSON Files (*.json)",
            "selected_credentials": "Đã chọn credentials: {}",
            "success": "Thành công",
            "saved_config": "Đã lưu cấu hình!",
            "error_save": "Không thể lưu cấu hình: {}",
            "error_sheet": "Vui lòng nhập Sheet ID",
            "error_keywords": "Vui lòng nhập danh sách từ khóa",
            "error_credentials": "Vui lòng chọn file credentials",
            "confirm_stop": "Xác nhận dừng",
            "confirm_stop_msg": "Bạn có chắc chắn muốn dừng tìm kiếm?",
            "confirm_logout": "Xác nhận đăng xuất",
            "confirm_logout_msg": "Bạn có chắc chắn muốn đăng xuất?",
            "change_password_btn": "🔑 Thay đổi mật khẩu",
            "change_username_btn": "👤 Thay đổi tên đăng nhập",
            "current_password": "Mật khẩu hiện tại:",
            "new_password": "Mật khẩu mới:",
            "confirm_new_password": "Xác nhận mật khẩu mới:",
            "new_username": "Tên đăng nhập mới:",
            "change_password_title": "Thay đổi mật khẩu",
            "change_username_title": "Thay đổi tên đăng nhập",
            "password_changed": "Mật khẩu đã được thay đổi thành công!",
            "username_changed": "Tên đăng nhập đã được thay đổi thành công!",
            "wrong_current_password": "Mật khẩu hiện tại không đúng!",
            "passwords_not_match": "Mật khẩu mới và xác nhận không khớp!",
            "username_exists": "Tên đăng nhập đã tồn tại!",
            "chrome_browser": "🌐 Chrome Browser",
            "browser_info": "Thông tin trình duyệt",
            "tieng_viet": "Tiếng Việt",
            "english": "English",
            "config_manager_tab": "📋 Quản lý Cấu hình",
            "saved_configs": "Danh sách cấu hình đã lưu",
            "config_name": "Tên cấu hình",
            "apply_config": "✅ Áp dụng",
            "delete_config": "🗑️ Xóa",
            "rename_config": "✏️ Đổi tên",
            "no_configs": "Chưa có cấu hình nào được lưu",
            "apply_success": "Đã áp dụng cấu hình!",
            "delete_confirm": "Xác nhận xóa",
            "delete_confirm_msg": "Bạn có chắc chắn muốn xóa cấu hình này?",
            "config_deleted": "Đã xóa cấu hình!",
            "rename_config_title": "Đổi tên cấu hình",
            "new_config_name": "Tên cấu hình mới:",
            "config_renamed": "Đã đổi tên cấu hình!",
            "config_name_exists": "Tên cấu hình này đã tồn tại!",
            "export_config": "📤 Xuất",
            "import_config": "📥 Nhập",
            "config_info": "Sheet ID: {} | Domain: {} | Pages: {} | Threads: {}",
        },
        "en": {
            "title": "Keyword Search Tool - SEA DRAGON TECHOLOGY - v1.6",
            "config_tab": "⚙️ Config",
            "chrome_tab": "🌐 Chrome",
            "log_tab": "📋 Log",
            "browser_tab": "🌐 Chrome Browser",
            "User": "User",
            "admin_tab": "🛡️ Admin Panel",
            "admin_group": "🛡️ Account Management",
            "admin_refresh_users": "🔄 Refresh List",
            "admin_user_list": "Accounts",
            "admin_selected_user": "Selected account:",
            "admin_current_role": "Current role:",
            "admin_new_role": "New role:",
            "admin_update_role": "💾 Update Role",
            "admin_clear_machine": "🧹 Clear machine info",
            "admin_no_user_selected": "Please select an account first.",
            "admin_update_role_success": "Updated role for account '{}'.",
            "admin_clear_machine_success": "Cleared machine info for account '{}'.",
            "admin_cannot_manage_self": "You cannot downgrade your own admin account.",
            "admin_user_info": "User: {} | Role: {} | Expired: {} | Machine: {}",
            "admin_machine_exists": "Yes",
            "admin_machine_missing": "No",
            "admin_expired_none": "None",
            "admin_load_failed": "Could not load account list: {}",
            "sheets": "📊 Google Sheets",
            "sheet_id": "📋 Sheet ID:",
            "credentials": "🔑 Credentials:",
            "select_btn": "📁 Select",
            "search_config": "🔍 Search Config",
            "pages": "📄 Pages:",
            "threads": "🧵 Threads:",
            "domain": "🎯 Domain:",
            "domain_placeholder": "E.g: example.com (optional)",
            "keywords": "🔑 Keywords List",
            "keywords_placeholder": "Enter one keyword per line...\nE.g:\nmarketing online\nseo tips\ndigital marketing",
            "keywords_count": "Keywords: {}",
            "start_btn": "▶️ Start",
            "stop_btn": "⏸️ Stop",
            "save_btn": "💾 Save",
            "edit_btn": "✏️ Edit",
            "open_sheet_btn": "📊 Open Sheet",
            "ua_config": "👤 User-Agent Config",
            "ua_category": "📋 User-Agent Category:",
            "ua_specific": "🎯 Specific User-Agent:",
            "window_config": "🪟 Window Config",
            "window_size": "📐 Window Size:",
            "headless": "🙈 Headless mode (no visible window)",
            "save_chrome_btn": "💾 Save Chrome Config",
            "reset_chrome_btn": "🔄 Load Default",
            "log_label": "📋 Log",
            "ready": "Ready",
            "searching": "Searching...",
            "completed": "Completed!",
            "error": "Error occurred",
            "warning": "Warning",
            "not_found": "Not selected",
            "select_credentials": "Select credentials.json",
            "json_files": "JSON Files (*.json)",
            "selected_credentials": "Credentials selected: {}",
            "success": "Success",
            "saved_config": "Configuration saved!",
            "error_save": "Cannot save configuration: {}",
            "error_sheet": "Please enter Sheet ID",
            "error_keywords": "Please enter keywords list",
            "error_credentials": "Please select credentials file",
            "confirm_stop": "Confirm Stop",
            "confirm_stop_msg": "Are you sure you want to stop searching?",
            "chrome_browser": "🌐 Chrome Browser",
            "browser_info": "Browser Information",
            "tieng_viet": "Tiếng Việt",
            "english": "English",
            "config_manager_tab": "📋 Config Manager",
            "saved_configs": "Saved Configuration List",
            "config_name": "Config Name",
            "apply_config": "✅ Apply",
            "delete_config": "🗑️ Delete",
            "rename_config": "✏️ Rename",
            "no_configs": "No saved configurations",
            "apply_success": "Configuration applied!",
            "delete_confirm": "Confirm Delete",
            "delete_confirm_msg": "Are you sure you want to delete this configuration?",
            "config_deleted": "Configuration deleted!",
            "rename_config_title": "Rename Configuration",
            "new_config_name": "New configuration name:",
            "config_renamed": "Configuration renamed!",
            "config_name_exists": "This configuration name already exists!",
            "export_config": "📤 Export",
            "import_config": "📥 Import",
            "config_info": "Sheet ID: {} | Domain: {} | Pages: {} | Threads: {}",
        },
    }

    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user  # Lưu username của người dùng hiện tại
        self.config_file = (
            f"config_{self.current_user}.json" if self.current_user else "config.json"
        )
        self.configs_list_file = (
            f"configs_{self.current_user}.json" if self.current_user else "configs.json"
        )  # File lưu danh sách cấu hình
        self.credentials_file = "credentials.json"
        self.search_thread = None
        self.search_threads = []
        self.language = "vi"  # Mặc định tiếng Việt
        self.selected_config_name = None  # Theo dõi cấu hình được chọn
        self.job_cards = []
        self.job_counter = 0
        self.user_manager = UserManager()
        self.current_user_role = "user"
        current_user_doc = self.user_manager.get_user(self.current_user) if self.current_user else None
        if current_user_doc:
            self.current_user_role = str(current_user_doc.get("role", "user")).strip().lower()
        self.admin_users_cache = {}
        self.admin_tab_index = None
        self.init_ui()
        self.load_chrome_config()
        self.load_proxy_config()
        self.load_configs_list()  # Tải danh sách cấu hình

    def t(self, key):
        """Lấy text dịch theo ngôn ngữ hiện tại"""
        return self.TRANSLATIONS[self.language].get(key, key)

    def is_current_admin(self):
        return self.current_user_role == "admin"

    def init_ui(self):
        """Khởi tạo giao diện"""
        self.setWindowTitle(self.t("title"))
        self.setGeometry(100, 100, 900, 700)

        # Tạo central widget với toolbar
        central_widget = QWidget()
        central_layout = QVBoxLayout()

        # Thêm toolbar chuyển đổi ngôn ngữ
        toolbar_layout = QHBoxLayout()
        
        # Logo bên trái
        self.logo_label = QLabel()
        pixmap = QPixmap("logo.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)
        # self.logo_label.setStyleSheet("margin: 5px;")
        toolbar_layout.addWidget(self.logo_label)
        
        toolbar_layout.addStretch()

        self.lang_vi_btn = QPushButton("Tiếng Việt")
        self.lang_vi_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 3px;
                border: none;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )
        self.lang_vi_btn.clicked.connect(self.set_language_vi)
        toolbar_layout.addWidget(self.lang_vi_btn)

        self.lang_en_btn = QPushButton("English")
        self.lang_en_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 3px;
                border: none;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """
        )
        self.lang_en_btn.clicked.connect(self.set_language_en)
        toolbar_layout.addWidget(self.lang_en_btn)

        central_layout.addLayout(toolbar_layout)

        # Tạo tab widget
        self.tab_widget = QTabWidget()
        central_layout.addWidget(self.tab_widget)

        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # === TAB CẤU HÌNH ===
        config_tab = QWidget()
        self.tab_widget.addTab(config_tab, self.t("config_tab"))
        config_layout = QVBoxLayout()
        config_layout.setSpacing(15)
        config_layout.setContentsMargins(15, 15, 15, 15)
        config_tab.setLayout(config_layout)

        self.jobs_scroll = QScrollArea()
        self.jobs_scroll.setWidgetResizable(True)
        self.jobs_scroll.setFrameShape(QFrame.NoFrame)
        self.jobs_scroll_content = QWidget()
        self.jobs_grid_layout = QGridLayout()
        self.jobs_grid_layout.setSpacing(16)
        self.jobs_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.jobs_scroll_content.setLayout(self.jobs_grid_layout)
        self.jobs_scroll.setWidget(self.jobs_scroll_content)
        config_layout.addWidget(self.jobs_scroll)

        self.add_job_button = QPushButton("➕ Thêm Job")
        self.add_job_button.setStyleSheet(
            """
            QPushButton {
                background-color: #673AB7;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover { background-color: #5E35B1; }
            QPushButton:pressed { background-color: #512DA8; }
        """
        )
        self.add_job_button.setMinimumHeight(36)
        self.add_job_button.clicked.connect(lambda: self.add_job_card())
        config_layout.addWidget(self.add_job_button)

        # === ACTION BUTTONS ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.stop_button = QPushButton(self.t("stop_btn"))
        self.stop_button.clicked.connect(self.stop_search)
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumHeight(36)
        self.stop_button.setStyleSheet(
            "QPushButton{background:#ef4444;color:white;border:none;border-radius:10px;padding:8px 14px;font-weight:600;}"
            "QPushButton:hover{background:#dc2626;}"
            "QPushButton:pressed{background:#b91c1c;}"
            "QPushButton:disabled{background:#d1d5db;color:#6b7280;}"
        )
        button_layout.addWidget(self.stop_button)

        self.save_button = QPushButton(self.t("save_btn"))
        self.save_button.clicked.connect(self.save_config)
        self.save_button.setMinimumHeight(36)
        self.save_button.setStyleSheet(
            "QPushButton{background:#10b981;color:white;border:none;border-radius:10px;padding:8px 14px;font-weight:600;}"
            "QPushButton:hover{background:#059669;}"
            "QPushButton:pressed{background:#047857;}"
            "QPushButton:disabled{background:#d1d5db;color:#6b7280;}"
        )
        button_layout.addWidget(self.save_button)

        self.edit_button = QPushButton(self.t("edit_btn"))
        self.edit_button.clicked.connect(self.edit_current_config)
        self.edit_button.setMinimumHeight(36)
        self.edit_button.setStyleSheet(
            "QPushButton{background:#f59e0b;color:white;border:none;border-radius:10px;padding:8px 14px;font-weight:600;}"
            "QPushButton:hover{background:#d97706;}"
            "QPushButton:pressed{background:#b45309;}"
            "QPushButton:disabled{background:#d1d5db;color:#6b7280;}"
        )
        button_layout.addWidget(self.edit_button)

        self.run_all_jobs_button = QPushButton("▶ Chạy tất cả job")
        self.run_all_jobs_button.setMinimumHeight(36)
        self.run_all_jobs_button.setStyleSheet(
            "QPushButton{background:#111827;color:white;border:none;border-radius:10px;padding:8px 16px;font-weight:700;}"
            "QPushButton:hover{background:#1f2937;}"
            "QPushButton:pressed{background:#0f172a;}"
            "QPushButton:disabled{background:#d1d5db;color:#6b7280;}"
        )
        self.run_all_jobs_button.clicked.connect(self.run_all_jobs)
        button_layout.addWidget(self.run_all_jobs_button)
        config_layout.addLayout(button_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        config_layout.addWidget(self.progress_bar)

        self.add_job_card()

        # === TAB PROXY SETTINGS ===
        proxy_tab = QWidget()
        self.tab_widget.addTab(proxy_tab, "🔗 Proxy")
        proxy_layout = QVBoxLayout()
        proxy_layout.setSpacing(15)
        proxy_layout.setContentsMargins(15, 15, 15, 15)
        proxy_tab.setLayout(proxy_layout)

        proxy_header_card = QFrame()
        proxy_header_card.setStyleSheet(
            "QFrame{background:#fff7ed; border:1px solid #fdba74; border-radius:12px;}"
        )
        proxy_header_layout = QVBoxLayout(proxy_header_card)
        proxy_header_layout.setSpacing(8)
        proxy_header_layout.setContentsMargins(16, 16, 16, 16)

        proxy_title_label = QLabel("🔗 Quản lý Proxy")
        proxy_title_label.setFont(QFont("Arial", 12, QFont.Bold))
        proxy_title_label.setStyleSheet("color:#111827; border:none; background:transparent;")
        proxy_header_layout.addWidget(proxy_title_label)

        proxy_desc_label = QLabel("Thiết lập danh sách key proxy xoay. Mỗi luồng đang chạy sẽ được cấp 1 proxy theo cơ chế phân bổ toàn cục của ứng dụng.")
        proxy_desc_label.setWordWrap(True)
        proxy_desc_label.setStyleSheet("color:#6b7280; border:none; background:transparent;")
        proxy_header_layout.addWidget(proxy_desc_label)
        proxy_layout.addWidget(proxy_header_card)

        # === PHẦN CẤU HÌNH PROXY ===
        proxy_group = QGroupBox("🔗 Cấu hình Proxy Xoay (mỗi luồng 1 key)")
        proxy_group.setFont(QFont("Arial", 10, QFont.Bold))
        proxy_group.setStyleSheet(
            """
            QGroupBox {
                color: #111827;
                border: 2px solid #fb923c;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 10px;
                background: #fffaf5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px 0 4px;
            }
        """
        )
        group_proxy_layout = QVBoxLayout()
        group_proxy_layout.setSpacing(12)

        # Enable proxy
        enable_proxy_layout = QHBoxLayout()
        enable_proxy_layout.addSpacing(150)
        self.enable_proxy_checkbox = QCheckBox("Bật proxy")
        self.enable_proxy_checkbox.setFont(QFont("Arial", 9))
        self.enable_proxy_checkbox.setMinimumHeight(25)
        self.enable_proxy_checkbox.stateChanged.connect(self.toggle_proxy_fields)
        enable_proxy_layout.addWidget(self.enable_proxy_checkbox)
        enable_proxy_layout.addStretch()
        group_proxy_layout.addLayout(enable_proxy_layout)

        # Proxy type
        proxy_type_layout = QHBoxLayout()
        proxy_type_label = QLabel("Loại proxy:")
        proxy_type_label.setFont(QFont("Arial", 9))
        proxy_type_label.setMinimumWidth(150)
        proxy_type_layout.addWidget(proxy_type_label)
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(["http", "https"])
        self.proxy_type_combo.setMinimumHeight(30)
        proxy_type_layout.addWidget(self.proxy_type_combo)
        proxy_type_layout.addStretch()
        group_proxy_layout.addLayout(proxy_type_layout)

        # Proxy list
        proxy_list_label = QLabel("📋 Danh sách key proxy (mỗi dòng 1 key = 1 luồng):")
        proxy_list_label.setFont(QFont("Arial", 9, QFont.Bold))
        group_proxy_layout.addWidget(proxy_list_label)

        # Proxy list text area
        proxy_list_desc = QLabel(
            "Mỗi dòng nhập 1 API key của proxy xoay.\nVD:\nUPFWmwMySvjfPGSdndAKZl\nKEY_2\nKEY_3\n\nKhi chạy, mỗi luồng sẽ tự lấy 1 proxy từ API của key tương ứng."
        )
        proxy_list_desc.setFont(QFont("Arial", 8))
        proxy_list_desc.setStyleSheet("color: #999; font-style: italic;")
        group_proxy_layout.addWidget(proxy_list_desc)

        self.proxy_list_input = PlainTextEdit()
        self.proxy_list_input.setPlaceholderText(
            "Nhập từng API key trên một dòng\nMỗi key tương ứng 1 luồng Chrome"
        )
        self.proxy_list_input.setMinimumHeight(220)
        self.proxy_list_input.setStyleSheet(
            "QTextEdit{background:#ffffff; border:1px solid #fed7aa; border-radius:10px; padding:10px;} QTextEdit:focus{border:1px solid #fb923c;}"
        )
        group_proxy_layout.addWidget(self.proxy_list_input)

        # Proxy list counter
        counter_layout = QHBoxLayout()
        self.proxy_counter_label = QLabel("Số proxy: 0")
        self.proxy_counter_label.setStyleSheet(
            "color: #666; font-size: 9px; font-weight: bold;"
        )
        self.proxy_list_input.textChanged.connect(self.update_proxy_counter)
        counter_layout.addWidget(self.proxy_counter_label)
        counter_layout.addStretch()
        group_proxy_layout.addLayout(counter_layout)

        proxy_group.setLayout(group_proxy_layout)
        proxy_layout.addWidget(proxy_group)

        # === NÚT LƯU PROXY CONFIG ===
        proxy_button_layout = QHBoxLayout()
        proxy_button_layout.setSpacing(10)

        self.save_proxy_button = QPushButton("💾 Lưu cấu hình Proxy")
        self.save_proxy_button.setStyleSheet(
            "QPushButton{background:#f97316;color:white;font-size:11px;font-weight:700;padding:10px 18px;border-radius:10px;border:none;}"
            "QPushButton:hover{background:#ea580c;}"
            "QPushButton:pressed{background:#c2410c;}"
        )
        self.save_proxy_button.setMinimumHeight(36)
        self.save_proxy_button.clicked.connect(self.save_proxy_config)
        proxy_button_layout.addWidget(self.save_proxy_button)

        self.test_proxy_button = QPushButton("🧪 Test Proxy")
        self.test_proxy_button.setStyleSheet(
            "QPushButton{background:#2563eb;color:white;font-size:11px;font-weight:700;padding:10px 18px;border-radius:10px;border:none;}"
            "QPushButton:hover{background:#1d4ed8;}"
            "QPushButton:pressed{background:#1e40af;}"
        )
        self.test_proxy_button.setMinimumHeight(36)
        self.test_proxy_button.clicked.connect(self.test_proxy_connection)
        proxy_button_layout.addWidget(self.test_proxy_button)

        proxy_button_layout.addStretch()
        proxy_layout.addLayout(proxy_button_layout)

        # Thêm khoảng trống cuối
        proxy_layout.addStretch()

        # === TAB CHROME SETTINGS ===
        chrome_tab = QWidget()
        self.tab_widget.addTab(chrome_tab, self.t("chrome_tab"))
        chrome_layout = QVBoxLayout()
        chrome_layout.setSpacing(14)
        chrome_layout.setContentsMargins(16, 16, 16, 16)
        chrome_tab.setLayout(chrome_layout)

        chrome_header_card = QFrame()
        chrome_header_card.setStyleSheet(
            "QFrame{background:#eff6ff; border:1px solid #bfdbfe; border-radius:12px;}"
        )
        chrome_header_layout = QVBoxLayout(chrome_header_card)
        chrome_header_layout.setSpacing(4)
        chrome_header_layout.setContentsMargins(16, 14, 16, 14)

        chrome_title_label = QLabel("🌐 Cấu hình Chrome")
        chrome_title_label.setFont(QFont("Arial", 13, QFont.Bold))
        chrome_title_label.setStyleSheet("color:#111827; border:none; background:transparent;")
        chrome_header_layout.addWidget(chrome_title_label)

        chrome_desc_label = QLabel(
            "Tùy chỉnh User-Agent, độ trễ và kích thước cửa sổ để tối ưu trải nghiệm chạy Chrome."
        )
        chrome_desc_label.setWordWrap(True)
        chrome_desc_label.setStyleSheet("color:#6b7280; border:none; background:transparent;")
        chrome_header_layout.addWidget(chrome_desc_label)
        chrome_layout.addWidget(chrome_header_card)

        def make_card(title_text, border_color="#e5e7eb", bg_color="#ffffff"):
            card = QFrame()
            card.setStyleSheet(
                f"QFrame{{background:{bg_color}; border:1px solid {border_color}; border-radius:12px;}}"
            )
            layout = QVBoxLayout(card)
            layout.setContentsMargins(16, 14, 16, 14)
            layout.setSpacing(10)
            title = QLabel(title_text)
            title.setFont(QFont("Arial", 11, QFont.Bold))
            title.setStyleSheet("color:#111827; border:none; background:transparent;")
            layout.addWidget(title)
            return card, layout

        # === PHẦN CẤU HÌNH USER-AGENT ===
        ua_group, group_ua_layout = make_card(self.t("ua_config"))

        ua_category_layout = QHBoxLayout()
        ua_category_layout.setSpacing(10)
        ua_category_label = QLabel(self.t("ua_category"))
        ua_category_label.setFont(QFont("Arial", 9))
        ua_category_label.setMinimumWidth(160)
        ua_category_label.setStyleSheet("color:#374151;")
        ua_category_layout.addWidget(ua_category_label)
        self.ua_category_combo = QComboBox()
        self.ua_category_combo.addItems(USER_AGENTS.keys())
        self.ua_category_combo.currentTextChanged.connect(self.update_ua_specific)
        self.ua_category_combo.setMinimumHeight(34)
        self.ua_category_combo.setStyleSheet(
            "QComboBox{background:white; border:1px solid #d1d5db; border-radius:8px; padding:6px 10px;}"
            "QComboBox:focus{border:1px solid #60a5fa;}"
        )
        ua_category_layout.addWidget(self.ua_category_combo)
        group_ua_layout.addLayout(ua_category_layout)

        ua_specific_layout = QHBoxLayout()
        ua_specific_layout.setSpacing(10)
        ua_specific_label = QLabel(self.t("ua_specific"))
        ua_specific_label.setFont(QFont("Arial", 9))
        ua_specific_label.setMinimumWidth(160)
        ua_specific_label.setStyleSheet("color:#374151;")
        ua_specific_layout.addWidget(ua_specific_label)
        self.ua_specific_combo = QComboBox()
        self.ua_specific_combo.setMinimumHeight(34)
        self.ua_specific_combo.setStyleSheet(
            "QComboBox{background:white; border:1px solid #d1d5db; border-radius:8px; padding:6px 10px;}"
            "QComboBox:focus{border:1px solid #60a5fa;}"
        )
        self.update_ua_specific()
        ua_specific_layout.addWidget(self.ua_specific_combo)
        group_ua_layout.addLayout(ua_specific_layout)
        chrome_layout.addWidget(ua_group)

        # === PHẦN CẤU HÌNH DELAY ===
        delay_group, group_delay_layout = make_card("⏱️ Cấu hình Delay")

        delay_layout = QHBoxLayout()
        delay_layout.setSpacing(10)
        delay_label = QLabel("⏱️ Thời gian delay (giây):")
        delay_label.setFont(QFont("Arial", 9))
        delay_label.setMinimumWidth(160)
        delay_label.setStyleSheet("color:#374151;")
        delay_layout.addWidget(delay_label)

        self.delay_input = QSpinBox()
        self.delay_input.setMinimum(0)
        self.delay_input.setMaximum(20)
        self.delay_input.setValue(2)
        self.delay_input.setMinimumHeight(34)
        self.delay_input.setMaximumWidth(90)
        self.delay_input.setStyleSheet(
            "QSpinBox{background:white; border:1px solid #d1d5db; border-radius:8px; padding:6px 8px;}"
            "QSpinBox:focus{border:1px solid #60a5fa;}"
        )
        delay_layout.addWidget(self.delay_input)

        delay_desc_label = QLabel("(0 = không delay, 1-20 giây)")
        delay_desc_label.setFont(QFont("Arial", 8))
        delay_desc_label.setStyleSheet("color:#6b7280;")
        delay_layout.addWidget(delay_desc_label)
        delay_layout.addStretch()
        group_delay_layout.addLayout(delay_layout)
        chrome_layout.addWidget(delay_group)

        # === PHẦN CẤU HÌNH CỬA SỔ ===
        window_group, group_window_layout = make_card(self.t("window_config"))

        window_size_layout = QHBoxLayout()
        window_size_layout.setSpacing(10)
        window_size_label = QLabel(self.t("window_size"))
        window_size_label.setFont(QFont("Arial", 9))
        window_size_label.setMinimumWidth(160)
        window_size_label.setStyleSheet("color:#374151;")
        window_size_layout.addWidget(window_size_label)

        self.window_width_input = QSpinBox()
        self.window_width_input.setMinimum(320)
        self.window_width_input.setMaximum(2560)
        self.window_width_input.setValue(375)
        self.window_width_input.setMinimumHeight(34)
        self.window_width_input.setStyleSheet(
            "QSpinBox{background:white; border:1px solid #d1d5db; border-radius:8px; padding:6px 8px;}"
            "QSpinBox:focus{border:1px solid #60a5fa;}"
        )
        window_size_layout.addWidget(self.window_width_input)

        x_label = QLabel("x")
        x_label.setFont(QFont("Arial", 10, QFont.Bold))
        x_label.setStyleSheet("color:#6b7280;")
        window_size_layout.addWidget(x_label)

        self.window_height_input = QSpinBox()
        self.window_height_input.setMinimum(480)
        self.window_height_input.setMaximum(1440)
        self.window_height_input.setValue(667)
        self.window_height_input.setMinimumHeight(34)
        self.window_height_input.setStyleSheet(
            "QSpinBox{background:white; border:1px solid #d1d5db; border-radius:8px; padding:6px 8px;}"
            "QSpinBox:focus{border:1px solid #60a5fa;}"
        )
        window_size_layout.addWidget(self.window_height_input)
        window_size_layout.addStretch()
        group_window_layout.addLayout(window_size_layout)

        profile_layout = QHBoxLayout()
        profile_layout.setSpacing(10)
        profile_label = QLabel("📁 Profile path:")
        profile_label.setFont(QFont("Arial", 9))
        profile_label.setMinimumWidth(160)
        profile_label.setStyleSheet("color:#374151;")
        profile_layout.addWidget(profile_label)
        self.profile_path_input = QLineEdit()
        self.profile_path_input.setPlaceholderText(r"VD: C:\Users\pc\AppData\Local\TSEO_Profiles")
        self.profile_path_input.setStyleSheet(
            "QLineEdit{background:white; border:1px solid #d1d5db; border-radius:8px; padding:6px 8px;}"
            "QLineEdit:focus{border:1px solid #60a5fa;}"
        )
        profile_layout.addWidget(self.profile_path_input)
        self.browse_profile_button = QPushButton("Chọn...")
        self.browse_profile_button.setMinimumHeight(34)
        self.browse_profile_button.clicked.connect(self.select_profile_path)
        profile_layout.addWidget(self.browse_profile_button)
        profile_layout.addStretch()
        group_window_layout.addLayout(profile_layout)

        self.delete_profile_checkbox = QCheckBox("Xóa profile sau khi chạy")
        self.delete_profile_checkbox.setFont(QFont("Arial", 9))
        self.delete_profile_checkbox.setMinimumHeight(26)
        self.delete_profile_checkbox.setStyleSheet("color:#374151;")
        delete_profile_layout = QHBoxLayout()
        delete_profile_layout.setSpacing(10)
        delete_profile_layout.addSpacing(160)
        delete_profile_layout.addWidget(self.delete_profile_checkbox)
        delete_profile_layout.addStretch()
        group_window_layout.addLayout(delete_profile_layout)

        headless_layout = QHBoxLayout()
        headless_layout.setSpacing(10)
        headless_layout.addSpacing(160)
        self.headless_checkbox = QCheckBox(self.t("headless"))
        self.headless_checkbox.setFont(QFont("Arial", 9))
        self.headless_checkbox.setMinimumHeight(26)
        self.headless_checkbox.setStyleSheet("color:#374151;")
        headless_layout.addWidget(self.headless_checkbox)
        headless_layout.addStretch()
        group_window_layout.addLayout(headless_layout)
        chrome_layout.addWidget(window_group)

        # === NÚT LƯU VÀ TẢI CHROME CONFIG ===
        chrome_actions_card = QFrame()
        chrome_actions_card.setStyleSheet("QFrame{background:transparent;}")
        chrome_button_layout = QHBoxLayout(chrome_actions_card)
        chrome_button_layout.setContentsMargins(16, 16, 16, 16)
        chrome_button_layout.setSpacing(10)

        self.save_chrome_button = QPushButton(self.t("save_chrome_btn"))
        self.save_chrome_button.setStyleSheet(
            "QPushButton{background:#2196F3;color:white;font-size:11px;font-weight:700;padding:10px 20px;border-radius:8px;border:none;}"
            "QPushButton:hover{background:#1976D2;}"
            "QPushButton:pressed{background:#0d47a1;}"
        )
        self.save_chrome_button.setMinimumHeight(38)
        self.save_chrome_button.clicked.connect(self.save_chrome_config)
        chrome_button_layout.addWidget(self.save_chrome_button)

        self.reset_chrome_button = QPushButton(self.t("reset_chrome_btn"))
        self.reset_chrome_button.setStyleSheet(
            "QPushButton{background:#f59e0b;color:white;font-size:11px;font-weight:700;padding:10px 20px;border-radius:8px;border:none;}"
            "QPushButton:hover{background:#d97706;}"
            "QPushButton:pressed{background:#b45309;}"
        )
        self.reset_chrome_button.setMinimumHeight(38)
        self.reset_chrome_button.clicked.connect(self.load_chrome_config)
        chrome_button_layout.addWidget(self.reset_chrome_button)

        chrome_button_layout.addStretch()
        chrome_layout.addWidget(chrome_actions_card)

        chrome_layout.addStretch()

        # === TAB LOG ===
        log_tab = QWidget()
        self.tab_widget.addTab(log_tab, self.t("log_tab"))
        log_tab_layout = QVBoxLayout()
        log_tab_layout.setSpacing(15)
        log_tab_layout.setContentsMargins(15, 15, 15, 15)
        log_tab.setLayout(log_tab_layout)

        log_header_card = QFrame()
        log_header_card.setStyleSheet(
            "QFrame{background:#eff6ff; border:1px solid #bfdbfe; border-radius:12px;}"
        )
        log_header_layout = QVBoxLayout(log_header_card)
        log_header_layout.setSpacing(8)
        log_header_layout.setContentsMargins(16, 16, 16, 16)

        log_title_label = QLabel("📋 Nhật ký hoạt động")
        log_title_label.setFont(QFont("Arial", 12, QFont.Bold))
        log_title_label.setStyleSheet("color:#111827; border:none; background:transparent;")
        log_header_layout.addWidget(log_title_label)

        log_desc_label = QLabel("Theo dõi tiến trình chạy job, proxy, kết quả tìm kiếm và các thông báo lỗi tại đây.")
        log_desc_label.setWordWrap(True)
        log_desc_label.setStyleSheet("color:#6b7280; border:none; background:transparent;")
        log_header_layout.addWidget(log_desc_label)

        log_tab_layout.addWidget(log_header_card)

        log_group = QGroupBox(self.t("log_label"))
        log_group.setFont(QFont("Arial", 10, QFont.Bold))
        log_group.setStyleSheet(
            "QGroupBox{color:#111827; border:2px solid #111827; border-radius:12px; margin-top:10px; padding-top:10px; background:#0f172a;}"
            "QGroupBox::title{subcontrol-origin: margin; left: 10px; padding: 0 4px 0 4px; color:#111827; background:#ffffff;}"
        )
        group_log_layout = QVBoxLayout()
        group_log_layout.setContentsMargins(12, 16, 12, 12)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet(
            "QTextEdit{background-color:#020617; color:#22c55e; font-family:Consolas; font-size:12px; border:1px solid #1e293b; border-radius:10px; padding:10px;}"
        )
        group_log_layout.addWidget(self.log_output)

        log_group.setLayout(group_log_layout)
        log_tab_layout.addWidget(log_group)

        log_actions_layout = QHBoxLayout()
        log_actions_layout.addStretch()
        self.clear_log_button = QPushButton("🧹 Xóa log")
        self.clear_log_button.setMinimumHeight(36)
        self.clear_log_button.setStyleSheet(
            "QPushButton{background:#334155;color:white;border:none;border-radius:10px;padding:8px 14px;font-weight:600;}"
            "QPushButton:hover{background:#1e293b;}"
            "QPushButton:pressed{background:#0f172a;}"
        )
        self.clear_log_button.clicked.connect(self.log_output.clear)
        log_actions_layout.addWidget(self.clear_log_button)
        log_tab_layout.addLayout(log_actions_layout)

        # === TAB CHROME BROWSER ===
        chrome_browser_tab = QWidget()
        self.tab_widget.addTab(chrome_browser_tab, self.t("browser_tab"))
        chrome_browser_layout = QVBoxLayout()
        chrome_browser_tab.setLayout(chrome_browser_layout)

        # === PHẦN CHROME BROWSER ===
        chrome_browser_group = QGroupBox(self.t("browser_tab"))
        chrome_browser_group.setFont(QFont("Arial", 10, QFont.Bold))
        group_chrome_browser_layout = QVBoxLayout()

        self.chrome_view = QWebEngineView()
        self.chrome_view.load(QUrl("https://www.google.com"))
        group_chrome_browser_layout.addWidget(self.chrome_view)

        chrome_browser_group.setLayout(group_chrome_browser_layout)
        chrome_browser_layout.addWidget(chrome_browser_group)

        # === TAB NGƯỜI DÙNG ===
        User = QWidget()
        self.user_tab_index = self.tab_widget.addTab(User, self.t("User"))
        user_layout = QVBoxLayout()
        user_layout.setSpacing(15)
        user_layout.setContentsMargins(15, 15, 15, 15)
        User.setLayout(user_layout)

        # === PHẦN NGƯỜI DÙNG ===
        user_group = QGroupBox("👤 " + self.t("User"))
        user_group.setFont(QFont("Arial", 10, QFont.Bold))
        user_group.setStyleSheet(
            """
            QGroupBox {
                color: #333;
                border: 2px solid #9C27B0;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 12px;
                background: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px 0 6px;
            }
        """
        )
        group_user_layout = QVBoxLayout()
        group_user_layout.setSpacing(18)
        group_user_layout.setContentsMargins(18, 18, 18, 18)

        # Thông tin người dùng
        user_info_card = QFrame()
        user_info_card.setStyleSheet(
            "QFrame{background:#faf5ff; border:1px solid #ead7f7; border-radius:12px;}"
        )
        user_info_layout = QVBoxLayout(user_info_card)
        user_info_layout.setSpacing(8)
        user_info_layout.setContentsMargins(16, 16, 16, 16)

        display_name = self.current_user if self.current_user else "User"
        self.user_info_label = QLabel(f"👋 Xin chào, {display_name}!")
        self.user_info_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.user_info_label.setStyleSheet("color: #111827; border:none; background:transparent;")
        user_info_layout.addWidget(self.user_info_label)

        self.user_desc_label = QLabel(
            "Bạn đang đăng nhập và có thể quản lý thông tin tài khoản cũng như sử dụng các tính năng của công cụ."
        )
        self.user_desc_label.setFont(QFont("Arial", 10))
        self.user_desc_label.setStyleSheet("color: #6b7280; border:none; background:transparent;")
        self.user_desc_label.setWordWrap(True)
        user_info_layout.addWidget(self.user_desc_label)

        self.user_role_badge = QLabel(f"Quyền hiện tại: {self.current_user_role}")
        self.user_role_badge.setStyleSheet(
            "color:#6d28d9; background:#ede9fe; border:none; border-radius:10px; padding:6px 10px; font-weight:600;"
        )
        self.user_role_badge.setMaximumWidth(180)
        user_info_layout.addWidget(self.user_role_badge)

        group_user_layout.addWidget(user_info_card)

        # Khu vực thao tác tài khoản
        actions_card = QFrame()
        actions_card.setStyleSheet(
            "QFrame{background:#f9fafb; border:1px solid #e5e7eb; border-radius:12px;}"
        )
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setSpacing(12)
        actions_layout.setContentsMargins(16, 16, 16, 16)

        actions_title = QLabel("Thiết lập tài khoản")
        actions_title.setFont(QFont("Arial", 11, QFont.Bold))
        actions_title.setStyleSheet("color:#111827; border:none; background:transparent;")
        actions_layout.addWidget(actions_title)

        actions_desc = QLabel("Cập nhật mật khẩu hoặc tên đăng nhập của bạn tại đây.")
        actions_desc.setWordWrap(True)
        actions_desc.setStyleSheet("color:#6b7280; border:none; background:transparent;")
        actions_layout.addWidget(actions_desc)

        account_buttons_layout = QHBoxLayout()
        account_buttons_layout.setSpacing(12)

        self.change_password_button = QPushButton(self.t("change_password_btn"))
        self.change_password_button.setStyleSheet(
            "QPushButton{background:#f59e0b;color:white;font-size:11px;font-weight:700;padding:12px 18px;border-radius:10px;border:none;min-width:200px;}"
            "QPushButton:hover{background:#d97706;}"
            "QPushButton:pressed{background:#b45309;}"
        )
        self.change_password_button.setMinimumHeight(42)
        self.change_password_button.clicked.connect(self.change_password)
        account_buttons_layout.addWidget(self.change_password_button)

        self.change_username_button = QPushButton(self.t("change_username_btn"))
        self.change_username_button.setStyleSheet(
            "QPushButton{background:#8b5cf6;color:white;font-size:11px;font-weight:700;padding:12px 18px;border-radius:10px;border:none;min-width:200px;}"
            "QPushButton:hover{background:#7c3aed;}"
            "QPushButton:pressed{background:#6d28d9;}"
        )
        self.change_username_button.setMinimumHeight(42)
        self.change_username_button.clicked.connect(self.change_username)
        account_buttons_layout.addWidget(self.change_username_button)

        actions_layout.addLayout(account_buttons_layout)
        group_user_layout.addWidget(actions_card)

        # Nút đăng xuất
        logout_card = QFrame()
        logout_card.setStyleSheet(
            "QFrame{background:#fff7f7; border:1px solid #fecaca; border-radius:12px;}"
        )
        logout_layout = QVBoxLayout(logout_card)
        logout_layout.setSpacing(10)
        logout_layout.setContentsMargins(16, 16, 16, 16)

        logout_title = QLabel("Phiên đăng nhập")
        logout_title.setFont(QFont("Arial", 11, QFont.Bold))
        logout_title.setStyleSheet("color:#111827; border:none; background:transparent;")
        logout_layout.addWidget(logout_title)

        logout_desc_label = QLabel("Đăng xuất khi bạn muốn quay lại màn hình đăng nhập hoặc đổi tài khoản khác.")
        logout_desc_label.setFont(QFont("Arial", 9))
        logout_desc_label.setStyleSheet("color: #6b7280; border:none; background:transparent;")
        logout_desc_label.setWordWrap(True)
        logout_layout.addWidget(logout_desc_label)

        logout_action_row = QHBoxLayout()
        logout_action_row.addStretch()
        self.logout_button = QPushButton(self.t("logout_btn"))
        self.logout_button.setStyleSheet(
            "QPushButton{background:#ef4444;color:white;font-size:12px;font-weight:700;padding:12px 20px;border-radius:10px;border:none;min-width:170px;}"
            "QPushButton:hover{background:#dc2626;}"
            "QPushButton:pressed{background:#b91c1c;}"
        )
        self.logout_button.setMinimumHeight(44)
        self.logout_button.clicked.connect(self.logout)
        logout_action_row.addWidget(self.logout_button)
        logout_layout.addLayout(logout_action_row)

        group_user_layout.addWidget(logout_card)

        user_group.setLayout(group_user_layout)
        user_layout.addWidget(user_group)

        if self.is_current_admin():
            self._create_admin_management_tab()

        # === TAB QUẢN LÝ CẤU HÌNH ===
        config_manager_tab = QWidget()
        self.config_manager_tab_index = self.tab_widget.addTab(
            config_manager_tab, self.t("config_manager_tab")
        )
        config_manager_layout = QVBoxLayout()
        config_manager_layout.setSpacing(15)
        config_manager_layout.setContentsMargins(15, 15, 15, 15)
        config_manager_tab.setLayout(config_manager_layout)

        config_intro_card = QFrame()
        config_intro_card.setStyleSheet(
            "QFrame{background:#fff7ed; border:1px solid #fed7aa; border-radius:12px;}"
        )
        config_intro_layout = QVBoxLayout(config_intro_card)
        config_intro_layout.setSpacing(8)
        config_intro_layout.setContentsMargins(16, 16, 16, 16)

        self.config_manager_title_label = QLabel("📋 Quản lý cấu hình đã lưu")
        self.config_manager_title_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.config_manager_title_label.setStyleSheet("color:#111827; border:none; background:transparent;")
        config_intro_layout.addWidget(self.config_manager_title_label)

        self.config_manager_desc_label = QLabel(
            "Chọn một cấu hình để xem nhanh thông tin, áp dụng lại vào form, đổi tên hoặc xóa khỏi danh sách."
        )
        self.config_manager_desc_label.setWordWrap(True)
        self.config_manager_desc_label.setStyleSheet("color:#6b7280; border:none; background:transparent;")
        config_intro_layout.addWidget(self.config_manager_desc_label)
        config_manager_layout.addWidget(config_intro_card)

        # === PHẦN DANH SÁCH CẤU HÌNH ===
        config_list_group = QGroupBox(self.t("saved_configs"))
        config_list_group.setFont(QFont("Arial", 10, QFont.Bold))
        config_list_group.setStyleSheet(
            """
            QGroupBox {
                color: #333;
                border: 2px solid #fb923c;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px 0 4px;
            }
        """
        )
        group_config_list_layout = QVBoxLayout()
        group_config_list_layout.setSpacing(12)
        group_config_list_layout.setContentsMargins(14, 14, 14, 14)

        self.config_list_widget = QListWidget()
        self.config_list_widget.setMinimumHeight(320)
        self.config_list_widget.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #e5e7eb;
                border-radius: 10px;
                background-color: #f9fafb;
                padding: 6px;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-bottom: 1px solid #f1f5f9;
                border-radius: 8px;
                margin-bottom: 4px;
            }
            QListWidget::item:selected {
                background-color: #fed7aa;
                color: #9a3412;
            }
            QListWidget::item:hover {
                background-color: #fff7ed;
            }
        """
        )
        self.config_list_widget.itemClicked.connect(self.on_config_selected)
        group_config_list_layout.addWidget(self.config_list_widget)

        info_card = QFrame()
        info_card.setStyleSheet(
            "QFrame{background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;}"
        )
        info_card_layout = QVBoxLayout(info_card)
        info_card_layout.setContentsMargins(14, 14, 14, 14)
        info_card_layout.setSpacing(8)

        self.config_info_title_label = QLabel("Thông tin cấu hình")
        self.config_info_title_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.config_info_title_label.setStyleSheet("color:#111827; border:none; background:transparent;")
        info_card_layout.addWidget(self.config_info_title_label)

        self.config_info_label = QLabel(self.t("no_configs"))
        self.config_info_label.setFont(QFont("Arial", 9))
        self.config_info_label.setStyleSheet("color:#6b7280; font-style:italic; border:none; background:transparent;")
        self.config_info_label.setWordWrap(True)
        info_card_layout.addWidget(self.config_info_label)

        group_config_list_layout.addWidget(info_card)
        config_list_group.setLayout(group_config_list_layout)
        config_manager_layout.addWidget(config_list_group)

        # === NÚT QUẢN LÝ CẤU HÌNH ===
        action_card = QFrame()
        action_card.setStyleSheet(
            "QFrame{background:#f9fafb; border:1px solid #e5e7eb; border-radius:12px;}"
        )
        action_card_layout = QVBoxLayout(action_card)
        action_card_layout.setContentsMargins(16, 16, 16, 16)
        action_card_layout.setSpacing(12)

        action_title = QLabel("Thao tác nhanh")
        action_title.setFont(QFont("Arial", 11, QFont.Bold))
        action_title.setStyleSheet("color:#111827; border:none; background:transparent;")
        action_card_layout.addWidget(action_title)

        action_desc = QLabel("Áp dụng cấu hình vào form hiện tại, đổi tên để dễ nhận biết hoặc xóa cấu hình không còn dùng.")
        action_desc.setWordWrap(True)
        action_desc.setStyleSheet("color:#6b7280; border:none; background:transparent;")
        action_card_layout.addWidget(action_desc)

        config_button_layout = QHBoxLayout()
        config_button_layout.setSpacing(10)

        self.apply_config_button = QPushButton(self.t("apply_config"))
        self.apply_config_button.setStyleSheet(
            "QPushButton{background:#10b981;color:white;font-size:11px;font-weight:700;padding:10px 18px;border-radius:10px;border:none;}"
            "QPushButton:hover{background:#059669;}"
            "QPushButton:pressed{background:#047857;}"
        )
        self.apply_config_button.setMinimumHeight(38)
        self.apply_config_button.clicked.connect(self.apply_selected_config)
        config_button_layout.addWidget(self.apply_config_button)

        self.rename_config_button = QPushButton(self.t("rename_config"))
        self.rename_config_button.setStyleSheet(
            "QPushButton{background:#f59e0b;color:white;font-size:11px;font-weight:700;padding:10px 18px;border-radius:10px;border:none;}"
            "QPushButton:hover{background:#d97706;}"
            "QPushButton:pressed{background:#b45309;}"
        )
        self.rename_config_button.setMinimumHeight(38)
        self.rename_config_button.clicked.connect(self.rename_selected_config)
        config_button_layout.addWidget(self.rename_config_button)

        self.delete_config_button = QPushButton(self.t("delete_config"))
        self.delete_config_button.setStyleSheet(
            "QPushButton{background:#ef4444;color:white;font-size:11px;font-weight:700;padding:10px 18px;border-radius:10px;border:none;}"
            "QPushButton:hover{background:#dc2626;}"
            "QPushButton:pressed{background:#b91c1c;}"
        )
        self.delete_config_button.setMinimumHeight(38)
        self.delete_config_button.clicked.connect(self.delete_selected_config)
        config_button_layout.addWidget(self.delete_config_button)

        config_button_layout.addStretch()
        action_card_layout.addLayout(config_button_layout)
        config_manager_layout.addWidget(action_card)

        config_manager_layout.addStretch()

        # Status bar
        self.statusBar().showMessage(self.t("ready"))

    def _create_admin_management_tab(self):
        """Tạo tab quản trị tài khoản cho admin."""
        admin_tab = QWidget()
        self.admin_tab_index = self.tab_widget.addTab(admin_tab, self.t("admin_tab"))

        admin_layout = QVBoxLayout()
        admin_layout.setSpacing(15)
        admin_layout.setContentsMargins(15, 15, 15, 15)
        admin_tab.setLayout(admin_layout)

        self.admin_group = QGroupBox(self.t("admin_group"))
        self.admin_group.setFont(QFont("Arial", 10, QFont.Bold))
        self.admin_group.setStyleSheet(
            """
            QGroupBox {
                color: #333;
                border: 2px solid #607D8B;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """
        )

        group_layout = QVBoxLayout()
        group_layout.setSpacing(10)

        top_action_layout = QHBoxLayout()
        self.admin_refresh_button = QPushButton(self.t("admin_refresh_users"))
        self.admin_refresh_button.setStyleSheet(
            """
            QPushButton {
                background-color: #607D8B;
                color: white;
                font-size: 10px;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
        """
        )
        self.admin_refresh_button.clicked.connect(self.load_admin_users)
        top_action_layout.addWidget(self.admin_refresh_button)
        top_action_layout.addStretch()
        group_layout.addLayout(top_action_layout)

        self.admin_user_list_label = QLabel(self.t("admin_user_list"))
        self.admin_user_list_label.setFont(QFont("Arial", 9, QFont.Bold))
        group_layout.addWidget(self.admin_user_list_label)

        self.admin_user_list_widget = QListWidget()
        self.admin_user_list_widget.setMinimumHeight(260)
        self.admin_user_list_widget.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #fafafa;
            }
            QListWidget::item {
                padding: 7px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #546E7A;
                color: white;
            }
        """
        )
        self.admin_user_list_widget.itemSelectionChanged.connect(
            self.on_admin_user_selected
        )
        group_layout.addWidget(self.admin_user_list_widget)

        self.admin_selected_user_label = QLabel(self.t("admin_selected_user") + " -")
        self.admin_role_current_label = QLabel(self.t("admin_current_role") + " -")
        group_layout.addWidget(self.admin_selected_user_label)
        group_layout.addWidget(self.admin_role_current_label)

        role_layout = QHBoxLayout()
        self.admin_new_role_label = QLabel(self.t("admin_new_role"))
        role_layout.addWidget(self.admin_new_role_label)

        self.admin_role_combo = QComboBox()
        self.admin_role_combo.addItems(["user", "tester", "admin"])
        role_layout.addWidget(self.admin_role_combo)
        role_layout.addStretch()
        group_layout.addLayout(role_layout)

        admin_button_layout = QHBoxLayout()
        admin_button_layout.setSpacing(10)

        self.admin_update_role_button = QPushButton(self.t("admin_update_role"))
        self.admin_update_role_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2E7D32;
                color: white;
                font-size: 10px;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1B5E20;
            }
        """
        )
        self.admin_update_role_button.clicked.connect(self.admin_update_selected_role)
        admin_button_layout.addWidget(self.admin_update_role_button)

        self.admin_clear_machine_button = QPushButton(self.t("admin_clear_machine"))
        self.admin_clear_machine_button.setStyleSheet(
            """
            QPushButton {
                background-color: #EF6C00;
                color: white;
                font-size: 10px;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #E65100;
            }
        """
        )
        self.admin_clear_machine_button.clicked.connect(self.admin_clear_machine_info)
        admin_button_layout.addWidget(self.admin_clear_machine_button)
        admin_button_layout.addStretch()
        group_layout.addLayout(admin_button_layout)

        self.admin_info_label = QLabel("")
        self.admin_info_label.setWordWrap(True)
        self.admin_info_label.setStyleSheet("color: #666; font-size: 9px;")
        group_layout.addWidget(self.admin_info_label)

        self.admin_group.setLayout(group_layout)
        admin_layout.addWidget(self.admin_group)
        admin_layout.addStretch()

        self.load_admin_users()

    def _get_selected_admin_username(self):
        if not hasattr(self, "admin_user_list_widget"):
            return None
        selected_items = self.admin_user_list_widget.selectedItems()
        if not selected_items:
            return None
        return selected_items[0].data(Qt.UserRole)

    def load_admin_users(self):
        """Tải danh sách người dùng để admin quản lý."""
        if not self.is_current_admin() or not hasattr(self, "admin_user_list_widget"):
            return

        selected_username = self._get_selected_admin_username()

        try:
            users = self.user_manager.list_users()
            users = sorted(users, key=lambda user: user.get("username", "").lower())

            self.admin_users_cache = {}
            self.admin_user_list_widget.clear()

            for user in users:
                username = user.get("username")
                if not username:
                    continue
                role = str(user.get("role", "user")).strip().lower()
                self.admin_users_cache[username] = user

                item = QListWidgetItem(f"[{role}] {username}")
                item.setData(Qt.UserRole, username)
                self.admin_user_list_widget.addItem(item)

                if selected_username and username == selected_username:
                    self.admin_user_list_widget.setCurrentItem(item)

            if not selected_username or self.admin_user_list_widget.currentItem() is None:
                self.on_admin_user_selected()

        except Exception as exc:
            QMessageBox.warning(
                self,
                self.t("warning"),
                self.t("admin_load_failed").format(str(exc)),
            )

    def on_admin_user_selected(self):
        """Hiển thị chi tiết tài khoản được chọn trong tab admin."""
        if not hasattr(self, "admin_user_list_widget"):
            return

        username = self._get_selected_admin_username()
        if not username:
            self.admin_selected_user_label.setText(self.t("admin_selected_user") + " -")
            self.admin_role_current_label.setText(self.t("admin_current_role") + " -")
            self.admin_info_label.setText("")
            return

        user = self.admin_users_cache.get(username, {})
        role = str(user.get("role", "user")).strip().lower()

        if role in ["user", "tester", "admin"]:
            self.admin_role_combo.setCurrentText(role)

        expired_at = user.get("expired_at")
        if expired_at is None:
            expired_text = self.t("admin_expired_none")
        elif isinstance(expired_at, str):
            expired_text = expired_at
        else:
            expired_text = str(expired_at)

        has_machine_info = bool(user.get("machine_info"))
        machine_text = (
            self.t("admin_machine_exists")
            if has_machine_info
            else self.t("admin_machine_missing")
        )

        self.admin_selected_user_label.setText(f"{self.t('admin_selected_user')} {username}")
        self.admin_role_current_label.setText(f"{self.t('admin_current_role')} {role}")
        self.admin_info_label.setText(
            self.t("admin_user_info").format(username, role, expired_text, machine_text)
        )

    def admin_update_selected_role(self):
        """Admin cập nhật role cho tài khoản được chọn."""
        if not self.is_current_admin():
            return

        username = self._get_selected_admin_username()
        if not username:
            QMessageBox.warning(self, self.t("warning"), self.t("admin_no_user_selected"))
            return

        new_role = self.admin_role_combo.currentText()

        if username == self.current_user and new_role != "admin":
            QMessageBox.warning(self, self.t("warning"), self.t("admin_cannot_manage_self"))
            return

        ok, message = self.user_manager.set_role(username, new_role, self.current_user)
        if not ok:
            QMessageBox.warning(self, self.t("warning"), message)
            return

        QMessageBox.information(
            self,
            self.t("success"),
            self.t("admin_update_role_success").format(username),
        )
        self.log(f"🛡️ {message} ({username} -> {new_role})")
        self.load_admin_users()

    def admin_clear_machine_info(self):
        """Admin xóa machine_info cho tài khoản được chọn."""
        if not self.is_current_admin():
            return

        username = self._get_selected_admin_username()
        if not username:
            QMessageBox.warning(self, self.t("warning"), self.t("admin_no_user_selected"))
            return

        self.user_manager.users.update_one(
            {"username": username}, {"$unset": {"machine_info": ""}}
        )
        QMessageBox.information(
            self,
            self.t("success"),
            self.t("admin_clear_machine_success").format(username),
        )
        self.log(f"🧹 Cleared machine_info for user {username}")
        self.load_admin_users()

    def _job_count_in_grid(self):
        return self.jobs_grid_layout.count()

    def _job_item_at(self, index):
        item = self.jobs_grid_layout.itemAt(index)
        return item.widget() if item else None

    def _reflow_job_cards(self):
        for i in reversed(range(self.jobs_grid_layout.count())):
            widget = self.jobs_grid_layout.itemAt(i).widget()
            self.jobs_grid_layout.removeWidget(widget)
            widget.setParent(None)
        for index, card in enumerate(self.job_cards):
            row = index // 2
            col = index % 2
            self.jobs_grid_layout.addWidget(card["frame"], row, col)

    def _create_job_style(self, border_color):
        return """
            QFrame {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
        """

    def add_job_card(self):
        job_index = len(self.job_cards) + 1
        card_frame = QFrame()
        card_frame.setObjectName(f"jobCard{job_index}")
        card_frame.setStyleSheet(self._create_job_style("#d1d5db"))
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Công việc")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color:#111827;")
        header.addWidget(title)
        header.addStretch()
        status = QLabel("⚪ Chờ chạy")
        status.setStyleSheet("padding: 4px 10px; background:#f3f4f6; border-radius:10px; color:#6b7280; font-weight:600;")
        header.addWidget(status)
        delete_btn = QPushButton("❌")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setStyleSheet("QPushButton{border:1px solid #e5e7eb; background:#fff; border-radius:8px;} QPushButton:hover{background:#f9fafb;}")
        delete_btn.clicked.connect(lambda _, f=card_frame: self.remove_job_card(f))
        header.addWidget(delete_btn)
        card_layout.addLayout(header)
        card_layout.addSpacing(6)

        def section(title_text, accent=None):
            box = QFrame()
            box.setStyleSheet(
                "QFrame{border:1px solid #e5e7eb; border-radius:10px; background:#f9fafb;}"
            )
            layout = QVBoxLayout(box)
            layout.setContentsMargins(14, 14, 14, 14)
            layout.setSpacing(12)
            label = QLabel(title_text)
            label.setFont(QFont("Arial", 10, QFont.DemiBold))
            label.setStyleSheet("color:#111827; border:none; background:transparent;")
            layout.addWidget(label)
            return box, layout

        sheets_box, sheets_layout = section("📊 Google Sheets")
        sheet_label = QLabel(self.t("sheet_id"))
        sheet_label.setStyleSheet("color:#374151; font-weight:600;")
        sheet_input = QLineEdit(); sheet_input.setPlaceholderText("Sheet ID")
        sheet_input.setStyleSheet("QLineEdit{border:1px solid #e5e7eb; border-radius:8px; padding:8px 10px;} QLineEdit:focus{border:1px solid #cbd5e1;}")
        open_sheet_btn = QPushButton(self.t("open_sheet_btn"))
        open_sheet_btn.setEnabled(False)
        open_sheet_btn.setStyleSheet("QPushButton{background:#6366f1;color:white;border:none;border-radius:8px;padding:8px 12px;font-weight:600;} QPushButton:hover{background:#4f46e5;} QPushButton:pressed{background:#4338ca;} QPushButton:disabled{background:#d1d5db;color:#6b7280;}")
        sheet_row = QHBoxLayout(); sheet_row.setSpacing(10)
        sheet_row.addWidget(sheet_input, 1); sheet_row.addWidget(open_sheet_btn)
        cred_label = QLabel(self.t("not_found"))
        cred_label.setStyleSheet("color:#6b7280;")
        cred_btn = QPushButton("Chọn")
        cred_btn.setStyleSheet("QPushButton{border:1px solid #e5e7eb; background:#fff; border-radius:8px; padding:8px 12px;} QPushButton:hover{background:#f9fafb;}")
        cred_row = QHBoxLayout(); cred_row.setSpacing(10)
        cred_row.addWidget(cred_label, 1); cred_row.addWidget(cred_btn)
        sheets_layout.addWidget(sheet_label); sheets_layout.addLayout(sheet_row); sheets_layout.addLayout(cred_row)
        card_layout.addWidget(sheets_box)

        search_box, search_layout = section("🔍 Cấu hình Tìm kiếm")
        grid = QGridLayout(); grid.setHorizontalSpacing(10); grid.setVerticalSpacing(10)
        pages = QSpinBox(); pages.setMinimum(1); pages.setMaximum(20); pages.setValue(3)
        pages.setStyleSheet("QSpinBox{border:1px solid #e5e7eb; border-radius:8px; padding:6px 8px;} QSpinBox:focus{border:1px solid #cbd5e1;}")
        threads = QSpinBox(); threads.setMinimum(1); threads.setMaximum(10); threads.setValue(5)
        threads.setStyleSheet("QSpinBox{border:1px solid #e5e7eb; border-radius:8px; padding:6px 8px;} QSpinBox:focus{border:1px solid #cbd5e1;}")
        domain = QLineEdit(); domain.setPlaceholderText(self.t("domain_placeholder"))
        domain.setStyleSheet("QLineEdit{border:1px solid #e5e7eb; border-radius:8px; padding:8px 10px;} QLineEdit:focus{border:1px solid #cbd5e1;}")
        grid.addWidget(QLabel(self.t("pages")), 0, 0); grid.addWidget(pages, 0, 1)
        grid.addWidget(QLabel(self.t("threads")), 0, 2); grid.addWidget(threads, 0, 3)
        grid.addWidget(QLabel(self.t("domain")), 1, 0); grid.addWidget(domain, 1, 1, 1, 3)
        search_layout.addLayout(grid)
        card_layout.addWidget(search_box)

        keyword_box, keyword_layout = section("🔑 Danh sách từ khóa")
        keywords = PlainTextEdit(); keywords.setPlaceholderText(self.t("keywords_placeholder"))
        keywords.setStyleSheet("QPlainTextEdit{border:1px solid #e5e7eb; border-radius:8px; padding:8px 10px; background:#fff;} QPlainTextEdit:focus{border:1px solid #cbd5e1;}")
        keyword_counter = QLabel(self.t("keywords_count").format(0))
        keyword_counter.setStyleSheet("color:#6b7280; font-size:12px;")
        keyword_layout.addWidget(keywords); keyword_layout.addWidget(keyword_counter)
        card_layout.addWidget(keyword_box)

        job_actions = QHBoxLayout()
        job_actions.setSpacing(10)
        start_btn = QPushButton("▶ Bắt đầu")
        start_btn.setStyleSheet("QPushButton{border:none; background:#2563eb; color:#fff; border-radius:10px; padding:10px 14px; font-weight:600;} QPushButton:hover{background:#1d4ed8;} QPushButton:disabled{background:#d1d5db; color:#6b7280;}")
        job_actions.addWidget(start_btn)
        job_actions.addStretch()
        card_layout.addLayout(job_actions)

        onsite_interaction_box, onsite_interaction_layout = section("🖱️ Tương tác trên site")
        onsite_interaction_layout.setSpacing(10)
        enabled_row = QHBoxLayout(); enabled_row.setSpacing(10)
        enable_onsite_interaction_checkbox = QCheckBox("Bật tương tác trên site")
        enable_onsite_interaction_checkbox.setStyleSheet("color:#374151;")
        enabled_row.addWidget(enable_onsite_interaction_checkbox)
        enabled_row.addStretch()
        onsite_interaction_layout.addLayout(enabled_row)

        range_row = QHBoxLayout(); range_row.setSpacing(10)
        range_label = QLabel("Thời gian ở lại trên site (s)")
        range_label.setStyleSheet("color:#374151; font-weight:600;")
        onsite_time_min_input = QSpinBox()
        onsite_time_min_input.setMinimum(1)
        onsite_time_min_input.setMaximum(9999)
        onsite_time_min_input.setValue(40)
        onsite_time_min_input.setStyleSheet("QSpinBox{border:1px solid #e5e7eb; border-radius:8px; padding:6px 8px;} QSpinBox:focus{border:1px solid #cbd5e1;}")
        onsite_time_max_input = QSpinBox()
        onsite_time_max_input.setMinimum(1)
        onsite_time_max_input.setMaximum(9999)
        onsite_time_max_input.setValue(60)
        onsite_time_max_input.setStyleSheet("QSpinBox{border:1px solid #e5e7eb; border-radius:8px; padding:6px 8px;} QSpinBox:focus{border:1px solid #cbd5e1;}")
        onsite_dash_label = QLabel("-")
        range_row.addWidget(range_label)
        range_row.addWidget(onsite_time_min_input)
        range_row.addWidget(onsite_dash_label)
        range_row.addWidget(onsite_time_max_input)
        onsite_interaction_layout.addLayout(range_row)

        def _toggle_onsite_local():
            enabled = enable_onsite_interaction_checkbox.isChecked()
            range_label.setEnabled(enabled)
            onsite_dash_label.setEnabled(enabled)
            onsite_time_min_input.setEnabled(enabled)
            onsite_time_max_input.setEnabled(enabled)

        enable_onsite_interaction_checkbox.stateChanged.connect(_toggle_onsite_local)
        enable_onsite_interaction_checkbox.setChecked(True)
        _toggle_onsite_local()

        extra_click_row = QHBoxLayout(); extra_click_row.setSpacing(10)
        enable_extra_clicks_checkbox = QCheckBox("Bật click thêm trên website")
        enable_extra_clicks_checkbox.setStyleSheet("color:#374151;")
        extra_click_row.addWidget(enable_extra_clicks_checkbox)
        extra_click_row.addStretch()
        onsite_interaction_layout.addLayout(extra_click_row)

        extra_click_count_row = QHBoxLayout(); extra_click_count_row.setSpacing(10)
        extra_click_count_label = QLabel("Số lần click thêm trên website")
        extra_click_count_label.setStyleSheet("color:#374151; font-weight:600;")
        extra_click_min_input = QSpinBox()
        extra_click_min_input.setMinimum(0)
        extra_click_min_input.setMaximum(50)
        extra_click_min_input.setValue(1)
        extra_click_min_input.setStyleSheet("QSpinBox{border:1px solid #e5e7eb; border-radius:8px; padding:6px 8px;} QSpinBox:focus{border:1px solid #cbd5e1;}")
        extra_click_dash_label = QLabel("-")
        extra_click_max_input = QSpinBox()
        extra_click_max_input.setMinimum(0)
        extra_click_max_input.setMaximum(50)
        extra_click_max_input.setValue(3)
        extra_click_max_input.setStyleSheet("QSpinBox{border:1px solid #e5e7eb; border-radius:8px; padding:6px 8px;} QSpinBox:focus{border:1px solid #cbd5e1;}")
        extra_click_count_row.addWidget(extra_click_count_label)
        extra_click_count_row.addWidget(extra_click_min_input)
        extra_click_count_row.addWidget(extra_click_dash_label)
        extra_click_count_row.addWidget(extra_click_max_input)
        extra_click_count_row.addStretch()
        onsite_interaction_layout.addLayout(extra_click_count_row)

        def _toggle_extra_click_local():
            enabled = enable_extra_clicks_checkbox.isChecked()
            extra_click_count_label.setEnabled(enabled)
            extra_click_dash_label.setEnabled(enabled)
            extra_click_min_input.setEnabled(enabled)
            extra_click_max_input.setEnabled(enabled)

        enable_extra_clicks_checkbox.stateChanged.connect(_toggle_extra_click_local)
        enable_extra_clicks_checkbox.setChecked(False)
        _toggle_extra_click_local()

        card_layout.addWidget(onsite_interaction_box)

        card_data = {
            "frame": card_frame, "status": status, "start_btn": start_btn,
            "sheet_id": sheet_input, "open_sheet_btn": open_sheet_btn,
            "credentials_label": cred_label, "credentials_btn": cred_btn,
            "pages": pages, "threads": threads, "domain": domain, "keywords": keywords,
            "keyword_counter": keyword_counter, "credentials_file": self.credentials_file,
            "enable_onsite_interaction": enable_onsite_interaction_checkbox,
            "onsite_time_min": onsite_time_min_input,
            "onsite_time_max": onsite_time_max_input,
            "enable_extra_clicks": enable_extra_clicks_checkbox,
            "extra_click_min": extra_click_min_input,
            "extra_click_max": extra_click_max_input,
        }
        cred_btn.clicked.connect(lambda: self.select_job_credentials(card_data))
        open_sheet_btn.clicked.connect(lambda: self.open_google_sheet_for_card(card_data))
        keywords.textChanged.connect(lambda: self.update_job_keyword_counter(card_data))
        sheet_input.textChanged.connect(lambda: self.update_job_start_state(card_data))
        sheet_input.textChanged.connect(lambda: self.update_job_sheet_button_state(card_data))
        keywords.textChanged.connect(lambda: self.update_job_start_state(card_data))
        domain.textChanged.connect(lambda: self.update_job_start_state(card_data))
        start_btn.clicked.connect(lambda: self.start_job_card(card_data))
        self.job_cards.append(card_data)
        self._reflow_job_cards()
        self.update_job_start_state(card_data)
        self.update_job_sheet_button_state(card_data)
        if len(self.job_cards) == 1:
            self._bind_first_job_aliases(card_data)
        return card_data

    def _bind_first_job_aliases(self, card):
        self.sheet_id_input = card["sheet_id"]
        self.num_pages_input = card["pages"]
        self.max_threads_input = card["threads"]
        self.domain_input = card["domain"]
        self.keywords_input = card["keywords"]
        self.credentials_label = card["credentials_label"]
        self.select_credentials_button = card["credentials_btn"]

    def remove_job_card(self, frame):
        self.job_cards = [c for c in self.job_cards if c["frame"] != frame]
        frame.deleteLater()
        self._reflow_job_cards()

    def select_job_credentials(self, card):
        file_path, _ = QFileDialog.getOpenFileName(self, self.t("select_credentials"), "", self.t("json_files"))
        if file_path:
            card["credentials_file"] = file_path
            card["credentials_label"].setText(os.path.basename(file_path))

    def update_job_keyword_counter(self, card):
        keywords = [k.strip() for k in card["keywords"].toPlainText().splitlines() if k.strip()]
        card["keyword_counter"].setText(self.t("keywords_count").format(len(keywords)))

    def update_job_sheet_button_state(self, card):
        sheet_id = card["sheet_id"].text().strip()
        if "open_sheet_btn" in card:
            card["open_sheet_btn"].setEnabled(bool(sheet_id))

    def update_job_start_state(self, card):
        has_sheet = bool(card["sheet_id"].text().strip())
        has_keywords = bool(card["keywords"].toPlainText().strip())
        has_credentials = bool(card.get("credentials_file"))
        ready = has_sheet and has_keywords and has_credentials
        if "start_btn" in card:
            card["start_btn"].setEnabled(ready)
        if ready:
            card["status"].setText("🟡 Sẵn sàng")
            card["status"].setStyleSheet("padding: 4px 10px; background:#fef3c7; border-radius:10px; color:#92400e; font-weight:600;")
        else:
            card["status"].setText("⚪ Chờ chạy")
            card["status"].setStyleSheet("padding: 4px 10px; background:#f3f4f6; border-radius:10px; color:#6b7280; font-weight:600;")

    def collect_job_config(self, card):
        return {
            "sheet_id": card["sheet_id"].text(),
            "num_pages": card["pages"].value(),
            "target_domain": card["domain"].text(),
            "max_threads": card["threads"].value(),
            "keywords": card["keywords"].toPlainText(),
            "ua_category": self.ua_category_combo.currentText(),
            "ua_specific": self.ua_specific_combo.currentText(),
            "window_width": self.window_width_input.value(),
            "window_height": self.window_height_input.value(),
            "headless": self.headless_checkbox.isChecked(),
            "delay_seconds": self.delay_input.value(),
            "proxy_enabled": self.enable_proxy_checkbox.isChecked(),
            "proxy_type": self.proxy_type_combo.currentText(),
            "proxy_list": [
                line.strip()
                for line in self.proxy_list_input.toPlainText().split("\n")
                if line.strip()
            ],
            "onsite_interaction_enabled": card["enable_onsite_interaction"].isChecked(),
            "onsite_time_range": f"{card['onsite_time_min'].value()}-{card['onsite_time_max'].value()}",
            "extra_clicks_enabled": card["enable_extra_clicks"].isChecked(),
            "extra_click_range": f"{card['extra_click_min'].value()}-{card['extra_click_max'].value()}",
            "profile_path": self.profile_path_input.text().strip(),
            "delete_profile": self.delete_profile_checkbox.isChecked(),
        }

    def start_job_card(self, card):
        if not card.get("credentials_file"):
            QMessageBox.warning(self, self.t("warning"), self.t("error_credentials"))
            return
        profile_path = self.profile_path_input.text().strip()
        if not profile_path:
            QMessageBox.warning(self, self.t("warning"), "Vui lòng chọn thư mục profile trước khi chạy job này")
            return
        if card.get("thread") and card["thread"].isRunning():
            return

        config = self.collect_job_config(card)
        thread = SearchThread(config, card["credentials_file"])
        thread.log_signal.connect(self.log)
        thread.progress_signal.connect(self.update_progress)
        thread.finished_signal.connect(
            lambda success, message, c=card, t=thread: self.job_card_finished(c, t, success, message)
        )

        self.search_threads.append(thread)
        card["thread"] = thread
        card["status"].setText("🟢 Đang chạy")
        card["status"].setStyleSheet("padding: 4px 10px; background:#ecfdf5; border-radius:10px; color:#166534; font-weight:600;")
        thread.start()
        self.run_all_jobs_button.setEnabled(True)

    def log(self, message):
        """Thêm log vào output"""
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def select_credentials(self):
        """Chọn file credentials"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.t("select_credentials"), "", self.t("json_files")
        )
        if file_path:
            self.credentials_file = file_path
            self.log(
                f"✅ "
                + self.t("selected_credentials").format(os.path.basename(file_path))
            )
            self.statusBar().showMessage(
                self.t("selected_credentials").format(os.path.basename(file_path))
            )

    def save_config(self):
        """Lưu cấu hình - Merge với config cũ và thêm vào danh sách"""
        # Hỏi tên cho cấu hình
        config_name, ok = QInputDialog.getText(
            self, self.t("config_name"), "Nhập tên cho cấu hình này:"
        )

        if not ok or not config_name.strip():
            return

        config_name = config_name.strip()

        # Kiểm tra xem tên có bị trùng không
        configs = {}
        if os.path.exists(self.configs_list_file):
            try:
                with open(self.configs_list_file, "r", encoding="utf-8") as f:
                    configs = json.load(f)
            except:
                pass

        if config_name in configs:
            reply = QMessageBox.question(
                self,
                self.t("warning"),
                f"Cấu hình '{config_name}' đã tồn tại. Bạn có muốn ghi đè?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        # Tải config cũ nếu có
        old_config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    old_config = json.load(f)
            except:
                pass

        jobs_payload = []
        for card in self.job_cards:
            jobs_payload.append(
                {
                    "sheet_id": card["sheet_id"].text(),
                    "num_pages": card["pages"].value(),
                    "target_domain": card["domain"].text(),
                    "max_threads": card["threads"].value(),
                    "keywords": card["keywords"].toPlainText(),
                    "credentials_file": card.get("credentials_file", ""),
                    "onsite_interaction_enabled": card["enable_onsite_interaction"].isChecked(),
                    "onsite_time_range": f"{card['onsite_time_min'].value()}-{card['onsite_time_max'].value()}",
                    "extra_clicks_enabled": card["enable_extra_clicks"].isChecked(),
                    "extra_click_range": f"{card['extra_click_min'].value()}-{card['extra_click_max'].value()}",
                }
            )

        main_sheet_id = self.sheet_id_input.text() if hasattr(self, "sheet_id_input") else ""
        main_num_pages = self.num_pages_input.value() if hasattr(self, "num_pages_input") else 3
        main_target_domain = self.domain_input.text() if hasattr(self, "domain_input") else ""
        main_max_threads = self.max_threads_input.value() if hasattr(self, "max_threads_input") else 5
        main_keywords = self.keywords_input.toPlainText() if hasattr(self, "keywords_input") else ""

        # Tạo config mới - merge với config cũ
        new_config = old_config.copy()  # Giữ những thông tin cũ
        new_config.update(
            {
                "sheet_id": main_sheet_id,
                "num_pages": main_num_pages,
                "target_domain": main_target_domain,
                "max_threads": main_max_threads,
                "keywords": main_keywords,
                "credentials_file": self.credentials_file,
                "jobs": jobs_payload,
            }
        )

        try:
            # Lưu vào file cấu hình chính
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(new_config, f, ensure_ascii=False, indent=2)

            # Thêm vào danh sách cấu hình
            configs[config_name] = {
                "sheet_id": main_sheet_id,
                "num_pages": main_num_pages,
                "target_domain": main_target_domain,
                "max_threads": main_max_threads,
                "keywords": main_keywords,
                "credentials_file": self.credentials_file,
                "jobs": jobs_payload,
                "ua_category": self.ua_category_combo.currentText(),
                "ua_specific": self.ua_specific_combo.currentText(),
                "window_width": self.window_width_input.value(),
                "window_height": self.window_height_input.value(),
                "headless": self.headless_checkbox.isChecked(),
                "profile_path": self.profile_path_input.text().strip(),
                "delete_profile": self.delete_profile_checkbox.isChecked(),
                "delay_seconds": self.delay_input.value(),
                "proxy_enabled": self.enable_proxy_checkbox.isChecked(),
                "proxy_type": self.proxy_type_combo.currentText(),
                "proxy_list": [
                    line.strip()
                    for line in self.proxy_list_input.toPlainText().split("\n")
                    if line.strip()
                ],
                "timestamp": datetime.now().isoformat(),
            }

            # Lưu danh sách cấu hình
            with open(self.configs_list_file, "w", encoding="utf-8") as f:
                json.dump(configs, f, ensure_ascii=False, indent=2)

            QMessageBox.information(self, self.t("success"), self.t("saved_config"))
            self.log("💾 " + self.t("saved_config") + f" - {config_name}")

            # Tải lại danh sách cấu hình
            self.load_configs_list()
        except Exception as e:
            QMessageBox.critical(
                self, self.t("error"), self.t("error_save").format(str(e))
            )

    def edit_current_config(self):
        """Sửa cấu hình hiện tại - Cập nhật thông tin cấu hình đã lưu"""
        # Kiểm tra xem đã chọn cấu hình nào chưa
        if not self.selected_config_name:
            QMessageBox.warning(
                self,
                self.t("warning"),
                "Vui lòng chọn một cấu hình để sửa từ danh sách bên tab 'Quản lý Cấu hình'",
            )
            return

        # Hiển thị dialog xác nhận
        reply = QMessageBox.question(
            self,
            "Xác nhận sửa cấu hình",
            f"Bạn có muốn cập nhật cấu hình '{self.selected_config_name}' với thông tin hiện tại không?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        try:
            # Tải danh sách cấu hình
            configs = {}
            if os.path.exists(self.configs_list_file):
                try:
                    with open(self.configs_list_file, "r", encoding="utf-8") as f:
                        configs = json.load(f)
                except:
                    pass

            if self.selected_config_name not in configs:
                QMessageBox.warning(self, self.t("warning"), "Cấu hình không tồn tại")
                return

            jobs_payload = []
            for card in self.job_cards:
                jobs_payload.append(
                    {
                        "sheet_id": card["sheet_id"].text(),
                        "num_pages": card["pages"].value(),
                        "target_domain": card["domain"].text(),
                        "max_threads": card["threads"].value(),
                        "keywords": card["keywords"].toPlainText(),
                        "credentials_file": card.get("credentials_file", ""),
                        "onsite_interaction_enabled": card["enable_onsite_interaction"].isChecked(),
                        "onsite_time_range": f"{card['onsite_time_min'].value()}-{card['onsite_time_max'].value()}",
                        "extra_clicks_enabled": card["enable_extra_clicks"].isChecked(),
                        "extra_click_range": f"{card['extra_click_min'].value()}-{card['extra_click_max'].value()}",
                    }
                )

            main_sheet_id = self.sheet_id_input.text() if hasattr(self, "sheet_id_input") else ""
            main_num_pages = self.num_pages_input.value() if hasattr(self, "num_pages_input") else 3
            main_target_domain = self.domain_input.text() if hasattr(self, "domain_input") else ""
            main_max_threads = self.max_threads_input.value() if hasattr(self, "max_threads_input") else 5
            main_keywords = self.keywords_input.toPlainText() if hasattr(self, "keywords_input") else ""

            # Cập nhật cấu hình với thông tin hiện tại từ form
            configs[self.selected_config_name] = {
                "sheet_id": main_sheet_id,
                "num_pages": main_num_pages,
                "target_domain": main_target_domain,
                "max_threads": main_max_threads,
                "keywords": main_keywords,
                "credentials_file": self.credentials_file,
                "jobs": jobs_payload,
                "ua_category": self.ua_category_combo.currentText(),
                "ua_specific": self.ua_specific_combo.currentText(),
                "window_width": self.window_width_input.value(),
                "window_height": self.window_height_input.value(),
                "headless": self.headless_checkbox.isChecked(),
                "profile_path": self.profile_path_input.text().strip(),
                "delete_profile": self.delete_profile_checkbox.isChecked(),
                "delay_seconds": self.delay_input.value(),
                "proxy_enabled": self.enable_proxy_checkbox.isChecked(),
                "proxy_type": self.proxy_type_combo.currentText(),
                "proxy_list": [
                    line.strip()
                    for line in self.proxy_list_input.toPlainText().split("\n")
                    if line.strip()
                ],
                "timestamp": datetime.now().isoformat(),
            }

            # Lưu danh sách cấu hình
            with open(self.configs_list_file, "w", encoding="utf-8") as f:
                json.dump(configs, f, ensure_ascii=False, indent=2)

            QMessageBox.information(
                self,
                "Thành công",
                f"Đã cập nhật cấu hình '{self.selected_config_name}'!",
            )
            self.log(f"✏️ Đã cập nhật cấu hình - {self.selected_config_name}")

            # Tải lại danh sách cấu hình
            self.load_configs_list()

        except Exception as e:
            QMessageBox.critical(
                self, self.t("error"), f"Không thể cập nhật cấu hình: {str(e)}"
            )
            self.log(f"❌ Lỗi khi cập nhật cấu hình: {str(e)}")


    def start_search(self):
        """Bắt đầu tìm kiếm"""
        # Validate
        if not self.sheet_id_input.text():
            QMessageBox.warning(self, self.t("warning"), self.t("error_sheet"))
            return

        if not self.keywords_input.toPlainText().strip():
            QMessageBox.warning(self, self.t("warning"), self.t("error_keywords"))
            return

        if not os.path.exists(self.credentials_file):
            QMessageBox.warning(self, self.t("warning"), self.t("error_credentials"))
            return

        if not self.profile_path_input.text().strip():
            QMessageBox.warning(self, self.t("warning"), "Vui lòng chọn thư mục profile trước khi chạy")
            return

        # Giữ lại cách chạy global cũ cho form chính
        config = {
            "sheet_id": self.sheet_id_input.text(),
            "num_pages": self.num_pages_input.value(),
            "target_domain": self.domain_input.text(),
            "max_threads": self.max_threads_input.value(),
            "keywords": self.keywords_input.toPlainText(),
            "ua_category": self.ua_category_combo.currentText(),
            "ua_specific": self.ua_specific_combo.currentText(),
            "window_width": self.window_width_input.value(),
            "window_height": self.window_height_input.value(),
            "headless": self.headless_checkbox.isChecked(),
            "delay_seconds": self.delay_input.value(),
            "proxy_enabled": self.enable_proxy_checkbox.isChecked(),
            "proxy_type": self.proxy_type_combo.currentText(),
            "proxy_list": [
                line.strip()
                for line in self.proxy_list_input.toPlainText().split("\n")
                if line.strip()
            ],
            "profile_path": self.profile_path_input.text().strip(),
            "delete_profile": self.delete_profile_checkbox.isChecked(),
            "onsite_interaction_enabled": False,
            "onsite_time_range": "40-60",
        }

        self.search_thread = SearchThread(config, self.credentials_file)
        self.search_thread.log_signal.connect(self.log)
        self.search_thread.progress_signal.connect(self.update_progress)
        self.search_thread.finished_signal.connect(self.search_finished)

        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.statusBar().showMessage(self.t("searching"))

        self.search_thread.start()

    def job_card_finished(self, card, thread, success, message):
        if thread in self.search_threads:
            self.search_threads.remove(thread)
        if card.get("thread") is thread:
            card["thread"] = None

        if success:
            card["status"].setText("✅ Hoàn thành")
            card["status"].setStyleSheet("padding: 4px 10px; background:#dcfce7; border-radius:10px; color:#166534; font-weight:600;")
        else:
            card["status"].setText("❌ Lỗi")
            card["status"].setStyleSheet("padding: 4px 10px; background:#fee2e2; border-radius:10px; color:#991b1b; font-weight:600;")

        self.log(message)
        self._update_running_job_ui_state()

    def run_all_jobs(self):
        if not self.job_cards:
            return
        started_any = False
        for card in self.job_cards:
            if card.get("thread") and card["thread"].isRunning():
                continue
            if not card.get("credentials_file"):
                continue
            if not card["sheet_id"].text().strip() or not card["keywords"].toPlainText().strip():
                continue
            self.start_job_card(card)
            started_any = True
        if not started_any:
            QMessageBox.warning(self, self.t("warning"), "Không có job nào đủ điều kiện để chạy.")
        else:
            self.stop_button.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.statusBar().showMessage(self.t("searching"))

    def _update_running_job_ui_state(self):
        any_job_running = any(
            card.get("thread") and card["thread"].isRunning() for card in self.job_cards
        )
        global_running = bool(self.search_thread and self.search_thread.isRunning())
        any_running = any_job_running or global_running

        self.stop_button.setEnabled(any_running)
        if any_running:
            self.progress_bar.setVisible(True)
            self.statusBar().showMessage(self.t("searching"))
        else:
            self.progress_bar.setVisible(False)
            self.statusBar().showMessage(self.t("ready"))

    def stop_search(self):
        """Dừng tìm kiếm"""
        reply = QMessageBox.question(
            self,
            self.t("confirm_stop"),
            self.t("confirm_stop_msg"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.log("⏸ Đang dừng tìm kiếm...")
            if self.search_thread and self.search_thread.isRunning():
                self.search_thread.stop()
            for thread in list(self.search_threads):
                try:
                    if thread.isRunning():
                        thread.stop()
                except Exception:
                    pass
            self.stop_button.setEnabled(False)
            self.statusBar().showMessage("Đã dừng")

    def update_progress(self, current, total):
        """Cập nhật progress bar"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def search_finished(self, success, message):
        """Xử lý khi tìm kiếm xong"""
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)

        # Đảm bảo thread được giải phóng
        if self.search_thread:
            self.search_thread.wait()
            self.search_thread = None

        if success:
            QMessageBox.information(self, self.t("success"), message)
            self.open_sheet_button.setEnabled(True)
        else:
            QMessageBox.warning(self, self.t("error"), message)

        self._update_running_job_ui_state()

        self._update_running_job_ui_state()

    def update_keyword_counter(self):
        """Cập nhật số lượng từ khóa"""
        text = self.keywords_input.toPlainText()
        keywords = [k.strip() for k in text.split("\n") if k.strip()]
        self.keyword_counter_label.setText(
            self.t("keywords_count").format(len(keywords))
        )

    def update_ua_specific(self):
        """Cập nhật danh sách User-Agent cụ thể dựa trên danh mục đã chọn"""
        category = self.ua_category_combo.currentText()
        self.ua_specific_combo.clear()
        if category in USER_AGENTS:
            self.ua_specific_combo.addItems(USER_AGENTS[category])

    def update_sheet_button_state(self):
        """Cập nhật trạng thái nút Mở Google Sheets"""
        sheet_id = self.sheet_id_input.text().strip()
        self.open_sheet_button.setEnabled(bool(sheet_id))

    def open_google_sheet(self):
        """Mở Google Sheets trong trình duyệt"""
        sheet_id = self.sheet_id_input.text().strip()
        if sheet_id:
            import webbrowser

            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
            webbrowser.open(url)
            self.log(f"🌐 " + self.t("selected_credentials").format(url))
        else:
            QMessageBox.warning(self, "Cảnh báo", "Không có Sheet ID để mở!")

    def open_google_sheet_for_card(self, card):
        """Mở Google Sheets theo sheet id của từng job card"""
        sheet_id = card["sheet_id"].text().strip()
        if sheet_id:
            import webbrowser

            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
            webbrowser.open(url)
            self.log(f"🌐 Opened sheet: {url}")
        else:
            QMessageBox.warning(self, self.t("warning"), "Không có Sheet ID để mở!")

    def save_chrome_config(self):
        """Lưu cấu hình Chrome"""
        # Tải config cũ nếu có
        old_config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    old_config = json.load(f)
            except:
                pass

        # Cập nhật cấu hình Chrome
        old_config.update(
            {
                "ua_category": self.ua_category_combo.currentText(),
                "ua_specific": self.ua_specific_combo.currentText(),
                "window_width": self.window_width_input.value(),
                "window_height": self.window_height_input.value(),
                "headless": self.headless_checkbox.isChecked(),
                "profile_path": self.profile_path_input.text().strip(),
                "delete_profile": self.delete_profile_checkbox.isChecked(),
                "delay_seconds": self.delay_input.value(),
            }
        )

        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(old_config, f, ensure_ascii=False, indent=2)

            QMessageBox.information(self, "Thành công", "Đã lưu cấu hình Chrome!")
            self.log("💾 Đã lưu cấu hình Chrome thành công")
        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi", f"Không thể lưu cấu hình Chrome: {str(e)}"
            )
            self.log(f"❌ Lỗi khi lưu cấu hình Chrome: {str(e)}")

    def load_chrome_config(self):
        """Tải cấu hình Chrome từ file config.json"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

                # Tải cấu hình Chrome
                ua_category = config.get("ua_category", "Windows Chrome")
                if ua_category in USER_AGENTS:
                    self.ua_category_combo.setCurrentText(ua_category)

                self.update_ua_specific()

                ua_specific = config.get("ua_specific", "")
                if ua_specific and ua_specific in USER_AGENTS.get(ua_category, []):
                    self.ua_specific_combo.setCurrentText(ua_specific)

                self.window_width_input.setValue(config.get("window_width", 375))
                self.window_height_input.setValue(config.get("window_height", 667))
                self.headless_checkbox.setChecked(config.get("headless", False))
                self.profile_path_input.setText(config.get("profile_path", ""))
                self.delete_profile_checkbox.setChecked(config.get("delete_profile", False))
                self.delay_input.setValue(config.get("delay_seconds", 2))

                self.log("📂 Đã tải cấu hình Chrome từ file")
            except Exception as e:
                self.log(f"⚠ Không thể tải cấu hình Chrome: {str(e)}")

    def load_configs_list(self):
        """Tải danh sách cấu hình từ file"""
        self.config_list_widget.clear()

        if not os.path.exists(self.configs_list_file):
            self.config_info_label.setText(self.t("no_configs"))
            return

        try:
            with open(self.configs_list_file, "r", encoding="utf-8") as f:
                configs = json.load(f)

            if not configs:
                self.config_info_label.setText(self.t("no_configs"))
                return

            # Thêm các cấu hình vào danh sách
            for config_name in sorted(configs.keys()):
                item = QListWidgetItem(config_name)
                self.config_list_widget.addItem(item)
        except Exception as e:
            self.log(f"❌ Lỗi khi tải danh sách cấu hình: {str(e)}")

    def on_config_selected(self, item):
        """Xử lý khi chọn một cấu hình"""
        config_name = item.text()
        self.selected_config_name = config_name

        # Tải thông tin cấu hình
        try:
            with open(self.configs_list_file, "r", encoding="utf-8") as f:
                configs = json.load(f)

            if config_name in configs:
                config = configs[config_name]
                # Hiển thị thông tin
                info_text = self.t("config_info").format(
                    config.get("sheet_id", "N/A")[:30],
                    config.get("target_domain", "N/A"),
                    config.get("num_pages", 3),
                    config.get("max_threads", 5),
                )
                self.config_info_label.setText(info_text)
        except Exception as e:
            self.log(f"❌ Lỗi: {str(e)}")

    def apply_selected_config(self):
        """Áp dụng cấu hình được chọn"""
        if not self.selected_config_name:
            QMessageBox.warning(self, self.t("warning"), "Vui lòng chọn một cấu hình")
            return

        try:
            with open(self.configs_list_file, "r", encoding="utf-8") as f:
                configs = json.load(f)

            if self.selected_config_name not in configs:
                QMessageBox.warning(self, self.t("error"), "Cấu hình không tồn tại")
                return

            config = configs[self.selected_config_name]
            jobs = config.get("jobs", [])

            if jobs:
                while len(self.job_cards) > 1:
                    card_to_remove = self.job_cards[-1]["frame"]
                    self.remove_job_card(card_to_remove)

                first_card = self.job_cards[0] if self.job_cards else self.add_job_card()
                first_card["sheet_id"].clear()
                first_card["pages"].setValue(3)
                first_card["domain"].clear()
                first_card["threads"].setValue(5)
                first_card["keywords"].clear()
                first_card["credentials_file"] = self.credentials_file
                first_card["credentials_label"].setText(self.t("not_found"))
                self.update_job_keyword_counter(first_card)
                self.update_job_start_state(first_card)

                for index, job in enumerate(jobs):
                    card = first_card if index == 0 else self.add_job_card()
                    card["sheet_id"].setText(job.get("sheet_id", ""))
                    card["pages"].setValue(job.get("num_pages", 3))
                    card["domain"].setText(job.get("target_domain", ""))
                    card["threads"].setValue(job.get("max_threads", 5))
                    card["keywords"].setPlainText(job.get("keywords", ""))
                    credentials_file = job.get("credentials_file", "")
                    card["credentials_file"] = credentials_file or self.credentials_file
                    card["credentials_label"].setText(
                        os.path.basename(credentials_file) if credentials_file else self.t("not_found")
                    )
                    card["enable_onsite_interaction"].setChecked(job.get("onsite_interaction_enabled", True))
                    card["onsite_time_min"].setValue(int(str(job.get("onsite_time_range", "40-60")).split("-")[0]))
                    card["onsite_time_max"].setValue(int(str(job.get("onsite_time_range", "40-60")).split("-")[-1]))
                    card["enable_extra_clicks"].setChecked(job.get("extra_clicks_enabled", False))
                    extra_range = str(job.get("extra_click_range", "1-3"))
                    if "-" in extra_range:
                        extra_parts = [p.strip() for p in extra_range.split("-") if p.strip()]
                        if len(extra_parts) == 2:
                            card["extra_click_min"].setValue(int(extra_parts[0]))
                            card["extra_click_max"].setValue(int(extra_parts[1]))
                    self.update_job_keyword_counter(card)
                    self.update_job_start_state(card)
                    self.toggle_onsite_fields()
                    self.toggle_extra_click_fields()

                self._bind_first_job_aliases(self.job_cards[0])
            else:
                self.sheet_id_input.setText(config.get("sheet_id", ""))
                self.num_pages_input.setValue(config.get("num_pages", 3))
                self.domain_input.setText(config.get("target_domain", ""))
                self.max_threads_input.setValue(config.get("max_threads", 5))
                self.keywords_input.setPlainText(config.get("keywords", ""))

                if "credentials_file" in config:
                    self.credentials_file = config["credentials_file"]

            # Áp dụng cấu hình Chrome
            ua_category = config.get("ua_category", "Windows Chrome")
            if ua_category in USER_AGENTS:
                self.ua_category_combo.setCurrentText(ua_category)

            self.update_ua_specific()

            ua_specific = config.get("ua_specific", "")
            if ua_specific and ua_specific in USER_AGENTS.get(ua_category, []):
                self.ua_specific_combo.setCurrentText(ua_specific)

            self.window_width_input.setValue(config.get("window_width", 375))
            self.window_height_input.setValue(config.get("window_height", 667))
            self.headless_checkbox.setChecked(config.get("headless", False))
            self.profile_path_input.setText(config.get("profile_path", ""))
            self.delete_profile_checkbox.setChecked(config.get("delete_profile", False))
            self.delay_input.setValue(config.get("delay_seconds", 2))

            # Áp dụng cấu hình Proxy
            self.enable_proxy_checkbox.setChecked(config.get("proxy_enabled", False))
            self.proxy_type_combo.setCurrentText(config.get("proxy_type", "http"))
            proxy_list = config.get("proxy_list", [])
            self.proxy_list_input.setPlainText("\n".join(proxy_list) if proxy_list else "")
            self.update_proxy_counter()
            self.toggle_proxy_fields()
            self.profile_path_input.setText(config.get("profile_path", ""))
            self.delete_profile_checkbox.setChecked(config.get("delete_profile", False))

            QMessageBox.information(self, self.t("success"), self.t("apply_success"))
            self.log(f"✅ {self.t('apply_success')} - {self.selected_config_name}")

            # Chuyển tới tab cấu hình chính
            self.tab_widget.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(
                self, self.t("error"), self.t("error_save").format(str(e))
            )

    def delete_selected_config(self):
        """Xóa cấu hình được chọn"""
        if not self.selected_config_name:
            QMessageBox.warning(self, self.t("warning"), "Vui lòng chọn một cấu hình")
            return

        reply = QMessageBox.question(
            self,
            self.t("delete_confirm"),
            f"{self.t('delete_confirm_msg')}\n\n'{self.selected_config_name}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        try:
            with open(self.configs_list_file, "r", encoding="utf-8") as f:
                configs = json.load(f)

            if self.selected_config_name in configs:
                del configs[self.selected_config_name]

                with open(self.configs_list_file, "w", encoding="utf-8") as f:
                    json.dump(configs, f, ensure_ascii=False, indent=2)

                QMessageBox.information(
                    self, self.t("success"), self.t("config_deleted")
                )
                self.log(f"🗑️ {self.t('config_deleted')} - {self.selected_config_name}")

                self.selected_config_name = None
                self.load_configs_list()
        except Exception as e:
            QMessageBox.critical(
                self, self.t("error"), self.t("error_save").format(str(e))
            )

    def rename_selected_config(self):
        """Đổi tên cấu hình được chọn"""
        if not self.selected_config_name:
            QMessageBox.warning(self, self.t("warning"), "Vui lòng chọn một cấu hình")
            return

        new_name, ok = QInputDialog.getText(
            self,
            self.t("rename_config_title"),
            self.t("new_config_name"),
            text=self.selected_config_name,
        )

        if not ok or not new_name.strip():
            return

        new_name = new_name.strip()

        if new_name == self.selected_config_name:
            return

        try:
            with open(self.configs_list_file, "r", encoding="utf-8") as f:
                configs = json.load(f)

            if new_name in configs:
                QMessageBox.warning(
                    self, self.t("warning"), self.t("config_name_exists")
                )
                return

            if self.selected_config_name in configs:
                configs[new_name] = configs[self.selected_config_name]
                del configs[self.selected_config_name]

                with open(self.configs_list_file, "w", encoding="utf-8") as f:
                    json.dump(configs, f, ensure_ascii=False, indent=2)

                QMessageBox.information(
                    self, self.t("success"), self.t("config_renamed")
                )
                self.log(
                    f"✏️ {self.t('config_renamed')} - {self.selected_config_name} → {new_name}"
                )

                self.selected_config_name = None
                self.load_configs_list()
        except Exception as e:
            QMessageBox.critical(
                self, self.t("error"), self.t("error_save").format(str(e))
            )

    def set_language_vi(self):
        """Chuyển sang tiếng Việt"""
        self.language = "vi"
        self.lang_vi_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 3px;
                border: 2px solid #2E7D32;
                min-width: 100px;
            }
        """
        )
        self.lang_en_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 3px;
                border: none;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """
        )
        self.update_ui_language()

    def set_language_en(self):
        """Chuyển sang tiếng Anh"""
        self.language = "en"
        self.lang_en_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 3px;
                border: 2px solid #0d47a1;
                min-width: 100px;
            }
        """
        )
        self.lang_vi_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 3px;
                border: none;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )
        self.update_ui_language()

    def change_password(self):
        """Thay đổi mật khẩu"""
        from PyQt5.QtWidgets import (
            QDialog,
            QVBoxLayout,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QPushButton,
            QFormLayout,
        )

        dialog = QDialog(self)
        dialog.setWindowTitle(self.t("change_password_title"))
        dialog.setModal(True)
        dialog.setFixedSize(350, 250)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Current password
        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.Password)
        self.current_password_input.setPlaceholderText("Nhập mật khẩu hiện tại...")
        self.current_password_input.setMinimumHeight(35)
        form_layout.addRow(
            self.t("current_password") + ":", self.current_password_input
        )

        # New password
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setPlaceholderText("Nhập mật khẩu mới...")
        self.new_password_input.setMinimumHeight(35)
        form_layout.addRow(self.t("new_password") + ":", self.new_password_input)

        # Confirm new password
        self.confirm_new_password_input = QLineEdit()
        self.confirm_new_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_new_password_input.setPlaceholderText("Nhập lại mật khẩu mới...")
        self.confirm_new_password_input.setMinimumHeight(35)
        form_layout.addRow(
            self.t("confirm_new_password") + ":", self.confirm_new_password_input
        )

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        cancel_button = QPushButton("Hủy")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)

        change_button = QPushButton("Thay đổi")
        change_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """
        )
        change_button.clicked.connect(lambda: self.do_change_password(dialog))
        button_layout.addWidget(change_button)

        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def do_change_password(self, dialog):
        """Thực hiện thay đổi mật khẩu"""
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_new_password_input.text()

        if not current_password or not new_password or not confirm_password:
            QMessageBox.warning(dialog, "Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        if new_password != confirm_password:
            QMessageBox.warning(dialog, "Cảnh báo", self.t("passwords_not_match"))
            return

        # Load users
        if os.path.exists("users.json"):
            try:
                with open("users.json", "r", encoding="utf-8") as f:
                    users = json.load(f)
            except:
                QMessageBox.warning(
                    dialog, "Lỗi", "Không thể tải thông tin người dùng!"
                )
                return
        else:
            QMessageBox.warning(dialog, "Lỗi", "Không tìm thấy file người dùng!")
            return

        # Find current user (assuming we have a way to know current user)
        # For simplicity, we'll assume there's only one user or we need to track current user
        current_user = None
        for username, hashed_password in users.items():
            if hashed_password == hashlib.sha256(current_password.encode()).hexdigest():
                current_user = username
                break

        if not current_user:
            QMessageBox.warning(dialog, "Cảnh báo", self.t("wrong_current_password"))
            return

        # Update password
        users[current_user] = hashlib.sha256(new_password.encode()).hexdigest()

        # Save users
        try:
            with open("users.json", "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(dialog, "Lỗi", f"Không thể lưu mật khẩu mới: {str(e)}")
            return

        QMessageBox.information(dialog, "Thành công", self.t("password_changed"))
        dialog.accept()

    def change_username(self):
        """Thay đổi tên đăng nhập"""
        from PyQt5.QtWidgets import (
            QDialog,
            QVBoxLayout,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QPushButton,
            QFormLayout,
        )

        dialog = QDialog(self)
        dialog.setWindowTitle(self.t("change_username_title"))
        dialog.setModal(True)
        dialog.setFixedSize(350, 200)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # New username
        self.new_username_input = QLineEdit()
        self.new_username_input.setPlaceholderText("Nhập tên đăng nhập mới...")
        self.new_username_input.setMinimumHeight(35)
        form_layout.addRow(self.t("new_username") + ":", self.new_username_input)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        cancel_button = QPushButton("Hủy")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)

        change_button = QPushButton("Thay đổi")
        change_button.setStyleSheet(
            """
            QPushButton {
                background-color: #9C27B0;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """
        )
        change_button.clicked.connect(lambda: self.do_change_username(dialog))
        button_layout.addWidget(change_button)

        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def do_change_username(self, dialog):
        """Thực hiện thay đổi tên đăng nhập"""
        new_username = self.new_username_input.text().strip()

        if not new_username:
            QMessageBox.warning(dialog, "Cảnh báo", "Vui lòng nhập tên đăng nhập mới!")
            return

        # Load users
        if os.path.exists("users.json"):
            try:
                with open("users.json", "r", encoding="utf-8") as f:
                    users = json.load(f)
            except:
                QMessageBox.warning(
                    dialog, "Lỗi", "Không thể tải thông tin người dùng!"
                )
                return
        else:
            QMessageBox.warning(dialog, "Lỗi", "Không tìm thấy file người dùng!")
            return

        # Check if username already exists
        if new_username in users:
            QMessageBox.warning(dialog, "Cảnh báo", self.t("username_exists"))
            return

        # Use the current logged-in user
        current_user = self.current_user
        if not current_user or current_user not in users:
            QMessageBox.warning(
                dialog, "Lỗi", "Không thể xác định người dùng hiện tại!"
            )
            return

        # Update username
        password = users[current_user]
        del users[current_user]
        users[new_username] = password

        # Rename config file if it exists
        old_config_file = f"config_{current_user}.json"
        new_config_file = f"config_{new_username}.json"
        if os.path.exists(old_config_file):
            try:
                os.rename(old_config_file, new_config_file)
            except Exception as e:
                self.log(f"⚠️ Không thể đổi tên file config: {str(e)}")

        # Save users
        try:
            with open("users.json", "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(
                dialog, "Lỗi", f"Không thể lưu tên đăng nhập mới: {str(e)}"
            )
            return

        QMessageBox.information(dialog, "Thành công", self.t("username_changed"))
        dialog.accept()

    def logout(self):
        """Đăng xuất và quay lại màn hình đăng nhập"""
        reply = QMessageBox.question(
            self,
            self.t("confirm_logout"),
            self.t("confirm_logout_msg"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.log("🚪 Đang đăng xuất...")
            # Xóa phiên đăng nhập đã lưu
            login_dialog = LoginDialog(parent=None)
            login_dialog.clear_remember_me_session()

            # Ẩn cửa sổ hiện tại trước khi hiển thị dialog đăng nhập
            self.hide()

            # Cleanup search threads if running
            for thread in list(self.search_threads):
                if thread and thread.isRunning():
                    thread.stop()
                    thread.wait()
            self.search_threads.clear()

            if login_dialog.exec_() == QDialog.Accepted:
                # Đăng nhập thành công, ẩn cửa sổ cũ và tạo cửa sổ mới
                self.hide()
                new_window = KeywordSearchGUI(current_user=login_dialog.logged_in_user)
                new_window.show()
            else:
                # Đăng nhập thất bại, hiển thị lại cửa sổ cũ
                self.show()
                QMessageBox.warning(
                    self, "Đăng nhập thất bại", "Đăng nhập thất bại. Vui lòng thử lại."
                )

    def toggle_proxy_fields(self):
        """Bật/tắt các trường proxy dựa trên checkbox"""
        enabled = self.enable_proxy_checkbox.isChecked()
        self.proxy_type_combo.setEnabled(enabled)
        self.proxy_list_input.setEnabled(enabled)

    def select_profile_path(self):
        """Chọn thư mục profile dùng chung cho toàn app"""
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục profile")
        if folder:
            self.profile_path_input.setText(folder)

    def toggle_onsite_fields(self):
        """Bật/tắt các trường tương tác trên site"""
        try:
            sender = self.sender()
            if sender is None:
                return
            for card in self.job_cards:
                if card.get("enable_onsite_interaction") is sender:
                    enabled = sender.isChecked()
                    card["onsite_time_min"].setEnabled(enabled)
                    card["onsite_time_max"].setEnabled(enabled)
                    return
        except RuntimeError:
            return

    def toggle_extra_click_fields(self):
        """Bật/tắt số lần click thêm theo checkbox"""
        try:
            sender = self.sender()
            if sender is None:
                return
            for card in self.job_cards:
                if card.get("enable_extra_clicks") is sender:
                    enabled = sender.isChecked()
                    card["extra_click_min"].setEnabled(enabled)
                    card["extra_click_max"].setEnabled(enabled)
                    return
        except RuntimeError:
            return

    def update_proxy_counter(self):
        """Cập nhật số proxy trong danh sách"""
        proxy_list = self.proxy_list_input.toPlainText().strip()
        if proxy_list:
            proxy_lines = [
                line.strip() for line in proxy_list.split("\n") if line.strip()
            ]
            count = len(proxy_lines)
            self.proxy_counter_label.setText(f"Số proxy: {count}")
        else:
            self.proxy_counter_label.setText("Số proxy: 0")

    def save_proxy_config(self):
        """Lưu cấu hình proxy"""
        proxy_list = self.proxy_list_input.toPlainText().strip()

        if self.enable_proxy_checkbox.isChecked() and not proxy_list:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập danh sách proxy!")
            return

        # Kiểm tra định dạng proxy
        if proxy_list:
            proxy_lines = [
                line.strip() for line in proxy_list.split("\n") if line.strip()
            ]
            for i, proxy in enumerate(proxy_lines, 1):
                if len(proxy) < 8:
                    QMessageBox.warning(
                        self,
                        "Cảnh báo",
                        f"Dòng {i}: Key proxy quá ngắn hoặc không hợp lệ!",
                    )
                    return
        else:
            proxy_lines = []

        # Tải config cũ nếu có
        old_config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    old_config = json.load(f)
            except:
                pass

        # Cập nhật cấu hình proxy
        old_config.update(
            {
                "proxy_enabled": self.enable_proxy_checkbox.isChecked(),
                "proxy_type": self.proxy_type_combo.currentText(),
                "proxy_list": proxy_lines,
            }
        )

        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(old_config, f, ensure_ascii=False, indent=2)

            QMessageBox.information(self, "Thành công", "Đã lưu cấu hình proxy!")
            self.log("💾 Đã lưu cấu hình proxy thành công")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu cấu hình proxy: {str(e)}")
            self.log(f"❌ Lỗi khi lưu cấu hình proxy: {str(e)}")

    def load_proxy_config(self):
        """Tải cấu hình proxy từ file config"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

                # Tải cấu hình proxy
                proxy_enabled = config.get("proxy_enabled", False)
                proxy_type = config.get("proxy_type", "http")
                proxy_list = config.get("proxy_list", [])

                self.enable_proxy_checkbox.setChecked(proxy_enabled)
                self.proxy_type_combo.setCurrentText(proxy_type)

                if proxy_list:
                    self.proxy_list_input.setPlainText("\n".join(proxy_list))
                    self.update_proxy_counter()

                self.toggle_proxy_fields()
                self.log("🔗 Đã tải cấu hình proxy")
            except Exception as e:
                self.log(f"⚠ Lỗi khi tải cấu hình proxy: {str(e)}")

    def test_proxy_connection(self):
        """Test kết nối proxy xoay bằng key."""
        if not self.enable_proxy_checkbox.isChecked():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng bật proxy trước!")
            return

        proxy_list = self.proxy_list_input.toPlainText().strip()
        if not proxy_list:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập danh sách key proxy!")
            return

        proxy_keys = [line.strip() for line in proxy_list.split("\n") if line.strip()]
        self.log(f"🧪 Đang test {len(proxy_keys)} key proxy...")

        success_count = 0
        fail_count = 0
        proxy_scheme = self.proxy_type_combo.currentText()

        for i, proxy_key in enumerate(proxy_keys, 1):
            try:
                api_url = f"https://proxyxoay.shop/api/get.php?key={proxy_key}&nhamang=random&tinhthanh=0&whitelist="
                api_resp = requests.get(api_url, timeout=10)
                proxy_http, proxy_error = parse_proxyxoay_response(api_resp.text)

                if not proxy_http:
                    self.log(f"❌ Key {i}: Không lấy được proxy - {proxy_error}")
                    fail_count += 1
                    continue

                proxy_hostport = proxy_http.strip().rstrip(":")
                proxy_url = f"{proxy_scheme}://{proxy_hostport}"

                proxies = {"http": proxy_url, "https": proxy_url}
                response = requests.get("https://www.google.com", proxies=proxies, timeout=10)

                if response.status_code == 200:
                    self.log(f"✅ Key {i}: OK - {proxy_url}")
                    success_count += 1
                else:
                    self.log(f"⚠️ Key {i}: Status {response.status_code} - {proxy_url}")
                    fail_count += 1
            except Exception as e:
                self.log(f"❌ Key {i}: Lỗi - {str(e)}")
                fail_count += 1

        result_msg = f"Kết quả: {success_count}/{len(proxy_keys)} thành công, {fail_count}/{len(proxy_keys)} thất bại"
        self.log(f"🧪 {result_msg}")
        QMessageBox.information(self, "Kết quả Test", result_msg)

    def update_ui_language(self):
        """Cập nhật giao diện theo ngôn ngữ"""
        self.setWindowTitle(self.t("title"))
        self.tab_widget.setTabText(0, self.t("config_tab"))
        self.tab_widget.setTabText(1, "🔗 Proxy")
        self.tab_widget.setTabText(2, self.t("chrome_tab"))
        self.tab_widget.setTabText(3, self.t("log_tab"))
        self.tab_widget.setTabText(4, self.t("browser_tab"))
        self.tab_widget.setTabText(self.user_tab_index, self.t("User"))
        if self.admin_tab_index is not None:
            self.tab_widget.setTabText(self.admin_tab_index, self.t("admin_tab"))
        self.tab_widget.setTabText(
            self.config_manager_tab_index, self.t("config_manager_tab")
        )
        self.statusBar().showMessage(self.t("ready"))

        # Cập nhật tất cả nút và nhãn
        if hasattr(self, "start_button"):
            self.start_button.setText(self.t("start_btn"))
        if hasattr(self, "stop_button"):
            self.stop_button.setText(self.t("stop_btn"))
        self.save_button.setText(self.t("save_btn"))
        self.open_sheet_button.setText(self.t("open_sheet_btn"))
        self.save_chrome_button.setText(self.t("save_chrome_btn"))
        self.reset_chrome_button.setText(self.t("reset_chrome_btn"))
        self.select_credentials_button.setText(self.t("select_btn"))
        self.headless_checkbox.setText(self.t("headless"))
        self.logout_button.setText(self.t("logout_btn"))
        self.lang_vi_btn.setText(self.t("tieng_viet"))
        self.lang_en_btn.setText(self.t("english"))
        self.apply_config_button.setText(self.t("apply_config"))
        self.rename_config_button.setText(self.t("rename_config"))
        self.delete_config_button.setText(self.t("delete_config"))

        if self.admin_tab_index is not None:
            self.admin_group.setTitle(self.t("admin_group"))
            self.admin_refresh_button.setText(self.t("admin_refresh_users"))
            self.admin_user_list_label.setText(self.t("admin_user_list"))
            self.admin_new_role_label.setText(self.t("admin_new_role"))
            self.admin_update_role_button.setText(self.t("admin_update_role"))
            self.admin_clear_machine_button.setText(self.t("admin_clear_machine"))
            self.on_admin_user_selected()

        # Cập nhật GroupBox titles
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if widget:
                for child in widget.findChildren(QGroupBox):
                    title = child.title()
                    if "Google Sheets" in title:
                        child.setTitle(self.t("sheets"))
                    elif "Search Config" in title or "Cấu hình Tìm kiếm" in title:
                        child.setTitle(self.t("search_config"))
                    elif "Keywords" in title or "Danh sách từ khóa" in title:
                        child.setTitle(self.t("keywords"))
                    elif "User-Agent Config" in title or "Cấu hình User-Agent" in title:
                        child.setTitle(self.t("ua_config"))
                    elif "Window Config" in title or "Cấu hình Cửa sổ" in title:
                        child.setTitle(self.t("window_config"))
                    elif "Log" in title:
                        child.setTitle(self.t("log_label"))
                    elif "Chrome Browser" in title:
                        child.setTitle(self.t("browser_tab"))
                    elif "👤" in title:
                        child.setTitle("👤 " + self.t("User"))
                    elif "🛡️" in title:
                        child.setTitle(self.t("admin_group"))

        # Cập nhật các QLabel - duyệt từng cái
        all_labels = self.findChildren(QLabel)
        for label in all_labels:
            text = label.text()
            # Cập nhật dựa trên nội dung hoặc parent widget
            if "Sheet ID" in text or (
                self.language == "vi" and "📋" in text and "Sheet" in text
            ):
                label.setText(self.t("sheet_id"))
            elif "Credentials" in text or (
                self.language == "vi" and "🔑" in text and "Credentials" in text
            ):
                label.setText(self.t("credentials"))
            elif "Pages" in text or "Số trang" in text:
                label.setText(self.t("pages"))
            elif "Threads" in text or "Số luồng" in text:
                label.setText(self.t("threads"))
            elif "Domain" in text or (
                self.language == "vi" and "🎯" in text and "Domain" in text
            ):
                label.setText(self.t("domain"))
            elif "User-Agent Category" in text or "Danh mục User-Agent" in text:
                label.setText(self.t("ua_category"))
            elif "Specific User-Agent" in text or "User-Agent cụ thể" in text:
                label.setText(self.t("ua_specific"))
            elif "Window Size" in text or "Kích thước cửa sổ" in text:
                label.setText(self.t("window_size"))
            elif "Chào mừng bạn đã đăng nhập!" in text:
                pass  # Giữ nguyên
            elif "Bạn có thể sử dụng tất cả các tính năng" in text:
                pass  # Giữ nguyên
            elif "Nhấn nút đăng xuất để quay lại" in text:
                pass  # Giữ nguyên

        # Cập nhật placeholder texts
        self.domain_input.setPlaceholderText(self.t("domain_placeholder"))
        self.keywords_input.setPlaceholderText(self.t("keywords_placeholder"))
        self.sheet_id_input.setPlaceholderText(
            "VD: 1cuj6slTO1wroK2OkBvd1HdyD_WKXTRmqqoC0bCEmKJE"
            if self.language == "vi"
            else "E.g: 1cuj6slTO1wroK2OkBvd1HdyD_WKXTRmqqoC0bCEmKJE"
        )
