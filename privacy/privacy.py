import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import bot
import os

ADMIN_ID = 6177259495

PRIVACY_MESSAGES = {
    "en": """*Privacy Policy & Disclaimer*

              • KiraBot

*1. Privacy & Data Collection*
We collect minimal data to provide core features:

• User ID  
• Username  
• First Name  
• Last Name  
• Bio (if available)

*Group Data:*
• Group ID  
• Group Title  
• Invite Link  
• Linked Channel  
• Permissions  
• Admin List (IDs only)

*2. Data Use*
Your data is only used internally for bot operations and is never shared.

*3. Data Deletion*
To delete your data, press "Delete My Data" below.

*4. Copyright*
All rights belong to their respective owners. This bot follows Telegram’s TOS.

*5. Agreement*
Using the bot means you accept these terms.""",

    "bn": """*গোপনীয়তা নীতি ও দাবিত্যাগ*

        • KiraBot

*১. গোপনীয়তা ও তথ্য সংগ্রহ*
আমরা মূল বৈশিষ্ট্য প্রদানের জন্য ন্যূনতম তথ্য সংগ্রহ করি:

• ব্যবহারকারীর আইডি  
• ব্যবহারকারীর নাম  
• প্রথম নাম  
• শেষ নাম  
• বায়ো (যদি উপলব্ধ থাকে)

*গ্রুপ তথ্য:*
• গ্রুপ আইডি  
• গ্রুপের শিরোনাম  
• আমন্ত্রণ লিঙ্ক  
• সংযুক্ত চ্যানেল  
• অনুমতি  
• অ্যাডমিন তালিকা (শুধুমাত্র আইডি)

*২. তথ্য ব্যবহার*
আপনার তথ্য শুধুমাত্র ব, বট পরিচালনার জন্য অভ্যন্তরীণভাবে ব্যবহৃত হয় এবং কখনো শেয়ার করা হয় না।

*৩. তথ্য মুছে ফেলা*
আপনার তথ্য মুছে ফেলতে, নীচে "আমার তথ্য মুছুন" বোতাম টিপুন।

*৪. কপিরাইট*
সমস্ত অধিকার তাদের নিজ নিজ মালিকদের। এই বট টেলিগ্রামের TOS অনুসরণ করে।

*৫. চুক্তি*
বট ব্যবহার করার মানে আপনি এই শর্তাবলী মেনে নিয়েছেন।""",

    "hi": """*गोपनीयता नीति और अस्वीकरण*

      • KiraBot

*1. गोपनीयता और डेटा संग्रह*
हम मुख्य सुविधाएँ प्रदान करने के लिए न्यूनतम डेटा एकत्र करते हैं:

• उपयोगकर्ता आईडी  
• उपयोगकर्ता नाम  
• पहला नाम  
• अंतिम नाम  
• बायो (यदि उपलब्ध हो)

*समूह डेटा:*
• समूह आईडी  
• समूह का शीर्षक  
• आमंत्रण लिंक  
• लिंक्ड चैनल  
• अनुमतियाँ  
• व्यवस्थापक सूची (केवल आईडी)

*2. डेटा उपयोग*
आपका डेटा केवल बॉट संचालन के लिए आंतरिक रूप से उपयोग किया जाता है और इसे कभी साझा नहीं किया जाता।

*3. डेटा हटाना*
अपना डेटा हटाने के लिए, नीचे "मेरा डेटा हटाएँ" दबाएँ।

*4. कॉपीराइट*
सभी अधिकार उनके संबंधित मालिकों के पास हैं। यह बॉट टेलीग्राम के TOS का पालन करता है।

*5. समझौता*
बॉट का उपयोग करने का मतलब है कि आप इन शर्तों को स्वीकार करते हैं।""",

    "ja": """*プライバシーポリシーと免責事項*

       • KiraBot

*1. プライバシーとデータ収集*
コア機能を提供するために最小限のデータを収集します：

• ユーザーID  
• ユーザー名  
• 名  
• 姓  
• バイオ（利用可能な場合）

*グループデータ:*
• グループID  
• グループタイトル  
• 招待リンク  
• リンクされたチャンネル  
• 権限  
• 管理者リスト（IDのみ）

*2. データ使用*
あなたのデータはボットの運営のために内部的にのみ使用され、共有されることはありません。

*3. データ削除*
データを削除するには、以下の「私のデータを削除」を押してください。

*4. 著作権*
すべての権利はそれぞれの所有者に帰属します。このボットはTelegramのTOSに従います。

*5. 同意*
ボットを使用することは、これらの条件に同意することを意味します。""",

    "zh": """*隐私政策与免责声明*

*机器人名称:* • KiraBot

*1. 隐私与数据收集*
我们仅收集提供核心功能所需的最少数据：

• 用户ID  
• 用户名  
• 名  
• 姓  
• 简介（如果有）

*群组数据:*
• 群组ID  
• 群组标题  
• 邀请链接  
• 关联频道  
• 权限  
• 管理员列表（仅ID）

*2. 数据使用*
您的数据仅用于机器人内部操作，绝不共享。

*3. 数据删除*
要删除您的数据，请按下面的“删除我的数据”。

*4. 版权*
所有权利归各自所有者所有。此机器人遵循Telegram的TOS。

*5. 协议*
使用机器人即表示您接受这些条款。""",

    "te": """*గోప్యతా విధానం & డిస్క్లైమర్*

     • KiraBot

*1. గోప్యత & డేటా సేకరణ*
మేము కోర్ ఫీచర్లను అందించడానికి కనీస డేటాను సేకరిస్తాము:

• యూజర్ ఐడీ  
• యూజర్ నేమ్  
• మొదటి పేరు  
• చివరి పేరు  
• బయో (ఒకవేళ అందుబాటులో ఉంటే)

*గ్రూప్ డేటా:*
• గ్రూప్ ఐడీ  
• గ్రూప్ టైటిల్  
• ఆహ్వాన లింక్  
• లింక్డ్ ఛానల్  
• అనుమతులు  
• అడ్మిన్ జాబితా (ఐడీలు మాత్రమే)

*2. డేటా వినియోగం*
మీ డేటా బాట్ ఆపరేషన్ల కోసం అంతర్గతంగా మాత్రమే ఉపయోగించబడుతుంది మరియు ఎప్పుడూ షేర్ చేయబడదు.

*3. డేటా తొలగింపు*
మీ డేటాను తొలగించడానికి, క్రింద "నా డేటాను తొలగించు" నొక్కండి.

*4. కాపీరైట్*
అన్ని హక్కులు వాటి సంబంధిత యజమానులకు చెందుతాయి. ఈ బాట్ టెలిగ్రామ్ యొక్క TOSని అనుసరిస్తుంది.

*5. ఒప్పందం*
బాట్ ఉపయోగించడం అంటే మీరు ఈ నిబంధనలను అంగీకరిస్తున్నారని అర్థం.""",

    "ur": """*رازداری کی پالیسی اور ڈس کلیمر*

    • KiraBot

*1. رازداری اور ڈیٹا جمع کرنا*
ہم بنیادی خصوصیات فراہم کرنے کے لیے کم سے کم ڈیٹا جمع کرتے ہیں:

• صارف آئی ڈی  
• صارف نام  
• پہلا نام  
• آخری نام  
• بائیو (اگر دستیاب ہو)

*گروپ ڈیٹا:*
• گروپ آئی ڈی  
• گروپ کا عنوان  
• دعوتی لنک  
• منسلک چینل  
• اجازتیں  
• ایڈمن فہرست (صرف آئی ڈیز)

*2. ڈیٹا کا استعمال*
آپ کا ڈیٹا صرف بوٹ آپریشنز کے لیے اندرونی طور پر استعمال ہوتا ہے اور کبھی شیئر نہیں کیا جاتا۔

*3. ڈیٹا حذف کرنا*
اپنا ڈیٹا حذف کرنے کے لیے، نیچے "میرا ڈیٹا حذف کریں" دبائیں۔

*4. کاپی رائٹ*
تمام حقوق ان کے متعلقہ مالکان کے پاس ہیں۔ یہ بوٹ ٹیلیگرام کے TOS کی پیروی کرتا ہے۔

*5. معاہدہ*
بوٹ استعمال کرنے کا مطلب ہے کہ آپ ان شرائط کو قبول کرتے ہیں۔"""
}


