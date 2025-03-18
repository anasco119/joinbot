import os
import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ChatMemberHandler,
)

# تهيئة المتغيرات من البيئة
TOKEN = os.environ.get('BOT_TOKEN')
YOUR_ADMIN_ID = os.environ.get('YOUR_ADMIN_ID')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
GROUP_ID = os.environ.get('GROUP_ID')

WELCOME_MESSAGE_TEXT = (
    " **Welcome to our channel!** \n"
    "To join the channel, please answer a few questions.\n"
    "Click the button below to get started. ✅\n\n"
    "✨ **مرحباً بك في قناتنا!** ✨\n"
    "للانضمام إلى القناة، يرجى الإجابة على بعض الأسئلة.\n"
    "اضغط على الزر أدناه للبدء. ✅"
)

BAD_WORDS_PATTERNS = [
    r"\bfuck\b",
    r"\bshit\b",
    r"\bass\b",
    r"\bbitch\b",
]

genie_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("ابدأ الآن", callback_data="start_questions")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE_TEXT, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "start_questions":
        context.user_data['q2'] = True
        await query.message.reply_text("ما هو هدفك من الانضمام إلى هذه القناة؟")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat.id)
    user_id = update.message.from_user.id
    message_text = update.message.text

    if chat_id == GROUP_ID:
        if "http://" in message_text or "https://" in message_text:
            await update.message.reply_text("❌ الروابط غير مسموحة في هذه المجموعة. ❌")
            await update.message.delete()
            return

        for pattern in BAD_WORDS_PATTERNS:
            if re.search(pattern, message_text, re.IGNORECASE):
                await update.message.reply_text("❌ اللغة غير اللائقة غير مسموحة. ❌")
                await update.message.delete()
                return

        if re.search(r"@\w+", message_text) and user_id != int(YOUR_ADMIN_ID):
            await update.message.reply_text("❌ لا يُسمح بذكر المعرفات الخارجية في هذه المجموعة. ❌")
            await update.message.delete()
            return

        if "Genie" in message_text or "@AIChatGeniebot" in message_text:
            if user_id in genie_users and user_id != int(YOUR_ADMIN_ID):
                await update.message.reply_text("❌ يمكنك استدعاء Genie مرة واحدة فقط. ❌")
                await update.message.delete()
                return
            genie_users.add(user_id)

    elif chat_id != GROUP_ID:
        if not context.user_data.get('q2'):
            await update.message.reply_text("⚠️ يرجى البدء بالضغط على /start ⚠️")
            return

        if not context.user_data.get('q3'):
            context.user_data['q3'] = message_text
            context.user_data['q4'] = True
            await update.message.reply_text("ما هي لغتك الأم؟")
        else:
            await handle_language(update, context)

async def handle_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('q4'):
        return

    context.user_data['lang'] = update.message.text

    await update.message.reply_text("✅ Your answers have been received! Processing... ✅\n\n✅ تم استلام إجاباتك! جاري المعالجة... ✅")
    try:
        if CHANNEL_ID:
            try:
                await context.bot.approve_chat_join_request(chat_id=CHANNEL_ID, user_id=update.message.from_user.id)
                await update.message.reply_text("✅ You have been successfully added to the channel! ✅\n\n✅ تمت إضافتك للقناة بنجاح! ✅")
            except Exception as e:
                print(f"Error adding user to channel: {e}")
                await update.message.reply_text("⏳ جاري معالجة طلبك، شكرًا لتفهمك! 🌟")
                await asyncio.sleep(2)
                invite_link = "https://t.me/EnglishConvs"
                await update.message.reply_text(
                    f"✨ **مرحباً بك في قناتنا!** ✨\n\n"
                    f"للانضمام إلى القناة، يرجى استخدام الرابط التالي:\n\n"
                    f"{invite_link}\n\n"
                    f"شكرًا لاهتمامك! 😊"
                )

        if YOUR_ADMIN_ID:
            await context.bot.send_message(
                chat_id=YOUR_ADMIN_ID,
                text=f"New join request:\n"
                     f"Name: {update.message.from_user.full_name}\n"
                     f"Username: @{update.message.from_user.username}\n"
                     f"User ID: {update.message.from_user.id}\n"
                     f"Goal: {context.user_data['q3']}\n"
                     f"Language: {context.user_data['lang']}\n"
            )
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ An error occurred, please try again later. ⚠️")
    
    context.user_data.clear()

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_member.new_chat_member.user
    await context.bot.send_message(
        chat_id=update.chat_member.chat.id,
        text=f" Welcome {user.full_name}! \n\n أهلاً بك {user.full_name}! "
    )

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN not set!")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^(عربي|English)$'), handle_language))
    app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))

    print("Bot is running...")
    PORT = int(os.environ.get("PORT", 8080))
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://joinbot-7mw7.onrender.com/{TOKEN}"
    )

if __name__ == "__main__":
    main()
