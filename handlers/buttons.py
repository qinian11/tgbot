from telegram import Update
from telegram.ext import ContextTypes
import sqlite3
from services.database import DB_PATH


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮点击事件"""
    query = update.callback_query
    action = query.data  # 获取按钮的回调数据
    await query.answer()  # 确保按钮被点击后不加载

    user_id = query.from_user.id

    # 使用上下文管理器处理数据库连接
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        if action == "bind_tgid":
            # 绑定 TGID
            await query.message.reply_text("请发送您的 TGID：")
            context.user_data["action"] = "bind_tgid"

        elif action == "add_actor":
            # 添加演员
            await query.message.reply_text("请发送要添加的演员名称（如有多个请用空格或者逗号隔开）：")
            context.user_data["action"] = "add_actor"

        elif action == "remove_actor":
            # 删除演员
            await query.message.reply_text("请发送要删除的演员名称：")
            context.user_data["action"] = "remove_actor"

        elif action == "clear_actors":
            # 清空演员
            try:
                # 删除用户与演员的绑定关系
                cursor.execute("""
                    DELETE FROM user_actor_binding 
                    WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?)
                """, (user_id,))
                conn.commit()
                await query.message.reply_text("演员列表已清空！")
            except Exception as e:
                await query.message.reply_text(f"清空演员列表失败，错误信息：{e}")

        elif action == "view_actors":
            # 查看演员列表
            try:
                # 查询用户绑定的演员
                cursor.execute("""
                    SELECT a.name
                    FROM user_actor_binding uab
                    JOIN actors a ON uab.actor_id = a.id
                    WHERE uab.user_id = (SELECT id FROM users WHERE telegram_id = ?)
                """, (user_id,))
                actors = [row[0] for row in cursor.fetchall()]
                num_actors = len(actors)  # 统计演员数量

                if actors:
                    # 使用 <code> 标签格式化演员列表
                    actor_list = " ".join([f"<code>{actor}</code>" for actor in actors])
                    await query.message.reply_text(
                        f"当前演员列表（{num_actors} 个）：{actor_list}",
                        parse_mode="HTML"
                    )
                else:
                    await query.message.reply_text("当前没有添加任何演员。")
            except Exception as e:
                await query.message.reply_text(f"获取演员列表失败，错误信息：{e}")

        elif action == "add_push":
            # 添加推送频道
            await query.message.reply_text("请发送要推送的频道名称：")
            context.user_data["action"] = "add_push"

        elif action == "remove_push":
            # 删除推送频道
            await query.message.reply_text("请发送要删除的频道名称：")
            context.user_data["action"] = "remove_push"

        elif action == "view_pushes":
            # 查看推送频道
            try:
                cursor.execute("""
                    SELECT resource_id 
                    FROM push_logs 
                    WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?)
                """, (user_id,))
                pushes = [row[0] for row in cursor.fetchall()]

                if pushes:
                    # 在频道名称前添加 "@"
                    push_list = "\n".join([f"@{push}" for push in pushes])
                    await query.message.reply_text(f"当前绑定的推送频道：\n{push_list}")
                else:
                    await query.message.reply_text("当前没有绑定任何推送频道。")
            except Exception as e:
                await query.message.reply_text(f"获取推送频道失败，错误信息：{e}")

        elif action == "enable_push":
            # 启用推送
            try:
                cursor.execute("UPDATE users SET is_push_enabled = 1 WHERE telegram_id = ?", (user_id,))
                conn.commit()
                await query.message.reply_text("推送功能已开启！")
            except Exception as e:
                await query.message.reply_text(f"启用推送失败，错误信息：{e}")

        elif action == "disable_push":
            # 禁用推送
            try:
                cursor.execute("UPDATE users SET is_push_enabled = 0 WHERE telegram_id = ?", (user_id,))
                conn.commit()
                await query.message.reply_text("推送功能已关闭！")
            except Exception as e:
                await query.message.reply_text(f"禁用推送失败，错误信息：{e}")

        elif action == "view_bot":
            # 查看机器人状态
            try:
                cursor.execute("SELECT id, telegram_id, is_push_enabled FROM users WHERE telegram_id = ?", (user_id,))
                user = cursor.fetchone()

                if user:
                    user_db_id = user[0]
                    telegram_id = user[1]
                    is_push_enabled = "开启" if user[2] == 1 else "关闭"

                    # 获取绑定的演员
                    cursor.execute("""
                        SELECT a.name
                        FROM user_actor_binding uab
                        JOIN actors a ON uab.actor_id = a.id
                        WHERE uab.user_id = ?
                    """, (user_db_id,))
                    bound_actors = [row[0] for row in cursor.fetchall()]
                    num_actors = len(bound_actors)

                    # 获取推送频道
                    cursor.execute("""
                        SELECT resource_id
                        FROM push_logs
                        WHERE user_id = ?
                    """, (user_db_id,))
                    push_channels = [f"@{row[0]}" for row in cursor.fetchall()]

                    # 格式化状态信息
                    status_message = (
                        f"<b>机器人状态信息：</b>\n"
                        f"<b>绑定ID：</b><code>{telegram_id}</code>\n"
                        f"<b>推送功能：</b>{is_push_enabled}\n\n"
                        f"<b>推送频道：</b>{', '.join(push_channels) if push_channels else '无'}\n\n"
                        f"<b>订阅演员信息（{num_actors} 个）：</b>\n"
                        f"{' '.join([f'<code>{actor}</code>' for actor in bound_actors]) if bound_actors else '无'}"
                    )
                else:
                    status_message = "未找到您的信息，请先绑定 TGID。"

                await query.message.reply_text(status_message, parse_mode="HTML")
            except Exception as e:
                await query.message.reply_text(f"获取机器人状态失败，错误信息：{e}")

        else:
            await query.message.reply_text("未知操作，请重试。")
