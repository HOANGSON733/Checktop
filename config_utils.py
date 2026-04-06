"""
config_utils.py
Xử lý đọc/ghi cấu hình, proxy, user-agent, lưu/đổi tên cấu hình.
"""

import json
import os
from datetime import datetime
from PyQt5.QtWidgets import QInputDialog, QMessageBox


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
        QMessageBox.critical(self, self.t("error"), self.t("error_save").format(str(e)))


def save_proxy_config(self):
    """Lưu cấu hình proxy"""
    proxy_list = self.proxy_list_input.toPlainText().strip()

    if self.enable_proxy_checkbox.isChecked() and not proxy_list:
        QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập danh sách proxy!")
        return

    # Kiểm tra định dạng proxy
    if proxy_list:
        proxy_lines = [line.strip() for line in proxy_list.split("\n") if line.strip()]
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
