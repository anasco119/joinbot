import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from flask import Flask, jsonify

# تحميل متغيرات البيئة
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
YOUR_ADMIN_ID = os.getenv('YOUR_ADMIN_ID')
GROUP_ID = os.getenv('GROUP_ID')

WELCOME_MESSAGE_TEXT = """
**Welcome to our channel!** To join the channel, please answer a few questions.
Click the button below to get started ✅

----------------------------

✨ **مرحباً بك في قناتنا!** ✨

للانضمام إلى القناة، يرجى الإجابة على بعض الأسئلة.
اضغط على الزر أدناه للبدء...
"""

user_data = {}
muted_users = set()

# إنشاء خادم HTTP باستخدام Flask
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!'

@app.route('/status')
def status():
    return jsonify(status='active', timestamp=str(datetime.now()))

if __name__ == '__main__':
    app.run(port=os.getenv('PORT', 3000))

# تعريف وظيفة لمعالجة الأعضاء الجدد
def new_chat_members(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    if str(chat_id) == GROUP_ID:
        for user in update.message.new_chat_members:
            welcome_message = f"**مرحباً بك، {user.first_name}!** \n\nيسعدنا انضمانك إلى مجموعتنا. نأمل أن تستفيد من محتوى المجموعة وتشاركنا بأفكارك!"

            context.bot.send_message(chat_id, welcome_message, parse_mode='Markdown')

# تعريف وظيفة لبدء الاستبيان
def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    user_data[chat_id] = {'q1': None, 'q2': None, 'q3': None, 'q4': None, 'q5': None, 'q6': None}

    keyboard = [[InlineKeyboardButton('start', callback_data='start_questions')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(WELCOME_MESSAGE_TEXT, reply_markup=reply_markup, parse_mode='Markdown')

# تعريف وظيفة لمعالجة الأزرار
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    data = query.data

    query.answer()

    if data == 'start_questions':
        keyboard = [[InlineKeyboardButton('yes', callback_data='yes'), InlineKeyboardButton('no', callback_data='no')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text('✅ **هل أنت على استعداد للالتزام بقواعد القناة؟** ✅\n\nAre you prepared to follow the channel guidelines?', reply_markup=reply_markup, parse_mode='Markdown')
    elif data == 'yes':
        user_data[chat_id]['q1'] = True
        keyboard = [[InlineKeyboardButton('yes', callback_data='yes2'), InlineKeyboardButton('no', callback_data='no2')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text('Are you available to actively participate in the channel?\n\n**هل أنت متفرغ للمشاركة الفعالة في القناة؟**', reply_markup=reply_markup, parse_mode='Markdown')
    elif data in ['no', 'no2']:
        query.edit_message_text('❌ **شكراً لاهتمامك.**', parse_mode='Markdown')
    elif data == 'yes2':
        user_data[chat_id]['q2'] = True
        query.edit_message_text('**ما هو هدفك من الانضمام إلى هذه القناة؟** (يرجى الرد برسالة نصية)\n\nWhat is your goal for joining this channel? (Please reply with a text message)', parse_mode='Markdown')

# تعريف وظيفة لمعالجة الرسائل النصية
def handle_message(update: Update, context: CallbackContext):
    # يمكنك إضافة معالجة الرسائل النصية هنا
    pass

def main():
    if not TOKEN:
        print('Error: BOT_TOKEN environment variable is not set.')
        return

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # إضافة المعالجات
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_chat_members))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print('Bot is starting...')
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
