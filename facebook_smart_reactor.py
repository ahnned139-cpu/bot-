import requests
import random
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from datetime import datetime

# ==============================
# إعدادات الأمير المتمرد
# ==============================
FB_ACCESS_TOKEN = "EAANwTeOIlqABQ7VLMuhZBLl9V9ytW50BZBtHAYft0OVHsfoTllmRt75tDzXhxQLm6gZBG99r4WOHUYV2m2ZAfaj2tQPE4BSKNifDUiuNl7SjIDqOLkWKsdxRnbIeSMphsZCQOaiuzPiSdDWOd1bxzhwVZCHbjTxHvmTBAbIVM5OD3y8ZCniqUtmWNundPjS"
TG_BOT_TOKEN = "8635455994:AAHSYuIyoYAcDUpKZE4rxhpIMqbGuQXuJYo"
BASE_URL = "https://graph.facebook.com/v17.0"

REACTIONS = ["LIKE", "LOVE", "HAHA", "SAD", "ANGRY", "CARE"]
DAILY_LIMIT = 20

bot_running = False
reacted_today = {}
friends_list = []

# ==============================
# دوال الفيسبوك
# ==============================
def get_friends():
    url = f"{BASE_URL}/me/friends?access_token={FB_ACCESS_TOKEN}"
    res = requests.get(url).json()
    friends = res.get("data", [])
    return [f['id'] for f in friends]

def get_friend_posts(friend_id):
    url = f"{BASE_URL}/{friend_id}/posts?access_token={FB_ACCESS_TOKEN}"
    res = requests.get(url).json()
    return res.get("data", [])

def choose_reaction(text):
    text = (text or "").lower()
    if any(word in text for word in ["نجاح","فرحة","مبروك","تهنئة"]):
        return "LOVE"
    elif any(word in text for word in ["ضحك","نكت","مضحك"]):
        return "HAHA"
    elif any(word in text for word in ["حزين","حزن","موت","فقد"]):
        return "SAD"
    elif any(word in text for word in ["غضب","تعب","زعل"]):
        return "ANGRY"
    elif any(word in text for word in ["دعم","تشجيع","رعاية"]):
        return "CARE"
    else:
        return "LIKE"

def react_to_post(post_id, reaction):
    url = f"{BASE_URL}/{post_id}/reactions?type={reaction}&access_token={FB_ACCESS_TOKEN}"
    res = requests.post(url)
    if res.status_code == 200:
        print(f"تم وضع {reaction} على المنشور {post_id}")
    else:
        print(f"فشل التفاعل على المنشور {post_id}: {res.text}")

# ==============================
# دوال تشغيل البوت
# ==============================
def run_facebook_bot(context: CallbackContext):
    global reacted_today, friends_list
    if not bot_running:
        return

    if not friends_list:
        friends_list = get_friends()
        print(f"عدد الأصدقاء: {len(friends_list)}")

    friends_to_react = random.sample(friends_list, min(10, len(friends_list)))
    print(f"\nالساعة {datetime.now().strftime('%H:%M')} - التفاعل مع الأصدقاء: {friends_to_react}")

    for friend_id in friends_to_react:
        if friend_id not in reacted_today:
            reacted_today[friend_id] = 0

        posts = get_friend_posts(friend_id)
        for post in posts:
            if reacted_today[friend_id] >= DAILY_LIMIT:
                break
            text = post.get("message", "")
            reaction = choose_reaction(text)
            react_to_post(post["id"], reaction)
            reacted_today[friend_id] += 1
            time.sleep(180)  # كل 3 دقائق

# ==============================
# أوامر تلجرام
# ==============================
def start(update: Update, context: CallbackContext):
    global bot_running
    bot_running = True
    update.message.reply_text("البوت شغال الآن ✅")
    run_facebook_bot(context)

def stop(update: Update, context: CallbackContext):
    global bot_running
    bot_running = False
    update.message.reply_text("تم إيقاف البوت مؤقتًا ⏸️")

def status(update: Update, context: CallbackContext):
    update.message.reply_text(f"التفاعلات اليوم: {reacted_today}")

# ==============================
# تشغيل بوت تلجرام
# ==============================
updater = Updater(TG_BOT_TOKEN)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("stop", stop))
dp.add_handler(CommandHandler("status", status))

updater.start_polling()
updater.idle()