import telebot 
from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from notes import notes, send_note
from help_languages.help_hindi import create_hindi_help
from help_languages.help_english import create_english_help
from help_languages.help_forward import create_Forward_help
from kick import disabled 
from data.data import store
from broadcasting.bcast import record_user_id
from telebot import util
from rules import display_rules
from help_languages.help_admins import create_admins_help
from help_languages.help_antiflood import create_antiflood_help
from help_languages.help_antiraid import create_antiraid_help
from help_languages.help_bans import create_bans_help
from help_languages.help_blocklist import create_blocklist_help
from help_languages.help_buttons import create_buttons_help
from help_languages.help_cleancommand import create_cleancommand_help
from help_languages.help_cleanservice import create_cleanservice_help
from help_languages.help_connection import create_connection_help
from help_languages.help_custom import create_custom_help
from help_languages.help_filters import create_filters_help
from help_languages.help_hindi import create_hindi_help
from help_languages.help_join import create_join_help
from help_languages.help_kicks import create_kicks_help
from help_languages.help_locks import create_locks_help
from help_languages.help_mute import create_mute_help
from help_languages.help_namechanger import create_namec_help
from help_languages.help_notes import create_notes_help
from help_languages.help_pins import create_pins_help
from help_languages.help_purges import create_purges_help
from help_languages.help_reports import create_reports_help
from help_languages.help_rules import create_rules_help
from help_languages.help_slowmode import create_slowmo_help
from help_languages.help_sticker import create_sticker_help
from help_languages.help_topics import create_topics_help
from help_languages.help_warns import create_warns_help
from help_languages.help_welcome import create_welcome_help


def get_user_link(user):
    """Generate a Telegram user link."""
    sanitized_name = telebot.util.escape(user.first_name)
    return f"<a href='tg://user?id={user.id}'>{sanitized_name}</a>"

def get_group_owner(chat):
    """Get the group owner."""
    try:
        administrators = bot.get_chat_administrators(chat.id)
        for admin in administrators:
            if admin.status == "creator":
                return get_user_link(admin.user)
        return "Unknown"
    except Exception as e:
        logger.error(f"Error fetching group owner: {str(e)}")
        return "Unknown"

def count_admins(chat):
    """Count the number of admins in the group."""
    try:
        return len(bot.get_chat_administrators(chat.id))
    except Exception as e:
        logger.error(f"Error counting admins: {str(e)}")
        return 0

def count_members(chat):
    """Count the total number of members in the group (including bots)."""
    try:
        return bot.get_chat_member_count(chat.id)
    except Exception as e:
        logger.error(f"Error counting members: {str(e)}")
        return 0

