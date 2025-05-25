import telebot
import os
from datetime import datetime
import functools
import json
from config import bot 

GROUP_DATA_DIR = "group_data"
USER_DATA_DIR = "user_data"

os.makedirs(GROUP_DATA_DIR, exist_ok=True)
os.makedirs(USER_DATA_DIR, exist_ok=True)

def store(func):
    @functools.wraps(func)
    def wrapper(message):
        chat = message.chat
        user = message.from_user
        
        if chat.type in ['group', 'supergroup']:
            admins = get_admins(chat.id)
            admin_ids = {admin['user_id'] for admin in admins}
            
            group_data = {
                'group_id': chat.id,
                'group_name': chat.title,
                'group_username': f"https://t.me/{chat.username}" if chat.username else "N/A",
                'bot_added_in': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                'group_bio': getattr(chat, 'description', 'N/A'),
                'linked_channel': getattr(chat, 'linked_chat_id', 'N/A'),
                'total_members': bot.get_chat_member_count(chat.id),
                'group_type': 'private' if getattr(chat, 'is_private', False) else 'public',
                'permissions': {
                    'send_text_messages': getattr(chat.permissions, 'can_send_messages', False),
                    'send_media': getattr(chat.permissions, 'can_send_media_messages', False),
                    'photos': getattr(chat.permissions, 'can_send_photos', False),
                    'videos': getattr(chat.permissions, 'can_send_videos', False),
                    'sticker_gif': getattr(chat.permissions, 'can_send_animations', False),
                    'music': getattr(chat.permissions, 'can_send_audios', False),
                    'files': getattr(chat.permissions, 'can_send_documents', False),
                    'voice_message': getattr(chat.permissions, 'can_send_voice_notes', False),
                    'video_message': getattr(chat.permissions, 'can_send_video_notes', False),
                    'embed_links': getattr(chat.permissions, 'can_send_other_messages', False),
                    'polls': getattr(chat.permissions, 'can_send_polls', False),
                    'add_user': getattr(chat.permissions, 'can_invite_users', False),
                    'pin_message': getattr(chat.permissions, 'can_pin_messages', False),
                    'change_chat_info': getattr(chat.permissions, 'can_change_info', False),
                    'charge_stars': False,
                },
                'slowmode': getattr(chat, 'slow_mode_delay', 'off'),
                'do_not_restrict_boosters': getattr(chat, 'join_to_send_messages', False),
                'removed_users': 0,
                'group_photo_link': get_chat_photo(chat.id),
                'group_admins': admins,
                'group_users': []
            }
            
            if user.id not in admin_ids:
                user_data = {
                    'first_name': user.first_name,
                    'last_name': user.last_name or "N/A",
                    'username': f"@{user.username}" if user.username else "N/A",
                    'user_bio': get_user_bio(user.id),
                    'user_id': user.id,
                    'user_phone': "N/A"
                }
                group_data['group_users'].append(user_data)
            
            save_group_data(chat.title, group_data)
        
        elif chat.type == 'private':
            user_data = {
                'user_id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name or "N/A",
                'username': f"@{user.username}" if user.username else "N/A",
                'user_bio': get_user_bio(user.id),
                'user_phone': "N/A",
            }
            save_user_data(user.first_name, user_data)
        
        return func(message)
    return wrapper

def get_chat_photo(chat_id):
    try:
        photos = bot.get_chat(chat_id).photo
        if photos:
            file_id = photos.big_file_id
            file_info = bot.get_file(file_id)
            return f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        return "N/A"
    except:
        return "N/A"

def get_user_bio(user_id):
    try:
        return bot.get_chat(user_id).bio or "N/A"
    except:
        return "N/A"

