# conversation.py
from telegram import Update
from telegram.ext import ContextTypes
import sqlite3
from services.database import DB_PATH


async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理用户发送的后续消息"""
    action = context.user_data.get("action")
    text = update.message.text.strip()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if action == "bind_tgid":
        # 绑定 TGID 到数据库
        try:
            telegram_id = text
            cursor.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (telegram_id,))
            conn.commit()
            await update.message.reply_text(f"TGID {telegram_id} 已绑定！")
        except Exception as e:
            await update.message.reply_text(f"绑定 TGID 失败，错误信息：{e}")


    elif action == "add_actor":
        # 添加多个演员到用户的绑定列表
        try:
            actor_names = text.strip()  # 获取用户输入的演员名称
            actor_list = [actor.strip() for actor in actor_names.replace(",", " ").split()]

            # 获取用户 ID
            user_id = update.effective_user.id
            cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
            user = cursor.fetchone()
            if not user:
                await update.message.reply_text("请先绑定 TGID。")
                return
            user_db_id = user[0]

            new_actors = []
            for actor_name in actor_list:
                # 添加演员到 actors 表（如果不存在）
                cursor.execute("INSERT OR IGNORE INTO actors (name) VALUES (?)", (actor_name,))
                # 获取演员 ID
                cursor.execute("SELECT id FROM actors WHERE name = ?", (actor_name,))
                actor = cursor.fetchone()
                if actor:
                    actor_id = actor[0]
                    # 绑定用户与演员的关系
                    cursor.execute("""
                        INSERT OR IGNORE INTO user_actor_binding (user_id, actor_id)
                        VALUES (?, ?)
                    """, (user_db_id, actor_id))
                    new_actors.append(actor_name)

            conn.commit()

            if new_actors:
                await update.message.reply_text(f"成功添加了 {len(new_actors)} 个演员：{', '.join(new_actors)}")
            else:
                await update.message.reply_text(f"这些演员已经绑定：{', '.join(actor_list)}")
        except Exception as e:
            await update.message.reply_text(f"添加演员失败，错误信息：{e}")

    elif action == "remove_actor":
        # 从用户的绑定列表中删除演员
        try:
            actor_name = text.strip()

            # 获取用户 ID
            user_id = update.effective_user.id
            cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
            user = cursor.fetchone()
            if not user:
                await update.message.reply_text("请先绑定 TGID。")
                return
            user_db_id = user[0]

            # 检查演员是否已绑定
            cursor.execute("""
                SELECT a.id
                FROM user_actor_binding uab
                JOIN actors a ON uab.actor_id = a.id
                WHERE uab.user_id = ? AND a.name = ?
            """, (user_db_id, actor_name))
            actor = cursor.fetchone()
            if not actor:
                await update.message.reply_text(f"演员 {actor_name} 未绑定！")
                return

            # 删除用户与演员的绑定关系
            actor_id = actor[0]
            cursor.execute("DELETE FROM user_actor_binding WHERE user_id = ? AND actor_id = ?", (user_db_id, actor_id))
            conn.commit()
            await update.message.reply_text(f"演员 {actor_name} 已成功移除！")
        except Exception as e:
            await update.message.reply_text(f"删除演员失败，错误信息：{e}")

    elif action == "add_push":
        # 添加推送频道
        try:
            user_id = update.effective_user.id
            channel_name = text.strip()

            # 检查输入是否合法
            if not channel_name.startswith("@") and "t.me/" not in channel_name:
                await update.message.reply_text("请输入有效的频道用户名或链接，例如 @channel 或 t.me/channel。")
                return

            # 处理频道名称
            if channel_name.startswith("@"):
                channel_name = channel_name[1:]  # 去掉 @
            elif "t.me/" in channel_name:
                channel_name = channel_name.split("t.me/")[-1].strip("/")  # 提取频道用户名

            # 检查用户是否存在
            cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
            result = cursor.fetchone()
            if not result:
                await update.message.reply_text("请先绑定 TGID 后再尝试添加推送频道。")
                return
            user_db_id = result[0]

            # 检查推送频道是否已存在
            cursor.execute("SELECT id FROM push_logs WHERE user_id = ? AND resource_id = ?", (user_db_id, channel_name))
            if cursor.fetchone():
                await update.message.reply_text(f"请勿重复添加推送频道 '@{channel_name}'")
                return
            # 插入推送频道
            cursor.execute("INSERT INTO push_logs (user_id, resource_id) VALUES (?, ?)", (user_db_id, channel_name))
            conn.commit()
            await update.message.reply_text(f"推送频道 '@{channel_name}' 已成功添加！")
        except Exception as e:
            await update.message.reply_text(f"添加推送失败，错误信息：{e}")

    elif action == "remove_push":
        # 移除推送频道
        try:
            user_id = update.effective_user.id
            channel_name = text.strip()

            # 处理频道名称
            if channel_name.startswith("@"):
                channel_name = channel_name[1:]  # 去掉 @
            elif "t.me/" in channel_name:
                channel_name = channel_name.split("t.me/")[-1].strip("/")  # 提取频道用户名

            # 检查推送频道是否存在
            cursor.execute("""
                SELECT id FROM push_logs
                WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?)
                AND resource_id = ?
            """, (user_id, channel_name))
            result = cursor.fetchone()
            if not result:
                await update.message.reply_text(f"推送频道 '@{channel_name}' 未绑定！")
                return

            # 删除推送频道
            cursor.execute("DELETE FROM push_logs WHERE id = ?", (result[0],))
            conn.commit()
            await update.message.reply_text(f"推送频道 '@{channel_name}' 已成功移除！")
        except Exception as e:
            await update.message.reply_text(f"移除推送失败，错误信息：{e}")

    else:
        # 无效操作
        await update.message.reply_text("无效的操作，请重新发送 /start。")

    # 清除用户当前操作状态
    context.user_data["action"] = None
    conn.close()
