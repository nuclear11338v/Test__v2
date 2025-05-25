import time
import sys
import os
import requests
import traceback
import threading
import signal
import atexit
import random
from datetime import datetime
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from colorama import init, Fore, Style
from telebot import TeleBot
import telebot
from config import bot, BOT_TOKEN, BOT_USERNAME, BOT_ID, BOT_OWNER, logger
import help_lan
import language
import start
import help_languages.help_forward
import data.data
import ban_sticker_pack.ban_sticker_pack
import joinapproval
import mute
import privacy.privacy
import basics.del_feature
import user_logs.user_logs
import basics.get_ids 
import private_fungtions.connections.connection
import private_fungtions.pbans
import cleancommand
import cleanservice
import purges
import namechanger
import bans
import kick
import admins
import rules
import warns
import vc
import topics
import notes
import chatting
import welcome
import reports
import broadcasting.bcast
import locks


init(autoreset=True)

def get_bot_info(token):
    """Extract bot ID from token and get username from Telegram API if not provided"""
    try:
        bot_id = BOT_ID if BOT_ID else token.split(':')[0]
        bot_username = BOT_USERNAME
        
        if not bot_username or not bot_id:
            response = requests.get(f'https://api.telegram.org/bot{token}/getMe').json()
            if response.get('ok'):
                bot_username = f"@{response['result']['username']}" if not bot_username else bot_username
                bot_id = response['result']['id'] if not bot_id else bot_id
            else:
                raise ValueError("• Fᴀɪʟᴇᴅ Tᴏ Gᴇᴛ Bᴏᴛ Iɴғᴏ Fʀᴏᴍ Tᴇʟᴇɢʀᴀᴍ API")
        
        return {
            'id': bot_id,
            'username': bot_username
        }
    except Exception as e:
        logger.error(f"• Bᴏᴛ ɪɴғᴏ ᴇxᴛʀᴀᴄᴛɪᴏɴ ғᴀɪʟᴇᴅ  ➠ {e}")
        raise

try:
    bot_info = get_bot_info(BOT_TOKEN)
    BOT_USERNAME = bot_info['username']
    BOT_ID = bot_info['id']
except Exception as e:
    logger.error(f"• Fᴀɪʟᴇᴅ ᴛᴏ ɪɴɪᴛɪᴀʟɪᴢᴇ ʙᴏᴛ ɪɴғᴏ ➠ {e}")
    print(f"{Fore.RED}• FATAL ERROR ➠ Cᴏᴜʟᴅ ɴᴏᴛ ɪɴɪᴛɪᴀʟɪᴢᴇ ʙᴏᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ. {Style.RESET_ALL}")
    sys.exit(1)

start_time = None
running = True
uptime_thread = None

ASCII_HEADER = f"""
{Fore.MAGENTA}{Style.BRIGHT}┳━┓ ┳━┓ ┳━┓
┣━┫ ┣━┫ ┣┳┫
┣┻┫ ┣┻┫ ┣┻┫
┻ ┻ ┻ ┻ ┻ ┻{Style.RESET_ALL}
{Fore.CYAN}\n🔥 {BOT_USERNAME} by {BOT_OWNER} 🔥{Style.RESET_ALL}
\n\n"""

def print_stylish(text: str, color: str = Fore.CYAN, bold: bool = True):
    """Print text with style and flair"""
    style = Style.BRIGHT if bold else Style.NORMAL
    print(f"{color}{style}{text}{Style.RESET_ALL}")

def display_uptime():
    """Show a slick live uptime counter"""
    global running
    with Progress(
        TextColumn(f"{Fore.MAGENTA}[progress.description]{{task.description}}{Style.RESET_ALL}"),
        BarColumn(bar_width=50),
        TimeElapsedColumn(),
        transient=False
    ) as progress:
        task_id = progress.add_task(f"{BOT_USERNAME} Rᴜɴɴɪɴɢ Fʀᴏᴍ ➠", total=None)
        seconds = 0
        while running:
            seconds += 1
            if seconds < 60:
                uptime_str = f"{seconds} second{'s' if seconds != 1 else ''}"
            elif seconds < 3600:
                minutes = seconds // 60
                uptime_str = f"{minutes} minute{'s' if minutes != 1 else ''}"
            elif seconds < 86400:
                hours = seconds // 3600
                uptime_str = f"{hours} hour{'s' if hours != 1 else ''}"
            elif seconds < 31536000:
                days = seconds // 86400
                uptime_str = f"{days} day{'s' if days != 1 else ''}"
            else:
                years = seconds // 31536000
                uptime_str = f"{years} year{'s' if years != 1 else ''}"
            progress.update(task_id, description=f"{BOT_USERNAME} Rᴜɴɴɪɴɢ Fʀᴏᴍ ➠ {uptime_str}")
            time.sleep(1)

