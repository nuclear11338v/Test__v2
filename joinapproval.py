import telebot
import json
import logging
from datetime import datetime, timedelta
from config import bot, logger
from kick import disabled
from user_logs.user_logs import log_action
import time
import threading
from ban_sticker_pack.ban_sticker_pack import is_admin, is_group

AUTO_APPROVAL_FILE = "auto_approval_status.json"
PENDING_APPROVALS_FILE = "pending_approvals.json"

# Load auto-approval status
try:
    with open(AUTO_APPROVAL_FILE, "r") as f:
        auto_approval_status = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    auto_approval_status = {}

# Load pending approvals
try:
    with open(PENDING_APPROVALS_FILE, "r") as f:
        pending_approvals = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    pending_approvals = {}

def save_auto_approval():
    with open(AUTO_APPROVAL_FILE, "w") as f:
        json.dump(auto_approval_status, f)

def save_pending_approvals():
    with open(PENDING_APPROVALS_FILE, "w") as f:
        json.dump(pending_approvals, f)

def parse_duration(duration_str):
    """Convert duration string (e.g., '3s', '1m', '2h') to seconds."""
    try:
        unit = duration_str[-1].lower()
        value = float(duration_str[:-1])
        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
        else:
            return None
    except (ValueError, IndexError):
        return None

def process_delayed_approval(chat_id, user_id, delay_seconds):
    """Handle delayed approval after specified duration."""
    time.sleep(delay_seconds)
    try:
        bot.approve_chat_join_request(chat_id, user_id)
        logging.info(f"Delayed approval for user {user_id} in {chat_id} after {delay_seconds} seconds")
        
        # Remove from pending approvals
        group_id = str(chat_id)
        if group_id in pending_approvals and str(user_id) in pending_approvals[group_id]:
            del pending_approvals[group_id][str(user_id)]
            if not pending_approvals[group_id]:
                del pending_approvals[group_id]
            save_pending_approvals()
    except telebot.apihelper.ApiTelegramException as e:
        if "too_many_requests" in str(e).lower():
            error_msg = f"Rate limit error: Unable to approve user {user_id} due to Telegram API limits."
            bot.send_message(chat_id, error_msg, parse_mode='Markdown')
            logging.error(error_msg)
        else:
            logging.error(f"Delayed approval error: {e}")