def get_admins(chat_id):
    admins = []
    try:
        admin_list = bot.get_chat_administrators(chat_id)
        for admin in admin_list:
            admin_data = {
                'first_name': admin.user.first_name,
                'last_name': admin.user.last_name or "N/A",
                'username': f"@{admin.user.username}" if admin.user.username else "N/A",
                'user_bio': get_user_bio(admin.user.id),
                'user_id': admin.user.id,
                'user_phone': "N/A",
                'is_owner': admin.status == 'creator'
            }
            admins.append(admin_data)
    except:
        pass
    return admins

def save_group_data(title, data):
    group_dir = os.path.join(GROUP_DATA_DIR, f"chat_{title}")
    os.makedirs(group_dir, exist_ok=True)
    
    new_data_str = format_group_data(data)
    
    existing_files = sorted([f for f in os.listdir(group_dir) if f.startswith("data_") and f.endswith(".txt")])
    
    if existing_files:
        latest_file = os.path.join(group_dir, existing_files[-1])
        with open(latest_file, 'r', encoding='utf-8') as f:
            existing_data_str = f.read()
        
        if new_data_str == existing_data_str:
            return
    
    file_number = len(existing_files) + 1
    file_path = os.path.join(group_dir, f"data_{file_number}.txt")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_data_str)

def save_user_data(first_name, data):
    user_dir = os.path.join(USER_DATA_DIR, f"user_{first_name}")
    os.makedirs(user_dir, exist_ok=True)
    
    new_data_str = format_user_data(data)
    
    existing_files = sorted([f for f in os.listdir(user_dir) if f.startswith("data_") and f.endswith(".txt")])
    
    if existing_files:
        latest_file = os.path.join(user_dir, existing_files[-1])
        with open(latest_file, 'r', encoding='utf-8') as f:
            existing_data_str = f.read()
        
        if new_data_str == existing_data_str:
            return
    
    file_number = len(existing_files) + 1
    file_path = os.path.join(user_dir, f"data_{file_number}.txt")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_data_str)

