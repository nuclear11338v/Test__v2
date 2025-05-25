from utilities.utils import SETTINGS_FILE
import json
import os
import logging

settings = {}

def load_settings():
    global settings
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
        else:
            settings = {}

        for chat_id in settings:
            settings[chat_id].setdefault("welcome", True)  # Default to True
            settings[chat_id].setdefault("goodbye", True)  # Default to True
            settings[chat_id].setdefault("welcome_msg", "Hey {username} welcome to {group}. Please follow the group rules")
            settings[chat_id].setdefault("goodbye_msg", "Goodbye {username} we miss you")
            settings[chat_id].setdefault("clean_welcome", False)
            settings[chat_id].setdefault("welcome_media", None)
            settings[chat_id].setdefault("goodbye_media", None)
            settings[chat_id].setdefault("last_welcome_id", None)
            settings[chat_id].setdefault("antiraid_enabled", False)
            settings[chat_id].setdefault("raid_time", 21600)
            settings[chat_id].setdefault("raid_action_time", 3600)
            settings[chat_id].setdefault("autoantiraid", 0)

        save_settings(settings)
        logging.info("Settings loaded and validated successfully")
        return settings
    except Exception as e:
        logging.error(f"Error loading settings: {str(e)}")
        return {}

def save_settings(data):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info("Settings saved successfully")
    except Exception as e:
        logging.error(f"Error saving settings: {str(e)}")

def get_group_settings(chat_id):
    chat_id_str = str(chat_id)
    if chat_id_str not in settings:
        settings[chat_id_str] = {
            "welcome": True,  # Default to True
            "goodbye": True,  # Default to True
            "welcome_msg": "Hey {username} welcome to {group}. Please follow the group rules",
            "goodbye_msg": "Goodbye {username} we miss you",
            "clean_welcome": False,
            "welcome_media": None,
            "goodbye_media": None,
            "last_welcome_id": None,
            "antiraid_enabled": False,
            "raid_time": 21600,
            "raid_action_time": 3600,
            "autoantiraid": 0
        }
        save_settings(settings)
        logging.info(f"Initialized settings for chat {chat_id}")
    return settings[chat_id_str]

settings = load_settings()