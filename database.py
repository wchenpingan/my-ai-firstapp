import sqlite3
import hashlib  # 👈 用来给密码加密的（安全第一）

DB_NAME = "chat_history.db"


def create_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 1. 聊天记录表 (加了一列 username，用来区分是谁聊的)
    c.execute('''
              CREATE TABLE IF NOT EXISTS history
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  username
                  TEXT,
                  role
                  TEXT,
                  content
                  TEXT
              )
              ''')
    # 2. 用户表 (存账号密码)
    c.execute('''
              CREATE TABLE IF NOT EXISTS users
              (
                  username
                  TEXT
                  PRIMARY
                  KEY,
                  password
                  TEXT
              )
              ''')
    conn.commit()
    conn.close()


# --- 新增：用户管理功能 ---

def make_password_safe(password):
    """把明文密码变成乱码 (哈希)，这样黑客偷了数据库也看不懂"""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    """注册新用户"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        safe_password = make_password_safe(password)
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, safe_password))
        conn.commit()
        return True  # 注册成功
    except sqlite3.IntegrityError:
        return False  # 注册失败（用户名可能重复了）
    finally:
        conn.close()


def login_user(username, password):
    """验证登录"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    safe_password = make_password_safe(password)
    # 查查有没有这个用户名和密码匹配的人
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, safe_password))
    result = c.fetchone()
    conn.close()
    return result is not None  # 如果找到了，返回 True


# --- 修改：聊天记录功能 (加上 username) ---

def add_message(username, role, content):
    """记账的时候，要带上用户名"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO history (username, role, content) VALUES (?, ?, ?)', (username, role, content))
    conn.commit()
    conn.close()


def get_history(username):
    """查账的时候，只查这个用户的"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT role, content FROM history WHERE username = ?', (username,))
    data = c.fetchall()
    conn.close()

    formatted_data = []
    for row in data:
        formatted_data.append({"role": row[0], "content": row[1]})
    return formatted_data