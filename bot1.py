from flask import Flask, request
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
import asyncio
from datetime import time, timedelta, timezone
import logging
import os

# 日志记录
logging.basicConfig(level=logging.INFO)

# 配置
TOKEN = "7905072858:AAEtXopc9kNe-92qlgCweRQ302Q2ycqMRI0"
WEBHOOK_URL = "https://telegram-bot-z8zl.onrender.com/webhook"  # 替换为你的Render URL
PORT = int(os.environ.get("PORT", 8080))

# Flask 初始化
flask_app = Flask(__name__)

# 初始化 Telegram Bot
application = Application.builder().token(TOKEN).build()

# === Handlers（保持你原有的逻辑）===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "register":
        await query.message.reply_text("👇 Tekan link bawah utk register ya:\nhttps://www.victorbet.net/download/url?referral=3FLEBW")
    elif query.data == "telegram_channel":
        await query.message.reply_text("🔊 Tekan link join channel: \nhttps://t.me/Victorbet_Channel")
    elif query.data == "contact_us":
        await query.message.reply_text("💬 Tekan link utk chat CS: \nhttps://direct.lc.chat/14684676/")

async def keyword_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "hi boss" in text or "daftar" in text:
        await update.message.reply_text("👇 Tekan link bawah utk register ya:\nhttps://www.victorbet.net/download/url?referral=3FLEBW")
    elif "livechat" in text:
        await update.message.reply_text("💬 Tekan link utk chat CS: \nhttps://direct.lc.chat/14684676/")
    else:
        await update.message.reply_text("👇 Tekan link bawah utk register ya:\nhttps://www.victorbet.net/download/url?referral=3FLEBW")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome {member.full_name} Join group！🎉")

async def scheduled_message(context: ContextTypes.DEFAULT_TYPE):
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

# 注册 handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_callback))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_reply))
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

# 设置每天提醒
malaysia = timezone(timedelta(hours=8))
application.job_queue.run_daily(scheduled_message, time=time(17, 0, tzinfo=malaysia))


# --- Flask Webhook 路由 ---
@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.update_queue.put(update))
    return "OK"


@flask_app.route("/")
def home():
    return "✅ VictorBot is alive with Webhook!"


# --- 启动 Flask 和 Telegram Webhook ---
def run():
    flask_app.run(host="0.0.0.0", port=PORT)

if __name__ == '__main__':
    # 设置 Telegram webhook
    import requests
    res = requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}"
    )
    print("Webhook 设置结果：", res.text)

    # 启动 Flask 服务（新线程）
    Thread(target=run).start()

    # 启动 Telegram 应用（非 polling，但处理队列）
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        stop_signals=None
    )
