import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackContext, CallbackQueryHandler
)
from datetime import time, timedelta, timezone
from flask import Flask
from threading import Thread

TOKEN = "7905072858:AAEtXopc9kNe-92qlgCweRQ302Q2ycqMRI0"
WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", 5000))  # Render 会自动设置端口
BASE_URL = "https://telegram-bot-z8zl.onrender.com"  # 改成你的 Render 域名

# --- Telegram Bot Handlers ---

async def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    with open("user_ids.txt", "a") as f:
        f.write(f"{chat_id}\n")
    with open("welcome.png", "rb") as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo, caption="Welcome to VictorBet💎👇")

    keyboard = [
        [InlineKeyboardButton("📝 Register", callback_data="register")],
        [InlineKeyboardButton("🚀 New Telegram Channel", callback_data="telegram_channel")],
        [InlineKeyboardButton("📲 Contact us", callback_data="contact_us")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select option at below：", reply_markup=reply_markup)

async def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "register":
        await query.message.reply_text("👇 Tekan link bawah utk register ya:\nhttps://www.victorbet.net/download/url?referral=3FLEBW")
    elif query.data == "telegram_channel":
        await query.message.reply_text("🔊 Tekan link join channel: \nhttps://t.me/Victorbet_Channel")
    elif query.data == "contact_us":
        await query.message.reply_text("💬 Tekan link utk chat CS: \nhttps://direct.lc.chat/14684676/")

async def keyword_reply(update: Update, context: CallbackContext) -> None:
    text = update.message.text.lower()
    if "hi boss" in text or "daftar" in text:
        await update.message.reply_text("👇 Tekan link bawah utk register ya:\nhttps://www.victorbet.net/download/url?referral=3FLEBW")
    elif "livechat" in text:
        await update.message.reply_text("💬 Tekan link utk chat CS: \nhttps://direct.lc.chat/14684676/")
    else:
        await update.message.reply_text("👇 Tekan link bawah utk register ya:\nhttps://www.victorbet.net/download/url?referral=3FLEBW")

async def welcome_new_member(update: Update, context: CallbackContext) -> None:
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome {member.full_name} Join group！🎉")

async def scheduled_message(context: CallbackContext):
    try:
        with open("user_ids.txt", "r") as f:
            user_ids = list(set(line.strip() for line in f if line.strip()))
        for user_id in user_ids:
            try:
                await context.bot.send_message(chat_id=int(user_id), text="📢 VictorBet 每日提醒：今天也别错过优惠活动！")
            except Exception as e:
                print(f"发送给 {user_id} 失败：{e}")
    except FileNotFoundError:
        print("没有 user_ids.txt 文件，还没有用户启动过 Bot")

# --- Flask Web 服务器（仅本地保活用）---

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "✅ VictorBot is running."

# --- 主函数 ---

def main():
    from telegram.ext import ApplicationBuilder

    app = ApplicationBuilder().token(TOKEN).build()

    # 只在本地 Polling 模式初始化 JobQueue，避免 NoneType
    if "RENDER" not in os.environ:
        from telegram.ext import JobQueue
        app.job_queue = JobQueue()
        app.job_queue.set_application(app)
        app.job_queue.start()

    # 添加 Telegram 处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    malaysia = timezone(timedelta(hours=8))

    if "RENDER" in os.environ:
        # Webhook 模式（Render 线上）
        webhook_url = f"{BASE_URL}{WEBHOOK_PATH}"
        print(f"🚀 正在使用 Webhook：{webhook_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=webhook_url,
            webhook_path=WEBHOOK_PATH
        )
    else:
        # 本地调试用 Polling
        app.job_queue.run_daily(scheduled_message, time=time(17, 0, tzinfo=malaysia))
        print("🖥️ 本地开发模式 - 使用 polling")
        app.run_polling()

# --- 本地模式启动 Flask 保活 ---

if "RENDER" not in os.environ:
    Thread(target=lambda: flask_app.run(host="0.0.0.0", port=PORT)).start()

if __name__ == "__main__":
    main()
