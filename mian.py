import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import time

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
YOUR_ADMIN_ID = os.environ.get('YOUR_ADMIN_ID')
Genie_ID = os.environ.get('Genie_ID')

def start(update, context):
    keyboard = [[InlineKeyboardButton("نعم", callback_data='yes'), InlineKeyboardButton("لا", callback_data='no')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('هل أنت على استعداد للالتزام بقواعد القناة؟', reply_markup=reply_markup)
    context.user_data['q1'] = None

def button(update, context):
    query = update.callback_query
    query.answer()
    if query.data == 'yes':
        context.user_data['q1'] = True
        keyboard = [[InlineKeyboardButton("نعم", callback_data='yes2'), InlineKeyboardButton("لا", callback_data='no')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="هل أنت متفرغ للمشاركة الفعالة في القناة؟", reply_markup=reply_markup)
        context.user_data['q2'] = None
    elif query.data == 'no':
        query.edit_message_text(text="شكراً لاهتمامك.")
        return

def button2(update, context):
    query = update.callback_query
    query.answer()
    if query.data == 'yes2':
        context.user_data['q2'] = True
        query.edit_message_text(text="ما هو هدفك من الانضمام إلى هذه القناة؟")
        context.user_data['q3'] = None
    elif query.data == 'no':
        query.edit_message_text(text="شكراً لاهتمامك.")
        return

def handle_message(update, context):
    if 'q3' in context.user_data and context.user_data['q3'] is None:
        context.user_data['q3'] = update.message.text
        update.message.reply_text("ما هي لغتك الأم؟")
        context.user_data['q4'] = None
    elif 'q4' in context.user_data and context.user_data['q4'] is None:
        context.user_data['q4'] = update.message.text
        if len(context.user_data['q3'].split()) >= 10:
            add_user_to_channel(update, context)
        else:
            update.message.reply_text("يجب أن تتكون رسالتك من 10 كلمات على الأقل.")

def add_user_to_channel(update, context):
    try:
        context.bot.add_chat_members(chat_id=CHANNEL_ID, user_ids=[update.effective_user.id])
        update.message.reply_text('تمت إضافتك إلى القناة! نأمل أن تستفيد وتشارك بفعالية.')
        context.bot.send_message(chat_id=update.effective_user.id, text="مرحباً بك في قناة تعلم اللغة الإنجليزية! نأمل أن تستفيد من المحتوى وتشارك بفعالية. يرجى الاطلاع على
