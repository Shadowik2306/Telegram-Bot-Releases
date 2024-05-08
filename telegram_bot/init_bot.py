import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from chat_info import *
import variables

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def check_new_releases(context: ContextTypes.DEFAULT_TYPE):
    handler = check_repos()
    for event in handler:
        chats = get_chat_with_topic(event)
        for chat_id in chats:
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"{handler[event]['name']}\n\n "
                                                f"{handler[event]['body']}")
            for asset in handler[event]['assets']:
                with open(f"static/{event}/{asset['name']}", "rb") as file:
                    await context.bot.send_document(chat_id=chat_id, document=file)


async def keyboard_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if update.effective_user.id not in variables.VERIFIED_USERS:
        await context.bot.editMessageText(chat_id=update.effective_chat.id,
                                          message_id=query.message.message_id,
                                          text="You dont have enough privileges")
        await set_repo(update, context)
        return

    if "SET_REPO" in query.data:
        set_chat(update.effective_chat.id, query.data[9:])
        await set_repo(update, context, edit=True)
    elif "DELETE_REPO" in query.data:
        delete_chat(update.effective_chat.id, query.data[12:])
        await set_repo(update, context, edit=True)
    elif "RETURN_SET" in query.data:
        await context.bot.editMessageText(chat_id=update.effective_chat.id,
                                          message_id=query.message.message_id,
                                          text="Preferences has been set")




async def set_repo(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    users_rep, all_rep = get_repos(update.effective_chat.id)
    keyboard = [
        [
            InlineKeyboardButton(repo if repo not in users_rep else "✓ " + repo,
                                 callback_data=f'SET_REPO_{repo}' if repo not in users_rep else f'DELETE_REPO_{repo}')
            for repo in all_rep
        ],
        [
            InlineKeyboardButton("Return", callback_data="RETURN_SET")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    if edit:
        await context.bot.editMessageReplyMarkup(chat_id=update.effective_chat.id,
                                                 message_id=update.callback_query.message.message_id,
                                                 reply_markup=reply_markup)
        return
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Lets select repository",
                                   reply_markup=reply_markup)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Hello, I am bot. I am going to redirect latest releases of your projects!")
    if not check_chat_existance(update.effective_chat.id):
        await set_repo(update, context)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="I have your preferences, but if you want to change it, type /set_repo")


async def main_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.to_dict()
    print(response)

    if "new_chat_participant" in response:
        if response["new_chat_participant"]["id"] == context.bot.id:
            await start(update, context)


def init_bot():
    application = ApplicationBuilder().token(variables.TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    set_repo_handler = CommandHandler('set_repo', set_repo)
    application.add_handler(start_handler)
    application.add_handler(set_repo_handler)
    job_queue = application.job_queue
    job_minute = job_queue.run_repeating(check_new_releases, interval=60, first=10)

    application.add_handler(CallbackQueryHandler(keyboard_callback))
    application.add_handler(MessageHandler(filters.ALL, main_group_message))
    application.run_polling()