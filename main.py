import os
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

WELCOME_MESSAGE_TEXT = (
    " **Welcome to our channel!** \n"
    "To join the channel, please answer a few questions.\n"
    "Click the button below to get started. ✅\n\n"
    "✨ **مرحباً بك في قناتنا!** ✨\n"
    "للانضمام إلى القناة، يرجى الإجابة على بعض الأسئلة.\n"
    "اضغط على الزر أدناه للبدء. ✅"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = [[InlineKeyboardButton("Start | ابدأ", callback_data='start_questions')]]
    await update.message.reply_text(WELCOME_MESSAGE_TEXT, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'start_questions':
        keyboard = [
            [InlineKeyboardButton("Yes | نعم", callback_data='yes'), 
             InlineKeyboardButton("No | لا", callback_data='no')]
        ]
        await query.edit_message_text("✅ Are you prepared to follow the channel guidelines? ✅\n\n✅ هل أنت على استعداد للالتزام بقواعد القناة؟ ✅", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'yes':
        keyboard = [
            [InlineKeyboardButton("Yes | نعم", callback_data='yes2'), 
             InlineKeyboardButton("No | لا", callback_data='no2')]
        ]
        await query.edit_message_text(" Are you available to actively participate in the channel? \n\n هل أنت متفرغ للمشاركة الفعالة في القناة؟ ", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data in ('no', 'no2'):
        await query.edit_message_text("❌ Thank you for your interest. ❌\n\n❌ شكراً لاهتمامك. ❌")
        context.user_data.clear()

    elif query.data == 'yes2':
        await query.edit_message_text(" What is your goal for joining this channel? (Please reply with a text message) \n\n ما هو هدفك من الانضمام إلى هذه القناة؟ (يرجى الرد برسالة نصية) ")
        context.user_data['q2'] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('q2'):
        await update.message.reply_text("⚠️ Please start by pressing /start ⚠️\n\n⚠️ يرجى البدء بالضغط على /start ⚠️")
        return

    # التحقق من وجود الهدف
    if not context.user_data.get('q3'):
        # حفظ الهدف
        context.user_data['q3'] = update.message.text
        # الانتقال إلى السؤال التالي (اللغة)
        await update.message.reply_text(" What is your native language? \n\n ما هي لغتك الأم؟ ")
        context.user_data['q4'] = True
    else:
        # إذا كان الهدف موجودًا، فهذا يعني أن المستخدم يحاول إرسال اللغة
        await handle_language(update, context)

async def handle_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('q4'):
        return

    # حفظ اللغة
    context.user_data['lang'] = update.message.text

    # إرسال رسالة تأكيد
    await update.message.reply_text("✅ Your answers have been received! Processing... ✅\n\n✅ تم استلام إجاباتك! جاري المعالجة... ✅")

    try:
        # إرسال معلومات المستخدم إلى الأدمن
        if YOUR_ADMIN_ID:
            await context.bot.send_message(
                chat_id=YOUR_ADMIN_ID,
                text=f"New join request:\n"
                     f"Name: {update.message.from_user.full_name}\n"
                     f"Username: @{update.message.from_user.username}\n"
                     f"User ID: {update.message.from_user.id}\n"
                     f"Goal: {context.user_data['q3']}\n"
                     f"Language: {context.user_data['lang']}\n\n"
                     f"طلب انضمام جديد:\n"
                     f"الاسم: {update.message.from_user.full_name}\n"
                     f"اسم المستخدم: @{update.message.from_user.username}\n"
                     f"معرف المستخدم: {update.message.from_user.id}\n"
                     f"الهدف: {context.user_data['q3']}\n"
                     f"اللغة: {context.user_data['lang']}"
            )

        if CHANNEL_ID:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=f" New member added: \n"
                     f"Name: {update.message.from_user.full_name}\n"
                     f"Username: @{update.message.from_user.username}\n"
                     f"User ID: {update.message.from_user.id}\n"
                     f"Goal: {context.user_data['q3']}\n"
                     f"Language: {context.user_data['lang']}\n\n"
                     f" تمت إضافة عضو جديد: \n"
                     f"الاسم: {update.message.from_user.full_name}\n"
                     f"اسم المستخدم: @{update.message.from_user.username}\n"
                     f"معرف المستخدم: {update.message.from_user.id}\n"
                     f"الهدف: {context.user_data['q3']}\n"
                     f"اللغة: {context.user_data['lang']}"
            )
            await update.message.reply_text("✅ You have been successfully added to the channel! ✅\n\n✅ تمت إضافتك للقناة بنجاح! ✅")
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ An error occurred, please try again later. ⚠️\n\n⚠️ حدث خطأ، يرجى المحاولة لاحقاً. ⚠️")

    # مسح بيانات المستخدم بعد الانتهاء
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

    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^(عربي|English)$'), handle_language))
    app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
