from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 你的 Bot Token（替换成你自己的）
TOKEN = "7905072858:AAEtXopc9kNe-92qlgCweRQ302Q2ycqMRI0"

# 处理 /start 命令
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("你好！我是你的 Telegram 机器人 😊")

# 处理普通消息（回声功能）
async def echo(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    await update.message.reply_text(f"你说了: {user_text}")

def main():
    app = Application.builder().token(TOKEN).build()

    # 添加指令处理
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("机器人已启动！")
    app.run_polling()

if __name__ == '__main__':
    main()