@bot.message_handler(regexp=r'^[\/!](start)(?:\s|$|@)')
@disabled
@store
@record_user_id
def command_start(message):
    try:
        user_link = get_user_link(message.from_user)
        first_name = message.from_user.first_name
        text = message.text.strip()

        args = message.text.split()
        if len(args) > 1 and args[1].startswith("rules_"):
            try:
                chat_id = args[1].replace("rules_", "")
                display_rules(chat_id, message.from_user.id, is_private=True)
                display_rules(chat_id, message.from_user.id, is_private=True)
                return
            except Exception as e:
                bot.send_message(message.from_user.id, "Invalid or expired link.")
                return

        if text.startswith('/start note_'):
            params = text[len('/start note_'):].split('_')
            if len(params) != 2:
                bot.send_message(message.chat.id, "Invalid note link!")
                return
            group_id, notename = params
            if group_id in notes and notename in notes[group_id]:
                send_note(message.chat.id, notes[group_id][notename])
            else:
                bot.send_message(message.chat.id, "Note not found!")
            return

        if text == '/start help':
            if message.chat.type == 'private':
                text, markup = create_english_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=help"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return

        if text == '/start admin':
            if message.chat.type == 'private':
                text, markup = create_admins_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=admins"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return

        if text == '/start antiflood':
            if message.chat.type == 'private':
                text, markup = create_antiflood_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=antiflood"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return

        if text == '/start antiraid':
            if message.chat.type == 'private':
                text, markup = create_antiraid_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=antiraid"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return

        if text == '/start ban':
            if message.chat.type == 'private':
                text, markup = create_bans_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=bans"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return

        if text == '/start forward':
            if message.chat.type == 'private':
                text, markup = create_Forward_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=japanese"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return

        if text == '/start hindi':
            if message.chat.type == 'private':
                text, markup = create_hindi_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=hindi"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return

        if text == '/start blocklist':
            if message.chat.type == 'private':
                text, markup = create_blocklist_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=blocklist"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return

        if text == '/start english':
            if message.chat.type == 'private':
                text, markup = create_english_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=chinese"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return

        if text == '/start button':
            if message.chat.type == 'private':
                text, markup = create_buttons_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=button"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return

        if text == '/start cleancommand':
            if message.chat.type == 'private':
                text, markup = create_cleancommand_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=cleancommand"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start cleanservice':
            if message.chat.type == 'private':
                text, markup = create_cleanservice_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=service"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start connection':
            if message.chat.type == 'private':
                text, markup = create_connection_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=connection"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start custom':
            if message.chat.type == 'private':
                text, markup = create_custom_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=custom"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start filters':
            if message.chat.type == 'private':
                text, markup = create_filters_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=filters"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start join':
            if message.chat.type == 'private':
                text, markup = create_join_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=join"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start kick':
            if message.chat.type == 'private':
                text, markup = create_kicks_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=kicks"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start lock':
            if message.chat.type == 'private':
                text, markup = create_locks_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=locks"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start mute':
            if message.chat.type == 'private':
                text, markup = create_mute_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=mute"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start namec':
            if message.chat.type == 'private':
                text, markup = create_namec_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=namec"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start notes':
            if message.chat.type == 'private':
                text, markup = create_notes_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=notes"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start pins':
            if message.chat.type == 'private':
                text, markup = create_pins_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=pins"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start purges':
            if message.chat.type == 'private':
                text, markup = create_purges_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=purges"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start reports':
            if message.chat.type == 'private':
                text, markup = create_reports_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=reports"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start rules':
            if message.chat.type == 'private':
                text, markup = create_rules_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=rules"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return

        if text == '/start slowmode':
            if message.chat.type == 'private':
                text, markup = create_slowmo_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=slowmode"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start sticker':
            if message.chat.type == 'private':
                text, markup = create_sticker_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=sticker"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start topics':
            if message.chat.type == 'private':
                text, markup = create_topics_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=topics"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start warn':
            if message.chat.type == 'private':
                text, markup = create_warns_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=warns"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return
            
        if text == '/start welcome':
            if message.chat.type == 'private':
                text, markup = create_welcome_help()
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    text="Click here",
                    url="https://t.me/MrsKiraBot?start=welcome"
                ))
                bot.reply_to(
                    message,
                    "Please use the help menu in private chat!",
                    reply_markup=markup
                )
            return

        if message.chat.type == 'private':
            caption = (
                "<b>╔═══━━━ 𝚆𝙴𝙻𝙲𝙾𝙼𝙴 ━━━═══╗</b>\n\n"
                f"‣ 𝙷𝙴𝚈, {user_link}\n\n"
                "<b>├── 🔸 𝙰𝙱𝙾𝚄𝚃 ──┤</b>\n"
                "│   ├─ 𝚅ᴇʀꜱɪᴏɴ : ⓿.➋\n"
                "│   ├─ 𝚄ᴘᴛɪᴍᴇ : 24/7\n"
                "│   └─ 𝙳ᴇ𝚟ᴇ𝚕𝚘𝚙ᴇ𝚛 : <a href='https://t.me/PB_X01'>𝙿𝙱 𝕏</a>\n"
                "│\n"
                "<b>├── 🔸 𝚂𝚄𝙿𝙿𝙾𝚁𝚃 ──┤</b>\n"
                "│   ├─ 𝙶ʀᴏᴜᴘ : <a href='https://t.me/KiraChatGroup'>𝚃𝙴𝙰𝙼</a>\n"
                "│   └─ 𝙲ʜᴀɴɴᴇʟ : <a href='https://t.me/KiraOfficialSupportChannel'>𝚄𝙿𝙳𝙰𝚃𝙴𝚂</a>\n"
                "│\n"
                "<b>╚═══━━━ 𝙿𝙾𝚆𝙴𝚁𝙴𝙳 𝙱𝚈 <a href='https://t.me/PB_X01'>𝙿𝙱 𝕏</a> ━━━═══╝</b>"
            )
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(
                text="Help",
                url="https://t.me/MrsKiraBot?start=help"
            ))
            bot.send_video(
                chat_id=message.chat.id,
                video="BAACAgUAAyEFAASJBnJVAAIFt2gNfx9zKjVi7AGNBjcXMl8WxB1VAAIDFwACQHlxVEMNXeCLXc-TNgQ",
                caption=caption,
                parse_mode='HTML',
                reply_markup=markup
            )
        else:
            group_owner = get_group_owner(message.chat)
            total_members = count_members(message.chat)
            total_admins = count_admins(message.chat)
            caption = (
                f"HEY THERE, {user_link}\n"
                f"TOTAL USER: {total_members}\n"
                f"TOTAL ADMINS: {total_admins}\n"
                f"OWNER: {group_owner}"
            )
            bot.send_video(
                chat_id=message.chat.id,
                video="BAACAgUAAyEFAASJBnJVAAIFt2gNfx9zKjVi7AGNBjcXMl8WxB1VAAIDFwACQHlxVEMNXeCLXc-TNgQ",
                caption=caption,
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Start command error: {str(e)}\n{traceback.format_exc()}")
        bot.reply_to(message, "Failed to process start command. Please try again later.")
       