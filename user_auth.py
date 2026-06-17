from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QCheckBox,
    QComboBox,
    QFrame,
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QPixmap
from db import UserManager
from utils import resource_path
from datetime import datetime, timedelta
import os


class LoginDialog(QDialog):
    """Dialog đăng nhập/đăng ký sử dụng MongoDB"""

    REMEMBER_ME_DAYS = 3

    INPUT_STYLE = (
        "QLineEdit{background:#ffffff; border:1px solid #d1d5db; border-radius:10px; "
        "padding:10px 14px; font-size:13px; color:#111827;}"
        "QLineEdit:focus{border:1px solid #3b82f6;}"
        "QLineEdit::placeholder{color:#9ca3af;}"
    )
    COMBO_STYLE = (
        "QComboBox{background:#ffffff; border:1px solid #d1d5db; border-radius:10px; "
        "padding:8px 14px; font-size:13px; color:#111827; min-height:20px;}"
        "QComboBox:focus{border:1px solid #3b82f6;}"
        "QComboBox::drop-down{border:none; width:24px;}"
        "QComboBox QAbstractItemView{background:#ffffff; border:1px solid #e5e7eb; "
        "selection-background-color:#eff6ff; selection-color:#111827;}"
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "login"
        self.logged_in_user = None
        self.user_role = None
        self.user_manager = UserManager()
        self.init_ui()

    def _field_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Arial", 10, QFont.Bold))
        label.setStyleSheet("color:#374151; border:none; background:transparent;")
        return label

    def _styled_input(self, placeholder="", password=False):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setMinimumHeight(44)
        field.setStyleSheet(self.INPUT_STYLE)
        if password:
            field.setEchoMode(QLineEdit.Password)
        return field

    def init_ui(self):
        self.setWindowTitle("Đăng nhập - Công cụ Tìm kiếm Từ khóa")
        self.setModal(True)
        self.setFixedSize(460, 560)
        self.setStyleSheet("QDialog{background:#f8fafc;}")

        root = QVBoxLayout()
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        header = QFrame()
        header.setStyleSheet(
            "QFrame{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #111827, stop:1 #1e3a5f); border:none;}"
        )
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(10)
        header_layout.setContentsMargins(28, 28, 28, 24)

        logo_row = QHBoxLayout()
        logo_row.setSpacing(14)
        self.logo_label = QLabel()
        logo_path = resource_path("logo1.png")
        if not os.path.exists(logo_path):
            logo_path = resource_path("logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(
                52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.logo_label.setPixmap(pixmap)
        logo_row.addWidget(self.logo_label)

        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(2)
        brand_name = QLabel(" Keyword Traffic Booster")
        brand_name.setFont(QFont("Arial", 15, QFont.Bold))
        brand_name.setStyleSheet("color:#ffffff; border:none; background:transparent;")
        brand_tagline = QLabel("Tìm kiếm từ khóa và tương tác bài viết tự động")
        brand_tagline.setStyleSheet("color:#94a3b8; border:none; background:transparent; font-size:12px;")
        brand_layout.addWidget(brand_name)
        brand_layout.addWidget(brand_tagline)
        logo_row.addLayout(brand_layout)
        logo_row.addStretch()
        header_layout.addLayout(logo_row)

        self.header_title = QLabel("Đăng nhập vào hệ thống")
        self.header_title.setFont(QFont("Arial", 13, QFont.Bold))
        self.header_title.setStyleSheet("color:#f8fafc; border:none; background:transparent;")
        header_layout.addWidget(self.header_title)

        self.header_desc = QLabel("Nhập thông tin tài khoản để tiếp tục sử dụng công cụ.")
        self.header_desc.setWordWrap(True)
        self.header_desc.setStyleSheet("color:#cbd5e1; border:none; background:transparent; font-size:12px;")
        header_layout.addWidget(self.header_desc)
        root.addWidget(header)

        content = QVBoxLayout()
        content.setSpacing(18)
        content.setContentsMargins(24, 22, 24, 24)

        form_card = QFrame()
        form_card.setStyleSheet(
            "QFrame{background:#ffffff; border:1px solid #e5e7eb; border-radius:16px;}"
        )
        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(18, 18, 18, 18)

        form_layout.addWidget(self._field_label("Tên đăng nhập"))
        self.username_input = self._styled_input("Nhập tên đăng nhập...")
        form_layout.addWidget(self.username_input)

        form_layout.addWidget(self._field_label("Mật khẩu"))
        self.password_input = self._styled_input("Nhập mật khẩu...", password=True)
        self.password_input.returnPressed.connect(self.login)
        form_layout.addWidget(self.password_input)

        self.confirm_password_label = self._field_label("Xác nhận mật khẩu")
        self.confirm_password_input = self._styled_input("Nhập lại mật khẩu...", password=True)
        self.confirm_password_input.returnPressed.connect(self.login)
        self.confirm_password_label.setVisible(False)
        self.confirm_password_input.setVisible(False)
        form_layout.addWidget(self.confirm_password_label)
        form_layout.addWidget(self.confirm_password_input)

        self.role_label = self._field_label("Quyền tài khoản")
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "tester", "admin"])
        self.role_combo.setMinimumHeight(44)
        self.role_combo.setStyleSheet(self.COMBO_STYLE)
        self.role_label.setVisible(False)
        self.role_combo.setVisible(False)
        form_layout.addWidget(self.role_label)
        form_layout.addWidget(self.role_combo)

        self.remember_me_checkbox = QCheckBox("Ghi nhớ đăng nhập")
        self.remember_me_checkbox.setFont(QFont("Arial", 10))
        self.remember_me_checkbox.setStyleSheet(
            "QCheckBox{color:#374151; spacing:8px;}"
            "QCheckBox::indicator{width:18px; height:18px; border-radius:4px; "
            "border:1px solid #d1d5db; background:#ffffff;}"
            "QCheckBox::indicator:checked{background:#111827; border:1px solid #111827;}"
        )
        form_layout.addWidget(self.remember_me_checkbox)
        content.addWidget(form_card)

        self.login_button = QPushButton("Đăng nhập")
        self.login_button.setMinimumHeight(48)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet(
            "QPushButton{background:#111827; color:white; font-weight:700; font-size:13px; "
            "border:none; border-radius:12px; padding:10px 16px;}"
            "QPushButton:hover{background:#1f2937;}"
            "QPushButton:pressed{background:#0f172a;}"
        )
        self.login_button.clicked.connect(self.login)
        content.addWidget(self.login_button)

        switch_row = QHBoxLayout()
        switch_row.setSpacing(6)
        switch_row.addStretch()
        self.switch_hint = QLabel("Chưa có tài khoản?")
        self.switch_hint.setStyleSheet("color:#6b7280; font-size:12px; border:none; background:transparent;")
        switch_row.addWidget(self.switch_hint)
        self.register_button = QPushButton("Đăng ký ngay")
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setStyleSheet(
            "QPushButton{background:transparent; color:#2563eb; font-weight:700; font-size:12px; "
            "border:none; padding:4px 6px;}"
            "QPushButton:hover{color:#1d4ed8;}"
        )
        self.register_button.clicked.connect(self.switch_to_register)
        switch_row.addWidget(self.register_button)
        switch_row.addStretch()
        content.addLayout(switch_row)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(
            "color:#6b7280; font-size:11px; border:none; background:transparent; padding:4px 0;"
        )
        content.addWidget(self.status_label)

        root.addLayout(content)
        self.setLayout(root)

    def switch_to_register(self):
        if self.mode == "login":
            self.mode = "register"
            self.setWindowTitle("Đăng ký - Công cụ Tìm kiếm Từ khóa")
            self.setFixedSize(460, 680)
            self.header_title.setText("Tạo tài khoản mới")
            self.header_desc.setText("Điền thông tin bên dưới để đăng ký sử dụng công cụ.")
            self.login_button.setText("Tạo tài khoản")
            self.register_button.setText("Quay lại đăng nhập")
            self.switch_hint.setText("Đã có tài khoản?")
            self.confirm_password_label.setVisible(True)
            self.confirm_password_input.setVisible(True)
            self.remember_me_checkbox.setVisible(False)
            self.role_label.setVisible(self.is_admin())
            self.role_combo.setVisible(self.is_admin())
            self.status_label.setText("")
            self.status_label.setStyleSheet(
                "color:#6b7280; font-size:11px; border:none; background:transparent; padding:4px 0;"
            )
        else:
            self.mode = "login"
            self.setWindowTitle("Đăng nhập - Công cụ Tìm kiếm Từ khóa")
            self.setFixedSize(460, 560)
            self.header_title.setText("Đăng nhập vào hệ thống")
            self.header_desc.setText("Nhập thông tin tài khoản để tiếp tục sử dụng công cụ.")
            self.login_button.setText("Đăng nhập")
            self.register_button.setText("Đăng ký ngay")
            self.switch_hint.setText("Chưa có tài khoản?")
            self.confirm_password_label.setVisible(False)
            self.confirm_password_input.setVisible(False)
            self.remember_me_checkbox.setVisible(True)
            self.role_label.setVisible(False)
            self.role_combo.setVisible(False)
            self.status_label.setText("")
            self.status_label.setStyleSheet(
                "color:#6b7280; font-size:11px; border:none; background:transparent; padding:4px 0;"
            )

    def is_admin(self):
        # Đơn giản: nếu đã đăng nhập và role là admin
        return self.user_role == "admin"

    def login(self):
        import platform, uuid, socket
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.status_label.setText("Vui lòng nhập đầy đủ thông tin!")
            self.status_label.setStyleSheet(
                "color:#dc2626; font-size:11px; border:none; background:#fef2f2; "
                "border-radius:8px; padding:8px 10px;"
            )
            return
        if self.mode == "login":
            ok, msg, role = self.user_manager.login(username, password)
            if ok:
                self.logged_in_user = username
                self.user_role = role
                self.status_label.setText("Đăng nhập thành công!")
                self.status_label.setStyleSheet(
                    "color:#166534; font-size:11px; border:none; background:#ecfdf5; "
                    "border-radius:8px; padding:8px 10px;"
                )
                if self.remember_me_checkbox.isChecked():
                    self.save_remember_me_session(username)
                # Nếu là user, hiển thị thông báo thời gian còn lại dựa trên expired_at
                if role == "user":
                    user = self.user_manager.get_user(username)
                    expired = user.get("expired_at") if user else None
                    if isinstance(expired, str):
                        expired = datetime.fromisoformat(expired)
                    if expired:
                        remaining = expired - datetime.utcnow()
                        days_left = max(0, remaining.days)
                        if remaining.total_seconds() > 0:
                            QMessageBox.information(
                                self,
                                "Thông báo dùng thử",
                                f"Tài khoản dùng thử còn {days_left} ngày.",
                            )
                        else:
                            QMessageBox.warning(
                                self,
                                "Hết hạn",
                                "Tài khoản user đã hết hạn sử dụng (3 ngày)!",
                            )
                            return
                QTimer.singleShot(1000, self.accept)
            else:
                self.status_label.setText(msg)
                self.status_label.setStyleSheet(
                    "color:#dc2626; font-size:11px; border:none; background:#fef2f2; "
                    "border-radius:8px; padding:8px 10px;"
                )
                if "hết hạn" in msg:
                    QMessageBox.warning(self, "Hết hạn", msg)
        else:
            # Lấy thông tin thiết bị khi đăng ký
            hostname = socket.gethostname()
            try:
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
            except:
                mac = str(uuid.getnode())
            os_info = platform.platform()
            machine_info = {"hostname": hostname, "mac": mac, "os": os_info}

            confirm_password = self.confirm_password_input.text()
            if password != confirm_password:
                self.status_label.setText("Mật khẩu xác nhận không khớp!")
                self.status_label.setStyleSheet(
                    "color:#dc2626; font-size:11px; border:none; background:#fef2f2; "
                    "border-radius:8px; padding:8px 10px;"
                )
                return
            # Nếu là admin thì cho chọn role, còn lại chỉ được user
            role = self.role_combo.currentText() if self.is_admin() else "user"
            # Kiểm tra đã có user với cùng thông tin máy chưa
            if role == "user" and self.user_manager.users.find_one({"machine_info": machine_info}):
                self.status_label.setText("Máy này đã đăng ký tài khoản trước đó!")
                self.status_label.setStyleSheet(
                    "color:#dc2626; font-size:11px; border:none; background:#fef2f2; "
                    "border-radius:8px; padding:8px 10px;"
                )
                return
            ok, msg = self.user_manager.register(
                username,
                password,
                role=role,
                creator_role=self.user_role,
                machine_info=machine_info if role == "user" else None,
            )
            if ok:
                self.status_label.setText("Đăng ký thành công! Vui lòng đăng nhập để sử dụng.")
                self.status_label.setStyleSheet(
                    "color:#166534; font-size:11px; border:none; background:#ecfdf5; "
                    "border-radius:8px; padding:8px 10px;"
                )
                # Hiển thị thông báo dùng thử cho user
                if role == "user":
                    QMessageBox.information(
                        self,
                        "Thông báo dùng thử",
                        "Bạn đang sử dụng tài khoản dùng thử. Hạn sử dụng: 3 ngày kể từ ngày đăng ký.",
                    )
                # Chuyển về chế độ đăng nhập (login)
                self.switch_to_register()  # Chuyển về login mode
            else:
                self.status_label.setText(msg)
                self.status_label.setStyleSheet(
                    "color:#dc2626; font-size:11px; border:none; background:#fef2f2; "
                    "border-radius:8px; padding:8px 10px;"
                )

    def save_remember_me_session(self, username):
        session_data = {
            "username": username,
            "timestamp": datetime.utcnow().isoformat(),
        }
        try:
            import json

            with open("session.json", "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi khi lưu phiên đăng nhập: {str(e)}")

    def _parse_iso_datetime(self, value):
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None

    def _is_user_trial_expired(self, user):
        if not user or user.get("role") != "user":
            return False

        expired = user.get("expired_at")
        if not expired:
            created = user.get("created_at")
            if isinstance(created, str):
                created = self._parse_iso_datetime(created)
            if not created:
                return True
            expired = created + timedelta(days=self.REMEMBER_ME_DAYS)
        elif isinstance(expired, str):
            expired = self._parse_iso_datetime(expired)

        if not expired:
            return True
        return datetime.utcnow() > expired

    def load_remember_me_session(self, return_status=False):
        session_file = "session.json"
        if os.path.exists(session_file):
            try:
                import json

                with open(session_file, "r", encoding="utf-8") as f:
                    session_data = json.load(f)
                username = session_data.get("username")
                timestamp = self._parse_iso_datetime(session_data.get("timestamp"))

                if not username or not timestamp:
                    self.clear_remember_me_session()
                    msg = "Phiên ghi nhớ đăng nhập không hợp lệ và đã được xóa."
                    return (None, msg) if return_status else None

                user = self.user_manager.get_user(username)
                if not user:
                    self.clear_remember_me_session()
                    msg = "Tài khoản đã lưu không còn tồn tại."
                    return (None, msg) if return_status else None

                role = str(user.get("role", "")).strip().lower()

                # Chỉ user dùng thử mới giới hạn phiên ghi nhớ 3 ngày; admin/tester không hết hạn.
                if role == "user":
                    if datetime.utcnow() - timestamp > timedelta(days=self.REMEMBER_ME_DAYS):
                        self.clear_remember_me_session()
                        msg = "Phiên ghi nhớ đăng nhập đã hết hạn sau 3 ngày."
                        return (None, msg) if return_status else None

                    if self._is_user_trial_expired(user):
                        self.clear_remember_me_session()
                        msg = "Tài khoản user đã hết hạn sử dụng (3 ngày)."
                        return (None, msg) if return_status else None

                return (username, None) if return_status else username
            except Exception:
                self.clear_remember_me_session()
                msg = "Không thể đọc phiên ghi nhớ đăng nhập."
                return (None, msg) if return_status else None
        return (None, None) if return_status else None

    def clear_remember_me_session(self):
        session_file = "session.json"
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
            except:
                pass