def format_group_data(data):
    perms = data['permissions']
    admins = data['group_admins']
    users = data.get('group_users', [])
    
    admin_str = "│ │ \n"
    for i, admin in enumerate(admins):
        role = "│ ├ • Gʀᴏᴜᴘ Oᴡɴᴇʀ" if admin['is_owner'] else f"Aᴅᴍɪɴ {i}"
        admin_str += f"│ ├ • {role}:\n"
        admin_str += f"│ ├ • Fɪʀsᴛ Nᴀᴍᴇ ➠ {admin['first_name']}\n"
        admin_str += f"│ ├ • Lᴀsᴛ Nᴀᴍᴇ ➠ {admin['last_name']}\n"
        admin_str += f"│ ├ • Usᴇʀɴᴀᴍᴇ ➠ {admin['username']}\n"
        admin_str += f"│ ├ • Usᴇʀ Bɪᴏ ➠ {admin['user_bio']}\n"
        admin_str += f"│ ├ • Usᴇʀ Iᴅ ➠ {admin['user_id']}\n"
        admin_str += f"│ └ • Usᴇʀ Pʜᴏɴᴇ ➠ {admin['user_phone']}\n│ \n"
        admin_str += "│ ===================\n│ \n│ "
    
    user_str = "│  │ \n"
    if not users:
        user_str += "├ • Nᴏ Usᴇʀs Rᴇᴄᴏʀᴅᴇᴅ Yᴇᴛ.\n└"
    else:
        for i, user in enumerate(users, 1):
            user_str += f"│ ├ • User:\n"
            user_str += f"First name - {user['first_name']}\n"
            user_str += f"Last name - {user['last_name']}\n"
            user_str += f"Username - {user['username']}\n"
            user_str += f"User bio - {user['user_bio']}\n"
            user_str += f"User id - {user['user_id']}\n"
            user_str += f"User phone - {user['user_phone']}\n"
            user_str += "│ ===================\n│ "
    
    return f"""
├── 🔸 {data['group_name']}
│ │
│ ├ • Gʀᴏᴜᴘ Iᴅ ➠ {data['group_id']}
│ ├ • Nᴀᴍᴇ ➠ {data['group_name']}
│ ├ • Usᴇʀɴᴀᴍᴇ ➠ {data['group_username']}
│ │
│ ├ • Bᴏᴛ Aᴅᴅᴇᴅ ➠ {data['bot_added_in']}
│ │
│ ├ • Bɪᴏ ➠ {data['group_bio']}
│ │
│ ├ • Lɪɴᴋᴇᴅ Cʜᴀɴɴᴇʟ ➠ {data['linked_channel']}
│ │
│ ├ • Mᴇᴍʙᴇʀs ➠ {data['total_members']}
│ │
│ └ • Gʀᴏᴜᴘ Tʏᴘᴇ ➠ {data['group_type']}
│
│
├──🔸 𝗣𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻𝘀
│ ├ • Sᴇɴᴅ Tᴇxᴛ Mᴇssᴀɢᴇs ➠ {perms['send_text_messages']}
│ ├ • Sᴇɴᴅ Mᴇᴅɪᴀ ➠ {perms['send_media']}
│ ├ • Pнoтoѕ ➠ {perms['photos']}
│ ├ • Vɪᴅᴇᴏs ➠ {perms['videos']}
│ ├ • Sᴛɪᴄᴋᴇʀ & Gɪғ ➠ {perms['sticker_gif']}
│ ├ • Mᴜsɪᴄ ➠ {perms['music']}
│ ├ • Fɪʟᴇs ➠ {perms['files']}
│ ├ • Vᴏɪᴄᴇ Mᴇssᴀɢᴇ ➠ {perms['voice_message']}
│ ├ • Vɪᴅᴇᴏ Mᴇssᴀɢᴇ ➠ {perms['video_message']}
│ ├ • Eᴍʙᴇᴅ Lɪɴᴋs ➠ {perms['embed_links']}
│ └ • Pᴏʟʟs ➠ {perms['polls']}
│
│
├───🔸 𝗔𝗱𝗱, 𝗣𝗶𝗻, 𝗘𝘁𝗰
│ │
│ ├ • Aᴅᴅ Usᴇʀ ➠ {perms['add_user']}
│ ├ • Pɪɴ Mᴇssᴀɢᴇ ➠ {perms['pin_message']}
│ ├ • Cʜᴀɴɢᴇ Cʜᴀᴛ Iɴғᴏ ➠ {perms['change_chat_info']}
│ ├ • Cʜᴀʀɢᴇ Sᴛᴀʀs Fᴏʀ Mᴇssᴀɢᴇ ➠ {perms['charge_stars']}
│ │
│ ├ • Sʟᴏᴡᴍᴏᴅᴇ ➠ {data['slowmode']}
│ ├ • Dᴏ Nᴏᴛ Rᴇsᴛʀɪᴄᴛ Bᴏᴏsᴛᴇʀs ➠ {data['do_not_restrict_boosters']}
│ │
│ ├ • Rᴇᴍᴏᴠᴇᴅ Usᴇʀs ➠ {data['removed_users']}
│ └ • Gʀᴏᴜᴘ Pʜᴏᴛᴏ Lɪɴᴋ ➠ {data['group_photo_link']}
│
│
├───🔸 𝗔𝗱𝗺𝗶𝗻𝘀
{admin_str}
│
│
├───🔸 𝗨𝘀𝗲𝗿𝘀
{user_str}
"""

def format_user_data(data):
    return f"""
├───🔸 {data['first_name']}
│ ├ • Usᴇʀ Iᴅ  ➠ {data['user_id']}
│ │    
│ ├ • Fɪʀsᴛ Nᴀᴍᴇ ➠ {data['first_name']}
│ ├ • Lᴀsᴛ Nᴀᴍᴇ ➠ {data['last_name']}
│ │
│ ├ • Usᴇʀɴᴀᴍᴇ ➠ {data['username']}
│ │
│ └ • Usᴇʀ Bɪᴏ ➠ {data['user_bio']}
"""
