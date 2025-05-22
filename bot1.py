from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import asyncio

# 你的 Bot Token（替换成你自己的）
TOKEN = "7905072858:AAEtXopc9kNe-92qlgCweRQ302Q2ycqMRI0"

# 处理 /start 命令（发送图片 + 按钮菜单）
async def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

     # ✅ 保存用户 chat_id
    with open("user_ids.txt", "a") as f:
        f.write(f"{chat_id}\n")
    
    # 发送图片（请替换 'welcome.jpg' 为你的图片路径）
    with open("welcome.png", "rb") as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo, caption="Welcome to VictorBet💎👇")

    # 创建按钮菜单
    keyboard = [
        [InlineKeyboardButton("📝 Register", callback_data="register")],
        [InlineKeyboardButton("🚀 New Telegram Channel", callback_data="telegram_channel")],
        [InlineKeyboardButton("📲 Contact us", callback_data="contact_us")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 发送按钮菜单
    await update.message.reply_text("Select option at below：", reply_markup=reply_markup)

# 处理按钮点击
async def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "register":
        await query.message.reply_text("👇 Tekan link bawah utk register ya:\nhttps://www.victorbet.net/download/url?referral=3FLEBW")
    elif query.data == "telegram_channel":
        await query.message.reply_text("🔊 Tekan link join channel: \nhttps://t.me/Victorbet_Channel")
    elif query.data == "contact_us":
        await query.message.reply_text("💬 Tekan link utk chat CS: \nhttps://direct.lc.chat/14684676/")

# 关键词自动回复 + 默认回复
async def keyword_reply(update: Update, context: CallbackContext) -> None:
    text = update.message.text.lower()

    if "hi boss" in text:
        await update.message.reply_text("👇 Tekan link bawah utk register ya:\nhttps://www.victorbet.net/download/url?referral=3FLEBW")
    elif "daftar" in text:
        await update.message.reply_text("👇 Tekan link bawah utk register ya:\nhttps://www.victorbet.net/download/url?referral=3FLEBW")
    elif "livechat" in text:
        await update.message.reply_text("💬 Tekan link utk chat CS: \nhttps://direct.lc.chat/14684676/")
    else:
        # 默认统一回复
        await update.message.reply_text("👇 Tekan link bawah utk register ya:\nhttps://www.victorbet.net/download/url?referral=3FLEBW")


# 群管理 - 欢迎新成员
async def welcome_new_member(update: Update, context: CallbackContext) -> None:
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome {member.full_name} Join group！🎉")

# 定时推送消息
async def scheduled_message(context: CallbackContext):
    try:
        # 读取所有用户 ID（去重）
        with open("user_ids.txt", "r") as f:
            user_ids = list(set(line.strip() for line in f if line.strip()))

        for user_id in user_ids:
            try:
                await context.bot.send_message(chat_id=int(user_id), text="📢 VictorBet 每日提醒：今天也别错过优惠活动！")
            except Exception as e:
                print(f"发送给 {user_id} 失败：{e}")

    except FileNotFoundError:
        print("没有 user_ids.txt 文件，还没有用户启动过 Bot")


# 机器人主程序
from datetime import time, timedelta, timezone

def main():
    app = Application.builder().token(TOKEN).build()

    # 处理指令和消息
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))  # 处理按钮点击
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))



    malaysia = timezone(timedelta(hours=8))
    app.job_queue.run_daily(scheduled_message, time=time(17,00, tzinfo=malaysia))
    print("✅ 正在执行 scheduled_message")


    print("🤖 机器人已启动！")
    app.run_polling()


if __name__ == '__main__':
    main()
