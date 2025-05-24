from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import asyncio
from datetime import time, timedelta, timezone

# Bot Token
TOKEN = "7905072858:AAEtXopc9kNe-92qlgCweRQ302Q2ycqMRI0"

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

# --- 启动函数 ---
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    malaysia = timezone(timedelta(hours=8))
    app.job_queue.run_daily(scheduled_message, time=time(17, 0, tzinfo=malaysia))
    print("✅ 正在执行 scheduled_message")

    print("🤖 Bot 正在运行！")
    app.run_polling()

if __name__ == '__main__':
    main()

    from flask import Flask
from threading import Thread

# 创建一个 Flask 实例
app_flask = Flask(__name__)

# 设置首页路由
@app_flask.route('/')
def home():
    return "✅ VictorBot is running."

# 启动 Flask 服务监听端口（Render 需要监听一个端口才不会报错）
def run_flask():
    app_flask.run(host="0.0.0.0", port=8080)

# 启动一个线程来运行 Flask
Thread(target=run_flask).start()

