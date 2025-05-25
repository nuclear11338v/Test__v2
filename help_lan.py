from telebot import TeleBot, types
from config import BOT_TOKEN, logger, bot
from help_languages.help_hindi import create_hindi_help
from help_languages.help_english import create_english_help
from help_languages.help_forward import create_Forward_help
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


# Update LANGUAGE_HELP dictionary to include 'admin'
LANGUAGE_HELP = {
    'hindi': create_hindi_help,
    'english': create_english_help,
    'Forward': create_Forward_help,
    'admin': create_admins_help,
    'antiflood': create_antiflood_help,
    'antiraid': create_antiraid_help,
    'ban': create_bans_help,
    'blocklist': create_blocklist_help,
    'button': create_buttons_help,
    'cleancommand': create_cleancommand_help,
    'cleanservice': create_cleanservice_help,
    'connection': create_connection_help,
    'custom': create_custom_help,
    'filters': create_filters_help,
    'hindi': create_hindi_help,
    'join': create_join_help,
    'kick': create_kicks_help,
    'lock': create_locks_help,
    'mute': create_mute_help,
    'namec': create_namec_help,
    'note': create_notes_help,
    'pin': create_pins_help,
    'purge': create_purges_help,
    'report': create_reports_help,
    'rule': create_rules_help,
    'slowmode': create_slowmo_help,
    'sticker': create_sticker_help,
    'topic': create_topics_help,
    'warn': create_warns_help,
    'welcome': create_welcome_help
}

@bot.message_handler(commands=['nhelp'])
def handle_lanhelp(message):
    if message.chat.type in ['group', 'supergroup']:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text="Cʟɪᴄᴋ Hᴇʀᴇ",
            url="https://t.me/MrsKiraBot?start=forward"
        ))
        bot.reply_to(
            message,
            "Cʟɪᴄᴋ Bᴜᴛᴛᴏɴ Bᴇʟᴏᴡ Fᴏʀ Hᴇʟᴘ",
            reply_markup=markup
        )
    else:
        response = "Available languages for help menu:\n- english\n- hindi\n- japanese\n- urdu\n- bengali\n- chinese\n- punjabi\n- telugu\n- admin\n\nex - '/help english'"
        bot.reply_to(message, response)

@bot.message_handler(regexp=r'^[\/!](help)(?:\s|$|@)')
def handle_help(message):
    # Extract the language argument from the command (e.g., /help english)
    command_text = message.text.lower().split()
    language = command_text[1] if len(command_text) > 1 else 'english'  # Default to English if no language specified

    if message.chat.type in ['group', 'supergroup']:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text="Cʟɪᴄᴋ Hᴇʀᴇ",
            url=f"https://t.me/MrsKiraBot?start={language}"
        ))
        bot.reply_to(
            message,
            "Cʟɪᴄᴋ Bᴜᴛᴛᴏɴ Bᴇʟᴏᴡ Fᴏʀ Hᴇʟᴘ",
            reply_markup=markup
        )
    else:
        try:
            # Check if the language is supported
            if language in LANGUAGE_HELP:
                text, markup = LANGUAGE_HELP[language]()
                bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
            else:
                bot.reply_to(message, f"Language '{language}' is not supported. Available languages: {', '.join(LANGUAGE_HELP.keys())}")
        except Exception as e:
            logger.error(f"Error in /help {language} command: {str(e)}")
            bot.reply_to(message, "An error occurred. Please try again later.")

@bot.message_handler(commands=['bengalihelp'])
def handle_bengalihelp(message):
    if message.chat.type in ['group', 'supergroup']:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text="Cʟɪᴄᴋ Hᴇʀᴇ",
            url="https://t.me/MrsKiraBot?start=bengali"
        ))
        bot.reply_to(
            message,
            "Cʟɪᴄᴋ Bᴜᴛᴛᴏɴ Bᴇʟᴏᴡ Fᴏʀ Hᴇʟᴘ",
            reply_markup=markup
        )
    else:
        try:
            text, markup = create_bengali_help()
            bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            logger.error(f"Error in /bengalihelp command: {str(e)}")
            bot.reply_to(message, "An error occurred. Please try again later.")

@bot.message_handler(commands=['hindihelp'])
def handle_hindihelp(message):
    if message.chat.type in ['group', 'supergroup']:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text="Cʟɪᴄᴋ Hᴇʀᴇ",
            url="https://t.me/MrsKiraBot?start=hindi"
        ))
        bot.reply_to(
            message,
            "Cʟɪᴄᴋ Bᴜᴛᴛᴏɴ Bᴇʟᴏᴡ Fᴏʀ Hᴇʟᴘ",
            reply_markup=markup
        )
    else:
        try:
            text, markup = create_hindi_help()
            bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            logger.error(f"Error in /hindihelp command: {str(e)}")
            bot.reply_to(message, "An error occurred. Please try again later.")

