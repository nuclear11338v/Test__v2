from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_hindi_help():
    """Generate main help menu content"""
    help_menu = """
    <b>📚 Hᴇʟᴘ Mᴇɴᴜ</b>
    HELP HINDI
    │   └ /start - Sтᴀʀт Tнᴇ Boт
    └──
    """
    
    buttons = [
        ("˹ Rᴜʟᴇs ˼", "hindi_rules"),
        ("˹ Locκs ˼", "hindi_lock"),
        ("˹ Dɪsᴀʙʟɪɴɢ ˼", "hindi_disable"),
        ("˹ Fᴏʀᴍᴀᴛ ˼", "hindi_format"),
        ("˹ Rᴇᴘoʀтs ˼", "hindi_reports"),
        ("˹ Bᴀɴs ˼", "hindi_ban"),
        ("˹ Wᴀʀɴs ˼", "hindi_warn"),
        ("˹ Muтᴇs ˼", "hindi_mute"),
        ("˹ Kιcκs ˼", "hindi_kick"),
        ("˹ Noтᴇs ˼", "hindi_note"),
        ("˹ Fʟooᴅs ˼", "hindi_flood"),
        ("˹ cнᴀттιɴԍ ˼", "hindi_chat"),
        ("˹ Bʟocκʟιsтs ˼", "mhindi_blocklist"),
        ("˹ Fιʟтᴇʀs ˼", "hindi_filter"),
        ("˹ Cʟᴇᴀɴco... ˼", "hindi_cleancommand"),
        ("˹ Bᴀsιc ˼", "hindi_basic"),
        ("˹ Auтo Aᴘᴘʀovᴇ ˼", "hindi_app"),
        ("˹ Aᴅмιɴ ˼", "hindi_botadmin"),
        ("˹ vc Hᴇʟᴘ ˼", "hindi_voicechat"),
        ("˹ ᴇxтʀᴀ ғᴇᴀтuʀᴇ ˼", "hindi_extra"),
        ("˹ Doɴᴀтᴇ ˼", "hindi_developersuppert"),
        ("➤ ˹ Suᴘᴘoʀт ˼", "hindi_groupsupport"),
        ("✿ ˹ 𝗰ʟ𝗼𝘀ᴇ ✘ ˼", "hindi_close")
    ]
    
    markup = types.InlineKeyboardMarkup()

    for i in range(0, len(buttons), 3):
        row = [types.InlineKeyboardButton(text, callback_data=data) 
               for text, data in buttons[i:i+3]]
        markup.add(*row)
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('hindi_'))
def handle_help_callback(call):
    try:
        if call.data == 'hindi_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'hindi_back':
            text, markup = create_hindi_help()
            bot.edit_message_text(
                text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=markup
            )
            return

        help_sections = {
            'hindi_rules': """
           📜 नियम
            ├── 🔸उपयोग
            │   │
            │   ├ /rules ➠ ग्रुप के नियम देखें।
            │   ├ /setrules टेक्स्ट ➠ ग्रुप के नियम सेट या अपडेट करें (केवल प्रशासक)
            │   ├ /privaterules [on | off] ➠
            │   └ :)
            │   └ DEV :- @PB_X01
            └──""",

            'hindi_disable': """
            अक्षम
            ├── 🔸उपयोग
            │   │
            │   ├ /disable [commad] ➠ सभी कमांड्स को अक्षम करें eg ( /disable help)
            │   ├ /disabledel [on | off]] ➠ कमांड्स को हटाएं, उदाहरण - /help, बॉट: कमांड को हटाएं
            │   └ DEV :- @PB_X01
            └──""",

            'hindi_app': """
            स्वचालित अनुमोदन
            ├── 🔸/approval on
            │   │
            │   └ स्वचालित रूप से उपयोगकर्ताओं के शामिल होने के अनुरोध स्वीकार करें
            │
            ├── 🔸/approval off
            │   │
            │   ├ स्वचालित शामिल होने के अनुरोध को बंद करें
            │   │
            │   └ DEV :- @PB_X01
            └──""",
            
            'hindi_chat': """
            चैटिंग
            ├── 🔸/chat चालू
            │   │
            │   └ उपयोगकर्ता चैटिंग सुविधा चालू करें
            │
            ├── 🔸/chat बंद
            │   │
            │   ├ उपयोगकर्ता चैटिंग सुविधा बंद करें
            │   │
            │   └ DEV :- @PB_X01
            └──""",
            
            'hindi_extra': """
            
            जल्द ही आ रहा है
            ├── 🔸/dell on/users/admin
            │   │
            │   └ स्वचालित रूप से संदेश हटाएं
            │
            ├── 🔸/dell off
            │   │
            │   └ स्वचालित रूप से संदेश हटाना बंद करें
            │
            ├── 🔸/link on
            │   │
            │   └ स्वचालित रूप से लिंक हटाएं। संदेश, फोटो में
            │
            ├── 🔸/link off
            │   │
            │   └ स्वचालित रूप से लिंक हटाना बंद करें
            │
            ├── 🔸/del [ reply ]
            │   │
            │   └ एक संदेश हटाएं
            │
            ├── 🔸/abuse [ word ]
            │   │
            │   └ /abuse कुत्ता - अपने ग्रुप में अपशब्द सेट करें
            │
            ├── 🔸/abuse on
            │   │
            │   └ अपशब्द संदेश हटाएं + उपयोगकर्ता को म्यूट करें
            │
            ├── 🔸/abuse off
            │   │
            │   └ अपशब्द संदेश हटाना और उपयोगकर्ता म्यूट करना बंद करें
            │
            ├── 🔸/feedback
            │   │
            │   ├ /feedback या फोटो चुनें और /feedback टाइप करें ताकि बॉट डेवलपर को फीडबैक भेजा जा सके
            │   │
            │   └ DEV :- @PB_X01
            ### COMMING SOON ###
            └──""",
            
            'hindi_format': """
            प्रारूपण  
            ├── 🔸मार्कडाउन प्रारूपण  
            │   ├ टेलीग्राम संदेशों, कैप्शन और बॉट प्रतिक्रियाओं में टेक्स्ट स्टाइलिंग के लिए मार्कडाउन का समर्थन करता है।  
            │   ├ समर्थित शैलियाँ:  
            │   │   ├ मोटा: *टेक्स्ट* का उपयोग करें → मोटा टेक्स्ट  
            │   │   ├ तिरछा: _टेक्स्ट_ का उपयोग करें → तिरछा टेक्स्ट  
            │   │   ├ मोनोस्पेस: `टेक्स्ट` का उपयोग करें → मोनोस्पेस टेक्स्ट  
            │   │   ├ स्ट्राइकथ्रू: ~टेक्स्ट~ का उपयोग करें → स्ट्राइकथ्रू टेक्स्ट  
            │   │   ├ लिंक: [टेक्स्ट](URL) का उपयोग करें → लिंक  
            │   ├ नोट्स:  
            │   │   ├ मार्कर और टेक्स्ट के बीच कोई स्थान नहीं (उदाहरण के लिए, * टेक्स्ट* काम नहीं करेगा)।  
            │   │   ├ शैलियों को नेस्ट करके जोड़ा जा सकता है (उदाहरण के लिए, *मोटा _तिरछा_* → मोटा तिरछा)।  
            │   │   └ कुछ क्लाइंट सभी शैलियों का समर्थन नहीं कर सकते (संगति के लिए MarkdownV2 का उपयोग करें)।  
            │   └ उदाहरण: *मोटा* _तिरछा_ [यहाँ क्लिक करें](https://telegram.org) → मोटा तिरछा यहाँ क्लिक करें  
            ├── 🔸बटन प्रारूपण  
            │   └ [Google](buttonurl://google.com) → Google से लिंक करने वाला एक इनलाइन बटन बनाता है
            ├── 🔸 Bᴏᴛ Iꜱ Cᴜʀʀᴇɴᴛʟʏ Rᴜɴɴɪɴɢ Bᴇᴛᴀ Vᴇʀꜱɪᴏɴ
            │   ├ V: 0.2
            │   └ ˹ DƐѴ ˼ :- @PB_X01 :)
            └──""",
            
            'hindi_flood': """
            
            ├── 🔸कमांड्स:
            │   │
            │   ├ /setflood [सीमा/बंद] ➠ संदेश सीमा सेट करें (5)
            │   ├ /setfloodtimer [अवधि] [सीमा]. उदाहरण /setfloodtimer 10 20s
            │   ├ /floodmode [कार्रवाई] ➠ सजा सेट करें (बैन/म्यूट)
            │   └ /clearflood [चालू/बंद] ➠ फ्लड संदेशों को स्वचालित रूप से हटाएं
            │
            ├── 🔸मैकेनिक्स:
            │   │
            │   ├ → प्रति उपयोगकर्ता संदेशों को ट्रैक करता है
            │   ├ → सीमा पर ट्रिगर होता है: 5 संदेश/10 सेकंड
            │   ├ → कार्रवाइयाँ: म्यूट/बैन/किक/अस्थायी बैन/अस्थायी म्यूट
            │   │
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",
            
            'hindi_note': """
            
            ├── 🔸कमांड्स
            │   │
            │   ├ /save [नाम] [टेक्स्ट] - नोट बनाएं
            │   ├ /get [नाम] / #नोटनाम - नोट प्राप्त करें
            │   ├ /clear [नाम] - नोट हटाएं
            │   ├ /privatenotes [चालू/बंद] - पीएम डिलीवरी टॉगल करें
            │
            ├── 🔸उन्नत सुविधाएँ
            │   │
            │   ├ → हैशटैग ट्रिगर: #नोटनाम
            │   ├ → मीडिया नोट्स का समर्थन करता है (फाइल का जवाब दें)
            │   ├ → नोट्स के लिए बटन
            │   │
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",
            
            'hindi_blocklist': """
            
            ├── 🔸 कमांड्स
            │   │
            │   ├ /addblocklist [शब्द] [कारण] - ट्रिगर जोड़ें
            │   ├ /rmblocklist [शब्द] - ट्रिगर हटाएं
            │   ├ /blocklistmode [कार्रवाई] - सजा सेट करें
            │   └ /blocklist - वर्तमान ट्रिगर्स दिखाएं
            │
            ├── 🔸 कार्रवाइयाँ
            │   │
            │   ├ हटाएं|म्यूट|बैन|किक|चेतावनी
            │   ├ रेगेक्स प्रारूप: * = वाइल्डकार्ड, ? = एकल वर्ण
            │   │
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",
            
            'hindi_filter': """
            
            ├── 🔸 कमांड्स  
            │   │  
            │   ├ /filter [ट्रिगर] [प्रतिक्रिया] ➠ स्वचालित-जवाब जोड़ें  
            │   ├ /filters ➠ सक्रिय फ़िल्टर सूचीबद्ध करें  
            │   ├ /stop [ट्रिगर] ➠ फ़िल्टर हटाएं  
            │   └ /stopall ➠ सभी फ़िल्टर साफ़ करें  
            │  
            ├── 🔸 सुविधाएँ:  
            │   │  
            │   ├ → रेगेक्स समर्थन: */filter hello.* "हाय!"  
            │   ├ → बटन समर्थन: [बटन](buttonurl://https://लिंक)  
            │   ├ → केस-असंवेदनशील मिलान
            │   │
            │   └ REPORT :- @PB_X01
            └──""",

            'hindi_lock': """
            
            ├── 🔸 कमांड्स:
            │   │
            │   ├ /lock [प्रकार] ➠ अनुमतियों को प्रतिबंधित करें
            │   ├ /unlock [प्रकार] ➠ प्रतिबंध हटाएं
            │   ├ प्रकार:
            │   └ सभी, मीडिया, स्टिकर, इमोजी, वीडियो, आदि
            │
            ├── 🔸 कार्यान्वयन:
            │   │
            │   ├ चैट अनुमतियों को संशोधित करता है
            │   ├ पहले प्रशासक स्थिति की पुष्टि करता है
            │   │
            │   ├ /lock all/media/sticker/emoji/video
            │   ├ /unlock all/media/sticker/emoji/video
            │   │
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",
            
            'hindi_basic': """
            
            ├── 🔸 कमांड्स
            │   │
            │   ├ /start ➠ बॉट शुरू करें
            │   ├ /help ➠ यह संदेश दिखाएं
            │   ├ /id, /info, /me ➠ उपयोगकर्ता का जवाब दें या सीधे भेजें - उपयोगकर्ता आईडी प्राप्त करें
            │   └ /ping - बॉट सिस्टम की जाँच करें
            │
            ├── 🔸
            │   │
            │   ├ ### COMMING SOON ###
            │   │
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",
            
            'hindi_botadmin': """
            
            ├── 🔸 कमांड्स
            │   │
            │   ├ /promote [reply/user_id] [शीर्षक] [अवधि]. उदाहरण - /promote [user_id/reply] | वैकल्पिक [शीर्षक] [अवधि]
            │   ├ /demote [user_id/reply]
            │   ├ /adminlist
            │   ├ /adminerror
            │   └ /anonadmin
            │
            ├── 🔸THANKS FOR USING ME :)
            │   │
            │   └ REPORT :- @PB_X01
            └──""",
            
            'hindi_cleancommand': """
            
            ├── 🔸 कमांड्स
            │   │
            │   ├ /cleancommand [प्रकार] - स्वचालित रूप से कमांड्स हटाएं
            │   ├ /keepcommand [प्रकार] - कमांड्स को व्हाइटलिस्ट करें
            │   ├ /cleanstatus - सेटिंग्स दिखाएं
            │   └ /cleanhelp - उपयोग दिखाएं
            │
            ├── 🔸 प्रकार:
            │   │
            │   ├ सभी|प्रशासक|उपयोगकर्ता|अन्य
            │   ├ उदाहरण: /cleancommand admin/user
            │   ├ निर्दिष्ट कमांड प्रकारों को तुरंत हटाता है
            │   │ ### UNDER MAINTENANCE
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",

            'hindi_developersuppert': """
            
            ├── 🔸𝗖𝗢𝗡𝗧𝗔𝗖𝗧
            │  │
            │  ├── 🔸@PB_X01
            │  ├── 🔸@assistant_off_OG
            └──""",

            'hindi_voicechat': """
            
            ├── 🔸𝗔𝘂𝘁𝗼𝗺𝗮𝘁𝗲𝗱 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀 :
            │   │
            │   ├ → vc sтᴀʀт/ᴇɴᴅ ᴅᴇтᴇcтιoɴ
            │   ├ → cusтoм נoιɴ ʙuттoɴs
            │   └ → sтʏʟᴇᴅ ᴀɴɴouɴcᴇмᴇɴтs
            │   
            ├── 🔸˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",

            'hindi_groupsupport': """
            
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
            
            'hindi_reports': """
            रिपोर्ट
            ├── 🔸 कमांड्स:
            │   │
            │   ├ /report [reply] - प्रशासकों को सचेत करें
            │   └ @admin - वैकल्पिक ट्रिगर
            │
            ├── 🔸 कार्यक्षमता:
            │   │
            │   ├ → ग्रुप सेटिंग: /reports [चालू/बंद]
            │   ├ → प्रशासकों के लिए उल्लेख लिंक बनाता है
            │   ├ → प्रशासकों को अन्य प्रशासकों की रिपोर्टिंग से रोकता है
            │   │
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",

            'hindi_ban': """
            𝗕𝗔𝗡 𝗛𝗘𝗟𝗣

            ├── 🔸 कमांड्स:
            │   │
            │   ├ /ban [reply/user] - स्थायी प्रतिबंध
            │   ├ /dban [reply] - संदेश हटाएं + प्रतिबंध
            │   ├ /sban [reply/user] [duration] - चुपके से प्रतिबंध
            │   ├ /tban [reply/user] [duration] - अस्थायी प्रतिबंध (1घं/7दिन)
            │   ├ /rban [user_id/reply] - बॉट यादृच्छिक रूप से उपयोगकर्ता को यादृच्छिक अवधि के लिए प्रतिबंधित करता है
            │   └ /unban [reply/user] - प्रतिबंध हटाएं
            │
            ├── 🔸 उदाहरण:
            │   │
            │   ├ → अवधि का उपयोग करें: 30मि, 24घं, 7दिन
            │   ├ → sban प्रशासक के कमांड को हटाता है
            │   ├ /ban 1234/reply
            │   │
            │   └ /tban 1234/reply 1स/1घं/1दिन/1सप्ताह/1महीना/1वर्ष
            │
            ├── 🔸 अनुमतियाँ:
            │   │
            │   ├ बॉट को चाहिए: "उपयोगकर्ताओं को प्रतिबंधित करें" अधिकार
            │   ├ उपयोगकर्ता को चाहिए: प्रशासक विशेषाधिकार
            │   │
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",

            'hindi_warn': """
            चेतावनी मदद
            ├── 🔸चेतावनी
            │   │
            │   ├ /warn [reply/user] [reason] - चेतावनी जोड़ें
            │   ├ /dwarn [reply] - संदेश हटाएं + चेतावनी दें
            │   ├ resetwarn [reply/user] - चेतावनियाँ साफ़ करें
            │   └ /warns - चेतावनियाँ जाँचें
            │
            ├── 🔸कॉन्फ़िगरेशन:
            │   │
            │   ├ → /settwarning [limit] - अधिकतम चेतावनियाँ सेट करें (3)
            │   ├ → सीमा पर स्वचालित म्यूट
            │   ├ → रीस्टार्ट के बाद भी स्थायी
            │   └ रिपोर्ट: @PB_X01
            │
            ├── 🔸उदाहरण:
            │   │
            │   ├── /warn 1234/reply टेस्ट / बिना कारण के
            │   │   └ [ /dwarn | /swarn | के लिए भी वही
            │   ├ /settwarning 3 (या कोई भी संख्या)
            │   ├ /resetwarn 1234/reply
            │   ├ /warns 1234/reply
            │   ├ बॉट बीटा संस्करण में है, इसलिए और अपडेट्स की प्रतीक्षा करें
            │   │
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",
            
            'hindi_button': """
            
            ├── 🔸𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎 :
            │   │
            │   ├ INLINEBUTTON - [button name](buttonurl://https://link)
            │   ├ hidden link button - [click here](https://link)
            │   ├ Support also multiple buttons eg " [button name](buttonurl://https://link)  [button name](buttonurl://https://link)"
            │   └ same for hidden link button
            │   │
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",

            'hindi_document': """
            
            ├── 🔸 DOCUMENTATION :
            │   │
            │   ├ WEB -
            │   ├ ASK ANYTHING - 
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",

            'hindi_mute': """
            म्यूट मदद
            ├── 🔸 कमांड्स:
            │   │
            │   ├ /mute [reply/user] [reason] - उपयोगकर्ता को म्यूट करें, वैकल्पिक कारण के साथ
            │   ├ /unmute [user] - उपयोगकर्ता का म्यूट हटाएं
            │   ├ /smute [reply/user] [reason] - चुपके से म्यूट (कमांड हटाता है)
            │   ├ /tmute [reply/user] [time] [reason] - अस्थायी म्यूट (1घं, 30मि, 7दिन)
            │   ├ /rmute [reply/user] - उपयोगकर्ता को यादृच्छिक अवधि के लिए म्यूट करें
            │   └ /unmute [reply/user] - प्रतिबंध हटाएं
            │
            ├── 🔸 उदाहरण:
            │   │
            │   ├ → लक्ष्य संदेश का जवाब दें या उपयोगकर्ता का उल्लेख करें
            │   ├ → समय प्रारूप: संख्या + इकाई (स/मि/घं/दिन)
            │   ├ /tmute 1234/reply 1स/1घं/1दिन/1सप्ताह/1महीना/1वर्ष
            │   └ /mute 1234/reply
            │
            ├── 🔸 अनुमतियाँ:
            │   │
            │   ├ बॉट को चाहिए: "सदस्यों को प्रतिबंधित करें" अधिकार
            │   ├ उपयोगकर्ता को चाहिए: प्रशासक विशेषाधिकार
            │   │
            │   └ ˹ ᖇEᑭOᖇT ˼ :- @PB_X01
            └──""",

            'hindi_kick': """
            किक मदद
            ├── 🔸 कमांड्स:
            │   │
            │   ├ /skick, /tkick, /dkick के समान
            │   ├ /kick [user] - उपयोगकर्ता को हटाएं
            │   └ /kickme - ग्रुप छोड़ें
            │
            ├── 🔸 उदाहरण:
            │   │
            │   ├ /kick @troublemaker
            │   └ /skick 123456789
            └──""",
        }

        if call.data in help_sections:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("✘ ˹ ʙᴀ𝗰𝗸 ˼", callback_data="hindi_back"))
            markup.add(
                types.InlineKeyboardButton("formatting", callback_data="hindi_format"),
                types.InlineKeyboardButton("button", callback_data="hindi_button"),
                types.InlineKeyboardButton("document", callback_data="hindi_document")
            )
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=format_message(help_sections[call.data]),
                parse_mode='HTML',
                reply_markup=markup
            )
        else:
            bot.answer_callback_query(call.id, "⏳ Section under development!", show_alert=False)

    except Exception as e:
        logger.error(f"Callback error: {str(e)}\n{traceback.format_exc()}")
        try:
            bot.answer_callback_query(call.id, "⚠️ Temporary issue. Try again later!")
        except Exception as e:
            logger.error(f"Failed to answer callback: {str(e)}")

