import sqlite3
from datetime import datetime

class ChatDatabase:
    def __init__(self, db_name="chat_room_v4.db"):
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        # اتصال به دیتابیس و ساخت جدول 
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                receiver TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def save_message(self, sender, message, receiver=None):
        # ذخیره پیام جدید
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%H:%M:%S")
        cursor.execute('''
            INSERT INTO messages (sender, message, receiver, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (sender, message, receiver, timestamp))
        conn.commit()
        conn.close()

    def get_messages_for_user(self, username):
        """
        فقط پیام‌هایی رو برمیگردونه که کاربر حق دیدنشون رو داره:
        - receiver IS NULL  → پیام عمومی (همه باید ببینن)
        - receiver = username → پیام خصوصی که برای من اومده
        - sender = username   → پیام خصوصی که من فرستادم
        بقیه (خصوصی بین دو نفر دیگه) مخفی می‌مونه.
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sender, message, receiver, timestamp
            FROM messages
            WHERE receiver IS NULL
               OR receiver = ?
               OR sender = ?
            ORDER BY id DESC
            LIMIT 20
        ''', (username, username))
        rows = cursor.fetchall()
        conn.close()
        # برگردوندن از بالا به پایین
        return rows[::-1]
