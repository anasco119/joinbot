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
    keyboard = [[InlineKeyboardButton("ابدأ الآن | Start Now", callback_data="start_questions")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE_TEXT, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_questions":
        context.user_data['q2'] = True
        await query.message.reply_text("🎯 ما هو هدفك من الانضمام إلى هذه القناة؟\nWhat is your goal for joining the channel?")
    elif query.data == "yes_rules":
        context.user_data['rules_agreement'] = "نعم | Yes"
        context.user_data['q6'] = True
        await query.message.reply_text("🌟 هل ستشارك مشاركة إيجابية في القناة؟\nWill you actively participate in the channel?")
        # إضافة أزرار نعم/لا للمشاركة الإيجابية
        keyboard = [
            [InlineKeyboardButton("نعم | Yes", callback_data="yes_participation")],
            [InlineKeyboardButton("لا | No", callback_data="no_participation")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("اختر:", reply_markup=reply_markup)
    elif query.data == "no_rules":
        context.user_data['rules_agreement'] = "لا | No"
        context.user_data['q6'] = True
        await query.message.reply_text("🌟 هل ستشارك مشاركة إيجابية في القناة؟\nWill you actively participate in the channel?")
        # إضافة أزرار نعم/لا للمشاركة الإيجابية
        keyboard = [
            [InlineKeyboardButton("نعم | Yes", callback_data="yes_participation")],
            [InlineKeyboardButton("لا | No", callback_data="no_participation")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("اختر:", reply_markup=reply_markup)
    elif query.data == "yes_participation":
        context.user_data['positive_participation'] = "نعم | Yes"
        await handle_language(update, context)
    elif query.data == "no_participation":
        context.user_data['positive_participation'] = "لا | No"
        await handle_language(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat.id)
    user_id = update.message.from_user.id
    message_text = update.message.text

    # التأكد من أن الرسائل تأتي من المجموعة المحددة
    if chat_id == GROUP_ID:
        # منع الروابط
        if "http://" in message_text or "https://" in message_text or "www." in message_text or ".com" in message_text or ".net" in message_text or ".org" in message_text:
            # إرسال رسالة التحليل
            analysis_msg = await update.message.reply_text("دعني أرى🤔 لاحظت شيئًا غريبًا هنا...\nI see something suspicious here...🤔\n\n🔍 جاري تحليل الرسالة...")
            await asyncio.sleep(4)  # تأخير لمحاكاة التحليل
            await analysis_msg.delete()  # حذف رسالة التحليل

            await asyncio.sleep(1)

            # إرسال رسالة اكتشاف المخالفة
            violation_msg = await update.message.reply_text("⚠️ تم اكتشاف رابط غير مسموح به!\nA forbidden link was detected!")
            await asyncio.sleep(2)  # تأخير
            await violation_msg.delete()  # حذف رسالة المخالفة

            await asyncio.sleep(1)

            # إرسال الرسالة النهائية مع الإجراء
            sender_name = update.message.from_user.full_name
            sender_username = f"@{update.message.from_user.username}" if update.message.from_user.username else "بدون معرف | No Username"
            action_msg = await update.message.reply_text(
                f"🚫 تم حذف الرسالة بسبب وجود رابط غير مسموح به.\n"
                f"المخالف: {sender_name} ({sender_username})\n"
                "يرجى تجنب نشر الروابط للمحافظة على جودة النقاش. 🤝\n\n"
                "The message has been deleted, and the sender has been warned."
            )
            await update.message.delete()  # حذف الرسالة المخالفة
            await asyncio.sleep(10)  # تأخير 10 ثوانٍ
            await action_msg.delete()  # حذف الرسالة النهائية
            return

        # منع الكلمات المسيئة
        for pattern in BAD_WORDS_PATTERNS:
            if re.search(pattern, message_text, re.IGNORECASE):
                # إرسال رسالة التحليل
                analysis_msg = await update.message.reply_text("🔍 جاري تحليل الرسالة...\nAnalyzing the message...")

                # إضافة تأثير النقاط المتحركة
                for _ in range(3):  # كرر العملية 3 مرات
                    await asyncio.sleep(1)  # تأخير 1 ثانية
                    await analysis_msg.edit_text("🔍 جاري تحليل الرسالة.\nAnalyzing the message.")  # تعديل الرسالة
                    await asyncio.sleep(1)
                    await analysis_msg.edit_text("🔍 جاري تحليل الرسالة..\nAnalyzing the message..")  # تعديل الرسالة
                    await asyncio.sleep(1)
                    await analysis_msg.edit_text("🔍 جاري تحليل الرسالة...\nAnalyzing the message...")  # تعديل الرسالة

                # حذف رسالة التحليل بعد الانتهاء
                await analysis_msg.delete()

                await asyncio.sleep(1)

                # إرسال رسالة اكتشاف المخالفة
                violation_msg = await update.message.reply_text("⚠️ تم اكتشاف لغة غير لائقة!\nInappropriate language was detected!")
                await asyncio.sleep(2)  # تأخير
                await violation_msg.delete()  # حذف رسالة المخالفة

                await asyncio.sleep(1)

                # إرسال الرسالة النهائية مع الإجراء
                sender_name = update.message.from_user.full_name
                sender_username = f"@{update.message.from_user.username}" if update.message.from_user.username else "بدون معرف | No Username"
                action_msg = await update.message.reply_text(
                    f"🚫 تم حذف الرسالة بسبب استخدام لغة غير لائقة.\n"
                    f"المخالف: {sender_name} ({sender_username})\n"
                    "يرجى استخدام لغة محترمة ومهذبة. 🌟\n\n"
                    "Inappropriate language was detected in the message!"
                )
                await update.message.delete()  # حذف الرسالة المخالفة
                await asyncio.sleep(10)  # تأخير 10 ثوانٍ
                await action_msg.delete()  # حذف الرسالة النهائية
                return

        # منع ذكر المعرفات الخارجية
        if re.search(r"@\w+", message_text) and user_id != YOUR_ADMIN_ID:
            await update.message.reply_text("🚫 لا يُسمح بذكر المعرفات الخارجية هنا. لنجعل النقاش متاحاً للجميع دون استثناء. 😊\nMentioning external usernames is not allowed here.")
            await update.message.delete()
            return

        # منع استدعاء البوت Genie أكثر من مرة
        if "Genie" in message_text or "@AIChatGeniebot" in message_text:
            if user_id in genie_users and user_id != YOUR_ADMIN_ID:
                await update.message.reply_text("🚫 يمكنك استدعاء Genie مرة واحدة فقط لتجنب الإزعاج. شكراً لتفهمك! 🙏\nYou can only call Genie once to avoid spamming. Thank you for understanding!")
                await update.message.delete()
                return
            genie_users.add(user_id)

    elif chat_id != GROUP_ID:
        # الرسائل الخاصة
        if not context.user_data.get('q2'):
            await update.message.reply_text("⚠️ يرجى البدء بالضغط على /start لاتباع الإرشادات. ⚠️\nPlease press /start to follow the instructions.")
            return

        if not context.user_data.get('q3'):
            context.user_data['q3'] = message_text  # حفظ الهدف
            context.user_data['q4'] = True
            await update.message.reply_text("🌍 ما هي لغتك الأم؟\nWhat is your mother language?")
        elif not context.user_data.get('q5'):
            context.user_data['lang'] = message_text  # حفظ اللغة
            context.user_data['q5'] = True
            # إضافة أزرار نعم/لا للالتزام بالقواعد
            keyboard = [
                [InlineKeyboardButton("نعم | Yes", callback_data="yes_rules")],
                [InlineKeyboardButton("لا | No", callback_data="no_rules")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("📜 هل ستلتزم بقواعد القناة؟\nWill you abide by the channel rules?", reply_markup=reply_markup)
        elif not context.user_data.get('q6'):
            # الانتظار حتى يتم الرد على السؤال السابق بالأزرار
            return
        else:
            # الانتظار حتى يتم الرد على السؤال الأخير بالأزرار
            return

async def handle_language(query: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('q6'):
        return

    # إرسال رسالة المعالجة
    processing_msg = await query.message.reply_text("✅ تم استلام إجاباتك! جارٍ معالجتها...")

    # إضافة تأثير النقاط المتحركة
    for _ in range(3):  # كرر العملية 3 مرات
        await asyncio.sleep(1)  # تأخير 1 ثانية
        await processing_msg.edit_text("✅ تم استلام إجاباتك! جارٍ معالجتها.")  # تعديل الرسالة
        await asyncio.sleep(1)
        await processing_msg.edit_text("✅ تم استلام إجاباتك! جارٍ معالجتها..")  # تعديل الرسالة
        await asyncio.sleep(1)
        await processing_msg.edit_text("✅ تم استلام إجاباتك! جارٍ معالجتها...")  # تعديل الرسالة

    # حذف رسالة المعالجة بعد الانتهاء
    await asyncio.sleep(1)
    await processing_msg.edit_text("📝 جاري توجيهك إلى القناة؛ الرجاء الانتظار...")

    # إرسال الرسالة التالية
    await asyncio.sleep(3)
    await query.message.reply_text("⏳ بضع ثواني فقط ...\n⌛ Redirecting you; please be patient💤...")
    await asyncio.sleep(3)
    try:
        if CHANNEL_ID:
            try:
                await context.bot.approve_chat_join_request(chat_id=CHANNEL_ID, user_id=query.from_user.id)
                await query.message.reply_text("✅ تمت إضافتك للقناة بنجاح! 🎉\n✅ You have been successfully added to the channel! 🎉")
            except Exception as e:
                print(f"Error adding user to channel: {e}")
                invite_link = "https://t.me/EnglishConvs"
                await query.message.reply_text(
                    f"🔗 يرجى الانضمام للقناة من خلال الرابط التالي:\n{invite_link}\n\nنرحب بك! 😊\n"
                    f"🔗 Please join the channel using the following link:\n{invite_link}\n\nWelcome! 😊"
                )
    except Exception as e:
        print(f"Error in handle_language: {e}")

        # إرسال جميع الإجابات إلى الأدمن
        if YOUR_ADMIN_ID:
            await context.bot.send_message(
                chat_id=YOUR_ADMIN_ID,
                text=(
                    f"📥 طلب انضمام جديد:\n"
                    f"الاسم: {update.message.from_user.full_name}\n"
                    f"اسم المستخدم: @{update.message.from_user.username}\n"
                    f"معرف المستخدم: {update.message.from_user.id}\n"
                    f"الهدف: {context.user_data['q3']}\n"
                    f"اللغة: {context.user_data['lang']}\n"
                    f"هل يلتزم بالقواعد؟: {context.user_data['rules_agreement']}\n"
                    f"هل سيشارك مشاركة إيجابية؟: {context.user_data['positive_participation']}"
                )
            )
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ حدث خطأ، يرجى المحاولة لاحقاً.\n⚠️ An error occurred, please try again later.")

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
