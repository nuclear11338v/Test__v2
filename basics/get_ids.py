import telebot
from config import bot
from kick import disabled
from data.data import store

def escape_html(text):
    return telebot.util.escape(text)

def get_user_link(user):
    if user.username:
        return f"@{escape_html(user.username)}"
    return f"<a href='tg://user?id={user.id}'>{escape_html(user.first_name)}</a>"

def get_user_bio(user_id):
    try:
        user_profile = bot.get_chat(user_id)
        return escape_html(user_profile.bio) if user_profile.bio else "No bio available"
    except:
        return "Bio not accessible"

@bot.message_handler(commands=['id'])
@store
@disabled
def handle_id(message):
    chat_id = message.chat.id

    if message.chat.type in ['group', 'supergroup']:
        args = message.text.split(maxsplit=1)

        if not message.reply_to_message and len(args) == 1:
            bot.reply_to(
                message,
                f"<b>Group ID:</b> <code>{chat_id}</code>\n\n"
                "Use /id reply to someone with <b>/id</b> to get their info.",
                parse_mode="HTML"
            )
            return

        if message.reply_to_message:
            target = message.reply_to_message.from_user
        else:
            query = args[1].strip()
            try:
                if query.startswith("@"):
                    target = bot.get_chat(query)
                else:
                    target = bot.get_chat(int(query))
            except:
                bot.reply_to(message, "❌ <b>User not found or invalid ID/username.</b>", parse_mode="HTML")
                return

        user_link = get_user_link(target)
        response = (
            f"👤 <b>User:</b> {user_link}\n\n"
            f"🆔 <b>ID:</b> <code>{target.id}</code>"
        )
        bot.reply_to(message, response, parse_mode="HTML")

    else:
        user = message.from_user
        bio = get_user_bio(user.id)
        response = (
            f"👤 <b>Your ID:</b> <code>{user.id}</code>\n\n"
            f"🧍 <b>Name:</b> {escape_html(user.first_name)}\n\n"
            f"📝 <b>Bio:</b> {bio}"
        )
        bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=['me', 'info'])
@store
def handle_me_info(message):
    user = message.from_user
    bio = get_user_bio(user.id)
    response = (
        f"👤 <b>Your ID:</b> <code>{user.id}</code>\n\n"
        f"🧍 <b>Name:</b> {escape_html(user.first_name)}\n"
        f"📝 <b>Bio:</b> {bio}"
    )
    bot.reply_to(message, response, parse_mode="HTML")