BUTTON_LABELS = {
    "en": {
        "show": "Show in English",
        "delete": "Delete My Data",
        "confirm": "Yes, I am sure",
        "cancel": "No, don't delete",
        "close": "Close"
    },
    "bn": {
        "show": "বাংলায় দেখান",
        "delete": "আমার তথ্য মুছুন",
        "confirm": "হ্যাঁ, আমি নিশ্চিত",
        "cancel": "না, মুছবেন না",
        "close": "বন্ধ করুন"
    },
    "hi": {
        "show": "हिंदी में दिखाएँ",
        "delete": "मेरा डेटा हटाएँ",
        "confirm": "हाँ, मैं निश्चित हूँ",
        "cancel": "नहीं, हटाएँ नहीं",
        "close": "बंद करें"
    },
    "ja": {
        "show": "日本語で表示",
        "delete": "私のデータを削除",
        "confirm": "はい、確信しています",
        "cancel": "いいえ、削除しないでください",
        "close": "閉じる"
    },
    "zh": {
        "show": "用中文显示",
        "delete": "删除我的数据",
        "confirm": "是的，我确定",
        "cancel": "不，不要删除",
        "close": "关闭"
    },
    "te": {
        "show": "తెలుగులో చూపించు",
        "delete": "నా డేటాను తొలగించు",
        "confirm": "అవును, నేను ఖచ్చితంగా ఉన్నాను",
        "cancel": "లేదు, తొలగించవద్దు",
        "close": "మూసివేయి"
    },
    "ur": {
        "show": "اردو میں دکھائیں",
        "delete": "میرا ڈیٹا حذف کریں",
        "confirm": "ہاں، میں یقین رکھتا ہوں",
        "cancel": "نہیں، حذف نہ کریں",
        "close": "بند کریں"
    }
}

