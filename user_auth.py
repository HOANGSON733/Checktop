from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QPushButton,
    QFormLayout,
    QMessageBox,
    QCheckBox,
    QComboBox,
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from db import UserManager
from datetime import datetime
import os


class LoginDialog(QDialog):
    """Dialog đăng nhập/đăng ký sử dụng MongoDB"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "login"
        self.logged_in_user = None
        self.user_role = None
        self.user_manager = UserManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Đăng nhập - Công cụ Tìm kiếm Từ khóa")
        self.setModal(True)
        self.setFixedSize(400, 340)
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        title_label = QLabel("Đăng nhập vào hệ thống")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên đăng nhập...")
        self.username_input.setMinimumHeight(35)
        form_layout.addRow("👤 Tên đăng nhập:", self.username_input)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Nhập mật khẩu...")
        self.password_input.setMinimumHeight(35)
        form_layout.addRow("🔑 Mật khẩu:", self.password_input)
        self.remember_me_checkbox = QCheckBox("Ghi nhớ đăng nhập")
        self.remember_me_checkbox.setFont(QFont("Arial", 9))
        self.remember_me_checkbox.setMinimumHeight(25)
        form_layout.addRow("", self.remember_me_checkbox)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Nhập lại mật khẩu...")
        self.confirm_password_input.setMinimumHeight(35)
        self.confirm_password_label = QLabel("🔒 Xác nhận mật khẩu:")
        form_layout.addRow(self.confirm_password_label, self.confirm_password_input)
        self.confirm_password_label.setVisible(False)
        self.confirm_password_input.setVisible(False)
        # Role selector (chỉ hiện khi đăng ký, nếu là admin)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "tester", "admin"])
        self.role_label = QLabel("Quyền tài khoản:")
        form_layout.addRow(self.role_label, self.role_combo)
        self.role_label.setVisible(False)
        self.role_combo.setVisible(False)
        layout.addLayout(form_layout)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.login_button = QPushButton("Đăng nhập")
        self.login_button.setStyleSheet(
            """
			QPushButton {
				background-color: #4CAF50;
				color: white;
				font-weight: bold;
				padding: 10px 20px;
				border-radius: 5px;
				border: none;
				min-width: 120px;
			}
			QPushButton:hover {
				background-color: #45a049;
			}
		"""
        )
        self.login_button.clicked.connect(self.login)
        button_layout.addWidget(self.login_button)
        self.register_button = QPushButton("Đăng ký")
        self.register_button.setStyleSheet(
            """
			QPushButton {
				background-color: #2196F3;
				color: white;
				font-weight: bold;
				padding: 10px 20px;
				border-radius: 5px;
				border: none;
				min-width: 120px;
			}
			QPushButton:hover {
				background-color: #1976D2;
			}
		"""
        )
        self.register_button.clicked.connect(self.switch_to_register)
        button_layout.addWidget(self.register_button)
        layout.addLayout(button_layout)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-size: 10px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def switch_to_register(self):
        if self.mode == "login":
            self.mode = "register"
            self.setWindowTitle("Đăng ký - Công cụ Tìm kiếm Từ khóa")
            self.login_button.setText("Tạo tài khoản")
            self.register_button.setText("Quay lại đăng nhập")
            self.confirm_password_label.setVisible(True)
            self.confirm_password_input.setVisible(True)
            # Nếu là admin thì cho chọn role, còn lại ẩn
            self.role_label.setVisible(self.is_admin())
            self.role_combo.setVisible(self.is_admin())
            self.status_label.setText("Chế độ đăng ký - Tạo tài khoản mới")
        else:
            self.mode = "login"
            self.setWindowTitle("Đăng nhập - Công cụ Tìm kiếm Từ khóa")
            self.login_button.setText("Đăng nhập")
            self.register_button.setText("Đăng ký")
            self.confirm_password_label.setVisible(False)
            self.confirm_password_input.setVisible(False)
            self.role_label.setVisible(False)
            self.role_combo.setVisible(False)
            self.status_label.setText("")

    def is_admin(self):
        # Đơn giản: nếu đã đăng nhập và role là admin
        return self.user_role == "admin"

    def login(self):
        import platform, uuid, socket
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.status_label.setText("❌ Vui lòng nhập đầy đủ thông tin!")
            self.status_label.setStyleSheet("color: #f44336; font-size: 10px;")
            return
        if self.mode == "login":
            ok, msg, role = self.user_manager.login(username, password)
            if ok:
                self.logged_in_user = username
                self.user_role = role
                self.status_label.setText("✅ Đăng nhập thành công!")
                self.status_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
                if self.remember_me_checkbox.isChecked():
                    self.save_remember_me_session(username)
                # Nếu là user, hiển thị thông báo dùng thử còn lại bao nhiêu ngày
                if role == "user":
                    user = self.user_manager.get_user(username)
                    created = user.get("created_at")
                    if isinstance(created, str):
                        created = datetime.fromisoformat(created)
                    days_left = 3 - (datetime.utcnow() - created).days
                    if days_left > 0:
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
                self.status_label.setText(f"❌ {msg}")
                self.status_label.setStyleSheet("color: #f44336; font-size: 10px;")
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
                self.status_label.setText("❌ Mật khẩu xác nhận không khớp!")
                self.status_label.setStyleSheet("color: #f44336; font-size: 10px;")
                return
            # Nếu là admin thì cho chọn role, còn lại chỉ được user
            role = self.role_combo.currentText() if self.is_admin() else "user"
            # Kiểm tra đã có user với cùng thông tin máy chưa
            if self.user_manager.users.find_one({"machine_info": machine_info}):
                self.status_label.setText("❌ Máy này đã đăng ký tài khoản trước đó!")
                self.status_label.setStyleSheet("color: #f44336; font-size: 10px;")
                return
            ok, msg = self.user_manager.register(
                username, password, role=role, creator_role=self.user_role, machine_info=machine_info
            )
            if ok:
                self.status_label.setText(
                    "✅ Đăng ký thành công! Vui lòng đăng nhập để sử dụng."
                )
                self.status_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
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
                self.status_label.setText(f"❌ {msg}")
                self.status_label.setStyleSheet("color: #f44336; font-size: 10px;")

    def save_remember_me_session(self, username):
        session_data = {"username": username, "timestamp": datetime.now().isoformat()}
        try:
            import json

            with open("session.json", "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi khi lưu phiên đăng nhập: {str(e)}")

    def load_remember_me_session(self):
        session_file = "session.json"
        if os.path.exists(session_file):
            try:
                import json

                with open(session_file, "r", encoding="utf-8") as f:
                    session_data = json.load(f)
                return session_data.get("username")
            except:
                return None
        return None

    def clear_remember_me_session(self):
        session_file = "session.json"
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
            except:
                pass