def handle_shutdown(signum, frame):
    """Gracefully shut down with style"""
    global running
    print_stylish("🛑 Sʜᴜᴛᴛɪɴɢ Dᴏᴡɴ... Pᴇᴀᴄᴇ Oᴜᴛ.", Fore.RED)
    running = False
    try:
        bot.stop_polling()
        print_stylish("» Pᴏʟʟɪɴɢ Sᴛᴏᴘᴘᴇᴅ Cʟᴇᴀɴʟʏ. « 🧹", Fore.GREEN)
    except Exception as e:
        logger.error(f"{Fore.RED} Sʜᴜᴛᴅᴏᴡɴ Eʀʀᴏʀ ➠ {e}\n{traceback.format_exc()}\nTɪᴍᴇsᴛᴀᴍᴘ ➠ {datetime.now()}{Style.RESET_ALL}")
        print_stylish(f"Fᴀɪʟᴇᴅ Tᴏ Sᴛᴏᴘ Pᴏʟʟɪɴɢ ➠ {e} 😿", Fore.RED)
    sys.exit(0)

def cleanup():
    """Clean up like a pro"""
    global running, uptime_thread
    print_stylish("🧹 Cʟᴇᴀɴɪɴɢ Uᴘ Rᴇsᴏᴜʀᴄᴇs...", Fore.YELLOW)
    running = False
    if uptime_thread and uptime_thread.is_alive():
        uptime_thread.join()
    print_stylish("Cʟᴇᴀɴᴜᴘ Cᴏᴍᴘʟᴇᴛᴇ! 🏁", Fore.GREEN)

