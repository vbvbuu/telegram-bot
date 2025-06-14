import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    CallbackContext, CallbackQueryHandler, JobQueue
)
from datetime import time, timedelta, timezone
import logging

TOKEN = "7905072858:AAEtXopc9kNe-92qlgCweRQ302Q2ycqMRI0"  # 替换成你的 Bot Token
WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", 5000))
BASE_URL = "https://telegram-bot-z8zl.onrender.com"  # 你的 Render 域名
CHANNEL_ID = -1002006991320  # 你的频道 ID
ADMIN_IDS = [7060111888]  # 替换成你自己的 Telegram ID（可以加多个）

async def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    with open("user_ids.txt", "a") as f:
        f.write(f"{chat_id}\n")
    with open("welcome.png", "rb") as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo, caption="Welcome to VictorBet💎👇")
    keyboard = [
        [InlineKeyboardButton("📝 Register", url="https://www.victorbet.net/download/url?referral=3FLEBW")],
        [InlineKeyboardButton("🚀 New Telegram Channel", url="https://t.me/victorbetMY_bot")],
        [InlineKeyboardButton("📲 Contact us", callback_data="contact_us")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select option at below：", reply_markup=reply_markup)

async def send_promo(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("🔗 马上注册", url="https://www.victorbet.net/download/url?referral=3FLEBW"),
            InlineKeyboardButton("💬 联系客服", url="https://direct.lc.chat/14684676/")
        ],
        [
            InlineKeyboardButton("📢 加入频道", url="https://t.me/Victorbet_Channel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=CHANNEL_ID, text="🎉 VictorBet 最新优惠上线啦！", reply_markup=reply_markup)

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

# ✅ rich post handler：发图 + 文案自动推送到频道，带 3 个按钮
async def handle_photo_post(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("🚫 你没有权限发布到频道。")
        return

    if update.message.caption and update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        caption = update.message.caption

        keyboard = [
            [
                InlineKeyboardButton("🔗 Register", url="https://www.victorbet.net/download/url?referral=3FLEBW"),
                InlineKeyboardButton("💬 Contact Us", url="https://direct.lc.chat/14684676/")
            ],
            [
                InlineKeyboardButton("📢 New Telegram Channel", url="https://t.me/Victorbet_Channel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=photo_file_id,
            caption=caption,
            reply_markup=reply_markup
        )
        await update.message.reply_text("✅ 已发布到频道！")
    else:
        await update.message.reply_text("❗ 请发送附带文字说明的图片。")

def main():
    malaysia = timezone(timedelta(hours=8))
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send_promo", send_promo))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_post))  # rich post handler

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
