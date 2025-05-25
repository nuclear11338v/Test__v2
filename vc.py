import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import bot




VC_START_MSGS = [
    "🎙️ *Vᴏɪᴄᴇ Sʏsᴛᴇᴍ Oɴʟɪɴᴇ!** \n🔥 *Cᴏɴɴᴇᴄᴛɪɴɢ Sᴏᴜɴᴅ Wᴀᴠᴇs*... 🎵 *Lᴇᴛ’s Mᴀᴋᴇ Sᴏᴍᴇ Nᴏɪsᴇ!*",
    "⚡ *Aᴜᴅɪᴏ Rᴇᴀʟᴍ Aᴄᴛɪᴠᴀᴛᴇᴅ!* \n🎧 *Fʀᴇǫᴜᴇɴᴄʏ Lᴏᴄᴋᴇᴅ*! 🚀 *Jᴜᴍᴘ Iɴ ᴛᴏ ᴛʜᴇ Vɪʙᴇ!*",
    "🌌 *Vᴏᴄᴀʟ Gᴀʟᴀxʏ Dᴇᴘʟᴏʏᴇᴅ!** \n🛸 *Sᴏᴜɴᴅ Pᴏʀᴛᴀʟ Oᴘᴇɴ*. 🎉 *Rᴇᴀᴅʏ ᴛᴏ Rᴏᴄᴋ?*",
    "🎶 *Bᴇᴀᴛs Sʏɴᴄɪɴɢ Uᴘ!* \n🔊 *Vᴏɪᴄᴇ Hᴜʙ Aʟɪᴠᴇ*! 💥 *Jᴏɪɴ ᴛʜᴇ Sᴏɴɪᴄ Pᴀʀᴛʏ!*",
]

# Updated, more attractive VC end messages
VC_END_MSGS = [
    "🔇 *Vᴏɪᴄᴇ Cʜᴀᴛ Sʜᴜᴛᴛɪɴɢ Dᴏᴡɴ!*\n❌ *Sᴏᴜɴᴅ Wᴀᴠᴇs Fᴀᴅɪɴɢ*... 😴 **Tɪᴍᴇ ᴛᴏ Cʜɪʟʟ!*",
    "🎵 *Aᴜᴅɪᴏ Aᴅᴠᴇɴᴛᴜʀᴇ Eɴᴅᴇᴅ!*\n🛑 *Mɪᴄs Oғғ*! 🌙 *Cᴀᴛᴄʜ Yᴀ Nᴇxᴛ Tɪᴍᴇ!*",
    "💤 *Sɪʟᴇɴᴄᴇ Tᴀᴋᴇs Oᴠᴇʀ!*\n📴 *Vᴏᴄᴀʟ Lɪɴᴋ Bʀᴏᴋᴇɴ*... 🎧 *Uɴᴛɪʟ ᴛʜᴇ Nᴇxᴛ Bᴇᴀᴛ!*",
    "🚫 *Sᴏɴɪᴄ Sᴛᴏʀᴍ Sᴛᴏᴘᴘᴇᴅ!* \n🔕 *Eᴄʜᴏᴇs Gᴏɴᴇ*! ✨ *Sᴛᴀʏ Tᴜɴᴇᴅ ғᴏʀ Mᴏʀᴇ!*",
]

def create_vc_keyboard(chat_username):
    """Create inline keyboard for VC actions"""
    if not chat_username:
        return None  # Handle cases where chat_username is not available
    
    join_url = f"https://t.me/{chat_username}?videochat"
    share_url = f"https://t.me/share/url?url={join_url}&text=🎉%20Join%20our%20epic%20Voice%20Chat%20now!%20🔊"

    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🎤 Jᴏɪɴ Vᴏɪᴄᴇ Cʜᴀᴛ", url=join_url),
        InlineKeyboardButton("📢 Sʜᴀʀᴇ Vᴄ Lɪɴᴋ", url=share_url)
    )
    return keyboard

@bot.message_handler(content_types=['video_chat_started'])
def handle_video_chat_started(message):
    """Handle when a voice chat starts"""
    try:
        chat_id = message.chat.id
        chat_username = message.chat.username
        fancy_text = random.choice(VC_START_MSGS)

        bot.send_message(
            chat_id,
            f"╭─── ✦ Vᴏɪᴄᴇ Cʜᴀᴛ Lᴀᴜɴᴄʜ ✦ ───╮\n"
            f"┃ 🎉 *Vᴏɪᴄᴇ Cʜᴀᴛ Iꜱ Nᴏᴡ Lɪᴠᴇ!* 🎉\n"
            f"┃\n"
            f"┃ {fancy_text}\n"
            f"┃\n"
            f"┃ 💥 *Dɪᴠᴇ Iɴᴛᴏ ᴛʜᴇ Sᴏɴɪᴄ Uɴɪᴠᴇʀsᴇ!*\n"
            f"╰───────────────────╯",
            reply_markup=create_vc_keyboard(chat_username),
            parse_mode='Markdown'
        )
    except Exception as e:
        bot.send_message(chat_id, "⚠️ Oops! Something went wrong while starting the voice chat.")
        print(f"Error in handle_video_chat_started: {e}")

@bot.message_handler(content_types=['video_chat_ended'])
def handle_video_chat_ended(message):
    """Handle when a voice chat ends"""
    try:
        chat_id = message.chat.id
        chat_username = message.chat.username
        fancy_text = random.choice(VC_END_MSGS)

        bot.send_message(
            chat_id,
            f"╭─── ✦ Vᴏɪᴄᴇ Cʜᴀᴛ Oғғ ✦ ───╮\n"
            f"┃ 😢 *Vᴏɪᴄᴇ Cʜᴀᴛ Hᴀꜱ Eɴᴅᴇᴅ!*\n"
            f"┃\n"
            f"┃ {fancy_text}\n"
            f"┃\n"
            f"┃ 🌟 *Sᴛᴀʏ Tᴜɴᴇᴅ ғᴏʀ ᴛʜᴇ Nᴇxᴛ Sᴇssɪᴏɴ!*\n"
            f"╰───────────────────╯",
            reply_markup=create_vc_keyboard(chat_username),
            parse_mode='Markdown'
        )
    except Exception as e:
        bot.send_message(chat_id, "⚠️ Oops! Something went wrong while ending the voice chat.")
        print(f"Error in handle_video_chat_ended: {e}")
