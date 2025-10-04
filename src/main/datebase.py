import sqlite3
import os

# 使用与本文件同级的 qq.db，确保从任何工作目录都能定位到 src/main/qq.db
DB_PATH = os.path.join(os.path.dirname(__file__), 'qq.db')

def create_table():
    """Create database table, skip if table already exists"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT,
            message_id TEXT,
            message TEXT,
            time TEXT
        )
    ''')
    conn.commit()
    conn.close()

def init_database():
    """Initialize database, create if database file doesn't exist"""
    if not os.path.exists(DB_PATH):
        print("Database file not found, creating new database...")
        create_table()
        print("Database initialized successfully!")
    else:
        # 文件已存在也确保表存在
        create_table()
        print("Database file exists, ensured table.")

def insert_data(group_id, message_id, message, time):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO qq (group_id, message_id, message, time) VALUES (?, ?, ?, ?)
    ''', (group_id, message_id, message, time))
    conn.commit()
    conn.close()

def remove_data(group_id, message_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM qq WHERE group_id = ? AND message_id = ?
    ''', (group_id, message_id))
    conn.commit()
    conn.close()

def find_if_exist(group_id, message_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM qq WHERE group_id = ? AND message_id = ?
    ''', (group_id, message_id))
    result = cursor.fetchone()
    conn.close()
    return result

def iter_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM qq
    ''')
    result = cursor.fetchall()
    conn.close()
    return result


def get_next_message_id_for_group_1() -> str:
    """Return next message_id (as string) for group_id='1'. Start from '1' if none."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT MAX(CAST(message_id AS INTEGER)) FROM qq WHERE group_id = '1'
    ''')
    row = cursor.fetchone()
    conn.close()
    max_id = (row[0] if row and row[0] is not None else 0)
    try:
        next_id = int(max_id) + 1
    except Exception:
        next_id = 1
    return str(next_id)
def remove_all_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM qq
    ''')
    conn.commit()
    conn.close()
if __name__ == "__main__":
    remove_all_data()
    # remove_data('1062848088', '889743639')
    for i in iter_data():
        print(i)