def start_bot():
    """Launch the Telegram bot with max swagger"""
    global start_time, uptime_thread, running
    os.system('cls' if os.name == 'nt' else 'clear')
    start_time = datetime.now()
    running = True

    print(ASCII_HEADER)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    atexit.register(cleanup)

    print_stylish("┏━━━━━━━━━━━━━━━━━━━━┓\n⭕ Sᴛᴀʀᴛɪɴɢ Bᴏᴛ ⭕\n┗━━━━━━━━━━━━━━━━━━━━┛\n\n", Fore.CYAN)
    time.sleep(2)

    print_stylish("\r┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n🏍️ Cᴏɴɴᴇᴄᴛɪɴɢ Tᴏ Dᴀᴛᴀʙᴀsᴇ  🏂\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n", Fore.YELLOW)
    try:
        with Progress(
            TextColumn(f"{Fore.YELLOW}┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n🏂 Cᴏɴɴᴇᴄᴛɪɴɢ Tᴏ Dᴀᴛᴀʙᴀsᴇ... 🏂\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛{Style.RESET_ALL}"),
            BarColumn(),
            transient=True
        ) as progress:
            task = progress.add_task("", total=100)
            for _ in range(100):
                progress.update(task, advance=random.uniform(0.5, 2.5))
                time.sleep(random.uniform(0.01, 0.05))
    except Exception as e:
        logger.error(f"{Fore.RED}💥 Dᴀᴛᴀʙᴀsᴇ Cᴏɴɴᴇᴄᴛɪᴏɴ Fᴀɪʟᴇᴅ ➠ {e}\n{traceback.format_exc()}\nTɪᴍᴇsᴛᴀᴍᴘ ➠ {datetime.now()}{Style.RESET_ALL}")
        print_stylish(f"Dᴀᴛᴀʙᴀsᴇ Eʀʀᴏʀ ➠  {e} 😿", Fore.RED)
    time.sleep(2)

    file_info = (
        f"{Fore.MAGENTA}{Style.BRIGHT}┏━━━━━━━━━━━━━━━━━━━━┓\n🟢      Fɪʟᴇ Iɴғᴏ  🟢\n┗━━━━━━━━━━━━━━━━━━━━┛\n"
        f"┏━━━━━━━━━━━━━━━━━━━━┓\n┃ Vᴇʀsɪᴏɴ ➠ 0.1\n"
        f"┃ Fɪʟᴇ Aᴜᴛʜᴏʀ ➠ Aʀᴍᴀɴ\n"
        f"┃ Aᴜᴛʜᴏʀ Eᴍᴀɪʟ ➠ armanhacker95@gmail.com\n"
        f"┃\n"
        f"┃ 🤖 Tʜɪs Fɪʟᴇ Mᴀᴅᴇ Fᴏʀ Tᴇʟᴇɢʀᴀᴍ Bᴏᴛ 🤖\n"
        f"┃ 🔥 Dᴇᴠᴇʟᴏᴘᴇʀ Fᴏᴜɴᴅ Oɴ Tᴇʟᴇɢʀᴀᴍ 🔥\n┃\n"
        f"┃ Dᴇᴠ Usᴇʀɴᴀᴍᴇ ➠ {BOT_OWNER} [ OFFLINE ] ( Oᴡɴᴇʀ Oғғ Tʜɪs Fɪʟᴇ )\n┃\n"
        f"┃ Assɪsᴛᴀɴᴛ ➠ @Dev_x_Ninja\n"
        f"┃ Dᴇᴍᴏ Bᴏᴛ ➠ {BOT_USERNAME}\n┗━━━━━━━━━━━━━━━━━━━━┛{Style.RESET_ALL}\n"
    )
    print(f"\r{file_info}")
    print("\n\n")
    time.sleep(2)

    bot_status = (
        f"{Fore.GREEN}{Style.BRIGHT}• Bᴏᴛ Is Rᴜɴɴɪɴɢ Sᴜᴄᴄᴇssғᴜʟʟʏ 🎉\n"
        f"• Bᴏᴛ ᴜsᴇʀɴᴀᴍᴇ ➠ {BOT_USERNAME}\n"
        f"• Bᴏᴛ Iᴅ ➠ {BOT_ID}\n"
        f"• Bᴏᴛ Oᴡɴᴇʀ ➠ {BOT_OWNER}{Style.RESET_ALL}"
    )
    print(bot_status)
    print("\n\n")
    time.sleep(2)

    print_stylish("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃⏳ Lᴀᴜɴᴄʜɪɴɢ Uᴘᴛɪᴍᴇ Cᴏᴜɴᴛᴇʀ ⏳┃", Fore.CYAN)
    uptime_thread = threading.Thread(target=display_uptime, daemon=True)
    uptime_thread.start()

    print_stylish("┃Rᴜɴɴɪɴɢ Pʀᴇ-Sᴛᴀʀᴛ Cʜᴇᴄᴋs┃\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n", Fore.YELLOW)
    try:
        if not BOT_TOKEN:
            raise ValueError("• Bᴏᴛ ᴛᴏᴋᴇɴ ɪs ᴍɪssɪɴɢ × 😿")
        print_stylish("• Bᴏᴛ Tᴏᴋᴇɴ Vᴀʟɪᴅᴀᴛᴇᴅ. √", Fore.GREEN)
    except Exception as e:
        logger.error(f"{Fore.RED}• Tᴏᴋᴇɴ Vᴀʟɪᴅᴀᴛɪᴏɴ Fᴀɪʟᴇᴅ ➠ {e}\n{traceback.format_exc()}\nTɪᴍᴇsᴛᴀᴍᴘ ➠ {datetime.now()}{Style.RESET_ALL}")
        print_stylish(f"Tᴏᴋᴇɴ Eʀʀᴏʀ ➠ {e} 😿", Fore.RED)
        sys.exit(1)

    try:
        if not hasattr(bot, "infinity_polling"):
            raise AttributeError("• Bᴏᴛ ɴᴏᴛ ɪɴɪᴛɪᴀʟɪᴢᴇᴅ ᴘʀᴏᴘᴇʀʟʏ. × 😿")
        print_stylish("• Bᴏᴛ Cᴏɴғɪɢ Vᴀʟɪᴅᴀᴛᴇᴅ √", Fore.GREEN)
    except Exception as e:
        logger.error(f"{Fore.RED}• Cᴏɴғɪɢ Vᴀʟɪᴅᴀᴛɪᴏɴ Fᴀɪʟᴇᴅ ➠ {e}\n{traceback.format_exc()}\nTɪᴍᴇsᴛᴀᴍᴘ ➠ {datetime.now()}{Style.RESET_ALL}")
        print_stylish(f"Cᴏɴғɪɢ Eʀʀᴏʀ ➠ {e} 😿", Fore.RED)
        sys.exit(1)

    try:
        if not os.path.exists("logs"):
            os.makedirs("logs")
            print_stylish("• Cʀᴇᴀᴛᴇᴅ Lᴏɢs Dɪʀᴇᴄᴛᴏʀʏ. 📁", Fore.GREEN)
    except Exception as e:
        logger.error(f"{Fore.RED}• Eɴᴠɪʀᴏɴᴍᴇɴᴛ Sᴇᴛᴜᴘ Fᴀɪʟᴇᴅ ➠ {e}\n{traceback.format_exc()}\nTɪᴍᴇsᴛᴀᴍᴘ ➠ {datetime.now()}{Style.RESET_ALL}")
        print_stylish(f"Eɴᴠɪʀᴏɴᴍᴇɴᴛ Eʀʀᴏʀ ➠ {e} 😿", Fore.RED)

    try:
        import telebot
        import rich
        import colorama
        print_stylish("• Aʟʟ Dᴇᴘᴇɴᴅᴇɴᴄɪᴇs Lᴏᴀᴅᴇᴅ. √\n\n", Fore.GREEN)
    except ImportError as e:
        logger.error(f"{Fore.RED}• Dᴇᴘᴇɴᴅᴇɴᴄʏ Cʜᴇᴄᴋ Fᴀɪʟᴇᴅ  ➠ {e}\n{traceback.format_exc()}\nTɪᴍᴇsᴛᴀᴍᴘ ➠ {datetime.now()}{Style.RESET_ALL}")
        print_stylish(f"⚠️ Dᴇᴘᴇɴᴅᴇɴᴄʏ Eʀʀᴏʀ ➠ {e} 😿", Fore.RED)
        sys.exit(1)

    print_stylish("• Sᴛᴀʀᴛɪɴɢ Pᴏʟʟɪɴɢ.\n\n", Fore.MAGENTA)
    while running:
        try:
            bot.infinity_polling()
        except Exception as e:
            logger.error(
                f"{Fore.RED}Pᴏʟʟɪɴɢ Eʀʀᴏʀ ➠ {e}\n"
                f"Tʏᴘᴇ ➠ {type(e).__name__}\n"
                f"Tɪᴍᴇsᴛᴀᴍᴘ ➠ {datetime.now()}\n"
                f"Tʀᴀᴄᴇʙᴀᴄᴋ ➠ {traceback.format_exc()}\n"
                f"Rᴇᴛʀʏɪɴɢ Iɴ 10 Sᴇᴄᴏɴᴅs.{Style.RESET_ALL}"
            )
            print_stylish(f"• Pᴏʟʟɪɴɢ Cʀᴀsʜᴇᴅ. ➠ {e} Rᴇᴛʀʏɪɴɢ Iɴ 10 Sᴇᴄᴏɴᴅs", Fore.RED)
            time.sleep(10)
        except KeyboardInterrupt:
            print_stylish("• Kᴇʏʙᴏᴀʀᴅ Iɴᴛᴇʀʀᴜᴘᴛ! Sʜᴜᴛᴛɪɴɢ Dᴏᴡɴ. 🛑", Fore.RED)
            running = False
            break
        except SystemExit:
            print_stylish("• Sʏsᴛᴇᴍ Exɪᴛ! Sʜᴜᴛᴛɪɴɢ Dᴏᴡɴ. 🛑", Fore.RED)
            running = False
            break
        finally:
            if not running:
                print_stylish("• Fɪɴᴀʟ Cʟᴇᴀɴᴜᴘ. 🏁", Fore.YELLOW)
                try:
                    bot.stop_polling()
                    print_stylish("• Pᴏʟʟɪɴɢ Sᴛᴏᴘᴘᴇᴅ. 🛑", Fore.GREEN)
                except Exception as e:
                    logger.error(f"{Fore.RED}• Cʟᴇᴀɴᴜᴘ Eʀʀᴏʀ ➠ {e}\n{traceback.format_exc()}\nTɪᴍᴇsᴛᴀᴍᴘ ➠ {datetime.now()}{Style.RESET_ALL}")
                    print_stylish(f"⚠️ Cʟᴇᴀɴᴜᴘ Eʀʀᴏʀ ➠ {e} 😿", Fore.RED)

    print_stylish("• Bᴏᴛ Hᴀs Sᴛᴏᴘᴘᴇᴅ. Uɴᴛɪʟ Nᴇxᴛ Tɪᴍᴇ. 🛑", Fore.CYAN)

if __name__ == '__main__':
    start_bot()