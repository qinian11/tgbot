import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers.commands import start
from handlers.buttons import button_callback
from handlers.conversation import handle_user_input
from services.database import init_db


TOKEN = "7285003048:AAEscHyR5pSuhFrFtvPpAcD2G0Fe1pdyI9A"
def main():
    # 初始化数据库
    init_db()

    # 配置日志模块
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO  # 设置日志级别为 INFO
    )
    logger = logging.getLogger(__name__)  # 创建日志记录器

    # 创建机器人应用程序
    app = Application.builder().token(TOKEN).build()

    # 日志消息：程序启动
    logger.info("机器人正在启动...")

    # 注册命令
    app.add_handler(CommandHandler("start", start))

    # 注册按钮回调
    app.add_handler(CallbackQueryHandler(button_callback))

    # 注册用户输入消息处理
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))

    # 启动机器人
    logger.info("机器人已启动，正在监听消息...")
    app.run_polling()

if __name__ == "__main__":
    main()