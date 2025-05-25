from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_english_help():
    """Generate main help menu content"""
    help_menu = """
    <b>📚 Hᴇʟᴘ Mᴇɴᴜ</b>

    ├── 🔹 Hey im MrsKira
    │   │
    │   ├ 𝘾𝙃𝙊𝙊𝙎𝙀 𝙊𝙋𝙏𝙄𝙊𝙉𝙎
    │   ├ 𝙁𝙄𝙍𝙎𝙏 𝙐 𝙉𝙀𝙀𝘿 𝙏𝙊 𝘼𝘿𝘿 𝙈𝙀 𝙏𝙊 𝘼 𝙂𝙍𝙊𝙐𝙋
    │   └ 𝙄𝙉𝙅𝙊𝙔 𝘽𝘼𝘽𝙔 𝙐𝙎𝙄𝙉𝙂 𝙏𝙃𝙄𝙎 𝘽𝙊𝙏 :)
    │
    ├── 🔹Sᴜᴘᴘᴏʀᴛ
    │   ├ /help - Sнow Tнιs Mᴇɴu
    │   ├ /ping - Cнᴇcκ Sʏsтᴇм
    │   └ /start - Sтᴀʀт Tнᴇ Boт
    └──
    """
    
    buttons = [
        ("˹ Rules ˼", "english_rules"),
        ("˹ Clean Service ˼", "english_cleanservice"),
        ("˹ Purges ˼", "english_purges"),
        ("˹ Topics ˼", "english_topics"),
        ("˹ Name Changer ˼", "english_namec"),
        ("˹ Logs ˼", "english_logs"),
        ("˹ Help Lan ˼", "english_lan"),
        ("˹ AntiRaid˼", "english_antiraid"),
        ("˹ Forward ˼", "english_forward"),
        ("˹ Sticker ˼", "english_sticker"),
        ("˹ Custom C ˼", "english_custom"),
        ("˹ Connection ˼", "english_connection"),
        ("˹ Private C ˼", "english_private"),
        ("˹ Locks ˼", "english_lock"),
        ("˹ Disabling ˼", "english_disable"),
        ("˹ Format ˼", "english_format"),
        ("˹ Reports ˼", "english_reports"),
        ("˹ Bans ˼", "english_ban"),
        ("˹ Warns ˼", "english_warn"),
        ("˹ Mutes ˼", "english_mute"),
        ("˹ Kicks ˼", "english_kick"),
        ("˹ Notes ˼", "english_note"),
        ("˹ Floods ˼", "english_flood"),
        ("˹ Chatting ˼", "english_chat"),
        ("˹ Blocklist ˼", "english_blocklist"),
        ("˹ Filters ˼", "english_filter"),
        ("˹ Clean Command ˼", "english_cleancommand"),
        ("˹ Basics ˼", "english_basic"),
        ("˹ Auto Approve ˼", "english_app"),
        ("˹ Admin ˼", "english_botadmin"),
        ("˹ VC Help ˼", "english_voicechat"),
        ("˹ Extra Feature˼", "english_extra"),
        ("˹ Doɴᴀтᴇ ˼", "english_developersuppert"),
        ("➤ ˹ Suᴘᴘoʀт ˼", "english_groupsupport"),
        ("˹ 𝗰ʟ𝗼𝘀ᴇ ✘ ˼", "english_close")
    ]
    
    markup = types.InlineKeyboardMarkup()

    for i in range(0, len(buttons), 3):
        row = [types.InlineKeyboardButton(text, callback_data=data) 
               for text, data in buttons[i:i+3]]
        markup.add(*row)
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('english_'))
def handle_help_callback(call):
    try:
        if call.data == 'english_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'english_back':
            text, markup = create_english_help()
            bot.edit_message_text(
                text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=markup
            )
            return

        help_sections = {
            'english_rules': """
<b>Rules Module Help</b>

<i>The Rules module allows admins to manage and display group rules in chats, with options for private rules, custom buttons.</i>

<b>Available Commands</b>

<blockquote>/rules</blockquote>
<b>Purpose:</b> Displays the group’s rules.
<b>Usage:</b> <code>/rules</code>

<b>Example:</b>
<code>/rules</code> - <b>Shows rules.</b>

<blockquote>/setrules</blockquote>
<b>Purpose:</b> Sets or updates the group’s rules.
<b>Usage:</b> <code>/setrules</code> Supports Markdown and buttons.

<b>Example:</b>
<code>/setrules No spam! [Join](buttonurl://t.me/YourRulesLink)</code> - <b>Sets rules with a button.</b>

<blockquote>/privaterules [yes/no/on/off]</blockquote>
<b>Purpose:</b> private rules mode, Rules sent in PM
<b>Usage:</b> <code>/privaterules [yes/no/on/off]</code>

<b>Example:</b>
<code>/privaterules on</code> - <b>Enables private rules.</b>
<code>/privaterules off</code> - <b>Disables private rules.</b>

<blockquote>/resetrules</blockquote>
<b>Purpose:</b> Clears all rules and buttons for the group.
<b>Usage:</b> <code>/resetrules</code>

<b>Example:</b>
<code>/resetrules</code> - <b>Resets rules to empty.</b>

<blockquote>/setrulesbutton</blockquote>
<b>Purpose:</b> Sets a custom name for the private rules button.
<b>Usage:</b> <code>/setrulesbutton</code>

<b>Example:</b>
<code>/setrulesbutton View Rules</code> - <b>Sets button name.</b>

<blockquote>/resetrulesbutton</blockquote>
<b>Purpose:</b> Resets the private rules button name to default ("Rules").
<b>Usage:</b> <code>/resetrulesbutton</code>

<b>Example:</b>
<code>/resetrulesbutton</code> - <b>Resets button name.</b>

<b>Example Workflow</b>
<b>Set rules:</b> <code>/setrules No spam! [Join](buttonurl://link)</code> - <b>Sets rules with a button.</b>
<b>Enable private rules:</b> <code>/privaterules on</code> - <b>Makes rules private.</b>
<b>Set button name:</b> <code>/setrulesbutton Group Rules</code> - <b>Customizes private rules button.</b>
<b>View rules:</b> <code>/rules</code> - <b>Shows rules.</b>
<b>View raw:</b> <code>/rules noformat</code> - <b>Shows unformatted rule text.</b>
<b>Reset rules:</b> <code>/resetrules</code> - <b>Clears all rules.</b>
<b>Reset button:</b> <code>/resetrulesbutton</code> - <b>Restores default button name.</b>""",

            'english_cleanservice': """
            📜 <b>Cleanservice Help</b>

<code>/cleanservice</code> [service]
<code>/cleanservicetypes</code> <b>check the service types</b>
<code>/keepservice</code> [service]
<b>Available service message types:</b>

• <b>all:</b> <i>All service messages</i>
• <b>other:</b> <i>Miscellaneous (boosts, payments, etc.)</i>
• <b>photo:</b> <i>Chat photo/background changes</i>
• <b>pin:</b> <i>Message pinning</i>
• <b>title:</b> <i>Chat/topic title changes</i>
• <b>videochat:</b> <i>Video chat actions</i>""",

            'english_antiraid': """
            📜 <b>Antiraid Help</b>

  <i>The AntiRaid module helps protect your  group from sudden influxes of new members, which could indicate a raid or spam attack. This module allows group admins to enable manual or automatic AntiRaid protection, set ban durations, and configure triggers for automatic detection.</i>

      <b>Available Commands:</b>

1. <code>/antiraid</code> <b>[duration/off]</b>
   - Enables or disables AntiRaid protection manually.  
   - <b>Usage:</b>
     - <code>/antiraid</code> - <b>Toggles AntiRaid on/off (default duration: 6 hours).</b>
     - <code>/antiraid 3h</code> - Enables AntiRaid for a specific duration (e.g., 3 hours). Use formats like <code>30m</code> (minutes), <code>3h</code> (hours), or <code>1d</code> (days).
     - <code>/antiraid off</code> - <b>Disables AntiRaid immediately.</b>
   - When enabled, new members are temporarily banned for the set ban duration (see <code>/raidactiontime</code>).  
   - Example: <code>/antiraid 2h</code> <b>(Enables AntiRaid for 2 hours).</b>

2. <code>/raidtime [duration]</code>
   - Sets or checks the duration for which AntiRaid remains active when enabled.  
   - <b>Usage</b>:  
     - <code>/raidtime</code> - <b>Shows the current AntiRaid duration.</b>  
     - <code>/raidtime 4h</code> - <b>Sets AntiRaid duration to 4 hours</b> (use <code>m</code>, h, or <code>d</code> for minutes, hours, or days).  
   - Example: <code>/raidtime 1d</code> (Sets AntiRaid to stay active for 1 day).

3. <code>/raidactiontime [duration]</code>
   - Sets or checks the duration for which new members are banned during an active AntiRaid.  
   - <b>Usage</b>:  
     - <code>/raidactiontime</code> - Shows the current ban duration.  
     - <code>/raidactiontime 1h</code> - Sets the ban duration to 1 hour (use <code>m</code>, <code>h</code>, or <code>d</code>).  
   - Example: <code>/raidactiontime 30m</code> (Bans new members for 30 minutes during AntiRaid).

4. <code>/autoantiraid [number/off]</code>
   - Configures automatic AntiRaid triggering based on the number of new members joining within a minute.  
   - <b>Usage</b>:  
     - <code>/autoantiraid</code> - <b>Shows the current AutoAntiRaid setting.</b>
     - <code>/autoantiraid 10</code> - <b>Triggers AntiRaid automatically if 10 or more users join in one minute.</b>
     - <code>/autoantiraid off</code> - <b>Disables AutoAntiRaid.</b>  
   - When triggered, AntiRaid enables for the duration set by <code>/raidtime</code>.  
   - Example: <code>/autoantiraid 5</code> (Triggers AntiRaid if 5 users join in a minute).

<b>Important Notes:</b>
- <b>AntiRaid</b>: <i>When active, temporarily bans new members to prevent raids. Bans are lifted after the ban duration expires</i> (set by <code>/raidactiontime</code>).
- <b>AutoAntiRaid</b>: Monitors join rates and automatically enables AntiRaid if the threshold is exceeded.
- AntiRaid automatically disables after the set duration (<code>/raidtime</code>) expires, and a notification is sent to the group.
- Ensure time formats are valid (e.g., <code>30m</code>, <code>2h</code>, <code>1d</code>). Invalid formats will result in an error.

<b>Example Workflow:</b>
1. Set AntiRaid duration: <code>/raidtime 6h</code>
2. Set ban duration: <code>/raidactiontime 1h</code>
3. Enable AutoAntiRaid: <code>/autoantiraid 8</code> (triggers if 8 users join in a minute)
4. Or manually enable: <code>/antiraid 3h</code> (enables AntiRaid for 3 hours)
""",
            
            'english_sticker': """
            📜 <b>Sticker Help</b>
            
            <i>This commands helps group admins manage sticker packs by banning, unbanning, and setting rules for their use.</i>
            
<b>🔧 General Commands</b>
1. <code>/bansticker [pack_name/URL/reply] [reason]</code>
   - Bans a sticker pack permanently.
   - How to specify pack:
     - Reply to a sticker to ban its pack.
     - Provide the pack name (e.g., PackName).
     - Use a URL (e.g., <code>https://t.me/addstickers/PackName</code>).
   - <b>Example:</b> <i>/bansticker PackName Spamming</i>
   - <b>Note:</b> Reason is optional.

2. <code>/tbansticker [pack_name/URL/reply] [duration] [reason]</code>
   - Temporarily bans a sticker pack.
   - <b>Duration format:</b> 1m (minutes), 1h (hours), 1d (days).
   - <b>Example:</b>me <i>/tbansticker PackName 1h Spamming</i>
   - <b>Note:</b> Duration is required; reason is optional.

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
<b>- All actions are logged.</b>""",

            'english_connection': """
            📜 <b>Connection Help</b>

     <i>This module allows you to manage your Telegram groups directly from the bot's private messages (PM).</i>
     
<i>Use the following commands to connect, disconnect, and manage your groups. All commands must be used in the bot's private chat.</i>

<b>Available Commands:</b>
<code>/connect [group_id]</code> - <b>Connects the bot to a group where you are an admin.</b>
<blockquote>Example: /connect -100123456789</blockquote>

You can provide multiple group IDs separated by spaces.

<b>Note:</b>
<i>The group ID must start with - (e.g., -100123456789), and you must be an admin in the group./disconnect [group_id] Disconnects the bot from a specific group.</i>

<pre>Example: /disconnect -100123456789</pre> <b>- The group must already be connected.</b>

<code>/disconnectall</code> <b>- Disconnects the bot from all connected groups.</b>

<b>Example:</b>
<code>/disconnectall</code>
<code>/reconnect [group_id]</code>
<b>Reconnects the bot to a group to verify access.</b>

<pre>Example: /reconnect -100123456789</pre> - <b>Checks if the group is still accessible and if you are an admin.</b>
Disconnects if the group is inaccessible or you are no longer an admin.

<code>/connectionLists</code> -<b> all groups currently connected to your account.</b>

<pre>Example: /connection</pre> <b>- Displays group titles and IDs, or notes if a group is inaccessible.</b>

<b>Important Notes:</b>
<i>All commands work only in private chats with the bot.You must be an admin in the group to connect or reconnect.</i>

Group IDs can be found by adding this bot to the group and type /id.""",
            
            'english_forward': """
            📜 <b>Help Message for Ban Forward Module</b>

<i>The Ban Forward module allows group admins to control forwarded messages in their Telegram group by automatically restricting users who forward messages from other users, chats, or anonymous sources. Admins can enable permanent or temporary bans, choose the restriction type (ban, kick, or mute), and set durations for temporary restrictions. All commands must be used in the group chat by group admins.</i>

<b>Available Commands:</b>

1. <code>/ban_forward [on/off/True/False/yes/no]</code> 
   - Enables or disables permanent restrictions for users who forward messages.  
   - <b>Usage</b>:  
     - <code>/ban_forward</code> - <b>Shows the current status of forward ban (on/off).</b>
     - <code>/ban_forward on</code> - <b>Enables forward ban, applying the set action (see /ban_forward_action) to users who forward messages.</b>
     - <code>/ban_forward off</code> - <b>Disables forward ban.</b>
   - <pre>Example: /ban_forward on</pre> <b>(Enables forward ban with the configured action).</b>

2. <code>/tban_forward [on/off/True/False/yes/no]</code>
   - Enables or disables temporary restrictions for users who forward messages.  
   - <b>Usage</b>:
     - <code>/tban_forward</code> - <b>Shows the current status of temporary forward ban (on/off).</b>
     - <code>/tban_forward on</code> - <b>Enables temporary forward ban, applying a temporary version of the set action (e.g., tban or tmute) for a set duration (default: 24 hours).</b>  
     - <code>/tban_forward off</code> - <b>Disables temporary forward ban.</b>
   - <pre>Example: /tban_forward on</pre><b>(Enables temporary restrictions for forwarded messages).</b>

3. <code>/ban_forward_action [ban/kick/mute]</code>
   - Sets or checks the action taken against users who forward messages when /ban_forward or /tban_forward is enabled.  
   - <b>Usage</b>:  
     - <code>/ban_forward_action</code> - <b>Shows the current action (ban, kick, or mute).</b>
     - <code>/ban_forward_action ban</code>- <b>Sets the action to permanently ban the user.</b>
     - <code>/ban_forward_action kick</code> - <b>Sets the action to kick the user (ban and immediately unban).</b>
     - <code>/ban_forward_action mute</code> - <b>Sets the action to mute the user (prevent sending messages).</b>
   - For /tban_forward, ban becomes tban and mute becomes tmute, applying the action temporarily for the set duration.  
   - <pre>Example: /ban_forward_action mute</pre> <b>(Sets the action to mute users who forward messages).</b>

<i>Important Notes:</i>
<b>- Forward Ban:</b> When enabled (/ban_forward on), users who forward messages are permanently restricted based on the set action (ban , kick , or mute). The forwarded message is deleted, and a notification is sent to the group.

<b>Temporary Forward Ban:</b>
When enabled (/tban_forward on), restrictions are temporary, with a default duration of 24 hours. Use tban for temporary bans or tmute for temporary mutes.

<b>Example Workflow:</b>
1. <b>Set the action:</b> <i>/ban_forward_action mute (Users will be muted for forwarding).</i>
2. <b>Enable forward ban:</b> <i>/ban_forward on (Permanent mute for forwarding messages).</i> 
3. <b>Or enable temporary ban</b>: <i>/tban_forward on (Temporary mute for 24 hours).</i>
4. <blockquote>Check status: /ban_forward or /tban_forward.</blockquote>""",
            
            'english_private': """
Under construction 😀""",
            
            'english_custom': """
<b>Help Message for Custom Commands Module</b>

<i>The Custom Commands module lets group admins create and manage custom group commands that trigger text, media (photos/videos), or buttons. Commands can be for all users, admins only, or non-admins only.</i>

<b>Commands:</b>
<pre>/add_command [command] [response]::[button_text|button_url;...]</pre>
<b>Purpose:</b> Adds a command for all users.

<b>Usage:</b>
<pre>/add_command [command] [response]</pre> - <b>Text response.</b>
<pre>/add_command [command] [response]::[button_text|button_url;...]</pre> - <b>Text with buttons.</b>

<b>Supports:</b>
<i>[text](buttonurl://url) in response.</i>
<b>Details:</b>
<b>[command]</b>: <i>Name (e.g., hello, no /). Not kick, ban, etc.</i>
<b>[response]:</b> <i>Text with placeholders: {username}, {first_name}, {last_name}, {group}, {id}.</i>
<i>[button_text|button_url;...]: Buttons (e.g., Google|https://google.com).</i>

<b>Example:</b>
<pre>/add_command hello Hi {first_name}!::Google|https://google.com</pre>
<pre>/add_command info [Google](buttonurl://https://google.com)</pre>

<b>Admin restricted:</b>
<pre>/rcommand [command] [response]::[button_text|button_url;...]</pre>
<b>Purpose:</b> <i>Admin-only command.</i>
<b>Usage:</b> <i>Same as /add_command, but only admins can use.</i>

<b>Example:</b>
<pre>/rcommand rules Admins: Rules!::Rules|https://example.com</pre>

<b>Non-Admin only:</b>
<pre>/ucommand [command] [response]::[button_text|button_url;...]</pre>
<b>Purpose</b>: <i>Non-admin-only command.</i>
<b>Usage:</b> <i>Same as /add_command, but only non-admins can use.</i>

<b>Example:</b>
<pre>/ucommand faq FAQs: [FAQ](buttonurl://https://faq.com)</pre>
<pre>/add_media_command [command] [photo|video] [media_url]::[caption]::[button_text|button_url;...]</pre>

<b>Purpose:</b> <i>Adds a command to send a photo/video for all users.</i>

<b>Usage:</b>
<pre>/add_media_command [command] [photo|video] [media_url]</pre> - <i>Media only.</i>
<pre>/add_media_command [command] [photo|video] [media_url]::[caption]::[buttons]</pre>- <i>With caption/buttons.</i>

<b>Details:</b>
[media_url]: Direct photo/video URL.
[caption]: Optional, supports placeholders.

<b>Example:</b>
<pre>/add_media_command meme photo https://example.com/meme.jpg::Funny!::More|https://memes.com</pre>

<code>/remove [command]</code>
<b>Purpose:</b> <i>Deletes a command.</i>
<b>Usage</b>: <code>/remove [command]</code>
<b>Example</b>: <code>/remove hello</code>

<code>/commands</code>
<b>Purpose:</b> <i>Lists all commands, showing responses, media, type (all/admin/user), and buttons.</i>
<blockquote>Usage: /commands</blockquote>

<b>Type:</b> all/users/admin Only: /add_command, /rcommand, /ucommand, /add_media_command, /remove

<b>Command Rules: No reserved names (kick, ban, etc).</b>

<b>Buttons</b>: Use text|url;text2|url2 or [text](buttonurl://url).
<b>MarkdownV2:</b> Supports *bold*, _italic_, [link](url). Special chars auto-escaped.
<b>Media:</b> URLs must be direct and accessible.

<b>Errors:</b> Check command syntax, URLs, or bot permissions if issues arise.

<b>Example Workflow</b>
<blockquote>/add_command greet Hi {first_name}!::Join|https://t.me/group</blockquote>
<blockquote>/rcommand admininfo Admins: [Status](buttonurl://https://example.com)</blockquote>
<blockquote>/ucommand help [FAQ](buttonurl://https://faq.com)</blockquote>
<blockquote>/add_media_command promo video https://example.com/promo.mp4::Watch!</blockquote>

<code>/commands</code> - <b>List all.</b>
<code>/remove greet</code> - <b>Delete command.</b>

<b>Troubleshooting:</b>
<i>Command Fails: Verify command exists (/commands), user permissions, bot permissions.</i>

<b>Button Issues:</b> Ensure text|url or [text](buttonurl://url) format.
<b>Media Fails:</b> Check URL validity.""",

            'english_disable': """
<b>Help Message for Disabling Module</b>

<i>The Disabling module lets group admins control bot commands in groups by disabling specific commands, all commands. Admins can also configure whether disabled command messages are deleted and whether admins are restricted from using disabled commands.</i>

All commands require admin privileges and must be used in group chats.

<b>Available Commands:</b>
<pre>/disable [command]|all|on|off|yes|no</pre>

<b>Purpose:</b>
Disables a specific command, all commands.

<b>Usage:</b>
<code>/disable [command]</code> - <b>Disables a specific command (e.g., kick, mute).</b>
<code>/disable all</code> - <b>Disables all supported commands.</b>
<code>/disable on|yes</code> - <b>Disables supported commands.</b>
<code>/disable off|no</code> - <b>Enables supported commands..</b>

<b>Valid Commands:</b>
<i>kick, skick, dkick, kickme, promote, mute, ban, unban, lock, unlock, pin, unpin, flood, setflood, filter, stop, etc. (full list available via bot).</i>

<b>Example:</b>
<code>/disable kick</code> - <b>Disables /kick.</b>
<code>/disable all</code> - <b>Disables all commands.</b>
<code>/disable on</code> - <b>Disables supported commands..</b>

<b>Note:</b>
Disabled commands are inaccessible to non-admins unless /disableadmin is enabled.
/enable [command]|all

<b>Purpose:</b>
Enables a previously disabled command or all commands.

<b>Usage:</b>
<code>/enable [command]</code> - <b>Enables a specific command.</b>
<code>/enable all</code> - <b>Enables all commands.</b>

<b>Example:</b>
<code>/enable kick</code> - <b>Enables /kick.</b>
<code>/enable all</code> - <b>Enables all commands.</b>

<b>Note:</b>
Enabling commands sets it to active for non-admins.
/disabledel on|off|yes|no

<b>Purpose:</b>
Controls whether disabled command messages are deleted for non-admins.

<b>Usage:</b>
<code>/disabledel on|yes</code> - <b>Deletes disabled command messages.</b>
<code>/disabledel off|no</code> - <b>Keeps disabled command messages.</b>

<b>Example:</b>
<code>/disabledel on</code> - <b>Deletes messages like /kick if disabled.</b>

<b>Note:</b>
Deletion applies only to non-admins.
<code>/disableadmin on|off|yes|no</code>

<b>Purpose:</b>
Controls whether admins can use disabled commands.

<b>Usage:</b>
<code>/disableadmin on|yes</code> - <b>Restricts admins from using disabled commands.</b>
<code>/disableadmin off|no</code> - <b>Allows admins to bypass restrictions.</b>

<b>Example:</b>
<code>/disableadmin on</code>- <b>Admins can’t use disabled commands.</b>

<b>Note:</b>
Command Scope: Supports many commands like kick, ban, mute, flood, etc.

<b>Behavior:</b>
Disabled commands are blocked for non-admins unless /disableadmin is on.
<code>/disable all</code> <b>disables all supported commands.</b>
/disabledel deletes disabled command messages if enabled.

<b>Permissions:</b>
Bot needs can_delete_messages for <code>/disabledel</code> and <b>can_restrict_members</b> for kick-related commands.

<b>Restrictions:</b>
Commands are case-insensitive. Reserved commands can’t be disabled beyond the valid list.

<b>Logging:</b>
Actions are logged for transparency.

<b>Example WorkflowDisable a command:</b>
<code>/disable kick</code> - <b>Stops /kick for non-admins.</b>

<b>Enable deletion</b>: <code>/disabledel on</code> - <b>Deletes disabled command messages.</b>
<b>Restrict admins:</b> <code>/disableadmin on</code> - <b>Admins can’t use disabled commands.</b>
<b>Re-enable:</b> <code>/enable kick</code> - <b>Restores /kick.</b>
<b>Enable all:</b> <code>/enable all</code> - <b>Restores all commands.</b>
 
<b>TroubleshootingCommand Not Disabled:</b>
Ensure the command is valid and you’re an admin.
 
<b>Messages Not Deleting:</b>
Check if /disabledel is on and bot has can_delete_messages.
<b>Admins Blocked:</b>
Verify /disableadmin is on if admins can’t use commands.""",

            'english_app': """
<b>Auto Approval.</b>
            
<blockquote>/approval on</blockquote>
Automatically accept join requests.

<blockquote>/approval off</blockquote>
<b>Turn off auto join requests</b>
""",
            
            'english_chat': """

/chat on
Turn on chatting.

/chat off
Turn off chatting
""",
            
            'english_extra': """
            
            ### COMMING SOON ###
            ├── 🔸/dell on/users/admin
            │   │
            │   └ Auтoмᴀтιcᴀʟʟʏ ᴅᴇʟᴇтᴇ  мᴇssᴀԍᴇs
            │
            ├── 🔸/dell off
            │   │
            │   └ тuʀɴ oғғ ᴀuтoмᴀтιcᴀʟʟʏ ᴅᴇʟᴇтᴇ мᴇssᴀԍᴇs
            │
            ├── 🔸/link on
            │   │
            │   └ ᴀuтoмᴀтιcᴀʟʟʏ ᴅᴇʟᴇтᴇ ʟιɴκs. ιɴ мᴇssᴀԍᴇ, ᴘнoтo
            │   
            ├── 🔸/link off
            │   │
            │   └ тuʀɴ oғғ ᴀuтoмᴀтιcᴀʟʟʏ ᴅᴇʟᴇтᴇ ʟιɴκs
            │
            ├── 🔸/del [ reply ]
            │   │
            │   └ ᴅᴇʟᴇтᴇ ᴀ мᴇssᴀԍᴇ
            │
            ├── 🔸/abuse [ word ]
            │   │
            │   └ /ᴀʙusᴇ κuттᴀ - sᴇтт ᴀ ᴀʙusᴇ ʟᴀɴ тo ʏouʀ ԍʀouᴘ
            │
            ├── 🔸/abuse on
            │   │
            │   └ ᴅᴇʟᴇтᴇ ᴀʙusᴇ мᴇssᴀԍᴇ + мuтᴇ usᴇʀ
            │
            ├── 🔸/abuse off
            │   │
            │   └ тuʀɴ oғғ ᴅᴇʟᴇтᴇ ᴀʙusᴇ мᴇssᴀԍᴇ + мuтᴇ usᴇʀ
            │
            ├── 🔸/feedback
            │   │
            │   ├ /ғᴇᴇᴅʙᴀcκ oʀ sᴇʟᴇcт ᴘнoтo ᴀɴᴅ тʏᴘᴇ /ғᴇᴇᴅʙᴀcκ тo sᴇɴᴅ ғᴇᴇᴅʙᴀcκ тo тнᴇ ʙoт ᴅᴇvᴇʟoᴘᴇʀ
            │   │
            │   └ DEV :- @PB_X01
            ### COMMING SOON ###
            └──""",
            
            'english_format': """
          <b>Formatting</b>

        ├── 🔸<b>Markdown formatting</b>
        
<i>Markdown for styling text in messages, captions, and bot responses.</i>

<b>Supported Styles:</b>
Bold: Use *Bold text* → <b>Bold text</b>
Italic: Use _Italic text_ → <i>Italic text</i>

Monospace: Use `Monospace text` → <code>Monospace text</code>
Strikethrough: Use ~Strikethrough text~ → <s>Strikethrough text</s>
Link: Use [text](URL) → <a href="https://example.com">text</a>

<b>Notes:</b>
No spaces between markers and text  (e.g., * text* won’t work).
Combine styles by nesting (e.g., *bold _italic_* → <b><i>Bold & Italic</i></b>).

<b>Some clients may not support all styles</b>

if *bold*, _italic_, ~Strikethrough~, Not working then use
**bold** | __italic__ | ~~Strikethrough~~

Example: *Bold* _italic_ [text](https://telegram.org)  → <b><i>Bold & Italic</i></b> <a href="https://telegram.org">text</a>
 
        ├── 🔸<b>Button Formatting</b>
             
[Google](buttonurl://google.com) → Creates an inline button linking to Google""",
            
            'english_flood': """
<b>Help for Antiflood Module</b>

<i>The Antiflood module prevents message flooding in groups by limiting how many messages a user can send consecutively or within a time period.</i>
<i>Admins can set the message limit, time-based restrictions, actions (ban, mute, kick, temporary ban/mute), and whether to delete flood messages.</i>

<b>Available Commands</b>

<pre>/flood</pre>
<b>Purpose:</b> <i>Displays current antiflood settings.</i>

<b>Usage:</b> <code>/flood</code>
<b>Output:</b> <i>Shows consecutive message limit, timed flood settings, action, and message deletion status.</i>

<pre>/setflood [number/off]</pre>
<b>Purpose:</b> <i>Sets or disables the consecutive message limit.</i>

<b>Usage:</b>
<code>/setflood [number]</code> - <b>Sets limit (e.g., 5 messages).</b>
<code>/setflood off</code> - <b>Disables consecutive flood detection.</b>

<b>Example:</b>
<code>/setflood 5</code> - <b>Triggers after 5 consecutive messages.</b>
<code>/setflood off</code> - <b>Turns off consecutive flood checks.</b>

<b>Note:</b>
<i>Non-negative numbers only.</i>
<code>/setfloodtimer  /off</code>
<b>Purpose</b>: <i>Sets or disables timed flood detection.</i>

<b>Usage:</b>
<code>/setfloodtimer [count] [duration]</code> - <b>Sets limit (e.g., 10 messages in 30 seconds).</b>
<code>/setfloodtimer off</code> - <b>Disables timed flood detection.</b>

<b>Duration Format:</b> 30s (seconds), 5m (minutes), 3h (hours), 1d (days).

<b>Example:</b>
<code>/setfloodtimer 10 30s</code> - <b>Triggers if 10 messages are sent in 30 seconds.</b>
<code>/setfloodtimer off</code> - <b>Disables timed checks.</b>

<b>Note:</b>
<i>Count must be positive; duration must be valid.</i>
<pre>/floodmode [ban/mute/kick/tban/tmute] [duration]</pre>

<b>Purpose</b>: <i>Sets the action for flood violations.</i>

<b>Usage:</b>
<code>/floodmode [action]</code> - <b>Sets action (ban, mute, kick).</b>
<code>/floodmode [tban/tmute] [duration]</code> - <b>Sets temporary action with duration.</b>

<b>Duration Format:</b> 30s, 5m, 3h, 1d.

<b>Example:</b>
<code>/floodmode mute</code> - <b>Mutes flooders indefinitely.</b>
<code>/floodmode tban 1d</code> - <b>Bans flooders for 1 day.Note: Duration required for tban or tmute.</b>
<pre>/clearflood [yes/no/on/off]</pre>

<b>Purpose:</b>
Enables/disables deletion of flood messages.

<b>Usage:</b>
<code>/clearflood yes/on</code> - <b>Deletes flood messages.</b>
<code>/clearflood no/off</code> - <b>Keeps flood messages.</b>

<b>Example:</b>
<code>/clearflood yes</code> - <b>Deletes messages that trigger flood actions.</b>
<code>/clearflood no</code> - <b>Leaves flood messages in chat.</b>

<b>Important Notes</b>
<b>Flood Detection</b>: Consecutive: Limits how many messages a user can send in a row.
<b>Timed</b>: Limits messages within a time window (e.g., 10 in 30 seconds).

<b>Actions:</b>
<b>ban:</b> Permanent ban.
<b>mute:</b> Mute user.
<b>kick:</b> Kick user from group.
tban/tmute: Temporary ban/mute for specified duration.

<b>Message Deletion</b>: If /clearflood is enabled, flood messages are deleted.

<b>Example WorkflowView settings:</b>
<code>/flood</code> - <b>Check current antiflood configuration.</b>
<i>Set consecutive limit:</i> <code>/setflood 5</code> - <b>Trigger after 5 messages.</b>
<i>Set timed limit</i>: <code>/setfloodtimer 10 30s</code> - <b>Trigger if 10 messages in 30 seconds.</b>
<i>Set action:</i> <code>/floodmode tban 1h</code> - <b>Ban flooders for 1 hour.</b>
<i>Enable deletion:</i> <code>/clearflood yes</code> - <b>Delete flood messages.</b>
<i>Disable antiflood:</i> <code>/setflood off</code> and <code>/setfloodtimer off</code> - <b>Turn off checks.</b>
<b>TroubleshootingFlood Not Triggering:</b> Verify flood_limit or timed_flood settings with /flood.

Messages Not Deleted: Ensure /clearflood is on and bot has can_delete_messages.""",
            
            'english_note': """
<b>Help Message for Notes Module</b>

<i>The Notes module allows group admins to save and manage notes in groups, which can be text or media (photo, video, audio, document) with optional buttons. Users can retrieve notes using commands or hashtags, and admins can make notes private to deliver via PM.</i>

<b>Available Commands</b>
<code>/save</code>
<b>Purpose:</b> <i>Saves a text note or media note (if replying to media).</i>

<b>Usage:</b>
<code>/save [notename] [text]</code> - <b>Saves a text note.</b>
Reply to a photo, video, audio, or document with <code>/save [notename] [caption].</code>
<b>Supports buttons:</b> [button text](buttonurl://url).

<b>Example:</b>
<code>/save rules Be kind! [Join](buttonurl://t.me/example)</code> - <b>Saves text note with a button.</b>
Reply to a photo with <code>/save photo1 Nice pic</code> - Saves photo note with caption.

<b>Note:</b>
<i>Max 200 notes per group.</i>
<code>/get</code>
<b>Purpose:</b> <i>Retrieves a note by name.</i>

<blockquote>Usage: /get [notename]</blockquote>
<b>Behavior:</b>
<i>Sends note directly (text or media with buttons) unless private notes are enabled.
If private, sends a PM to view the note.</i>

<b>Example:</b>
<code>/get rules</code> - <b>Sends the "rules" note.</b>

<b>Note:</b> <i>Available to all users.</i>
<code>/notes</code> <b>or</b> <code>/saved</code>
<b>Purpose:</b> <i>Lists all note names in the group.</i>
<b>Usage:</b> <code>/notes</code> <b>or</b> <code>/saved</code>

<code>/clear</code>
<b>Purpose:</b> <i>Deletes a specific note.</i>
<b>Usage:</b> <blockquote>/clear [notename]</blockquote>

<b>Example:</b>
<code>/clear rules</code> - <b>Deletes the "rules" note.</b>
<code>/clearall</code>
<b>Purpose:</b> <i>Deletes all notes in the group.</i>

<blockquote>Usage: /clearall</blockquote>
<b>Example:</b>
<code>/clearall</code> - <b>Removes all notes.</b>
<code>/privatenotes on/off</code>
<b>Purpose:</b> <i>Enables/disables private note delivery via PM.</i>

<blockquote>Usage: /privatenotes [on/off]</blockquote>
<b>Example:</b>
<code>/privatenotes on</code> - <b>Notes sent as PM.</b>
<code>/privatenotes off</code> - <b>Notes sent directly in chat.</b>
<blockquote>#notename</blockquote>
<b>Purpose:</b> <i>Retrieves a note using a hashtag.</i>

<blockquote>Usage: #notename</blockquote>
<b>Example:</b>
<code>#rules</code> - <b>Sends the "rules" note (or PM if private).</b>
<b>Important Notes</b>
<code>Admin Only:</code>
<blockquote>/save, /clear, /clearall, and /privatenotes.</blockquote>

<b>Note Types:</b>
<b>Text:</b> <i>Simple text with optional buttons.</i>
<b>Media:</b> <i>Photo, video, audio, or document with optional caption and buttons.</i>
<b>Buttons:</b> <i>Use [text](buttonurl://url) in text/caption for inline buttons (one row).</i>

<b>Formatting:</b> <i>Notes use MarkdownV2; ensure valid syntax for buttons and text.</i>

<b>Example Workflow</b>
<b>Save a note:</b> <code>/save rules Be kind! [Join](buttonurl://t.me/example)</code> - <b> Saves text note with button.</b>
<b>Save media:</b> Reply to a photo with <code>/save photo1 Nice pic</code> - Saves photo note.
<b>Enable private notes:</b> <code>/privatenotes on</code> - <b>Notes sent via PM.</b>
<b>View notes:</b> <code>/notes</code> - <b>Lists all notes.</b>
<b>Retrieve note:</b> <code>"/get rules"</code> or <code>"#rules"</code> - <b>Sends note or PM.</b>
<b>Delete note:</b> <code>/clear rules</code> - <b>Removes "rules" note.</b>
<b>Clear all:</b> <code>/clearall</code> - <b>Deletes all notes.</b>

<blockquote>- 200 Notes per group</blockquote>

<b>Buttons Not Showing:</b>
<b>Check</b>
<blockquote>[text](buttonurl://url) syntax.</blockquote>
""",
            
            'english_blocklist': """
<b>Blocklist Module Help</b>

<i>The Blocklist module blocks specific content in groups based on trigger patterns. Admins can add triggers with reasons, set actions (e.g., ban, mute, kick), and choose to delete offending messages.</i>

<b>Available Commands:</b>
<code>/addblocklist [text] [reason]</code>
<b>Purpose:</b> Adds a trigger pattern with a reason to the blocklist.

<b>Usage:</b> <code>//blocklist</code>  Use quotes for multi-word triggers: <i>"bad phrase".</i>
<b>Supports wildcards:</b> * (non-whitespace), ** (any characters), ? (single character).

<b>Example:</b>
<code>/addblocklist spam* Spamming detected</code> - <b>Blocks words starting with "spam".</b>
<code>/addblocklist "bad word" Inappropriate language</code> - <b>Blocks exact phrase.</b>

<code>/rmblocklist</code>
<b>Purpose:</b> Removes a specific trigger from the blocklist.
<b>Usage:</b> <code>/rmblocklist</code>
<b>Example:</b>
<code>/rmblocklist spam*</code> - <b>Removes "spam*" trigger.</b>

<code>/unblocklistall</code>
<b>Purpose:</b> Removes all triggers from the blocklist.
<b>Usage:</b> <code>/unblocklistall</code>
<b>Example:</b>
<code>/unblocklistall</code> - <b>Clears all triggers.</b>
<b>Note:</b> Chat creator only.

<code>/blocklist</code>
<b>Purpose:</b> Lists all triggers, action mode, deletion setting, and reason.
<b>Usage:</b> <code>/blocklist</code>

<code>/blocklistmode</code>
<b>Purpose</b>: Sets the action for blocked content.
<b>Usage:</b> /blocklistmode
<b>Modes:</b> nothing, ban, mute, kick, warn, tban, tmute.
<b>Example:</b>
<code>/blocklistmode ban</code> - <b>Bans users for blocked content.</b>
<code>/blocklistmode nothing</code> - <b>No action, may still delete messages.</b>

<code>/blocklistdelete [yes/no/on/off]</code>
<b>Purpose:</b> Enables/disables deletion of blocked messages.
<b>Usage:</b> <code>/blocklistdelete [yes/no/on/off]</code>
<b>Example:</b>
<code>/blocklistdelete yes</code> - <b>Deletes blocked messages.</b>
<code>/blocklistdelete no</code> - <b>Keeps blocked messages.</b>

<code>/setblocklistreason</code>
<b>Purpose:</b> Sets the default reason for blocklist actions.
<b>Usage:</b> <code>/setblocklistreason</code>
<b>Example:</b>
<code>/setblocklistreason Policy violation</code> - <b>Sets default reason.</b>

<code>/resetblocklistreason</code>
<b>Purpose:</b> Resets the default reason to <i>"Blocked content detected"</i>.
<b>Usage:</b> <code>/resetblocklistreason</code>
<b>Example:</b>
<code>/resetblocklistreason</code> - <b>Resets default reason.</b>

<b>Example Workflow</b>
<b>Add trigger:</b> <code>/addblocklist spam* Spamming detected</code> - <b>Blocks "spam" variants.</b>
<b>Set mode:</b> <code>/blocklistmode mute</code> - <b>Mutes users for blocked content.</b>
<b>Enable deletion:</b> <code>/blocklistdelete yes</code> - <b>Deletes blocked messages.</b>
<b>Set reason:</b> <code>/setblocklistreason Policy violation</code> - <b>Sets default reason.</b>
<b>View triggers:</b> <code>/blocklist</code> - <b>Lists all settings.</b>
<b>Remove trigger:</b> <code>/rmblocklist spam*</code> - <b>Removes trigger.</b>
<b>Clear all:</b> <code>/unblocklistall</code> - <b>Removes all triggers (creator only).</b>
""",
            
            'english_filter': """
<b>Filters Module Help</b>

<i>The Filters module allows admins to set triggers that automatically respond with predefined messages or media when specific words or phrases are detected in chats.</i>

<b>Available Commands</b>
<code>/filter [trigger(s)] [response]</code>
<b>Purpose:</b> Adds one or more triggers with a response.
 
<b>Usage:</b> <code>/filter [trigger] [response]</code> <b>Triggers can be single words or quoted phrases.</b>
<i>Multiple triggers can be separated by spaces or quotes.</i>
 
<blockquote>Responses support HTML.</blockquote>
 
<b>Example:</b>
<code>/filter hello Hi there!</code> - <b>Responds to "hello" with "Hi there!".</b>
<code>/filter "good morning" Good day! [Visit](buttonurl://https://google.com)</code> - <b>Responds to "good morning" with a button.</b>
 
<blockquote>/filters</blockquote>
<b>Purpose:</b> Lists all active filters in the group.

<blockquote>/stop</blockquote>
<b>Purpose:</b> Removes a specific filter trigger.
<b>Usage:</b> <code>/stop</code>
<b>Example:</b>
<code>/stop hello</code> - <b>Removes the "hello" filter.</b>

<blockquote>/stopall</blockquote>
<b>Purpose:</b> Removes all filters in the group.
<b>Usage:</b> <code>/stopall</code>
<b>Example:</b>
<code>/stopall</code> - <b>Clears all filters.</b>


<b>Example Workflow</b>
<b>Add filter:</b> <code>/filter hello 👋</code> - <b>Sets response for "hello".</b>
<b>List filters:</b> <code>/filters</code> - <b>Shows all triggers.</b>
<b>Remove filter:</b> <code>/stop hello</code> - <b>Removes "hello" filter.</b>
<b>Clear all:</b> <code>/stopall</code> - <b>Removes all filters.</b>
""",

            'english_lock': """
<b>Locks Module Help</b>

<i>The Locks module enables admins to restrict specific types of content or actions in chats.</i>

<b>Available Commands</b>
<code>/lock</code>
<b>Purpose:</b> <i>Locks a specific content type or action, preventing non-admins from sending it.</i>

<b>Usage:</b> <code>/lock</code>
<b>Valid types:</b> all, album, invitelink, anonchannel, audio, bot, botlink, button, commands, comment, contact, document, email, emoji, emojicustom, emojigame, externalreply, game, gif, inline, location, phone, photo, poll, spoiler, text, url, video, videonote, voice.
all: Disables all messaging.

<b>Example:</b>
<code>/lock photo</code> - <b>Prevents non-admins from sending photos.</b>
<code>/lock all</code> - <b>Locks the entire chat for non-admins.</b>

<blockquote>/unlock</blockquote>
<b>Purpose:</b> <i>Unlocks a specific content type or action, allowing non-admins to send it.</i>
<b>Usage:</b> <code>/unlock</code> Same valid types as <code>/lock.</code>
all: Restores default chat permissions.

<b>Example:</b>
<code>/unlock photo</code> - <b>Allows non-admins to send photos.</b>
<code>/unlock all</code> - <b>Unlocks the entire chat.</b>

<b>Lock Types:</b>
<b>all:</b> <i>Blocks all messages (sets no permissions).</i>
<b>album:</b> <i>Blocks media groups.</i>
<b>invitelink:</b> <i>Blocks Telegram invite links.</i>
<b>anonchannel:</b> <i>Blocks anonymous channel messages.</i>
<b>audio:</b> <i>Blocks audio files.</i>
<b>bot:</b> <i>Blocks messages from bots.</i>
<b>botlink:</b> <i>Blocks bot mentions.</i>
<b>button:</b> <i>Blocks messages with inline keyboards.</i>
<b>commands:</b> <i>Blocks bot commands (/command).</i>
<b>comment:</b> <i>Blocks topic messages.</i>
<b>contact:</b> <i>Blocks contact sharing.</i>
<b>document:</b> <i>Blocks documents/files.</i>
<b>email:</b> <i>Blocks email addresses.</i>
<b>emoji:</b> <i>Blocks Unicode emojis (U+1F300–U+1F9FF).</i>
<b>emojicustom:</b> <i>Blocks animated stickers.</i>
<b>emojigame:</b> <i>Blocks game messages.</i>
<b>externalreply:</b> <i>Blocks replies to forwarded messages.</i>
<b>game:</b> <i>Blocks Telegram games</i>.
<b>gif:</b> <i>Blocks animations/GIFs.</i>
<b>inline:</b> <i>Blocks inline bot messages.</i>
<b>location:</b> <i>Blocks location sharing.</i>
<b>phone:</b> <i>Blocks phone numbers.</i>
<b>photo:</b> <i>Blocks photos.</i>
<b>poll:</b> <i>Blocks polls.</i>
<b>spoiler:</b> <i>Blocks messages with spoilers.</i>
<b>text:</b> <i>Blocks plain text.</i>
<b>url:</b> <i>Blocks URLs.</i>
<b>video:</b> <i>Blocks videos.</i>
<b>videonote:</b> <i>Blocks video notes.</i>

<b>Example Workflow</b>
<b>Lock content:</b> <code>/lock url</code> - <b>Prevents non-admins from sending URLs.</b>
<b>Lock chat:</b> <code>/lock all</code> - <b>Disables all messaging for non-admins.</b>
<b>Unlock content:</b> <code>/unlock url</code> - <b>Allows URLs again.</b>
<b>Unlock chat:</b> <code>/unlock all</code> - <b>Restores messaging permissions.</b>
""",
            
            'english_basic': """
            
            ├── 🔸𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎
            │   │
            │   ├ /start ➠ ѕтαят тнє вσт
            │   ├ /help ➠ ѕнσω тнιѕ мєѕѕαgє
            │   ├ /id, /info, /me, ➠ ʀᴇᴘʟʏ usᴇʀ oʀ ᴅιʀᴇcт sᴇɴᴅ - ғᴇт usᴇʀ ιᴅs 
            │   └ /ping - cнᴇcκ ʙoт sʏsтᴇм
            │
            ├── 🔸
            │   │
            │   ├ ### COMMING SOON ###
            │   │
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",
            
            'english_botadmin': """
<b>Admins Module Help</b>

<i>This module help group--admins to Promote/Demote users</i>

<b>Available Commands</b>
<code>/promote [user_id|reply] [title] [duration]</code>
<b>Purpose:</b> <i>Promotes a user to admin with specified permissions and optional title/duration.</i>
<b>Usage:</b> <code>/promote [user_id|reply] [title] [duration]</code>
<i>User can be specified by ID, username, or replying to their message.</i>

<b>Title:</b> Optional custom admin title (max 16 characters).
<b>Duration:</b> Optional temporary promotion (e.g., 30m, 2h, 1d).

<b>Example:</b>
<code>/promote 123456 Moderator 1d</code> - <b>Promotes user with title for 1 day.</b>
<code>/promote (reply)</code> - <b>Promotes replied user.</b>

<code>/demote [user_id|reply]</code>
<b>Purpose:</b> <i>Demotes an admin, removing all admin permissions.</i>
<b>Usage:</b> <code>/demote [user_id|reply]</code>
<i>User can be specified by ID, username, or replying to their message.</i>

<b>Example:</b>
<code>/demote 1234561</code> - <b>Demotes replied user.</b>

<blockquote>/adminlist</blockquote>
<b>Purpose:</b> <i>Lists all admins in the group.
Usage: /adminlist</i>

<b>Refreshes admin cache</b>
<blockquote>/admincache</blockquote>
<b>Purpose:</b> <i>Manually refreshes the admin cache for the group.</i>
<b>Usage:</b> <code>/admincache</code>
<b>Example:</b>
<code>/admincache</code> - <b>Updates cached admin list.</b>

<blockquote>/adminerror [yes/no/on/off]</blockquote>
<b>Purpose:</b> <i>Enables/disables admin error messages for failed actions.</i>
<b>Usage:</b> <code>/adminerror [yes/no/on/off]</code>.

<b>Example Workflow</b>
<b>Promote user:</b> <code>/promote 123412 Moderator</code> - <b>Promotes with title.</b>
<b>Demote user:</b> <code>/demote 123412</code> - <b>Removes admin status.</b>
<b>List admins:</b> <code>/adminlist</code> - <b>Shows all admins.</b>
<b>Refresh cache:</b> <code>/admincache</code> - <b>Updates admin list.</b>
""",
            
            'english_cleancommand': """
<b>Cleancommand Module Help</b>

<i>The Cleancommand module allows admins to configure automatic deletion or retention of command messages in chats based on the sender's status (admin, user, or all).</i>

<b>Available Commands</b>
<blockquote>/cleancommandtypes</blockquote>

<b>Purpose:</b> <i>Lists valid types for /cleancommand and /keepcommand.</i>
<b>Usage:</b> <code>/cleancommandtypes</code>

<blockquote>/cleancommand [admin|user|all]</blockquote>
<b>Purpose:</b> Sets the type of command messages to delete automatically.
<b>Usage:</b> <code>/cleancommand [admin|user|all]</code>

<b>- admin:</b> <i>Deletes commands sent by admins.</i>
<b>- user:</b> <i>Deletes commands sent by non-admins.</i>
<b>- all:</b> <i>Deletes all command messages.</i>

<b>Example:</b>
<code>/cleancommand user</code> - <b>Deletes non-admin command messages.</b>
<code>/cleancommand all</code> - <b>Deletes all command messages.</b>

<blockquote>/keepcommand [admin|user|all]</blockquote>
<b>Purpose:</b> <i>Sets the type of command messages to keep (overrides /cleancommand).</i>
<b>Usage:</b> <code>/keepcommand [admin|user|all]</code>

<b>Example:</b>
<code>/keepcommand admin</code> - <b>Keeps admin command messages.</b>
<code>/keepcommand all</code> - <b>Keeps all command messages.</b>

<b>Important Notes</b>
<b>Enforcement:</b>
Command messages (starting with /) are checked for deletion.
<code>/cleancommand</code> <b>sets which messages to delete; /keepcommand sets exceptions.</b>
<b>Example:</b> If <code>/cleancommand all</code> and <code>/keepcommand admin</code>, all commands are deleted except those from admins.

<b>Example Workflow</b>
<b>List types:</b> <code>/cleancommandtypes</code> - <b>Shows valid options.</b>
<b>Set deletion:</b> <code>/cleancommand user</code> - <b>Deletes non-admin commands.</b>
<b>Set retention:</b> <code>/keepcommand admin</code> - <b>Keeps admin commands.</b>
<b>Adjust settings:</b> <code>/cleancommand all</code> - <b>Deletes all commands, but admin commands remain due to <code>/keepcommand</code>.</b>
""",

            'english_developersuppert': """
            
            ├── 🔸𝗖𝗢𝗡𝗧𝗔𝗖𝗧
            │  │
            │  ├── 🔸@PB_X01
            │  ├── 🔸@assistant_off_OG
            └──""",

            'english_voicechat': """
            
            ├── 🔸𝗔𝘂𝘁𝗼𝗺𝗮𝘁𝗲𝗱 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀 :
            │   │
            │   ├ → vc sтᴀʀт/ᴇɴᴅ ᴅᴇтᴇcтιoɴ
            │   ├ → cusтoм נoιɴ ʙuттoɴs
            │   └ → sтʏʟᴇᴅ ᴀɴɴouɴcᴇмᴇɴтs
            │   
            ├── 🔸˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",

            'english_groupsupport': """
            
            ├── 🔸 𝗦𝗨𝗣𝗣𝗢𝗥𝗧 𝗖𝗛𝗔𝗧
            │   │
            │   ├ @TEAM_X_OG
            │   ├ @CLICKMEKARNA
            │   └ @mdfreeddos
            │   
            ├── 🔸𝗔𝗕𝗢𝗨𝗧 𝗗𝗘𝗩𝗘𝗟𝗢𝗣𝗘𝗥
            │
            │   ├ @MR_ARMan_OWNER1
            │
            │
            ├── 🔸𝗠𝗢𝗥𝗘 𝗕�_O𝗧'𝗦
            │   │
            │   ├ ### COMMING SOON ###
            │   │   
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",
            
            'english_reports': """
            R𝗘𝗣𝗢𝗥𝗧

            ├── 🔸 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎 :
            │   │
            │   ├ /report [reply] - Aʟᴇʀт Aᴅмιɴs
            │   └ @admin - Aʟтᴇʀɴᴀтιvᴇ Tʀιԍԍᴇʀ
            │   
            ├── 🔸𝗙𝘂𝗻𝗰𝘁𝗶𝗼𝗻𝗮𝗹𝗶𝘁𝘆 :
            │   │
            │   ├ → Gʀouᴘ Sᴇттιɴԍ: /reports [Oɴ/Oғғ]
            │   ├ → Cʀᴇᴀтᴇs Mᴇɴтιoɴ Lιɴκs Foʀ Aᴅмιɴs
            │   ├ → Pʀᴇvᴇɴтs Aᴅмιɴ Rᴇᴘoʀтιɴԍ Aᴅмιɴs
            └──""",

            'english_ban': """
<b>Bans Module Help</b>

<i>The Bans module enables admins to manage user bans in chats, including permanent, temporary, silent, and random-duration bans, as well as unbanning and self-banning.</i>

<b>Available Commands</b>
<code>/ban [user_id | reply] [reason]</code>
<b>Purpose:</b> Permanently bans a user from the group.

<b>Example:</b>
<code>/ban 27736544 Spam</code> - <b>Bans user with reason.</b>
<code>/ban (reply)</code> - <b>Bans replied user.</b>

<code>/sban [user_id | reply] [reason]</code>
<b>Purpose:</b> <i>Silently bans a user and deletes the command and replied messages.</i>

<b>Example:</b>
<code>/sban 1727365</code> - <b>Silently bans user.</b>
<code>/sban (reply) Spam</code> - <b>Bans and deletes messages.</b>

<code>/tban [user_id | reply] [reason]</code>
<b>Purpose:</b> <i>Temporarily bans a user for a specified duration.</i>
<b>Usage:</b> <code>/tban [user_id | reply] [reason]</code>
<b>Duration format:</b> [number][s|m|h|d|w] (seconds, minutes, hours, days, weeks).
<b>Max duration:</b> 366 days.

<b>Example:</b>
<code>/tban 272636 Spam 1h</code> - <b>Bans for 1 hour.</b>
<code>/tban (reply) 30m</code> - <b>Bans for 30 minutes.</b>

<blockquote>/dban [reply] [reason]</blockquote>
<b>Purpose:</b> <i>Bans a user and deletes their replied message.</i>
<b>Usage:</b> <code>/dban [reply] [reason]</code>

<b>Example:</b>
<code>/dban (reply) Spam</code> - <b>Bans and deletes message.</b>

<blockquote>/rban [user_id | reply] [reason]</blockquote>
<b>Purpose:</b> <i>Bans a user for a random duration (1 minute to 1 week).</i>
<b>Usage:</b> <code>/rban [user_id | reply] [reason]</code>

<b>Example:</b>
<code>/rban 34543223</code> - <b>Bans for random duration.</b>
<code>/rban (reply) Spam</code> - <b>Bans with reason.</b>

<blockquote>/unban [user_id | reply] [reason]</blockquote>
<b>Purpose:</b> <i>Unbans a user from the group.</i>
<b>Usage:</b> <code>/unban [user_id | reply] [reason]</code>
Example:
<code>/unban 2726383 Mistake</code> - <b>Unbans with reason.</b>
<code>/unban 123456</code> - <b>Unbans user.</b>

<blockquote>/banme [reason]</blockquote>
<b>Purpose:</b> Allows a user to ban themselves from the group.
<b>Usage:</b> <code>/banme [reason]</code>
<b>Example:</b>
<code>/banme I need a break</code> - <b>Self-bans with reason.</b>

<b>Example Workflow</b>
<b>Ban user:</b> <code>/ban 12345678 Spam</code> - <b>Permanently bans with reason.</b>
<b>Silent ban:</b> <code>/sban</code> (reply) - <b>Bans and deletes messages discreetly.</b>
<b>Temp ban:</b> <code>/tban 1734637 Flood 2h</code> - <b>Bans for 2 hours.</b>
<b>Delete and ban:</b> <code>/dban</code> (reply) - <b>Bans and deletes replied message.</b>
<b>Random ban:</b> <code>/rban 1733636</code> - <b>Bans for random duration.</b>
<b>Unban user:</b> <code>/unban 7272636 Mistake</code> - <b>Unbans with reason.</b>
<b>Self-ban:</b> <code>/banme Taking a break</code> - <b>User bans themselves.</b>
""",

            'english_warn': """
<b>Warns Module Help</b>

<i>The Warns module enables admins to manage user warnings in chats, with configurable limits, modes, and durations.</i>

<b>Available Commands</b>
<code>/warn [user_id | @username | reply] [reason]</code>
<b>Purpose:</b> Issues a warning to a user with an optional reason.
<b>Usage:</b> <code>/warn [user_id | @username | reply] [reason]</code>

<b>Example:</b>
<code>/warn @username Spam</code> - <b>Warns user with reason.</b>
<code>/warn (reply) Flooding</code> - <b>Warns replied user.</b>

<code>/swarn [user_id | @username | reply] [reason]</code>
<b>Purpose:</b> Silently issues a warning and deletes the command message.
<b>Usage:</b> <code>/swarn [user_id | @username | reply] [reason]</code>

<b>Example:</b>
<code>/swarn @username Spam</code> - <b>Silently warns user.</b>
<code>/swarn</code> (reply) - <b>Silently warns replied user.</b>

<code>/dwarn [user_id | @username | reply] [reason]</code>
<b>Purpose:</b> Issues a warning and deletes the replied message (if applicable).
<b>Usage:</b> <code>/dwarn [user_id | @username | reply] [reason]</code>

<b>Example:</b>
<code>/dwarn <b>(reply)</b> Spam</code> - <b>Warns and deletes replied message.</b>
<code>/dwarn @username Flood</code> - <b>Warns user.</b>

<code>/rmwarn [user_id | @username | reply]</code>
<b>Purpose:</b> <i>Removes one warning from a user.</i>
<b>Usage:</b> <code>/rmwarn [user_id | @username | reply]</code>

<b>Example:</b>
<code>/rmwarn @username</code> - <b>Removes one warning.</b>
<code>/rmwarn <b>(reply)</b></code> - <b>Removes one warning from replied user.</b>

<code>/resetwarn [user_id | @username | reply]</code>
<b>Purpose:</b> <i>Resets all warnings for a user.</i>
<b>Usage:</b> <code>/resetwarn [user_id | @username | reply]</code>

<b>Example:</b>
<code>/resetwarn @username</code> - <b>Clears all warnings.</b>
<code>/resetwarn <b>(reply)</b></code> - <b>Clears warnings for replied user.</b>

<blockquote>/resetallwarnings</blockquote>
<b>Purpose:</b> <i>Resets all warnings for all users in the chat.</i>
<b>Usage:</b> <code>/resetallwarnings</code>

<b>Example:</b>
<code>/resetallwarnings</code> - <b>Clears all warnings in the group.</b>

<blockquote>/warnings</blockquote>
<b>Purpose:</b> <i>Displays current warning settings (limit, mode, time).</i>

<blockquote>/warningmode [ban|mute|kick]</blockquote>
<b>Purpose:</b> <i>Sets the action when the warn limit is reached.</i>
<b>Usage:</b> <code>/warningmode [ban|mute|kick]</code>
<b>ban:</b> Permanently bans the user.
<b>mute:</b> Mutes for the warn time duration.
<b>kick:</b> Kicks (bans then unbans).

<b>Example:</b>
<code>/warningmode ban</code> - <b>Sets ban as the action.</b>

<blockquote>/warnlimit</blockquote>
<b>Purpose:</b> Sets the maximum number of warnings before action.
<b>Usage:</b> <code>/warnlimit</code>

<b>Example:</b>
<code>/warnlimit 5</code> - <b>Sets warn limit to 5.</b>

<code>/warntime [time]</code>
<b>Purpose:</b> Sets the duration for warnings and mute actions.
<b>Usage:</b> <code>/warntime [time]</code>
<b>Time format:</b> [number][s|m|h|d|w|mo|y] (seconds, minutes, hours, days, weeks, months, years).

<b>Example:</b>
<code>/warntime 2h</code> - <b>Sets warn/mute duration to 2 hours.</b>
<code>/warntime</code> - <b>Shows current warn time.</b>

<b>Example Workflow</b>
<b>Configure settings:</b> <code>/warnlimit 4</code>, <code>/warningmode ban</code>, <code>/warntime 1d</code> - <b>Sets limit to 4, action to ban, duration to 1 day.</b>

<b>Warn user:</b> <code>/warn @username Spam</code> - <b>Issues warning (1/4).</b>
<b>Silent warn:</b> <code>/swarn (reply) Flood</code> - <b>Warns silently, deletes command.</b>
<b>Delete and warn:</b> <code>/dwarn (reply)</code> - <b>Warns and deletes message.</b>
<b>Remove warning:</b> <code>/rmwarn @username</code> - <b>Reduces count to 0/4.</b>
<b>Reset warnings:</b> <code>/resetwarn @username</code> - <b>Clears all warnings.</b>
<b>Reset all:</b> <code>/resetallwarnings</code> - <b>Clears all warnings in chat.</b>
<b>Check settings:</b> <code>/warnings</code> - <b>Shows current configuration.</b>
""",
            
            'english_button': """
            
            ├── 🔸𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎 :
            │   │
            │   ├ INLINEBUTTON - [button name](buttonurl://https://link)
            │   ├ hidden link button - [click here](https://link)
            │   ├ Support also multiple buttons eg " [button name](buttonurl://https://link)  [button name](buttonurl://https://link)"
            │   └ same for hidden link button
            │   │
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",

            'english_document': """
            
            ├── 🔸 DOCUMENTATION :
            │   │
            │   ├ WEB -
            │   ├ ASK ANYTHING - 
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",

            'english_mute': """
            𝗠𝗨𝗧𝗘 𝗛𝗘𝗟𝗣

            ├── 🔸 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎 :
            │   │
            │   ├ /mute [reply/user] [reason] - мuтᴇ usᴇʀ wιтн oᴘтιoɴᴀʟ ʀᴇᴀsoɴ
            │   ├ /unmute [user] - uɴмuтᴇ usᴇʀ
            │   ├ /smute [reply/user] [reason] - sιʟᴇɴт мuтᴇ (ᴅᴇʟᴇтᴇs coммᴀɴᴅ)
            │   ├ /tmute [reply/user] [time] [reason] - тᴇмᴘ мuтᴇ (1н, 30м, 7ᴅ)
            │   ├ /rmute [reply/user] - mute user with random duration
            │   └ /unmute [reply/user] - ʀᴇмovᴇ ʀᴇsтʀιcтιoɴs
            │
            ├── 🔸 𝗘𝘅𝗮𝗺𝗽𝗹𝗲𝘀 :
            │   │
            │   ├ → ʀᴇᴘʟʏ тo тᴀʀԍᴇт мᴇssᴀԍᴇ oʀ мᴇɴтιoɴ usᴇʀ
            │   ├ → тιмᴇ ғoʀмᴀт: ɴuмʙᴇʀ + uɴιт (s/м/н/ᴅ)
            │   ├ /tmute 1234/reply 1s/1h/1d/1w/1m/1y
            │   └ /mute 1234/reply
            │
            ├── 🔸𝗣𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻𝘀 :
            │   │
            │   ├ ʙoт ʀᴇQuιʀᴇs: "ʀᴇsтʀιcт мᴇмʙᴇʀs" ʀιԍнт
            │   ├ usᴇʀ ʀᴇQuιʀᴇs: ᴀᴅмιɴ ᴘʀιvιʟᴇԍᴇs
            │   │
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",

            'english_kick': """
            👢 �_K𝗜𝗖𝗞 𝗛𝗘𝗟𝗣

            ├── 🔸𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎 :
            │   │
            │   ├ same as /skick, /tkick, /dkick
            │   ├ /kick [user] - ʀᴇмovᴇ usᴇʀ
            │   └ /kickme - ʟᴇᴀvᴇ ԍʀouᴘ
            │
            ├── 🔸𝗘𝘅𝗮𝗺𝗽𝗹𝗲𝘀 :
            │   │
            │   ├ /kick @troublemaker
            │   └ /skick 123456789
            └──""",
        }

        if call.data in help_sections:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("✘ ˹ ʙᴀ𝗰𝗸 ˼", callback_data="english_back"))
            markup.add(
                types.InlineKeyboardButton("formatting", callback_data="english_format"),
                types.InlineKeyboardButton("button", callback_data="english_button"),
                types.InlineKeyboardButton("document", callback_data="english_document")
            )
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=format_message(help_sections[call.data]),
                parse_mode='HTML',
                reply_markup=markup
            )
        else:
            bot.answer_callback_query(call.id, "⏳ Section under development!", show_alert=True)

    except Exception as e:
        logger.error(f"Callback error: {str(e)}\n{traceback.format_exc()}")
        try:
            bot.answer_callback_query(call.id, f"Error in Callback.\nPlease try again.", show_alert=True)
        except Exception as e:
            logger.error(f"Failed to answer callback: {str(e)}")

