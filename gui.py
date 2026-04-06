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
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QMimeData, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from search_logic import SearchThread
from config_utils import *

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
        self.language = "vi"  # Mặc định tiếng Việt
        self.selected_config_name = None  # Theo dõi cấu hình được chọn
        self.init_ui()
        self.load_config()
        self.load_configs_list()  # Tải danh sách cấu hình

    def t(self, key):
        """Lấy text dịch theo ngôn ngữ hiện tại"""
        return self.TRANSLATIONS[self.language].get(key, key)

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

        # === PHẦN GOOGLE SHEETS ===
        sheets_group = QGroupBox(self.t("sheets"))
        sheets_group.setFont(QFont("Arial", 10, QFont.Bold))
        sheets_group.setStyleSheet(
            """
            QGroupBox {
                color: #333;
                border: 2px solid #34A853;
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
        group_sheets_layout = QVBoxLayout()
        group_sheets_layout.setSpacing(12)

        # Google Sheet ID
        sheet_layout = QHBoxLayout()
        sheet_label = QLabel(self.t("sheet_id"))
        sheet_label.setFont(QFont("Arial", 9))
        sheet_label.setMinimumWidth(120)
        sheet_layout.addWidget(sheet_label)
        self.sheet_id_input = QLineEdit()
        self.sheet_id_input.setPlaceholderText(
            "VD: 1cuj6slTO1wroK2OkBvd1HdyD_WKXTRmqqoC0bCEmKJE"
        )
        self.sheet_id_input.textChanged.connect(self.update_sheet_button_state)
        self.sheet_id_input.setMinimumHeight(30)
        sheet_layout.addWidget(self.sheet_id_input)
        group_sheets_layout.addLayout(sheet_layout)

        # Credentials file
        credentials_layout = QHBoxLayout()
        credentials_label = QLabel(self.t("credentials"))
        credentials_label.setFont(QFont("Arial", 9))
        credentials_label.setMinimumWidth(120)
        credentials_layout.addWidget(credentials_label)
        self.credentials_label = QLabel(self.t("not_found"))
        self.credentials_label.setStyleSheet(
            "color: #666; font-style: italic; font-size: 9px;"
        )
        credentials_layout.addWidget(self.credentials_label, 1)
        self.select_credentials_button = QPushButton(self.t("select_btn"))
        self.select_credentials_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 9px;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 3px;
                border: none;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """
        )
        self.select_credentials_button.setMaximumWidth(80)
        self.select_credentials_button.setMinimumHeight(30)
        self.select_credentials_button.clicked.connect(self.select_credentials)
        credentials_layout.addWidget(self.select_credentials_button)
        group_sheets_layout.addLayout(credentials_layout)

        sheets_group.setLayout(group_sheets_layout)
        config_layout.addWidget(sheets_group)

        # === PHẦN TÌM KIẾM ===
        search_group = QGroupBox(self.t("search_config"))
        search_group.setFont(QFont("Arial", 10, QFont.Bold))
        search_group.setStyleSheet(
            """
            QGroupBox {
                color: #333;
                border: 2px solid #2196F3;
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
        group_search_layout = QVBoxLayout()
        group_search_layout.setSpacing(12)

        # Số trang
        pages_layout = QHBoxLayout()
        pages_label = QLabel(self.t("pages"))
        pages_label.setFont(QFont("Arial", 9))
        pages_label.setMinimumWidth(120)
        pages_layout.addWidget(pages_label)
        self.num_pages_input = QSpinBox()
        self.num_pages_input.setMinimum(1)
        self.num_pages_input.setMaximum(20)
        self.num_pages_input.setValue(3)
        self.num_pages_input.setMinimumHeight(30)
        self.num_pages_input.setMaximumWidth(80)
        pages_layout.addWidget(self.num_pages_input)
        pages_layout.addStretch()
        group_search_layout.addLayout(pages_layout)

        # Số thread
        threads_layout = QHBoxLayout()
        threads_label = QLabel(self.t("threads"))
        threads_label.setFont(QFont("Arial", 9))
        threads_label.setMinimumWidth(120)
        threads_layout.addWidget(threads_label)
        self.max_threads_input = QSpinBox()
        self.max_threads_input.setMinimum(1)
        self.max_threads_input.setMaximum(10)
        self.max_threads_input.setValue(5)
        self.max_threads_input.setMinimumHeight(30)
        self.max_threads_input.setMaximumWidth(80)
        threads_layout.addWidget(self.max_threads_input)
        threads_layout.addStretch()
        group_search_layout.addLayout(threads_layout)

        # Tên miền mục tiêu
        domain_layout = QHBoxLayout()
        domain_label = QLabel(self.t("domain"))
        domain_label.setFont(QFont("Arial", 9))
        domain_label.setMinimumWidth(120)
        domain_layout.addWidget(domain_label)
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText(self.t("domain_placeholder"))
        self.domain_input.setText("huyenhocviet.com")
        self.domain_input.setMinimumHeight(30)
        domain_layout.addWidget(self.domain_input)
        group_search_layout.addLayout(domain_layout)

        search_group.setLayout(group_search_layout)
        config_layout.addWidget(search_group)

        # === PHẦN TỪ KHÓA ===
        keyword_group = QGroupBox(self.t("keywords"))
        keyword_group.setFont(QFont("Arial", 10, QFont.Bold))
        keyword_group.setStyleSheet(
            """
            QGroupBox {
                color: #333;
                border: 2px solid #FF5722;
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
        keyword_layout = QVBoxLayout()
        keyword_layout.setSpacing(10)

        self.keywords_input = PlainTextEdit()
        self.keywords_input.setPlaceholderText(self.t("keywords_placeholder"))
        self.keywords_input.setMinimumHeight(150)
        self.keywords_input.textChanged.connect(self.update_keyword_counter)
        keyword_layout.addWidget(self.keywords_input)

        # Keywords counter
        counter_layout = QHBoxLayout()
        self.keyword_counter_label = QLabel(self.t("keywords_count").format(0))
        self.keyword_counter_label.setStyleSheet(
            "color: #666; font-size: 9px; font-weight: bold;"
        )
        counter_layout.addWidget(self.keyword_counter_label)
        counter_layout.addStretch()
        keyword_layout.addLayout(counter_layout)

        keyword_group.setLayout(keyword_layout)
        config_layout.addWidget(keyword_group)

        # === PHẦN NÚT ĐIỀU KHIỂN ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.start_button = QPushButton(self.t("start_btn"))
        self.start_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        self.start_button.setMinimumHeight(35)
        self.start_button.clicked.connect(self.start_search)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton(self.t("stop_btn"))
        self.stop_button.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c1180a;
            }
        """
        )
        self.stop_button.setMinimumHeight(35)
        self.stop_button.clicked.connect(self.stop_search)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        self.save_button = QPushButton(self.t("save_btn"))
        self.save_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0956cc;
            }
        """
        )
        self.save_button.setMinimumHeight(35)
        self.save_button.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_button)

        # Nút Sửa - để cập nhật cấu hình hiện tại
        self.edit_button = QPushButton(self.t("edit_btn"))
        self.edit_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #EF6C00;
            }
        """
        )
        self.edit_button.setMinimumHeight(35)
        self.edit_button.clicked.connect(self.edit_current_config)
        button_layout.addWidget(self.edit_button)

        self.open_sheet_button = QPushButton(self.t("open_sheet_btn"))
        self.open_sheet_button.setStyleSheet(
            """
            QPushButton {
                background-color: #34A853;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2E7D32;
            }
            QPushButton:pressed {
                background-color: #246e1f;
            }
        """
        )
        self.open_sheet_button.setMinimumHeight(35)
        self.open_sheet_button.clicked.connect(self.open_google_sheet)
        self.open_sheet_button.setEnabled(bool(self.sheet_id_input.text().strip()))
        button_layout.addWidget(self.open_sheet_button)

        config_layout.addLayout(button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #2196F3;
                border-radius: 5px;
                text-align: center;
                background-color: #f5f5f5;
                min-width: 200px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """
        )
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setMinimumWidth(200)
        config_layout.addWidget(self.progress_bar)

        # === TAB PROXY SETTINGS ===
        proxy_tab = QWidget()
        self.tab_widget.addTab(proxy_tab, "🔗 Proxy")
        proxy_layout = QVBoxLayout()
        proxy_layout.setSpacing(15)
        proxy_layout.setContentsMargins(15, 15, 15, 15)
        proxy_tab.setLayout(proxy_layout)

        # === PHẦN CẤU HÌNH PROXY ===
        proxy_group = QGroupBox("🔗 Cấu hình Proxy (Chia theo số luồng)")
        proxy_group.setFont(QFont("Arial", 10, QFont.Bold))
        proxy_group.setStyleSheet(
            """
            QGroupBox {
                color: #333;
                border: 2px solid #FF5722;
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
        self.proxy_type_combo.addItems(["http", "https", "socks4", "socks5"])
        self.proxy_type_combo.setMinimumHeight(30)
        proxy_type_layout.addWidget(self.proxy_type_combo)
        proxy_type_layout.addStretch()
        group_proxy_layout.addLayout(proxy_type_layout)

        # Proxy list
        proxy_list_label = QLabel("📋 Danh sách Proxy (mỗi luồng 1 proxy):")
        proxy_list_label.setFont(QFont("Arial", 9, QFont.Bold))
        group_proxy_layout.addWidget(proxy_list_label)

        # Proxy list text area
        proxy_list_desc = QLabel(
            "Định dạng: host:port:username:password\nVD:\n14.224.225.129:45008:aHCtaC:stSDcl\n192.168.1.1:8080:user:pass"
        )
        proxy_list_desc.setFont(QFont("Arial", 8))
        proxy_list_desc.setStyleSheet("color: #999; font-style: italic;")
        group_proxy_layout.addWidget(proxy_list_desc)

        self.proxy_list_input = PlainTextEdit()
        self.proxy_list_input.setPlaceholderText(
            "Nhập từng proxy trên một dòng\nĐịnh dạng: host:port:username:password"
        )
        self.proxy_list_input.setMinimumHeight(200)
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
            """
            QPushButton {
                background-color: #FF5722;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #D84315;
            }
            QPushButton:pressed {
                background-color: #BF360C;
            }
        """
        )
        self.save_proxy_button.setMinimumHeight(35)
        self.save_proxy_button.clicked.connect(self.save_proxy_config)
        proxy_button_layout.addWidget(self.save_proxy_button)

        self.test_proxy_button = QPushButton("🧪 Test Proxy")
        self.test_proxy_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """
        )
        self.test_proxy_button.setMinimumHeight(35)
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
        chrome_layout.setSpacing(15)
        chrome_layout.setContentsMargins(15, 15, 15, 15)
        chrome_tab.setLayout(chrome_layout)

        # === PHẦN CẤU HÌNH USER-AGENT ===
        ua_group = QGroupBox(self.t("ua_config"))
        ua_group.setFont(QFont("Arial", 10, QFont.Bold))
        ua_group.setStyleSheet(
            """
            QGroupBox {
                color: #333;
                border: 2px solid #2196F3;
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
        group_ua_layout = QVBoxLayout()
        group_ua_layout.setSpacing(12)

        # User-Agent category
        ua_category_layout = QHBoxLayout()
        ua_category_label = QLabel(self.t("ua_category"))
        ua_category_label.setFont(QFont("Arial", 9))
        ua_category_label.setMinimumWidth(150)
        ua_category_layout.addWidget(ua_category_label)
        self.ua_category_combo = QComboBox()
        self.ua_category_combo.addItems(USER_AGENTS.keys())
        self.ua_category_combo.currentTextChanged.connect(self.update_ua_specific)
        self.ua_category_combo.setMinimumHeight(30)
        ua_category_layout.addWidget(self.ua_category_combo)
        group_ua_layout.addLayout(ua_category_layout)

        # User-Agent specific
        ua_specific_layout = QHBoxLayout()
        ua_specific_label = QLabel(self.t("ua_specific"))
        ua_specific_label.setFont(QFont("Arial", 9))
        ua_specific_label.setMinimumWidth(150)
        ua_specific_layout.addWidget(ua_specific_label)
        self.ua_specific_combo = QComboBox()
        self.ua_specific_combo.setMinimumHeight(30)
        self.update_ua_specific()  # Initialize
        ua_specific_layout.addWidget(self.ua_specific_combo)
        group_ua_layout.addLayout(ua_specific_layout)

        ua_group.setLayout(group_ua_layout)
        chrome_layout.addWidget(ua_group)

        # === PHẦN CẤU HÌNH DELAY ===
        delay_group = QGroupBox("⏱️ Cấu hình Delay")
        delay_group.setFont(QFont("Arial", 10, QFont.Bold))
        delay_group.setStyleSheet(
            """
            QGroupBox {
                color: #333;
                border: 2px solid #FF9800;
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
        group_delay_layout = QVBoxLayout()
        group_delay_layout.setSpacing(12)

        # Delay time
        delay_layout = QHBoxLayout()
        delay_label = QLabel("⏱️ Thời gian delay (giây):")
        delay_label.setFont(QFont("Arial", 9))
        delay_label.setMinimumWidth(150)
        delay_layout.addWidget(delay_label)

        self.delay_input = QSpinBox()
        self.delay_input.setMinimum(0)
        self.delay_input.setMaximum(20)
        self.delay_input.setValue(2)
        self.delay_input.setMinimumHeight(30)
        self.delay_input.setMaximumWidth(80)
        delay_layout.addWidget(self.delay_input)

        delay_desc_label = QLabel("(0 = không delay, 1-20 giây)")
        delay_desc_label.setFont(QFont("Arial", 8))
        delay_desc_label.setStyleSheet("color: #666;")
        delay_layout.addWidget(delay_desc_label)

        delay_layout.addStretch()
        group_delay_layout.addLayout(delay_layout)

        delay_group.setLayout(group_delay_layout)
        chrome_layout.addWidget(delay_group)

        # === PHẦN CẤU HÌNH CỬA SỔ ===
        window_group = QGroupBox(self.t("window_config"))
        window_group.setFont(QFont("Arial", 10, QFont.Bold))
        window_group.setStyleSheet(
            """
            QGroupBox {
                color: #333;
                border: 2px solid #4CAF50;
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
        group_window_layout = QVBoxLayout()
        group_window_layout.setSpacing(12)

        # Window size
        window_size_layout = QHBoxLayout()
        window_size_label = QLabel(self.t("window_size"))
        window_size_label.setFont(QFont("Arial", 9))
        window_size_label.setMinimumWidth(150)
        window_size_layout.addWidget(window_size_label)

        self.window_width_input = QSpinBox()
        self.window_width_input.setMinimum(320)
        self.window_width_input.setMaximum(2560)
        self.window_width_input.setValue(375)
        self.window_width_input.setMinimumHeight(30)
        window_size_layout.addWidget(self.window_width_input)

        x_label = QLabel("x")
        x_label.setFont(QFont("Arial", 10, QFont.Bold))
        window_size_layout.addWidget(x_label)

        self.window_height_input = QSpinBox()
        self.window_height_input.setMinimum(480)
        self.window_height_input.setMaximum(1440)
        self.window_height_input.setValue(667)
        self.window_height_input.setMinimumHeight(30)
        window_size_layout.addWidget(self.window_height_input)

        window_size_layout.addStretch()
        group_window_layout.addLayout(window_size_layout)

        # Headless mode
        headless_layout = QHBoxLayout()
        headless_layout.addSpacing(150)
        self.headless_checkbox = QCheckBox(self.t("headless"))
        self.headless_checkbox.setFont(QFont("Arial", 9))
        self.headless_checkbox.setMinimumHeight(25)
        headless_layout.addWidget(self.headless_checkbox)
        headless_layout.addStretch()
        group_window_layout.addLayout(headless_layout)

        window_group.setLayout(group_window_layout)
        chrome_layout.addWidget(window_group)

        # === NÚT LƯU VÀ TẢI CHROME CONFIG ===
        chrome_button_layout = QHBoxLayout()
        chrome_button_layout.setSpacing(10)

        self.save_chrome_button = QPushButton(self.t("save_chrome_btn"))
        self.save_chrome_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """
        )
        self.save_chrome_button.setMinimumHeight(35)
        self.save_chrome_button.clicked.connect(self.save_chrome_config)
        chrome_button_layout.addWidget(self.save_chrome_button)

        self.reset_chrome_button = QPushButton(self.t("reset_chrome_btn"))
        self.reset_chrome_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FFC107;
                color: black;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #FFB300;
            }
            QPushButton:pressed {
                background-color: #FFA000;
            }
        """
        )
        self.reset_chrome_button.setMinimumHeight(35)
        self.reset_chrome_button.clicked.connect(self.load_chrome_config)
        chrome_button_layout.addWidget(self.reset_chrome_button)

        chrome_button_layout.addStretch()
        chrome_layout.addLayout(chrome_button_layout)

        # Thêm khoảng trống cuối
        chrome_layout.addStretch()

        # === TAB LOG ===
        log_tab = QWidget()
        self.tab_widget.addTab(log_tab, self.t("log_tab"))
        log_tab_layout = QVBoxLayout()
        log_tab.setLayout(log_tab_layout)

        # === PHẦN LOG ===
        log_group = QGroupBox(self.t("log_label"))
        log_group.setFont(QFont("Arial", 10, QFont.Bold))
        group_log_layout = QVBoxLayout()

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet(
            "background-color: #1e1e1e; color: #00ff00; font-family: Consolas;"
        )
        group_log_layout.addWidget(self.log_output)

        log_group.setLayout(group_log_layout)
        log_tab_layout.addWidget(log_group)

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
        self.tab_widget.addTab(User, self.t("User"))
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
        group_user_layout = QVBoxLayout()
        group_user_layout.setSpacing(20)

        # Thông tin người dùng
        user_info_layout = QVBoxLayout()
        user_info_layout.setSpacing(10)

        user_info_label = QLabel("👋 Chào mừng bạn đã đăng nhập!")
        user_info_label.setFont(QFont("Arial", 12, QFont.Bold))
        user_info_label.setStyleSheet("color: #333;")
        user_info_layout.addWidget(user_info_label)

        user_desc_label = QLabel(
            "Bạn có thể sử dụng tất cả các tính năng của công cụ tìm kiếm từ khóa."
        )
        user_desc_label.setFont(QFont("Arial", 10))
        user_desc_label.setStyleSheet("color: #666;")
        user_desc_label.setWordWrap(True)
        user_info_layout.addWidget(user_desc_label)

        group_user_layout.addLayout(user_info_layout)

        # Nút quản lý tài khoản
        account_buttons_layout = QVBoxLayout()
        account_buttons_layout.setSpacing(10)

        # Nút thay đổi mật khẩu
        self.change_password_button = QPushButton(self.t("change_password_btn"))
        self.change_password_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 6px;
                border: none;
                min-width: 180px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #EF6C00;
            }
        """
        )
        self.change_password_button.setMinimumHeight(40)
        self.change_password_button.clicked.connect(self.change_password)
        account_buttons_layout.addWidget(self.change_password_button, 0, Qt.AlignCenter)

        # Nút thay đổi tên đăng nhập
        self.change_username_button = QPushButton(self.t("change_username_btn"))
        self.change_username_button.setStyleSheet(
            """
            QPushButton {
                background-color: #9C27B0;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 6px;
                border: none;
                min-width: 180px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:pressed {
                background-color: #6A1B9A;
            }
        """
        )
        self.change_username_button.setMinimumHeight(40)
        self.change_username_button.clicked.connect(self.change_username)
        account_buttons_layout.addWidget(self.change_username_button, 0, Qt.AlignCenter)

        group_user_layout.addLayout(account_buttons_layout)

        # Nút đăng xuất
        logout_layout = QVBoxLayout()
        logout_layout.setSpacing(15)

        self.logout_button = QPushButton(self.t("logout_btn"))
        self.logout_button.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 15px 30px;
                border-radius: 8px;
                border: none;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """
        )
        self.logout_button.setMinimumHeight(45)
        self.logout_button.clicked.connect(self.logout)
        logout_layout.addWidget(self.logout_button, 0, Qt.AlignCenter)

        logout_desc_label = QLabel("Nhấn nút đăng xuất để quay lại màn hình đăng nhập.")
        logout_desc_label.setFont(QFont("Arial", 9))
        logout_desc_label.setStyleSheet("color: #999;")
        logout_desc_label.setAlignment(Qt.AlignCenter)
        logout_layout.addWidget(logout_desc_label)

        group_user_layout.addLayout(logout_layout)

        user_group.setLayout(group_user_layout)
        user_layout.addWidget(user_group)

        # === TAB QUẢN LÝ CẤU HÌNH ===
        config_manager_tab = QWidget()
        self.tab_widget.addTab(config_manager_tab, self.t("config_manager_tab"))
        config_manager_layout = QVBoxLayout()
        config_manager_layout.setSpacing(15)
        config_manager_layout.setContentsMargins(15, 15, 15, 15)
        config_manager_tab.setLayout(config_manager_layout)

        # === PHẦN DANH SÁCH CẤU HÌNH ===
        config_list_group = QGroupBox(self.t("saved_configs"))
        config_list_group.setFont(QFont("Arial", 10, QFont.Bold))
        config_list_group.setStyleSheet(
            """
            QGroupBox {
                color: #333;
                border: 2px solid #FF5722;
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
        group_config_list_layout = QVBoxLayout()
        group_config_list_layout.setSpacing(12)

        # Config list widget
        self.config_list_widget = QListWidget()
        self.config_list_widget.setMinimumHeight(300)
        self.config_list_widget.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: #f9f9f9;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
        """
        )
        self.config_list_widget.itemClicked.connect(self.on_config_selected)
        group_config_list_layout.addWidget(self.config_list_widget)

        # Config info display
        self.config_info_label = QLabel(self.t("no_configs"))
        self.config_info_label.setFont(QFont("Arial", 9))
        self.config_info_label.setStyleSheet("color: #666; font-style: italic;")
        self.config_info_label.setWordWrap(True)
        group_config_list_layout.addWidget(self.config_info_label)

        config_list_group.setLayout(group_config_list_layout)
        config_manager_layout.addWidget(config_list_group)

        # === NÚT QUẢN LÝ CẤU HÌNH ===
        config_button_layout = QHBoxLayout()
        config_button_layout.setSpacing(10)

        self.apply_config_button = QPushButton(self.t("apply_config"))
        self.apply_config_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        self.apply_config_button.setMinimumHeight(35)
        self.apply_config_button.clicked.connect(self.apply_selected_config)
        config_button_layout.addWidget(self.apply_config_button)

        self.rename_config_button = QPushButton(self.t("rename_config"))
        self.rename_config_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #EF6C00;
            }
        """
        )
        self.rename_config_button.setMinimumHeight(35)
        self.rename_config_button.clicked.connect(self.rename_selected_config)
        config_button_layout.addWidget(self.rename_config_button)

        self.delete_config_button = QPushButton(self.t("delete_config"))
        self.delete_config_button.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c1180a;
            }
        """
        )
        self.delete_config_button.setMinimumHeight(35)
        self.delete_config_button.clicked.connect(self.delete_selected_config)
        config_button_layout.addWidget(self.delete_config_button)

        config_button_layout.addStretch()
        config_manager_layout.addLayout(config_button_layout)

        # Thêm khoảng trống cuối
        config_manager_layout.addStretch()

        # Status bar
        self.statusBar().showMessage(self.t("ready"))

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

        # Tạo config mới - merge với config cũ
        new_config = old_config.copy()  # Giữ những thông tin cũ
        new_config.update(
            {
                "sheet_id": self.sheet_id_input.text(),
                "num_pages": self.num_pages_input.value(),
                "target_domain": self.domain_input.text(),
                "max_threads": self.max_threads_input.value(),
                "keywords": self.keywords_input.toPlainText(),
                "credentials_file": self.credentials_file,
            }
        )

        try:
            # Lưu vào file cấu hình chính
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(new_config, f, ensure_ascii=False, indent=2)

            # Thêm vào danh sách cấu hình
            configs[config_name] = {
                "sheet_id": self.sheet_id_input.text(),
                "num_pages": self.num_pages_input.value(),
                "target_domain": self.domain_input.text(),
                "max_threads": self.max_threads_input.value(),
                "keywords": self.keywords_input.toPlainText(),
                "credentials_file": self.credentials_file,
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

            # Cập nhật cấu hình với thông tin hiện tại từ form
            configs[self.selected_config_name] = {
                "sheet_id": self.sheet_id_input.text(),
                "num_pages": self.num_pages_input.value(),
                "target_domain": self.domain_input.text(),
                "max_threads": self.max_threads_input.value(),
                "keywords": self.keywords_input.toPlainText(),
                "credentials_file": self.credentials_file,
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

    def load_config(self):
        """Tải cấu hình"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

                self.sheet_id_input.setText(config.get("sheet_id", ""))
                self.num_pages_input.setValue(config.get("num_pages", 3))
                self.domain_input.setText(config.get("target_domain", ""))
                self.max_threads_input.setValue(config.get("max_threads", 5))
                self.keywords_input.setPlainText(config.get("keywords", ""))

                if "credentials_file" in config:
                    self.credentials_file = config["credentials_file"]
                    self.statusBar().showMessage(
                        self.t("selected_credentials").format(
                            os.path.basename(self.credentials_file)
                        )
                    )

                self.load_chrome_config()
                self.load_proxy_config()
                self.log("📂 " + self.t("saved_config"))
            except Exception as e:
                self.log(f"⚠ " + self.t("error_save").format(str(e)))

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

        # Chuẩn bị config
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
        }

        # Khởi tạo thread
        self.search_thread = SearchThread(config, self.credentials_file)
        self.search_thread.log_signal.connect(self.log)
        self.search_thread.progress_signal.connect(self.update_progress)
        self.search_thread.finished_signal.connect(self.search_finished)

        # UI state
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.statusBar().showMessage(self.t("searching"))

        # Bắt đầu
        self.search_thread.start()

    def stop_search(self):
        """Dừng tìm kiếm"""
        if self.search_thread and self.search_thread.isRunning():
            reply = QMessageBox.question(
                self,
                self.t("confirm_stop"),
                self.t("confirm_stop_msg"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.log("⏸ Đang dừng tìm kiếm...")
                self.search_thread.stop()
                self.stop_button.setEnabled(False)
                self.start_button.setEnabled(True)
                self.statusBar().showMessage("Đã dừng")

    def update_progress(self, current, total):
        """Cập nhật progress bar"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def search_finished(self, success, message):
        """Xử lý khi tìm kiếm xong"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)

        # Đảm bảo thread được giải phóng
        if self.search_thread:
            self.search_thread.wait()
            self.search_thread = None

        if success:
            self.statusBar().showMessage(self.t("completed"))
            QMessageBox.information(self, self.t("success"), message)
            self.open_sheet_button.setEnabled(True)
        else:
            self.statusBar().showMessage(self.t("error"))
            QMessageBox.warning(self, self.t("error"), message)

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

            # Áp dụng cấu hình lên UI
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
            self.delay_input.setValue(config.get("delay_seconds", 2))

            # Áp dụng cấu hình Proxy
            self.enable_proxy_checkbox.setChecked(config.get("proxy_enabled", False))
            self.proxy_type_combo.setCurrentText(config.get("proxy_type", "http"))
            proxy_list = config.get("proxy_list", [])
            if proxy_list:
                self.proxy_list_input.setPlainText("\n".join(proxy_list))
                self.update_proxy_counter()
            self.toggle_proxy_fields()

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

            # Cleanup search thread if running
            if self.search_thread and self.search_thread.isRunning():
                self.search_thread.stop()
                self.search_thread.wait()
            
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
                parts = proxy.split(":")
                if len(parts) != 4:
                    QMessageBox.warning(
                        self,
                        "Cảnh báo",
                        f"Dòng {i}: Định dạng proxy sai!\nĐúng: host:port:username:password",
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
        """Test kết nối proxy"""
        if not self.enable_proxy_checkbox.isChecked():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng bật proxy trước!")
            return

        proxy_list = self.proxy_list_input.toPlainText().strip()
        if not proxy_list:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập danh sách proxy!")
            return

        proxy_lines = [line.strip() for line in proxy_list.split("\n") if line.strip()]

        self.log(f"🧪 Đang test {len(proxy_lines)} proxy...")

        success_count = 0
        fail_count = 0

        for i, proxy_line in enumerate(proxy_lines, 1):
            try:
                parts = proxy_line.split(":")
                if len(parts) != 4:
                    self.log(f"❌ Proxy {i}: Định dạng sai - {proxy_line}")
                    fail_count += 1
                    continue

                host, port, username, password = parts

                try:
                    port = int(port)
                except ValueError:
                    self.log(f"❌ Proxy {i}: Port không hợp lệ - {port}")
                    fail_count += 1
                    continue

                proxy_type = self.proxy_type_combo.currentText()
                proxy_url = f"{proxy_type}://{username}:{password}@{host}:{port}"

                proxies = {"http": proxy_url, "https": proxy_url}

                response = requests.get(
                    "https://www.google.com", proxies=proxies, timeout=5
                )
                if response.status_code == 200:
                    self.log(f"✅ Proxy {i}: OK - {host}:{port}")
                    success_count += 1
                else:
                    self.log(
                        f"⚠️ Proxy {i}: Status {response.status_code} - {host}:{port}"
                    )
                    fail_count += 1
            except Exception as e:
                self.log(f"❌ Proxy {i}: Lỗi - {str(e)}")
                fail_count += 1

        result_msg = f"Kết quả: {success_count}/{len(proxy_lines)} thành công, {fail_count}/{len(proxy_lines)} thất bại"
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
        self.tab_widget.setTabText(5, self.t("User"))
        self.statusBar().showMessage(self.t("ready"))

        # Cập nhật tất cả nút và nhãn
        self.start_button.setText(self.t("start_btn"))
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
