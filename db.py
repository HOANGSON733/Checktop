def ensure_default_admins():
    """Tạo 2 tài khoản admin mặc định nếu chưa có admin nào."""
    user_manager = UserManager()
    admin_count = user_manager.users.count_documents({"role": "admin"})
    if admin_count == 0:
        # Tạo 2 admin mặc định
        user_manager.users.insert_one({
            "username": "admin1",
            "password": user_manager.hash_password("admin123"),
            "role": "admin",
            "created_at": datetime.utcnow()
        })
        user_manager.users.insert_one({
            "username": "admin2",
            "password": user_manager.hash_password("admin123"),
            "role": "admin",
            "created_at": datetime.utcnow()
        })
        print("Đã tạo 2 tài khoản admin mặc định: admin1/admin123, admin2/admin123")
import pymongo, os
import threading
from dotenv import load_dotenv

# ===============================
# MODEL LAYER
# ===============================



from datetime import datetime, timedelta
import hashlib

class DatabaseConnection:
    """Singleton class để quản lý kết nối MongoDB (thread-safe)"""
    _instance = None
    _client = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def connect(self):
        if self._client is None:
            with self._lock:
                if self._client is None:
                    load_dotenv()
                    mongo_uri = "mongodb://seadragon:seadragon%40admin@crm.sdtc.vn:27017/"
                    self._client = pymongo.MongoClient(mongo_uri, maxPoolSize=50)
        return self._client

    def get_database(self, db_name="checktop_app"):
        client = self.connect()
        return client[db_name]

    def close(self):
        with self._lock:
            if self._client:
                self._client.close()
                self._client = None


class UserManager:
    """Quản lý user, đăng ký, đăng nhập, phân quyền, kiểm tra hạn sử dụng"""
    def __init__(self, db_name="checktop_app"):
        self.db = DatabaseConnection().get_database(db_name)
        self.users = self.db["users"]

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password, role="user", creator_role=None, machine_info=None):
        """
        Đăng ký user mới. Ai cũng đăng ký được user. Chỉ admin mới tạo được admin/tester.
        creator_role: role của người tạo (None nếu tự đăng ký)
        machine_info: dict thông tin máy (hostname, mac, os)
        """
        if self.users.find_one({"username": username}):
            return False, "Tên đăng nhập đã tồn tại!"
        if role in ["admin", "tester"] and creator_role != "admin":
            return False, "Chỉ admin mới tạo được tài khoản admin/tester."
        now = datetime.utcnow()
        user_doc = {
            "username": username,
            "password": self.hash_password(password),
            "role": role,
            "created_at": now,
        }
        if machine_info:
            user_doc["machine_info"] = machine_info
        if role == "user":
            user_doc["expired_at"] = now + timedelta(days=3)
        self.users.insert_one(user_doc)
        return True, "Đăng ký thành công!"

    def login(self, username, password):
        user = self.users.find_one({"username": username})
        if not user:
            return False, "Sai tên đăng nhập hoặc mật khẩu!", None
        if user["password"] != self.hash_password(password):
            return False, "Sai tên đăng nhập hoặc mật khẩu!", None
        # Kiểm tra hạn sử dụng nếu là user
        if user["role"] == "user":
            expired = user.get("expired_at")
            if not expired:
                # Nếu chưa có expired_at, fallback về created_at + 3 ngày
                created = user.get("created_at")
                if not created:
                    return False, "Tài khoản không hợp lệ!", None
                if isinstance(created, str):
                    created = datetime.fromisoformat(created)
                expired = created + timedelta(days=3)
            if isinstance(expired, str):
                expired = datetime.fromisoformat(expired)
            if datetime.utcnow() > expired:
                return False, "Tài khoản user đã hết hạn sử dụng (3 ngày)!", None
        return True, "Đăng nhập thành công!", user["role"]

    def get_user(self, username):
        return self.users.find_one({"username": username})

    def set_role(self, username, new_role, admin_username):
        admin = self.get_user(admin_username)
        if not admin or admin["role"] != "admin":
            return False, "Chỉ admin mới được đổi quyền."
        if new_role not in ["admin", "tester", "user"]:
            return False, "Role không hợp lệ."
        self.users.update_one({"username": username}, {"$set": {"role": new_role}})
        return True, "Đã đổi quyền thành công."

    def list_users(self):
        return list(self.users.find({}, {"_id": 0, "password": 0}))
