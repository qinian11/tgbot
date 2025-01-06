from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import os

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""

    # 获取用户的 Telegram ID
    tg_id = update.message.from_user.id

    # 定义按钮
    keyboard = [
        [InlineKeyboardButton("绑定TGID", callback_data="bind_tgid")],
        [InlineKeyboardButton("添加演员", callback_data="add_actor"), InlineKeyboardButton("删除演员", callback_data="remove_actor")],
        [InlineKeyboardButton("查看演员", callback_data="view_actors"), InlineKeyboardButton("清空演员", callback_data="clear_actors")],
        [InlineKeyboardButton("添加推送", callback_data="add_push"), InlineKeyboardButton("删除推送", callback_data="remove_push")],
        [InlineKeyboardButton("查看推送频道", callback_data="view_pushes")],
        [InlineKeyboardButton("开启推送", callback_data="enable_push"), InlineKeyboardButton("关闭推送", callback_data="disable_push")],
        [InlineKeyboardButton("查看机器人状态", callback_data="view_bot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 设置图片路径
    photo_path = os.path.join(os.path.dirname(__file__), "会员.jpg")

    # 发送图片和按钮界面
    try:
        await update.message.reply_photo(
            photo=open(photo_path, "rb"),
            caption=(
                f"欢迎使用推送机器人！\n"
                f"你的ID为：`{tg_id}`\n\n"
                f"请选择以下操作：\n"
                "- 绑定TGID: 用于绑定用户到机器人。\n"
                "- 添加演员: 添加关注的演员。\n"
                "- 删除演员: 删除不再关注的演员。\n"
                "- 查看演员: 查看所有已绑定的演员。\n"
                "- 清空演员: 删除所有绑定的演员。\n"
                "- 添加推送: 添加推送的目标频道。\n"
                "- 删除推送: 移除推送的目标频道。\n"
                "- 查看推送频道: 查看当前绑定的推送频道。\n"
                "- 开启推送: 开始接收推送消息。\n"
                "- 关闭推送: 停止接收推送消息。\n"
                "- 查看机器人状态: 查看机器人当前的绑定信息。\n"
            ),
            parse_mode="Markdown",  # 使用 Markdown 格式
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(
            f"无法发送图片，请检查文件路径是否正确。\n错误信息：{e}"
        )