@bot.message_handler(regexp=r'^[\/!](approve)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_auto_approval(message):
    cmd = message.text.split()
    if len(cmd) < 2:
        bot.reply_to(message, "Usage: /approve on/off/yes/no or /approve <duration> (e.g., 3s, 1m, 2h)", disable_web_page_preview=True)
        return

    option = cmd[1].lower()
    group_id = str(message.chat.id)

    if option in ['on', 'yes']:
        auto_approval_status[group_id] = True
        reply = "*Auto-Approval Enabled!*\n\nI will now automatically approve join requests!"
        log_details = {"operation": "enable"}
    elif option in ['off', 'no']:
        auto_approval_status[group_id] = False
        reply = "*Auto-Approval Disabled!*\n\nJoin requests will require manual approval."
        log_details = {"operation": "disable"}
    else:
        # Check for duration-based approval
        duration = parse_duration(option)
        if duration is None:
            bot.reply_to(message, "Invalid option! Use on/off/yes/no or a duration (e.g., 3s, 1m, 2h)", disable_web_page_preview=True)
            return
        auto_approval_status[group_id] = {"mode": "delayed", "duration": duration}
        reply = f"*Delayed Auto-Approval Enabled!*\n\nJoin requests will be approved after {option}."
        log_details = {"operation": "delayed", "duration": option}

    save_auto_approval()
    log_action(
        chat_id=message.chat.id,
        action="approve",
        executor=message.from_user,
        target=message.chat,
        details=log_details
    )
    bot.reply_to(message, reply, parse_mode='Markdown', disable_web_page_preview=True)

@bot.message_handler(regexp=r'^[\/!](approvalqueue)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_approval_queue(message):
    group_id = str(message.chat.id)
    if group_id not in pending_approvals or not pending_approvals[group_id]:
        bot.reply_to(message, "No pending approvals in this group.", parse_mode='Markdown', disable_web_page_preview=True)
        return

    queue_info = "*Pending Approvals:*\n\n"
    for user_id, info in pending_approvals[group_id].items():
        queue_info += f"User ID: {user_id}\n"
        queue_info += f"Username: {info['username']}\n"
        queue_info += f"Scheduled Approval: {info['approval_time']}\n\n"

    bot.reply_to(message, queue_info, parse_mode='Markdown', disable_web_page_preview=True)

@bot.message_handler(regexp=r'^[\/!](cancelapproval)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_cancel_approval(message):
    cmd = message.text.split()
    if len(cmd) < 2:
        bot.reply_to(message, "Usage: /cancelapproval <user_id>", disable_web_page_preview=True)
        return

    user_id = cmd[1]
    group_id = str(message.chat.id)

    if group_id in pending_approvals and user_id in pending_approvals[group_id]:
        del pending_approvals[group_id][user_id]
        if not pending_approvals[group_id]:
            del pending_approvals[group_id]
        save_pending_approvals()
        bot.reply_to(message, f"Cancelled pending approval for user {user_id}.", parse_mode='Markdown', disable_web_page_preview=True)
    else:
        bot.reply_to(message, f"No pending approval found for user {user_id}.", parse_mode='Markdown', disable_web_page_preview=True)

@bot.chat_join_request_handler()
def handle_approval(message: telebot.types.ChatJoinRequest):
    try:
        group_id = str(message.chat.id)
        approval_settings = auto_approval_status.get(group_id, True)

        # If auto-approval is disabled
        if approval_settings is False:
            return

        # Handle delayed approval
        if isinstance(approval_settings, dict) and approval_settings.get("mode") == "delayed":
            delay_seconds = approval_settings["duration"]
            if group_id not in pending_approvals:
                pending_approvals[group_id] = {}
            pending_approvals[group_id][str(message.from_user.id)] = {
                "username": message.from_user.first_name,
                "approval_time": (datetime.now() + timedelta(seconds=delay_seconds)).strftime("%Y-%m-%d %H:%M:%S")
            }
            save_pending_approvals()
            bot.send_message(message.chat.id, f"Join request from [{message.from_user.first_name}](tg://user?id={message.from_user.id}) will be approved after {delay_seconds} seconds.", parse_mode='Markdown', disable_web_page_preview=True)
            threading.Thread(target=process_delayed_approval, args=(message.chat.id, message.from_user.id, delay_seconds)).start()
            return

        # Immediate approval
        try:
            bot.approve_chat_join_request(message.chat.id, message.from_user.id)
            logging.info(f"Approved user {message.from_user.id} in {message.chat.id}")
        except telebot.apihelper.ApiTelegramException as e:
            if "too_many_requests" in str(e).lower():
                error_msg = f"Rate limit error: Unable to approve user {message.from_user.id} due to Telegram API limits."
                bot.send_message(message.chat.id, error_msg, parse_mode='Markdown')
                logging.error(error_msg)
            else:
                logging.error(f"Approval error: {e}")
            return

        chat = bot.get_chat(message.chat.id)
        admins = bot.get_chat_administrators(message.chat.id)
        owner = next((a for a in admins if a.status == 'creator'), None)

        notification = """
🚀 *New User Approved!* ♛

├── ✿ *User*: [{user_name}](tg://user?id={user_id})
│   ├── ➻ *Group*: [{group_name}](https://t.me/{group_username})
│   └── ∞ *Time*: {approval_time}
└── ★ *Stats*
    ├── ✅ Approved: `{approved_count}`
    └── ⏳ Pending: `{pending_count}`
""".format(
            user_name=message.from_user.first_name,
            user_id=message.from_user.id,
            group_name=chat.title,
            group_username=chat.username or chat.id,
            approval_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            approved_count=len(auto_approval_status),
            pending_count=len(pending_approvals.get(group_id, {}))
        )

        notification_sent = False

        # Try sending to owner first
        if owner:
            try:
                bot.send_message(owner.user.id, notification, parse_mode='Markdown', disable_web_page_preview=True)
                notification_sent = True
            except Exception as e:
                logging.error(f"Owner notification failed: {e}")

        # If owner notification failed, try other admins
        if not notification_sent:
            for admin in admins:
                if admin.status == 'administrator':
                    try:
                        bot.send_message(admin.user.id, notification, parse_mode='Markdown', disable_web_page_preview=True)
                        notification_sent = True
                        break
                    except Exception as e:
                        logging.error(f"Admin {admin.user.id} notification failed: {e}")

        # If no admin could be notified, send to group
        if not notification_sent:
            try:
                bot.send_message(message.chat.id, "Failed to notify admins about new user approval.", parse_mode='Markdown')
            except Exception as e:
                logging.error(f"Group notification failed: {e}")

    except Exception as e:
        logging.error(f"Approval error: {e}")