MESSAGES = {
    "en": {
        "confirm_delete": "Are you sure?",
        "data_will_be_deleted": "Your data will be deleted shortly.",
        "data_deleted": "Hey there, your data has been deleted.",
        "admin_notify": "User has been notified about data deletion.",
        "admin_fail": "Failed to notify user: {error}"
    },
    "bn": {
        "confirm_delete": "আপনি কি নিশ্চিত?",
        "data_will_be_deleted": "আপনার তথ্য শীঘ্রই মুছে ফেলা হবে।",
        "data_deleted": "হ্যালো, আপনার তথ্য মুছে ফেলা হয়েছে।",
        "admin_notify": "ব্যবহারকারীকে তথ্য মুছে ফেলার বিষয়ে অবহিত করা হয়েছে।",
        "admin_fail": "ব্যবহারকারীকে অবহিত করতে ব্যর্থ: {error}"
    },
    "hi": {
        "confirm_delete": "क्या आप निश्चित हैं?",
        "data_will_be_deleted": "आपका डेटा जल्द ही हटा दिया जाएगा।",
        "data_deleted": "हाय, आपका डेटा हटा दिया गया है।",
        "admin_notify": "उपयोगकर्ता को डेटा हटाने के बारे में सूचित किया गया है।",
        "admin_fail": "उपयोगकर्ता को सूचित करने में विफल: {error}"
    },
    "ja": {
        "confirm_delete": "本当によろしいですか？",
        "data_will_be_deleted": "あなたのデータはまもなく削除されます。",
        "data_deleted": "こんにちは、あなたのデータは削除されました。",
        "admin_notify": "ユーザーにデータ削除について通知しました。",
        "admin_fail": "ユーザーに通知できませんでした: {error}"
    },
    "zh": {
        "confirm_delete": "你确定吗？",
        "data_will_be_deleted": "您的数据将很快被删除。",
        "data_deleted": "您好，您的数据已被删除。",
        "admin_notify": "已通知用户数据已删除。",
        "admin_fail": "无法通知用户: {error}"
    },
    "te": {
        "confirm_delete": "మీరు ఖచ్చితంగా ఉన్నారా?",
        "data_will_be_deleted": "మీ డేటా త్వరలో తొలగించబడుతుంది.",
        "data_deleted": "హాయ్, మీ డేటా తొలగించబడింది.",
        "admin_notify": "యూజర్‌కు డేటా తొలగింపు గురించి తెలియజేయబడింది.",
        "admin_fail": "యూజర్‌కు తెలియజేయడంలో విఫలమైంది: {error}"
    },
    "ur": {
        "confirm_delete": "کیا آپ یقینی ہیں؟",
        "data_will_be_deleted": "آپ کا ڈیٹا جلد ہی حذف کر دیا جائے گا۔",
        "data_deleted": "ہیلو، آپ کا ڈیٹا حذف کر دیا گیا ہے۔",
        "admin_notify": "صارف کو ڈیٹا حذف کرنے کے بارے میں مطلع کر دیا گیا ہے۔",
        "admin_fail": "صارف کو مطلع کرنے میں ناکام: {error}"
    }
}

