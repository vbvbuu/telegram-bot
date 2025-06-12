import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    CallbackContext, CallbackQueryHandler, JobQueue
)
from datetime import time, timedelta, timezone
import logging

TOKEN = "7905072858:AAEtXopc9kNe-92qlgCweRQ302Q2ycqMRI0"
WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", 5000))
BASE_URL = "https://telegram-bot-z8zl.onrender.com"  # 你自己的域名

async def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    with open("user_ids.txt", "a") as f:
        f.write(f"{chat_id}\n")
    with open("welcome.png", "rb") as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo, caption="Welcome to VictorBet💎👇")
    keyboard = [
        [InlineKeyboardButton("📝 Register", url="https://www.victorbet.net/download/url?referral=3FLEBW")],
        [InlineKeyboardButton("🚀 New Telegram Channel", url="https://t.me/Victorbet_Channel")],
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
        await update.message.reply_text("👇 Tekan link bawah utk register ya:\nhttps://www.victorbet.net/download/url?referral=3FLEBW\n💬 Tekan link utk chat CS ajar register: \nhttps://direct.lc.chat/14684676/")
    elif "livechat" in text:
        await update.message.reply_text("💬 Tekan link utk chat CS: \nhttps://direct.lc.chat/14684676/")
    else:
        await update.message.reply_text("👇 Tekan link bawah utk register ya:\nhttps://www.victorbet.net/download/url?referral=3FLEBW\n💬 Tekan link utk chat CS ajar register: \nhttps://direct.lc.chat/14684676/")

async def welcome_new_member(update: Update, context: CallbackContext) -> None:
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome {member.full_name} Join group！🎉")

async def scheduled_message(context: CallbackContext):
    try:
        with open("user_ids.txt", "r") as f:
            user_ids = list(set(line.strip() for line in f if line.strip()))
        for user_id in user_ids:
            try:
                await context.bot.send_message(chat_id=int(user_id), text="📢 VictorBet Daily notification：Topup skrg n BIGWIN！")
            except Exception as e:
                print(f"发送给 {user_id} 失败：{e}")
    except FileNotFoundError:
        print("没有 user_ids.txt 文件，还没有用户启动过 Bot")

def main():
    malaysia = timezone(timedelta(hours=8))
    app = ApplicationBuilder().token(TOKEN).build()

    # 添加处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    # 初始化并启动 job_queue
    job_queue = app.job_queue
    job_queue.run_daily(scheduled_message, time=time(17, 0, tzinfo=malaysia))
    job_queue.start()

    if os.environ.get("RENDER"):
        webhook_url = f"{BASE_URL}{WEBHOOK_PATH}"
        print(f"🚀 Starting webhook with URL: {webhook_url} on port {PORT}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=WEBHOOK_PATH,
            webhook_url=webhook_url,
        )
    else:
        print("🖥️ Running in polling mode")
        app.run_polling()

if __name__ == "__main__":
    main()
