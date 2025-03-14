import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ChatMemberHandler,
)

# Get environment variables
TOKEN = os.environ.get('BOT_TOKEN')
YOUR_ADMIN_ID = os.environ.get('YOUR_ADMIN_ID')  # يجب أن يكون رقم معرفك وليس اسم المستخدم
CHANNEL_ID = os.environ.get('CHANNEL_ID')  # تأكد أن هذا هو المعرف الرقمي للقناة أو اسم المستخدم مع @

# رسالة الترحيب الثابتة (يمكن استخدامها في أماكن متعددة)
WELCOME_MESSAGE_TEXT = (
    "🌟 مرحباً بك في قناتنا! 🌟\n"
    "للانضمام إلى القناة، يرجى الإجابة على بعض الأسئلة.\n"
    "اضغط على الزر أدناه للبدء."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'q1' not in context.user_data:
        context.user_data['q1'] = None

    keyboard = [[InlineKeyboardButton("ابدأ", callback_data='start_questions')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE_TEXT, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'start_questions':
        keyboard = [[InlineKeyboardButton("نعم", callback_data='yes'), InlineKeyboardButton("لا", callback_data='no')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text('✅ هل أنت على استعداد للالتزام بقواعد القناة؟', reply_markup=reply_markup)

    elif query.data == 'yes':
        context.user_data['q1'] = True
        keyboard = [[InlineKeyboardButton("نعم", callback_data='yes2'), InlineKeyboardButton("لا", callback_data='no2')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text('📚 هل أنت متفرغ للمشاركة الفعالة في القناة؟', reply_markup=reply_markup)

    elif query.data == 'no' or query.data == 'no2':
        await query.edit_message_text('❌ شكراً لاهتمامك.')

    elif query.data == 'yes2':
        context.user_data['q2'] = True
        await query.edit_message_text('📝 ما هو هدفك من الانضمام إلى هذه القناة؟ (يرجى الرد برسالة نصية)')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'q1' not in context.user_data or not context.user_data['q1']:
        await update.message.reply_text('يرجى استخدام الأمر /start للبدء.')
        return

    if 'q2' not in context.user_data or not context.user_data['q2']:
        await update.message.reply_text('يرجى متابعة الأسئلة من خلال الأزرار.')
        return

    if 'q3' not in context.user_data:
        context.user_data['q3'] = update.message.text
        if len(context.user_data['q3'].split()) >= 10:
            await update.message.reply_text('🌍 ما هي لغتك الأم؟')
        else:
            await update.message.reply_text('❌ يجب أن يكون هدفك من الانضمام أكثر تفصيلاً (10 كلمات على الأقل). الرجاء المحاولة مرة أخرى.')
            context.user_data['q3'] = None

    elif 'q4' not in context.user_data:
        context.user_data['q4'] = update.message.text
        await update.message.reply_text('✅ شكراً لإجاباتك! سيتم الآن محاولة إضافتك تلقائياً إلى القناة.')

        if CHANNEL_ID:
            try:
                # محاولة الإضافة التلقائية للقناة
                await context.bot.add_chat_member(chat_id=CHANNEL_ID, user_id=update.message.from_user.id)
                await update.message.reply_text('🎉 تم إضافتك بنجاح إلى القناة! مرحباً بك!')

            except Exception as e:
                # في حالة الفشل، يتم إرسال الطلب إلى الأدمن
                error_message = f"Error adding user to channel: {e}"
                print(error_message)

                if YOUR_ADMIN_ID:
                    admin_message = (
                        f"🔔 طلب انضمام جديد لم يتم إضافته تلقائيًا:\n"
                        f"- المستخدم: {update.message.from_user.first_name} (@{update.message.from_user.username})\n"
                        f"- هدف الانضمام: {context.user_data['q3']}\n"
                        f"- اللغة الأم: {context.user_data['q4']}\n"
                        f"- معرف المستخدم: {update.message.from_user.id}\n\n"
                        f"⚠️ لم يتمكن البوت من إضافته للقناة تلقائيًا. يرجى المراجعة."
                    )
                    try:
                        await context.bot.send_message(chat_id=int(YOUR_ADMIN_ID), text=admin_message)
                        await update.message.reply_text(
                            '⚠️ لم نتمكن من إضافتك تلقائياً. تم إرسال طلبك إلى الأدمن وسيتم مراجعته قريباً.'
                        )
                    except Exception as admin_error:
                        print(f"Error sending message to admin: {admin_error}")

# إضافة ترحيب تلقائي عند انضمام أي عضو
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("welcome_new_member function called!")  # طباعة للتأكد من استدعاء الدالة
    if update.chat_member.new_chat_member:
        user = update.chat_member.new_chat_member.user
        welcome_message = f"🌟 مرحباً بك، {user.full_name}! 🎉\nيسعدنا انضمامك إلى قناتنا. نأمل أن تستمتع بمحتوى القناة. إذا كان لديك أي استفسار، لا تتردد في التواصل!"
        try:
            await context.bot.send_message(chat_id=update.chat_member.chat.id, text=welcome_message)
        except Exception as e:
            print(f"Error sending welcome message: {e}") # طباعة الخطأ في حالة حدوث مشكلة

# دالة معالجة اختبار البوت (عند استدعاء البوت بالمعرف أو كلمة مفتاحية)
async def test_bot_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    print(f"Bot test initiated by user: {user.username or user.first_name} (ID: {user.id})")
    await update.message.reply_text(WELCOME_MESSAGE_TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ابدأ", callback_data='start_questions')]]))


def main():
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable is not set.")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    # إضافة معالج الترحيب التلقائي
    application.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    # تعطيل معالج الرسائل النصية العام لمنع الرد على كل رسالة
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # إضافة معالج لاختبار وصول البوت (mention أو كلمة مفتاحية)
    application.add_handler(MessageHandler(
        filters.TEXT & filters.GroupChat & (filters.MENTION_ME | filters.Regex(r".*اختبار البوت.*")),
        test_bot_access
    ))


    print("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()