@bot.message_handler(commands=['japanesehelp'])
def handle_japanesehelp(message):
    if message.chat.type in ['group', 'supergroup']:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text="Cʟɪᴄᴋ Hᴇʀᴇ",
            url="https://t.me/MrsKiraBot?start=japanese"
        ))
        bot.reply_to(
            message,
            "Cʟɪᴄᴋ Bᴜᴛᴛᴏɴ Bᴇʟᴏᴡ Fᴏʀ Hᴇʟᴘ",
            reply_markup=markup
        )
    else:
        try:
            text, markup = create_japanese_help()
            bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            logger.error(f"Error in /japanesehelp command: {str(e)}")
            bot.reply_to(message, "An error occurred. Please try again later.")

@bot.message_handler(commands=['punjabihelp'])
def handle_punjabihelp(message):
    if message.chat.type in ['group', 'supergroup']:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text="Cʟɪᴄᴋ Hᴇʀᴇ",
            url="https://t.me/MrsKiraBot?start=punjabi"
        ))
        bot.reply_to(
            message,
            "Cʟɪᴄᴋ Bᴜᴛᴛᴏɴ Bᴇʟᴏᴡ Fᴏʀ Hᴇʟᴘ",
            reply_markup=markup
        )
    else:
        try:
            text, markup = create_punjabi_help()
            bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            logger.error(f"Error in /punjabihelp command: {str(e)}")
            bot.reply_to(message, "An error occurred. Please try again later.")

@bot.message_handler(commands=['teluguhelp'])
def handle_teluguhelp(message):
    if message.chat.type in ['group', 'supergroup']:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text="Cʟɪᴄᴋ Hᴇʀᴇ",
            url="https://t.me/MrsKiraBot?start=telugu"
        ))
        bot.reply_to(
            message,
            "Cʟɪᴄᴋ Bᴜᴛᴛᴏɴ Bᴇʟᴏᴡ Fᴏʀ Hᴇʟᴘ",
            reply_markup=markup
        )
    else:
        try:
            text, markup = create_telugu_help()
            bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            logger.error(f"Error in /teluguhelp command: {str(e)}")
            bot.reply_to(message, "An error occurred. Please try again later.")

@bot.message_handler(commands=['urduhelp'])
def handle_urduhelp(message):
    if message.chat.type in ['group', 'supergroup']:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text="Cʟɪᴄᴋ Hᴇʀᴇ",
            url="https://t.me/MrsKiraBot?start=urdu"
        ))
        bot.reply_to(
            message,
            "Cʟɪᴄᴋ Bᴜᴛᴛᴏɴ Bᴇʟᴏᴡ Fᴏʀ Hᴇʟᴘ",
            reply_markup=markup
        )
    else:
        try:
            text, markup = create_urdu_help()
            bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            logger.error(f"Error in /urduhelp command: {str(e)}")
            bot.reply_to(message, "An error occurred. Please try again later.")

@bot.message_handler(commands=['englishhelp'])
def handle_englishhelp(message):  # Fixed the function name from handle_urduhelp to handle_englishhelp
    if message.chat.type in ['group', 'supergroup']:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text="Cʟɪᴄᴋ Hᴇʀᴇ",
            url="https://t.me/MrsKiraBot?start=english"
        ))
        bot.reply_to(
            message,
            "Cʟɪᴄᴋ Bᴜᴛᴛᴏɴ Bᴇʟᴏᴡ Fᴏʀ Hᴇʟᴘ",
            reply_markup=markup
        )
    else:
        try:
            text, markup = create_english_help()
            bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            logger.error(f"Error in /englishhelp command: {str(e)}")
            bot.reply_to(message, "An error occurred. Please try again later.")

@bot.message_handler(commands=['chinesehelp'])
def handle_chinesehelp(message):  # Fixed the incorrect handler for chinesehelp
    if message.chat.type in ['group', 'supergroup']:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text="Cʟɪᴄᴋ Hᴇʀᴇ",
            url="https://t.me/MrsKiraBot?start=chinese"
        ))
        bot.reply_to(
            message,
            "Cʟɪᴄᴋ Bᴜᴛᴛᴏɴ Bᴇʟᴏᴡ Fᴏʀ Hᴇʟᴘ",
            reply_markup=markup
        )
    else:
        try:
            text, markup = create_chinese_help()
            bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            logger.error(f"Error in /chinesehelp command: {str(e)}")
            bot.reply_to(message, "An error occurred. Please try again later.")