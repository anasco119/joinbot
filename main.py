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
YOUR_ADMIN_ID = int(os.environ.get('YOUR_ADMIN_ID'))
CHANNEL_ID = os.environ.get('CHANNEL_ID')
GROUP_ID = os.environ.get('GROUP_ID')

WELCOME_MESSAGE_TEXT = (
    "✨ **مرحباً بك في قناتنا!** ✨\n\n"
    "للانضمام إلى القناة، يرجى الإجابة على بعض الأسئلة.\n"
    "اضغط على الزر أدناه للبدء. ✅"
)

# قائمة بالكلمات المسيئة والممنوعة (باستخدام أنماط regex)
BAD_WORDS_PATTERNS = [
    r"\bfuck\b",
    r"\bshit\b",
    r"\bass\b",
    r"\bbitch\b",
    r"\bكسم\b",
    r"\bذبي\b",
    r"\bلوطي\b",
    r"\bشرموطة\b",
    r"\bنيك\b",
]

# قائمة بالمستخدمين الذين استدعوا البوت Genie
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
        await query.message.reply_text("🎯 ما هو هدفك من الانضمام إلى هذه القناة؟")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat.id)
    user_id = update.message.from_user.id
    message_text = update.message.text

    # التأكد من أن الرسائل تأتي من المجموعة المحددة
    if chat_id == GROUP_ID:
        # منع الروابط
        if "http://" in message_text or "https://" in message_text or "www" in message_text or ".com" in message_text or ".net" in message_text or ".org" in message_text:
            # إرسال رسالة التحليل
            analysis_msg = await update.message.reply_text("دعني أرى🤔 لاحظت شيئًا غريبًا هنا .../n
                                                            I see something suspicious here...🤔/n
                                                                                                /n
                                                                              🔍جاري تحليل الرسالة..")
            await asyncio.sleep(4)  # تأخير لمحاكاة التحليل
            await analysis_msg.delete()  # حذف رسالة التحليل

            await asyncio.sleep(1)

            # إرسال رسالة اكتشاف المخالفة
            violation_msg = await update.message.reply_text(" تم اكتشاف رابط غير مسموح به")
            await asyncio.sleep(4)  # تأخير
            await violation_msg.delete()  # حذف رسالة المخالفة

            await asyncio.sleep(1)
            
            # إرسال الرسالة النهائية مع الإجراء
            sender_name = update.message.from_user.full_name
            sender_username = f"@{update.message.from_user.username}" if update.message.from_user.username else "بدون معرف"
            action_msg = await update.message.reply_text(
                f"🚫 تم حذف الرسالة بسبب وجود رابط غير مسموح به.\n"
                f"المخالف: {sender_name} ({sender_username})\n"
                "يرجى تجنب نشر الروابط للمحافظة على جودة النقاش. 🤝/n
                /n
                 The message has been deleted, and the sender has been warned."
            )
            await update.message.delete()  # حذف الرسالة المخالفة
            await asyncio.sleep(10)  # تأخير 10 ثوانٍ
            await action_msg.delete()  # حذف الرسالة النهائية
            return

        # منع الكلمات المسيئة
        for pattern in BAD_WORDS_PATTERNS:
            if re.search(pattern, message_text, re.IGNORECASE):
                # إرسال رسالة التحليل
                analysis_msg = await update.message.reply_text("🔍 جاري تحليل الرسالة... يرجى الانتظار.")
                await asyncio.sleep(4)  # تأخير لمحاكاة التحليل
                await analysis_msg.delete()  # حذف رسالة التحليل

                await asyncio.sleep(1)

                # إرسال رسالة اكتشاف المخالفة
                violation_msg = await update.message.reply_text("⚠️ تم اكتشاف لغة غير لائقة!")
                await asyncio.sleep(2)  # تأخير
                await violation_msg.delete()  # حذف رسالة المخالفة

                await asyncio.sleep(1)

                # إرسال الرسالة النهائية مع الإجراء
                sender_name = update.message.from_user.full_name
                sender_username = f"@{update.message.from_user.username}" if update.message.from_user.username else "بدون معرف"
                action_msg = await update.message.reply_text(
                    f"🚫 تم حذف الرسالة بسبب استخدام لغة غير لائقة.\n"
                    f"المخالف: {sender_name} ({sender_username})\n"
                    "يرجى استخدام لغة محترمة ومهذبة. 🌟/n
                     /n
                      Inappropriate language was detected in the message!"
                )
                await update.message.delete()  # حذف الرسالة المخالفة
                await asyncio.sleep(10)  # تأخير 10 ثوانٍ
                await action_msg.delete()  # حذف الرسالة النهائية
                return

        # منع ذكر المعرفات الخارجية
        if re.search(r"@\w+", message_text) and user_id != YOUR_ADMIN_ID:
            await update.message.reply_text("🚫 لا يُسمح بذكر المعرفات الخارجية هنا. لنجعل النقاش متاحاً للجميع دون استثناء. 😊")
            await update.message.delete()
            await asyncio.sleep(4)  # تأخير 10 ثوانٍ
            await action_msg.delete()  # حذف الرسالة النهائية
                return
            return

        # منع استدعاء البوت Genie أكثر من مرة
        if "Genie" in message_text or "@AIChatGeniebot" in message_text:
            if user_id in genie_users and user_id != YOUR_ADMIN_ID:
                await update.message.reply_text("🚫 يمكنك استدعاء Genie مرة واحدة فقط لتجنب الإزعاج. شكراً لتفهمك! 🙏")
                await update.message.delete()
                await asyncio.sleep(4)  # تأخير 10 ثوانٍ
                await action_msg.delete()  # حذف الرسالة النهائية
                return
                
            genie_users.add(user_id)

    elif chat_id != GROUP_ID:
        # الرسائل الخاصة
        if not context.user_data.get('q2'):
            await update.message.reply_text("⚠️ يرجى البدء بالضغط على /start لاتباع الإرشادات. ⚠️")
            return

        if not context.user_data.get('q3'):
            context.user_data['q3'] = message_text  # حفظ الهدف
            context.user_data['q4'] = True
            await update.message.reply_text("🌍 ما هي لغتك الأم؟")
        else:
            await handle_language(update, context)

async def handle_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('q4'):
        return

    context.user_data['lang'] = update.message.text
    await update.message.reply_text("✅ تم استلام إجاباتك! جارٍ معالجتها...")

    try:
        if CHANNEL_ID:
            try:
                await context.bot.approve_chat_join_request(chat_id=CHANNEL_ID, user_id=update.message.from_user.id)
                await update.message.reply_text("✅ تمت إضافتك للقناة بنجاح! 🎉")
            except Exception as e:
                print(f"Error adding user to channel: {e}")
                invite_link = "https://t.me/EnglishConvs"
                await update.message.reply_text(
                    f"🔗 يرجى الانضمام للقناة من خلال الرابط التالي:\n{invite_link}\n\nنرحب بك! 😊"
                )

        if YOUR_ADMIN_ID:
            await context.bot.send_message(
                chat_id=YOUR_ADMIN_ID,
                text=(
                    f"📥 طلب انضمام جديد:\n"
                    f"الاسم: {update.message.from_user.full_name}\n"
                    f"اسم المستخدم: @{update.message.from_user.username}\n"
                    f"معرف المستخدم: {update.message.from_user.id}\n"
                    f"الهدف: {context.user_data['q3']}\n"
                    f"اللغة: {context.user_data['lang']}"
                )
            )
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ حدث خطأ، يرجى المحاولة لاحقاً.")

    context.user_data.clear()

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass  # لم تتم إضافة آلية للترحيب بالأعضاء الجدد بعد

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
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
