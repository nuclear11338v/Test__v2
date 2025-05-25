from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_sticker_help():
    """Generate main help menu content"""
    help_menu = """
            📜 <b>Sticker Help</b>
            
            <i>This commands helps group admins manage sticker packs by banning, unbanning, and setting rules for their use.</i>
            
<b>🔧 General Commands</b>
1. <code>/bansticker</code> [pack_name/URL/reply] [reason]
   - Bans a sticker pack permanently.
   - How to specify pack:
     - Reply to a sticker to ban its pack.
     - Provide the pack name (e.g., PackName).
     - Use a URL (e.g., <code>https://t.me/addstickers/PackName</code>).
   - Example: <i>/bansticker PackName Spamming</i>
   - Note: Reason is optional.

2. <code>/tbansticker</code> [pack_name/URL/reply] [duration] [reason]
   - Temporarily bans a sticker pack.
   - Duration format: 1m (minutes), 1h (hours), 1d (days).
   - Example: <i>/tbansticker PackName 1h Spamming</i>
   - Note: Duration is required; reason is optional.

3. <code>/unbansticker</code> [pack_name/URL] [reason]
   - Unbans a sticker pack.
   - Example: <i>/unbansticker PackName No longer needed</i>
   - Note: Reason is optional.

⚙️ <b>Settings Commands</b>
4. <code>/banstickermode</code> [mute/ban/kick/delete] [reason]
   - Sets the action for banned sticker use.
   - Options: mute, ban, kick, delete (default).
   - Example: <i>/banstickermode ban Inappropriate content</i>
   - Note: Reason is optional.

5. <code>/wbansticker</code> [on/off] [reason]
   - Enables/disables warnings for banned stickers.
   - Example: <i>/wbansticker on Enable warnings</i>
   - Note: Reason is optional.

6. <code>/wbanstickerlimit</code> [number/default] [reason]
   - Sets warning limit before action.
   - Range: 1 to 100; default = 3.
   - Example: <i>/wbanstickerlimit 5 Strict enforcement</i>
   - Note: Reason is optional.

7. <code>/wbanstickermode</code> [ban/kick/mute] [reason]
   - Sets action after warning limit.
   - Example: <i>/wbanstickermode mute Reduce disruptions</i>
   - Note: Reason is optional.

8. <code>/allowadmins</code> [on/off] [reason]
   - Allows/restricts admins from using commands.
   - Only for group owner.
   - Example: <i>/allowadmins on Admins trusted</i>
   - Note: Reason is optional.

9. <code>/banstickeron</code> [all/user/admin] [reason]
   - Sets who is affected by bans.
   - Options: all (default), user (non-admins), admin.
   - Example: <i>/banstickeron user Protect admins</i>
   - Note: Reason is optional.

 <b>Status Command</b>
10. <code>/banstickerstatus</code>
    - Shows current settings and banned packs.
    - Example: <i>/banstickerstatus</i>

<b>💡 Tips</b>
<i>- Use letters, numbers, underscores, or hyphens for pack names.</i>
<i>- Reply to stickers for easy banning.</i>
<i>- Check settings with /banstickerstatus.</i>
<b>- All actions are logged.</b>
    """
    
    buttons = [
        ("Close", "sticker_close"),
        ("Back", "sticker_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('sticker_'))
def handle_help_callback(call):
    try:
        if call.data == 'sticker_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'sticker_back':
            text, markup = create_english_help()
            bot.edit_message_text(
                text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=markup
            )
            return

        bot.answer_callback_query(call.id, "⏳ Section under development!", show_alert=True)

    except Exception as e:
        logger.error(f"Callback error: {str(e)}\n{traceback.format_exc()}")
        try:
            bot.answer_callback_query(call.id, f"Error in Callback.\nPlease try again.", show_alert=True)
        except Exception as e:
            logger.error(f"Failed to answer callback: {str(e)}")