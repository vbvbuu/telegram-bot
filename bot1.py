from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, CallbackContext, CallbackQueryHandler
)
from flask import Flask, request, abort
import asyncio
from datetime import time, timedelta, timezone
import logging

# Bot Token
TOKEN = "7905072858:AAEtXopc9kNe-92qlgCweRQ302Q2ycqMRI0"
# 你的公网Webhook地址（替换成你的域名和路径）
WEBHOOK_URL = "https://api.telegram.org/bot7905072858:AAEtXopc9kNe-92qlgCweRQ302Q2ycqMRI0/setWebhook?url=https://telegram-bot-z8zl.onrender.com/webhook"

# --- Telegram Bot 功能 ---

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

# --- Flask + Webhook ---

app_flask = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 创建 Telegram Application
application = Application.builder().token(TOKEN).build()

# 添加处理器
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_callback))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_reply))
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

# 添加每日定时任务（马来西亚时间17:00）
malaysia = timezone(timedelta(hours=8))
application.job_queue.run_daily(scheduled_message, time=time(17, 0, tzinfo=malaysia))
application.job_queue.start()

# 设置 webhook
async def set_webhook():
    await application.bot.set_webhook(WEBHOOK_URL)

# 在 Flask 中处理 Telegram 发送过来的 update
@app_flask.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        # 用 asyncio 运行 handler
        asyncio.run(application.update_queue.put(update))
        return "OK"
    else:
        abort(405)

# 根路径可以用于检测服务运行状态
@app_flask.route('/')
def home():
    return "✅ VictorBot is running."

# 启动时设置Webhook和运行Flask
if __name__ == '__main__':
    # 先设置Webhook，再启动 Flask 服务
    import threading

    def run():
        app_flask.run(host="0.0.0.0", port=8080)

    async def main_async():
        await set_webhook()
        print("Webhook 已设置:", WEBHOOK_URL)

    # 异步设置Webhook
    asyncio.run(main_async())

    # Flask线程
    threading.Thread(target=run).start()

    # 启动 Application 的事件循环（运行 Handler）
    application.run_polling(stop_signals=None)  # 这里不真正polling，是让event loop运行处理队列