def get_language_buttons():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(BUTTON_LABELS["en"]["show"], callback_data="lang_en"),
        InlineKeyboardButton(BUTTON_LABELS["bn"]["show"], callback_data="lang_bn"),
        InlineKeyboardButton(BUTTON_LABELS["hi"]["show"], callback_data="lang_hi")
    )
    markup.row(
        InlineKeyboardButton(BUTTON_LABELS["ja"]["show"], callback_data="lang_ja"),
        InlineKeyboardButton(BUTTON_LABELS["zh"]["show"], callback_data="lang_zh"),
        InlineKeyboardButton(BUTTON_LABELS["te"]["show"], callback_data="lang_te"),
        InlineKeyboardButton(BUTTON_LABELS["ur"]["show"], callback_data="lang_ur")
    )
    markup.row(
        InlineKeyboardButton(BUTTON_LABELS["en"]["delete"], callback_data="delete_request"),
        InlineKeyboardButton("Download my data", callback_data="download_data")
    )
    return markup

@bot.message_handler(regexp=r'^[\/!](privacy)(?:\s|$|@)')
def handle_privacy(message):
    if message.chat.type != "private":
        return

    bot.send_message(
        message.chat.id,
        PRIVACY_MESSAGES["en"],
        reply_markup=get_language_buttons(),
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def handle_language(call):
    lang = call.data.split("_")[1]
    bot.edit_message_text(
        PRIVACY_MESSAGES[lang],
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=get_language_buttons(),
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "delete_request")
def delete_request(call):
    lang = "en"
    confirm_markup = InlineKeyboardMarkup()
    confirm_markup.row(
        InlineKeyboardButton(BUTTON_LABELS[lang]["confirm"], callback_data="delete_confirm"),
        InlineKeyboardButton(BUTTON_LABELS[lang]["cancel"], callback_data="cancel_delete")
    )
    bot.edit_message_text(
        MESSAGES[lang]["confirm_delete"],
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=confirm_markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "cancel_delete")
def cancel_delete(call):
    bot.edit_message_text(
        PRIVACY_MESSAGES["en"],
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=get_language_buttons(),
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "delete_confirm")
def confirm_delete(call):
    lang = "en"
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(BUTTON_LABELS[lang]["close"], callback_data="close"))
    bot.edit_message_text(
        MESSAGES[lang]["data_will_be_deleted"],
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )

    user = call.from_user
    text = f"*User:*\nFirst: `{user.first_name}`\nLast: `{user.last_name or 'N/A'}`\nUsername: `@{user.username}`\nRequested to delete their data."
    admin_btn = InlineKeyboardMarkup()
    admin_btn.row(InlineKeyboardButton("Deleted", callback_data=f"deleted_user_{user.id}"))

    bot.send_message(ADMIN_ID, text, parse_mode="Markdown", reply_markup=admin_btn)

@bot.callback_query_handler(func=lambda call: call.data.startswith("deleted_user_"))
def admin_confirm(call):
    user_id = int(call.data.split("_")[-1])
    lang = "en"
    try:
        bot.send_message(user_id, MESSAGES[lang]["data_deleted"])
        bot.edit_message_text(
            MESSAGES[lang]["admin_notify"],
            call.message.chat.id,
            call.message.message_id
        )
    except Exception as e:
        bot.send_message(ADMIN_ID, MESSAGES[lang]["admin_fail"].format(error=e))

@bot.callback_query_handler(func=lambda call: call.data == "close")
def close_btn(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "download_data")
def download_data(call):
    user = call.from_user
    file_path = f"user_data/user_{user.first_name}/data_1.txt"

    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as file:
                bot.send_document(
                    call.message.chat.id,
                    file,
                    caption="Here is your data file.",
                    reply_to_message_id=call.message.message_id
                )
        except Exception as e:
            bot.reply_to(call.message, f"Error sending file: {str(e)}")
    else:
        bot.reply_to(call.message, "No data file found for your account.")