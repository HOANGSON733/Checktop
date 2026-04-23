import sys
import os
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5.QtGui import QIcon
from gui import KeywordSearchGUI
from login import LoginDialog
from search_logic import run_headless
from utils import resource_path


def main():
    # ⚡ Fix lỗi render Qt (khuyên dùng)
    os.environ["QT_OPENGL"] = "software"

    if len(sys.argv) > 1 and sys.argv[1] == "--headless":
        run_headless()
    else:
        # ✅ TẠO app TRƯỚC
        app = QApplication(sys.argv)

        app.setStyle("Fusion")
        app.setQuitOnLastWindowClosed(True)

        # ✅ set icon SAU khi có app
        app.setWindowIcon(QIcon(resource_path("logo1.png")))

        login_dialog = LoginDialog()
        remembered_user, session_notice = login_dialog.load_remember_me_session(
            return_status=True
        )

        if remembered_user:
            window = KeywordSearchGUI(current_user=remembered_user)
            window.show()
            sys.exit(app.exec_())
        else:
            if session_notice:
                QMessageBox.information(login_dialog, "Phiên đăng nhập", session_notice)
            if login_dialog.exec_() == QDialog.Accepted:
                window = KeywordSearchGUI(current_user=login_dialog.logged_in_user)
                window.show()
                sys.exit(app.exec_())
            else:
                sys.exit(0)


if __name__ == "__main__":
    main()