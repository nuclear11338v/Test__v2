import telebot
import json
import os
import re
from functools import wraps
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import bot
from kick import disabled
from ban_sticker_pack.ban_sticker_pack import is_admin, is_group

NOTE_FILE = "note_data.json"
MAX_NOTES_PER_GROUP = 200

def load_notes():
    if os.path.exists(NOTE_FILE):
        with open(NOTE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_notes(notes):
    with open(NOTE_FILE, 'w') as f:
        json.dump(notes, f, indent=2)

def escape_markdown_v2(text):
    special_chars = r'([_\*\[\]\(\)~`>#\+-=|\{\}\.!])'
    return re.sub(special_chars, r'\\\1', text)

notes = load_notes()

def get_group_id(chat_id):
    return str(chat_id)

def parse_buttons(text):
    buttons = []
    cleaned_text = text
    button_pattern = r'\[([^\]]+)\]\(buttonurl://([^\)]+)\)'
    matches = re.findall(button_pattern, text)
    
    if matches:
        row = []
        for button_text, url in matches:
            row.append({"text": button_text, "url": url})
        buttons.append(row)
        cleaned_text = re.sub(button_pattern, '', text).strip()
    
    return cleaned_text, buttons

@bot.message_handler(regexp=r'^[\/!](save)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_save_note(message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            bot.reply_to(message, "Usage: /save <notename> <note text>")
            return

        notename = args[1].lower()
        group_id = get_group_id(message.chat.id)
        
        if group_id not in notes:
            notes[group_id] = {}
        if len(notes[group_id]) >= MAX_NOTES_PER_GROUP:
            bot.reply_to(message, f"Maximum limit of {MAX_NOTES_PER_GROUP} notes reached.")
            return

        note_content = {
            'text': args[2] if len(args) > 2 else '',
            'type': 'text',
            'user_id': message.from_user.id,
            'buttons': []
        }

        if message.reply_to_message:
            reply = message.reply_to_message
            if reply.photo:
                note_content['type'] = 'photo'
                note_content['file_id'] = reply.photo[-1].file_id
            elif reply.video:
                note_content['type'] = 'video'
                note_content['file_id'] = reply.video.file_id
            elif reply.audio:
                note_content['type'] = 'audio'
                note_content['file_id'] = reply.audio.file_id
            elif reply.document:
                note_content['type'] = 'document'
                note_content['file_id'] = reply.document.file_id
            if reply.caption:
                note_content['text'] = reply.caption

        if note_content['text']:
            cleaned_text, buttons = parse_buttons(note_content['text'])
            note_content['text'] = cleaned_text
            note_content['buttons'] = buttons

        notes[group_id][notename] = note_content
        save_notes(notes)
        bot.reply_to(message, f"Note '{notename}' saved successfully!")
    except Exception as e:
        bot.reply_to(message, f"Error saving note: {str(e)}")

@bot.message_handler(commands=['get', 'notes', 'saved', 'clear', 'clearall', 'privatenotes'])
@is_group
@disabled
def command_allcommands(message):
    try:
        command = message.text.split()[0][1:].lower()
        group_id = get_group_id(message.chat.id)

        if command == 'get':
            notename = message.text.split(maxsplit=1)[1].lower() if len(message.text.split()) > 1 else ''
            if not notename:
                bot.reply_to(message, "Usage: /get <notename>")
                return
            get_note(message, notename)

        elif command in ['notes', 'saved']:
            if group_id not in notes or not notes[group_id]:
                bot.reply_to(message, "No notes found in this chat.")
                return
            note_list = "\n".join([key for key in notes[group_id].keys() if key != 'private_notes'])
            bot.reply_to(message, f"Available notes:\n{note_list}")

        elif command == 'clear':
            if not is_admin(lambda x: True)(message):
                return
            notename = message.text.split(maxsplit=1)[1].lower() if len(message.text.split()) > 1 else ''
            if not notename:
                bot.reply_to(message, "Usage: /clear <notename>")
                return
            if group_id in notes and notename in notes[group_id]:
                del notes[group_id][notename]
                save_notes(notes)
                bot.reply_to(message, f"Note '{notename}' deleted.")
            else:
                bot.reply_to(message, f"Note '{notename}' not found!")

        elif command == 'clearall':
            if not is_admin(lambda x: True)(message):
                return
            if group_id in notes:
                del notes[group_id]
                save_notes(notes)
                bot.reply_to(message, "All notes deleted.")
            else:
                bot.reply_to(message, "No notes to delete.")

        elif command == 'privatenotes':
            if not is_admin(lambda x: True)(message):
                return
            setting = message.text.split(maxsplit=1)[1].lower() if len(message.text.split()) > 1 else ''
            if setting not in ['on', 'off']:
                bot.reply_to(message, "Usage: /privatenotes on/off")
                return
            notes.setdefault(group_id, {})['private_notes'] = setting == 'on'
            save_notes(notes)
            bot.reply_to(message, f"Private notes turned {setting}")

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(regexp=r'^#\w+')
@is_group
@disabled
def handle_hashtag(message):
    try:
        notename = message.text[1:].lower()
        get_note(message, notename)
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

def get_note(message, notename):
    group_id = get_group_id(message.chat.id)
    
    if group_id not in notes or notename not in notes[group_id]:
        bot.reply_to(message, f"Note '{notename}' not found!")
        return

    note = notes[group_id][notename]
    is_private = notes[group_id].get('private_notes', False)

    if is_private:
        markup = InlineKeyboardMarkup()
        start_param = f"note_{group_id}_{notename}"
        button_url = f"https://t.me/{bot.get_me().username}?start={start_param}"
        markup.add(InlineKeyboardButton("Click here", url=button_url))
        bot.reply_to(message, "Click to get the note in PM", reply_markup=markup)
    else:
        send_note(message.chat.id, note)

def send_note(chat_id, note):
    try:
        markup = None
        if note.get('buttons'):
            markup = InlineKeyboardMarkup()
            for row in note['buttons']:
                markup.row(*[InlineKeyboardButton(**button) for button in row])
        
        text = escape_markdown_v2(note.get('text', ''))

        if note['type'] == 'photo':
            bot.send_photo(chat_id, note['file_id'], caption=text, parse_mode='MarkdownV2', reply_markup=markup)
        elif note['type'] == 'video':
            bot.send_video(chat_id, note['file_id'], caption=text, parse_mode='MarkdownV2', reply_markup=markup)
        elif note['type'] == 'audio':
            bot.send_audio(chat_id, note['file_id'], caption=text, parse_mode='MarkdownV2', reply_markup=markup)
        elif note['type'] == 'document':
            bot.send_document(chat_id, note['file_id'], caption=text, parse_mode='MarkdownV2', reply_markup=markup)
        else:
            bot.send_message(chat_id, text, parse_mode='MarkdownV2', reply_markup=markup)
    except Exception as e:
        bot.send_message(chat_id, f"Error sending note: {str(e)}")