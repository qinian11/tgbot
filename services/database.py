import sqlite3
import os

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'bot_database.db')  # 获取数据库的绝对路径

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 启用外键约束
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 用户唯一 ID
            telegram_id TEXT UNIQUE NOT NULL,       -- 用户的 Telegram ID
            is_push_enabled BOOLEAN DEFAULT 1       -- 是否启用推送 (0=禁用, 1=启用)
        )
    """)
    #bound_actors TEXT NOT NULL, -- 用户绑定的演员列表，用逗号分隔,改进前的代码

    # 用户与演员的绑定关系，建立一个独立的多对多关系表user_actor_binding表
    # 用户表
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_actor_binding (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                actor_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (actor_id) REFERENCES actors (id) ON DELETE CASCADE,
                UNIQUE(user_id, actor_id)
            )
        """)

    # 演员表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 演员唯一 ID
            name TEXT NOT NULL  UNIQUE                    -- 演员名
        )
    """)

    # 资源表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 资源唯一 ID
            actor_id INTEGER NOT NULL,              -- 关联的演员 ID
            title TEXT NOT NULL,                    -- 资源标题
            image_url TEXT,                         -- 资源图片链接
            magnet TEXT NOT NULL,                   -- 磁力链接
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (actor_id) REFERENCES actors (id) ON DELETE CASCADE -- 外键关联演员表
        )
    """)

    # 推送日志表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS push_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 推送日志唯一 ID
            user_id INTEGER NOT NULL,               -- 关联的用户 ID
            resource_id INTEGER NOT NULL,           -- 关联的资源 ID
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, -- 推送时间
            status TEXT DEFAULT 'success',          -- 推送状态（success, failed）
            error_message TEXT,                     -- 失败原因（仅在 status 为 failed 时填写）
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE, -- 外键关联用户表
            FOREIGN KEY (resource_id) REFERENCES resources (id) ON DELETE CASCADE -- 外键关联资源表
        )
    """)

    # 提交所有表创建操作
    conn.commit()

    # 创建索引（可选，用于查询优化）
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_telegram_id ON users (telegram_id);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_actor_name ON actors (name);
    """)

    conn.commit()
    conn.close()
