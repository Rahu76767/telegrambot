"""
╔═══════════════════════════════════════════════════════════════╗
║   💕 REAL DATING BOT v5.0 — FULLY FIXED & USER FRIENDLY     ║
╚═══════════════════════════════════════════════════════════════╝
"""

import telebot
from telebot import types, apihelper
apihelper.ENABLE_MIDDLEWARE = True

from datetime import datetime, timedelta
import json, os, random, threading, time, qrcode
from io import BytesIO
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN       = os.getenv("TELEGRAM_TOKEN", "8511522063:AAGGf9sZ8GAN0nK3liAj3_oNEzGmuEbuxpM").strip()
ADMIN_ID    = 1405765652
ADMIN_IDS   = [1405765652, 1502832674]
ADMIN_USERNAME = "@Rober_rev"
UPI_ID      = "rahulramapuri76@oksbi"
ADMIN_FILE  = os.path.join(os.path.dirname(__file__), "admins.json")
MAX_THREADS = 8
MATCH_EXPIRY_HOURS    = 24
BOOST_DURATION_MINUTES = 30
MAX_PHOTOS  = 2
SEED_ID_PREFIX = 900000000

def load_admins():
    global ADMIN_IDS
    try:
        if os.path.exists(ADMIN_FILE):
            with open(ADMIN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    ADMIN_IDS = [int(x) for x in data]
    except Exception as e:
        logger.error(f"Failed to load admins: {e}")

def save_admins():
    try:
        with open(ADMIN_FILE, "w", encoding="utf-8") as f:
            json.dump(ADMIN_IDS, f)
    except Exception as e:
        logger.error(f"Failed to save admins: {e}")

load_admins()

def is_admin(user_id):
    try:
        return int(user_id) in ADMIN_IDS
    except Exception:
        return False

LANGUAGES = {
    "en": {
        "name": "🇬🇧 English", "welcome": "💕 Welcome to Real Dating!",
        "choose_plan": "Choose your plan:", "age_question": "What's your age?",
        "city_question": "Which city are you from?", "gender_question": "What's your gender?",
        "find_match": "Find Match", "add_photos": "Add Photos", "messages": "Messages",
        "settings": "Settings", "match_found": "New Match Found!", "no_matches": "No matches yet!",
        "profile": "My Profile", "leaderboard": "Leaderboard", "boost": "Boost Profile",
        "super_like": "Super Like",
    },
    "hi": {
        "name": "🇮🇳 हिंदी", "welcome": "💕 रियल डेटिंग में आपका स्वागत है!",
        "choose_plan": "अपनी योजना चुनें:", "age_question": "आपकी उम्र क्या है?",
        "city_question": "आप किस शहर से हैं?", "gender_question": "आप कौन हैं?",
        "find_match": "मैच खोजें", "add_photos": "फोटो जोड़ें", "messages": "संदेश",
        "settings": "सेटिंग्स", "match_found": "नया मैच मिला!", "no_matches": "अभी कोई मैच नहीं!",
        "profile": "मेरी प्रोफ़ाइल", "leaderboard": "लीडरबोर्ड",
        "boost": "प्रोफ़ाइल बूस्ट", "super_like": "सुपर लाइक",
    },
    "mr": {
        "name": "🇮🇳 मराठी", "welcome": "💕 रिअल डेटिंगमध्ये आपले स्वागत आहे!",
        "choose_plan": "आपली योजना निवडा:", "age_question": "तुमचे वय किती आहे?",
        "city_question": "तुम्ही कोणत्या शहरात आहात?", "gender_question": "तुमचे लिंग काय आहे?",
        "find_match": "जोडी शोधा", "add_photos": "फोटो जोडा", "messages": "संदेश",
        "settings": "सेटिंग्ज", "match_found": "नवीन जोडी सापडली!", "no_matches": "अजून कोणतीही जोडी नाही!",
        "profile": "माझी प्रोफाइल", "leaderboard": "लीडरबोर्ड",
        "boost": "प्रोफाइल बूस्ट", "super_like": "सुपर लाइक",
    }
}
DEFAULT_LANG = "en"

PLANS = {
    "🆓 Free":     {"price":0,   "duration_days":7,  "matches_per_day":3,   "super_likes_per_day":1,
                    "can_boost":False,"see_who_liked":False,"verified_badge":False,"description":"Basic access, 3 matches/day"},
    "💛 Silver":   {"price":99,  "duration_days":30, "matches_per_day":15,  "super_likes_per_day":3,
                    "can_boost":False,"see_who_liked":False,"verified_badge":False,"description":"15 matches/day, 3 super likes"},
    "💎 Gold":     {"price":199, "duration_days":30, "matches_per_day":50,  "super_likes_per_day":10,
                    "can_boost":True, "see_who_liked":True, "verified_badge":True, "description":"50 matches/day + Boost + See who liked"},
    "👑 Platinum": {"price":399, "duration_days":30, "matches_per_day":999, "super_likes_per_day":999,
                    "can_boost":True, "see_who_liked":True, "verified_badge":True, "description":"Unlimited + Priority matching"},
}

GENDERS = {
    "👨 Male":"male","👩 Female":"female",
    "🏳️‍🌈 Non-Binary":"non_binary","🤷 Prefer not to say":"undisclosed"
}
LOOKING_FOR = {
    "💑 Serious Relationship":"serious","🤝 Friendship":"friendship",
    "🎯 Casual Dating":"casual","🌍 Travel Buddy":"travel",
    "📚 Study Partner":"study","🎮 Gaming Partner":"gaming",
    "🏃 Fitness Partner":"fitness","💼 Networking":"networking"
}
HOBBIES = {
    "🎵 Music":"music","📚 Reading":"reading","🎮 Gaming":"gaming","🏋️ Fitness":"fitness",
    "🎨 Art":"art","✈️ Travelling":"travelling","🍳 Cooking":"cooking","🎬 Movies":"movies",
    "🌿 Nature":"nature","📸 Photography":"photography","💃 Dancing":"dancing",
    "🧘 Yoga":"yoga","🐾 Pets":"pets","🎭 Theatre":"theatre"
}
ICEBREAKERS = [
    "If you could travel anywhere tomorrow, where would you go? ✈️",
    "What's your favourite comfort food? 🍕",
    "Morning person or night owl? 🌅🌙",
    "What's a skill you'd love to learn? 🎯",
    "Describe your perfect weekend in 3 words 🌟",
    "What movie changed your perspective? 🎬",
    "If you had a superpower, what would it be? 🦸",
    "Tea, coffee, or neither? ☕",
    "Cats or dogs? 🐱🐶",
    "Mountains or beach? 🏔️🏖️",
    "What makes you laugh the most? 😂"
]
CITIES = [
    "Delhi","Mumbai","Bangalore","Pune","Hyderabad","Chennai","Kolkata",
    "Chandigarh","Ahmedabad","Jaipur","Lucknow","Bhopal","Indore","Nagpur",
    "Surat","Kochi","Coimbatore","Visakhapatnam","Patna","Other"
]
# ═══════════════════ BOT INIT & STATE ═══════════════════
try:
    bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=MAX_THREADS, skip_pending=True)
except Exception as e:
    logger.critical(f"Failed to init bot: {e}"); raise

user_data={}; pending_payments={}; active_chats={}; user_languages={}
pending_likes={}; boosted_users={}; daily_usage={}; analytics=defaultdict(int)
featured_photos=[]; admin_featured_temp={}; support_requests={}
_hobby_temp={}  # temp hobby selection per user during registration

# Admin wizard state — declared early so lambda guards can reference them
admin_creating_seed={}; admin_creating_lady={}
admin_pending_actions={}; admin_replyas_context={}

data_lock = threading.RLock()

# ═══════════════════ DATABASE ═══════════════════
def save_all_data():
    threading.Thread(target=_save_sync, daemon=True).start()

def _save_sync():
    with data_lock:
        try:
            for fname, obj in [
                ("dating_users.json",user_data),("pending_payments.json",pending_payments),
                ("active_chats.json",active_chats),("pending_likes.json",pending_likes),
                ("featured_photos.json",featured_photos),
            ]:
                with open(fname,"w") as f: json.dump(obj,f,indent=2)
        except Exception as e: logger.error(f"Save error: {e}")

def load_all_data():
    global user_data,pending_payments,active_chats,pending_likes,featured_photos
    for fname,var in [
        ("dating_users.json","user_data"),("pending_payments.json","pending_payments"),
        ("active_chats.json","active_chats"),("pending_likes.json","pending_likes"),
        ("featured_photos.json","featured_photos"),
    ]:
        try:
            if os.path.exists(fname):
                with open(fname,"r") as f: globals()[var]=json.load(f)
        except Exception as e: logger.error(f"Load error ({fname}): {e}")
    logger.info(f"Loaded {len(user_data)} users")

def get_user_profile(uid): return user_data.get(str(uid),{})
def update_user(uid,data):
    with data_lock:
        user_data[str(uid)]=data; save_all_data(); invalidate_match_cache(uid)

_match_cache={}; _CACHE_TTL=60
def get_cached_matches(uid,limit=10):
    now=time.time(); cached=_match_cache.get(uid)
    if cached and (now-cached[0])<_CACHE_TTL: return cached[1][:limit]
    r=get_matches(uid,limit=limit); _match_cache[uid]=(now,r); return r
def invalidate_match_cache(uid=None):
    if uid: _match_cache.pop(uid,None)
    else: _match_cache.clear()

def get_user_language(uid): return user_languages.get(uid,DEFAULT_LANG)
def set_user_language(uid,lang): user_languages[uid]=lang
def get_text(uid,key):
    lang=get_user_language(uid)
    return LANGUAGES.get(lang,LANGUAGES[DEFAULT_LANG]).get(key,LANGUAGES[DEFAULT_LANG].get(key,key))
def esc(text):
    if not text: return ""
    return str(text).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def safe_answer(cid,text="",show_alert=False):
    try: bot.answer_callback_query(cid,text=text,show_alert=show_alert)
    except Exception as e:
        if "query is too old" not in str(e) and "query ID is invalid" not in str(e):
            logger.warning(f"answer_callback: {e}")

def admin_in_wizard(uid):
    return is_admin(uid) and (
        uid in admin_creating_seed or uid in admin_creating_lady or
        uid in admin_pending_actions or uid in admin_replyas_context
    )

def get_daily_usage(uid):
    today=datetime.now().strftime("%Y-%m-%d"); u=daily_usage.get(str(uid),{})
    if u.get("date")!=today:
        u={"date":today,"matches_used":0,"super_likes_used":0}; daily_usage[str(uid)]=u
    return u
def increment_usage(uid,key):
    u=get_daily_usage(uid); u[key]=u.get(key,0)+1; daily_usage[str(uid)]=u
def get_plan_limits(uid):
    return PLANS.get(get_user_profile(uid).get("plan","🆓 Free"),PLANS["🆓 Free"])

def generate_upi_qr(amount):
    try:
        upi=f"upi://pay?pa={UPI_ID}&pn=RealDatingBot&am={amount}&tn=Premium"
        qr=qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=8,border=2)
        qr.add_data(upi); qr.make(fit=True)
        img=qr.make_image(fill_color="black",back_color="white")
        bio=BytesIO(); img.save(bio,format="PNG"); bio.seek(0); return bio
    except Exception as e: logger.error(f"QR: {e}"); return None

def get_profile_score(p):
    score=0
    for field,pts in {"age":10,"city":10,"gender":10,"looking_for":10,"hobbies":20,"bio":15,"photos":25}.items():
        if field=="hobbies":
            n=len(p.get("hobbies",[])); score+=pts if n>=3 else (pts//2 if n>=1 else 0)
        elif field=="photos": score+=min(len(p.get("photos",[]))*5,pts)
        elif p.get(field): score+=pts
    return score

# ═══════════════════ MATCHING ENGINE ═══════════════════
def get_matches(user_id,limit=10):
    p=get_user_profile(user_id)
    if not p.get("profile_complete"): return []
    ug=p.get("gender"); ul=p.get("looking_for",""); uh=set(p.get("hobbies",[]))
    ua=p.get("age",22); uc=p.get("city",""); blocked=set(p.get("blocked_users",[]))
    now=datetime.now(); matches=[]
    for uid,q in user_data.items():
        if uid==str(user_id): continue
        if not q.get("profile_complete") or not q.get("active"): continue
        if int(uid) in blocked: continue
        oa=q.get("age",22)
        if abs(ua-oa)>10: continue
        sc=0
        if ug=="male" and q.get("gender")=="female": sc+=60
        elif ug=="female" and q.get("gender")=="male": sc+=60
        elif ug==q.get("gender") and ug in ("non_binary","undisclosed"): sc+=40
        elif q.get("gender") in ("non_binary","undisclosed"): sc+=30
        else: sc+=20
        common=uh&set(q.get("hobbies",[])); sc+=len(common)*15
        if uc.lower()==q.get("city","").lower(): sc+=25
        if ul and ul==q.get("looking_for"): sc+=20
        sc+=get_profile_score(q)//10
        be=boosted_users.get(uid)
        boosted=bool(be and datetime.fromisoformat(be)>now)
        if boosted: sc+=50
        if sc>40:
            matches.append({"user_id":int(uid),"name":q.get("name","User"),
                "gender_display":q.get("gender_display",""),"age":oa,
                "city":q.get("city","Unknown"),"hobbies":list(common)[:3],
                "looking_for":q.get("looking_for_display",""),
                "bio":(q.get("bio","")[:80] if q.get("bio") else ""),
                "match_score":min(sc,99),"is_verified":q.get("verified",False),
                "is_boosted":boosted,"is_seed":q.get("is_seed",False),
                "chat_id":q.get("chat_id")})
    matches.sort(key=lambda x:(x["is_boosted"],x["match_score"]),reverse=True)
    return matches[:limit]

# ═══════════════════ MAIN MENU ═══════════════════
def send_main_menu(chat_id,uid,extra_text=""):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    markup.add(f"💞 {get_text(uid,'find_match')}",f"⭐ {get_text(uid,'super_like')}")
    markup.add(f"📸 {get_text(uid,'add_photos')}",f"💬 {get_text(uid,'messages')}")
    markup.add(f"🚀 {get_text(uid,'boost')}",f"🏆 {get_text(uid,'leaderboard')}")
    markup.add(f"👤 {get_text(uid,'profile')}",f"⚙️ {get_text(uid,'settings')}")
    p=get_user_profile(uid); score=get_profile_score(p)
    filled=int(score/10); bar="█"*filled+"░"*(10-filled)
    text=(f"{extra_text}\n\n[{bar}] {score}% | {p.get('plan','🆓 Free')}"
          if extra_text else f"[{bar}] {score}% | {p.get('plan','🆓 Free')}")
    bot.send_message(chat_id,text,reply_markup=markup,parse_mode="HTML")
# ══════════ PRIORITY: Admin character mode — registered FIRST ══════════
@bot.message_handler(func=lambda msg: (
    msg.text and is_admin(msg.from_user.id) and
    msg.from_user.id in admin_replyas_context and
    not msg.text.startswith('/') and not admin_in_wizard(msg.from_user.id)
))
def admin_character_message(message):
    aid=message.from_user.id; ctx=admin_replyas_context.get(aid)
    if not ctx: return
    sid=ctx['seed_id']; uid=ctx['user_id']; sname=ctx['seed_name']
    up=get_user_profile(uid); tc=up.get('chat_id') if up else None
    if not tc: bot.send_message(message.chat.id,f"❌ User {uid} not reachable."); return
    bot.send_message(tc, message.text.strip())   # plain text, no header
    ikm=types.InlineKeyboardMarkup()
    ikm.add(types.InlineKeyboardButton("🔴 Exit character mode",callback_data="stopreplyas_btn"))
    bot.send_message(message.chat.id,f"✅ <i>Sent as {sname}</i>",parse_mode="HTML",reply_markup=ikm)
    ck=f"chat_{min(sid,uid)}_{max(sid,uid)}"
    with data_lock:
        if ck not in active_chats:
            active_chats[ck]={"user1":min(sid,uid),"user2":max(sid,uid),"started_at":datetime.now().isoformat(),"messages":0}
        active_chats[ck]["messages"]=active_chats[ck].get("messages",0)+1; save_all_data()

@bot.callback_query_handler(func=lambda call: call.data=="stopreplyas_btn" and is_admin(call.from_user.id))
def stopreplyas_btn(call):
    safe_answer(call.id)
    ctx=admin_replyas_context.pop(call.from_user.id,None)
    if ctx: bot.send_message(call.message.chat.id,f"✅ Exited character mode for <b>{ctx['seed_name']}</b>.",parse_mode="HTML")
    else: bot.send_message(call.message.chat.id,"ℹ️ Not in character mode.")

# ═══════════════════ START & LANGUAGE ═══════════════════
@bot.message_handler(commands=['start'])
def start(message):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=2)
    for li in LANGUAGES.values(): markup.add(li['name'])
    bot.send_message(message.chat.id,"💕 <b>Real Dating Bot</b>\n\nFind your perfect match!\n\n🌐 Select your language:",reply_markup=markup,parse_mode="HTML")

@bot.message_handler(func=lambda msg: msg.text in [LANGUAGES[k]['name'] for k in LANGUAGES])
def select_language(message):
    uid=message.from_user.id
    for code,info in LANGUAGES.items():
        if info['name']==message.text: set_user_language(uid,code); break
    p=get_user_profile(uid)
    if p and p.get("profile_complete"):
        send_main_menu(message.chat.id,uid,get_text(uid,'welcome'))
    else:
        markup=types.InlineKeyboardMarkup(row_width=1)
        for pname,pi in PLANS.items():
            markup.add(types.InlineKeyboardButton(f"{pname} — ₹{pi['price']} — {pi['description']}",callback_data=f"selectplan_{pname}"))
        bot.send_message(message.chat.id,
            f"{get_text(uid,'welcome')}\n\n{get_text(uid,'choose_plan')}\n\n"
            f"💡 <b>Tip:</b> Start free, upgrade anytime!",reply_markup=markup,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("selectplan_"))
def select_plan_cb(call):
    safe_answer(call.id); uid=call.from_user.id
    pname=call.data[len("selectplan_"):]
    if pname not in PLANS: return
    _activate_plan(call.message.chat.id,uid,pname,call.from_user)

@bot.message_handler(func=lambda msg: msg.text and any(msg.text.startswith(p) for p in PLANS.keys()) and not admin_in_wizard(msg.from_user.id))
def select_plan_text(message):
    pname=message.text.split(" — ")[0]
    if pname not in PLANS: return
    _activate_plan(message.chat.id,message.from_user.id,pname,message.from_user)

def _activate_plan(chat_id,uid,pname,tg_user):
    pi=PLANS[pname]; p=get_user_profile(uid)
    p.update({"user_id":uid,"username":tg_user.username or tg_user.first_name,
        "name":tg_user.first_name,"chat_id":chat_id,"language":get_user_language(uid),
        "blocked_users":p.get("blocked_users",[]),"photos":p.get("photos",[]),
        "hobbies":p.get("hobbies",[]),"active":True,
        "joined_at":p.get("joined_at",datetime.now().isoformat())})
    if pi["price"]==0:
        p.update({"plan":pname,"plan_price":0,"subscribed_at":datetime.now().isoformat(),
            "plan_expires":(datetime.now()+timedelta(days=pi["duration_days"])).isoformat(),"verified":False})
        update_user(uid,p); analytics["free_signups"]+=1; _start_reg_flow(chat_id,uid)
    else:
        p["selected_plan"]=pname; p["selected_price"]=pi["price"]; update_user(uid,p)
        bot.send_message(chat_id,f"💳 <b>{pname} — ₹{pi['price']}</b>\n\n📱 Scan UPI QR to pay:",parse_mode="HTML")
        qr=generate_upi_qr(pi["price"])
        if qr: bot.send_photo(chat_id,qr,caption=f"Pay ₹{pi['price']} to: <code>{UPI_ID}</code>",parse_mode="HTML")
        bot.send_message(chat_id,
            "📸 <b>After payment:</b>\n1️⃣ Take a screenshot\n2️⃣ Send it here\n3️⃣ Verified within minutes!",parse_mode="HTML")

# ═══════════════════ REGISTRATION FLOW ═══════════════════
def _start_reg_flow(chat_id,uid):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=6)
    for a in range(18,61): markup.add(str(a))
    bot.send_message(chat_id,f"🎂 {get_text(uid,'age_question')}",reply_markup=markup)

@bot.message_handler(func=lambda msg: (
    msg.text and msg.text.isdigit() and 18<=int(msg.text)<=65 and
    not get_user_profile(msg.from_user.id).get("setup_active") and
    not get_user_profile(msg.from_user.id).get("profile_complete") and
    get_user_profile(msg.from_user.id).get("plan") and
    not admin_in_wizard(msg.from_user.id)
))
def set_age(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    if not p: return
    p["age"]=int(message.text); update_user(uid,p)
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=2)
    for c in CITIES: markup.add(c)
    bot.send_message(message.chat.id,f"✅ {message.text} years!\n\n📍 {get_text(uid,'city_question')}",reply_markup=markup)

@bot.message_handler(func=lambda msg: (
    msg.text in CITIES and not get_user_profile(msg.from_user.id).get("setup_active") and
    not get_user_profile(msg.from_user.id).get("profile_complete") and
    get_user_profile(msg.from_user.id).get("age") and not admin_in_wizard(msg.from_user.id)
))
def set_city(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    if not p: return
    p["city"]=message.text; update_user(uid,p)
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=2)
    for g in GENDERS.keys(): markup.add(g)
    bot.send_message(message.chat.id,f"✅ {message.text}!\n\n{get_text(uid,'gender_question')}",reply_markup=markup)

@bot.message_handler(func=lambda msg: (
    msg.text in GENDERS.keys() and not get_user_profile(msg.from_user.id).get("setup_active") and
    not get_user_profile(msg.from_user.id).get("profile_complete") and
    get_user_profile(msg.from_user.id).get("city") and not admin_in_wizard(msg.from_user.id)
))
def set_gender(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    if not p: return
    p["gender"]=GENDERS[message.text]; p["gender_display"]=message.text; update_user(uid,p)
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=2)
    for lf in LOOKING_FOR.keys(): markup.add(lf)
    bot.send_message(message.chat.id,"💫 What are you looking for?",reply_markup=markup)

@bot.message_handler(func=lambda msg: (
    msg.text in LOOKING_FOR.keys() and not get_user_profile(msg.from_user.id).get("setup_active") and
    not get_user_profile(msg.from_user.id).get("profile_complete") and
    get_user_profile(msg.from_user.id).get("gender") and not admin_in_wizard(msg.from_user.id)
))
def set_looking_for(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    if not p: return
    p["looking_for"]=LOOKING_FOR[message.text]; p["looking_for_display"]=message.text; update_user(uid,p)
    _send_hobby_picker(message.chat.id,uid,[])

def _send_hobby_picker(chat_id,uid,selected):
    markup=types.InlineKeyboardMarkup(row_width=2)
    for hn in HOBBIES.keys():
        tick="✅ " if hn in selected else ""
        markup.add(types.InlineKeyboardButton(f"{tick}{hn}",callback_data=f"hobby_{hn}"))
    if selected:
        markup.add(types.InlineKeyboardButton(f"✔️ Done ({len(selected)} selected)",callback_data="hobby_done"))
    bot.send_message(chat_id,
        "🎯 <b>Select your hobbies!</b>\n\nTap each hobby, then tap ✔️ Done.\n<i>Select at least 3 for better matches.</i>",
        reply_markup=markup,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("hobby_") and not admin_in_wizard(call.from_user.id))
def hobby_cb(call):
    uid=call.from_user.id; p=get_user_profile(uid)
    if not p: safe_answer(call.id); return
    if call.data=="hobby_done":
        selected=_hobby_temp.get(uid,[])
        if not selected: safe_answer(call.id,"⚠️ Select at least one hobby!",show_alert=True); return
        p["hobbies"]=selected; update_user(uid,p); _hobby_temp.pop(uid,None)
        safe_answer(call.id,"✅ Hobbies saved!")
        # Is this during setup wizard?
        if p.get("setup_active"):
            p["setup_step"]="bio"; update_user(uid,p)
            try: bot.edit_message_text(f"✅ Hobbies: {', '.join(selected[:4])}{'...' if len(selected)>4 else ''}",call.message.chat.id,call.message.message_id)
            except Exception: pass
            ask_setup_step(call.message.chat.id,uid,"bio")
        elif p.get("editing_hobbies"):
            p.pop("editing_hobbies",None); update_user(uid,p)
            try: bot.edit_message_text(f"✅ Hobbies updated: {', '.join(selected[:4])}",call.message.chat.id,call.message.message_id)
            except Exception: pass
            send_main_menu(call.message.chat.id,uid)
        else:
            try: bot.edit_message_text(f"✅ Hobbies: {', '.join(selected[:4])}{'...' if len(selected)>4 else ''}",call.message.chat.id,call.message.message_id)
            except Exception: pass
            bot.send_message(call.message.chat.id,"✏️ Write a short bio (max 150 chars):",reply_markup=types.ReplyKeyboardRemove())
        return
    hname=call.data[len("hobby_"):]
    if hname not in HOBBIES: safe_answer(call.id); return
    selected=_hobby_temp.get(uid,[])
    if hname in selected: selected.remove(hname)
    else: selected.append(hname)
    _hobby_temp[uid]=selected
    safe_answer(call.id,f"{'✅' if hname in selected else '❌'} {hname}")
    markup=types.InlineKeyboardMarkup(row_width=2)
    for hn in HOBBIES.keys():
        tick="✅ " if hn in selected else ""
        markup.add(types.InlineKeyboardButton(f"{tick}{hn}",callback_data=f"hobby_{hn}"))
    if selected:
        markup.add(types.InlineKeyboardButton(f"✔️ Done ({len(selected)} selected)",callback_data="hobby_done"))
    try: bot.edit_message_reply_markup(call.message.chat.id,call.message.message_id,reply_markup=markup)
    except Exception: pass

@bot.message_handler(func=lambda msg: (
    msg.text and not msg.text.startswith("/") and
    msg.text not in GENDERS and msg.text not in LOOKING_FOR and msg.text not in CITIES and
    not (msg.text.isdigit() if msg.text else False) and "," not in msg.text and
    not get_user_profile(msg.from_user.id).get("profile_complete") and
    get_user_profile(msg.from_user.id).get("hobbies") and
    not get_user_profile(msg.from_user.id).get("setup_active") and
    not admin_in_wizard(msg.from_user.id)
))
def set_bio(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    if not p or p.get("profile_complete"): return
    p["bio"]=message.text[:150]; p["profile_complete"]=True; p["last_active"]=datetime.now().isoformat()
    update_user(uid,p); analytics["profiles_created"]+=1
    send_main_menu(message.chat.id,uid,f"🎉 <b>Profile Complete!</b> ({get_profile_score(p)}%)\n\n📸 Add photos for more matches!")
# ═══════════════════ PHOTOS ═══════════════════
@bot.message_handler(func=lambda msg: (
    msg.text and get_text(msg.from_user.id,'add_photos') in msg.text and
    not admin_in_wizard(msg.from_user.id)
))
def add_photos_menu(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    p["waiting_for_photo"]="profile"; update_user(uid,p); n=len(p.get("photos",[]))
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Done adding photos",callback_data="done_photos"))
    bot.send_message(message.chat.id,
        f"📸 <b>Add Photos</b>\n\n{n}/{MAX_PHOTOS} uploaded\n\n"
        f"• Send your best photos\n• Clear face photos get 3x more matches\n• Max {MAX_PHOTOS} photos\n\nSend photos below:",
        reply_markup=markup,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data=="done_photos")
def done_photos_cb(call):
    safe_answer(call.id,"✅ Photos saved!"); uid=call.from_user.id; p=get_user_profile(uid)
    p.pop("waiting_for_photo",None); update_user(uid,p)
    send_main_menu(call.message.chat.id,uid,f"📸 Photos saved! Score: {get_profile_score(p)}%")

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    # Admin seed wizard
    if is_admin(uid) and uid in admin_creating_seed:
        s=admin_creating_seed.get(uid)
        if s and s.get("step")=="photo": _handle_seed_photo_inner(message); return
    # Admin lady wizard
    if is_admin(uid) and uid in admin_creating_lady:
        s=admin_creating_lady.get(uid)
        if s and s.get("step")=="photo": _handle_lady_photo_inner(message); return
    # Admin featured
    if is_admin(uid) and uid in admin_featured_temp:
        fid=message.photo[-1].file_id; admin_featured_temp[uid].append(fid)
        bot.send_message(message.chat.id,f"✅ Featured photo added ({len(admin_featured_temp[uid])}). /savefeatured when done."); return
    # Payment screenshot
    if p.get("selected_plan") and not p.get("waiting_for_photo"):
        handle_payment_screenshot(message); return
    # Regular profile photo
    if "photos" not in p: p["photos"]=[]
    if len(p["photos"])<MAX_PHOTOS:
        p["photos"].append(message.photo[-1].file_id); update_user(uid,p)
        n=len(p["photos"]); score=get_profile_score(p)
        markup=types.InlineKeyboardMarkup()
        if n<MAX_PHOTOS: markup.add(types.InlineKeyboardButton("✅ Done",callback_data="done_photos"))
        bot.send_message(message.chat.id,
            f"📸 Photo {n}/{MAX_PHOTOS} added! Score: {score}%"+
            (f"\n\nSend one more or tap Done." if n<MAX_PHOTOS else "\n\n✅ Max photos reached!"),
            reply_markup=markup if n<MAX_PHOTOS else None)
    else:
        bot.send_message(message.chat.id,f"❌ Max {MAX_PHOTOS} photos. Go to 👤 My Profile → Edit to manage.")

@bot.message_handler(commands=['done'])
def done_cmd(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    p.pop("waiting_for_photo",None)
    if p.get("setup_active"): _finalize_user_setup(message.chat.id,uid,p)
    else:
        p.pop("setup_active",None); update_user(uid,p)
        bot.send_message(message.chat.id,"✅ Done!")
        send_main_menu(message.chat.id,uid)

@bot.message_handler(commands=['cancel'])
def cancel_cmd(message):
    uid=message.from_user.id; p=get_user_profile(uid); cleared=[]
    for flag in ["waiting_for_photo","editing_bio","editing_city","editing_lf","support_mode","editing_hobbies"]:
        if p.pop(flag,None): cleared.append(flag)
    if p.get("setup_active"): p.pop("setup_active",None); p.pop("setup_step",None); cleared.append("setup")
    _hobby_temp.pop(uid,None)
    if cleared: update_user(uid,p)
    if is_admin(uid):
        admin_creating_seed.pop(uid,None); admin_creating_lady.pop(uid,None)
        admin_pending_actions.pop(uid,None); admin_replyas_context.pop(uid,None)
    if cleared or is_admin(uid):
        bot.send_message(message.chat.id,"✅ Cancelled.",reply_markup=types.ReplyKeyboardRemove())
        send_main_menu(message.chat.id,uid)
    else:
        bot.send_message(message.chat.id,"ℹ️ Nothing to cancel.")

# ═══════════════════ FIND MATCHES ═══════════════════
@bot.message_handler(func=lambda msg: msg.text and get_text(msg.from_user.id,'find_match') in msg.text)
def find_matches(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    if not p.get("profile_complete"):
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("👤 Complete Profile",callback_data="goto_profile"))
        bot.send_message(message.chat.id,"⚠️ Complete your profile first!\n\nTap below to go to your profile.",reply_markup=markup); return
    limits=get_plan_limits(uid); usage=get_daily_usage(uid)
    if usage["matches_used"]>=limits["matches_per_day"]:
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬆️ Upgrade Plan",callback_data="cb_upgrade"))
        bot.send_message(message.chat.id,
            f"⏰ <b>Daily limit reached!</b>\n\n{limits['matches_per_day']} matches used.\nResets at midnight or upgrade! 💎",
            reply_markup=markup,parse_mode="HTML"); return
    matches=get_cached_matches(uid,limit=10)
    if not matches:
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("👤 Edit Profile",callback_data="goto_profile"),
                   types.InlineKeyboardButton("📸 Add Photos",callback_data="goto_photos"))
        bot.send_message(message.chat.id,
            "😅 <b>No matches yet!</b>\n\n• Add more photos 📸\n• Add more hobbies 🎯\n• Try different city",
            reply_markup=markup,parse_mode="HTML"); return
    match=random.choice(matches[:5]); increment_usage(uid,"matches_used")
    pending_likes.setdefault(str(uid),{})[str(match["user_id"])]=datetime.now().isoformat()
    hobby_text=", ".join(match["hobbies"]) if match["hobbies"] else "—"
    vt=" ✅" if match["is_verified"] else ""; bt=" 🚀" if match["is_boosted"] else ""
    bio_text=f"\n\n📝 <i>{esc(match['bio'])}</i>" if match["bio"] else ""
    remaining=limits["matches_per_day"]-usage["matches_used"]-1
    msg=(f"💕 <b>{get_text(uid,'match_found')}</b>\n\n"
         f"👤 <b>{esc(match['name'])}</b>{vt}{bt}\n"
         f"{esc(match['gender_display'])} • {match['age']} yrs • 📍 {esc(match['city'])}\n"
         f"🎯 {esc(match['looking_for'])}\n🎵 Common: {hobby_text}{bio_text}\n\n"
         f"📊 Match: <b>{match['match_score']}%</b>  <i>({remaining} left today)</i>")
    markup=types.InlineKeyboardMarkup(row_width=3)
    markup.add(types.InlineKeyboardButton("💕 Like",callback_data=f"like_{match['user_id']}"),
               types.InlineKeyboardButton("⭐ Super Like",callback_data=f"superlike_{match['user_id']}"),
               types.InlineKeyboardButton("⏭ Skip",callback_data=f"skip_{match['user_id']}"))
    markup.add(types.InlineKeyboardButton("🚩 Report",callback_data=f"report_{match['user_id']}"))
    op=get_user_profile(match["user_id"]); photos=op.get("photos",[])
    if photos:
        try:
            bot.send_photo(message.chat.id,photos[0],caption=msg,reply_markup=markup,parse_mode="HTML")
            analytics["matches_shown"]+=1; return
        except Exception: pass
    bot.send_message(message.chat.id,msg,reply_markup=markup,parse_mode="HTML")
    analytics["matches_shown"]+=1

# ═══════════════════ SUPER LIKE ═══════════════════
@bot.message_handler(func=lambda msg: msg.text and get_text(msg.from_user.id,'super_like') in msg.text)
def super_like_menu(message):
    uid=message.from_user.id; limits=get_plan_limits(uid); usage=get_daily_usage(uid)
    left=limits["super_likes_per_day"]-usage["super_likes_used"]
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💞 Find a match to Super Like",callback_data="goto_findmatch"))
    bot.send_message(message.chat.id,
        f"⭐ <b>Super Like</b>\n\nStands out — they get a special notification!\n\n"
        f"🔢 Left today: <b>{left}/{limits['super_likes_per_day']}</b>\n\n"
        f"💡 Tap 💞 Find Match, then use the ⭐ button.",
        reply_markup=markup,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("superlike_"))
def super_like_match(call):
    uid=call.from_user.id; lid=int(call.data.split("_")[1])
    limits=get_plan_limits(uid); usage=get_daily_usage(uid)
    if usage["super_likes_used"]>=limits["super_likes_per_day"]:
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬆️ Upgrade",callback_data="cb_upgrade"))
        safe_answer(call.id,"⭐ Daily super like limit reached!",show_alert=True); return
    increment_usage(uid,"super_likes_used")
    lp=get_user_profile(uid); lkp=get_user_profile(lid)
    try:
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💕 Like Back",callback_data=f"like_{uid}"),
                   types.InlineKeyboardButton("⏭ Skip",callback_data=f"skip_{uid}"))
        bot.send_message(lkp.get("chat_id"),
            f"⭐ <b>You got a Super Like!</b>\n\n<b>{esc(lp.get('name','Someone'))}</b> "
            f"({lp.get('age')} yrs, {esc(lp.get('city'))}) really wants to connect 💕\n\nTap <b>Like Back</b> to match!",
            reply_markup=markup,parse_mode="HTML")
    except Exception as e: logger.error(f"Super like notify: {e}")
    safe_answer(call.id,"⭐ Super Like sent!")
    left=limits["super_likes_per_day"]-usage["super_likes_used"]
    bot.send_message(call.message.chat.id,f"⭐ <b>Super Like sent!</b> ({left} left today)",parse_mode="HTML")
    analytics["super_likes"]+=1

# ═══════════════════ LIKE / SKIP / REPORT ═══════════════════
@bot.callback_query_handler(func=lambda call: call.data.startswith("like_"))
def like_match(call):
    lid=call.from_user.id; rid=int(call.data.split("_")[1])
    ck=f"chat_{min(lid,rid)}_{max(lid,rid)}"
    with data_lock:
        if ck not in active_chats:
            active_chats[ck]={"user1":lid,"user2":rid,"started_at":datetime.now().isoformat(),"messages":0}
        save_all_data()
    lp=get_user_profile(lid); rp=get_user_profile(rid)
    rname=esc(rp.get('name') or f"User {rid}"); lname=esc(lp.get('name') or f"User {lid}")
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 Chat Now →",callback_data=f"openchat_{rid}"))
    bot.send_message(call.message.chat.id,
        f"🎉 <b>It's a Match!</b> 🎉\n\nYou and <b>{rname}</b> liked each other!\n\n💬 Chat right here — no external apps!",
        reply_markup=markup,parse_mode="HTML")
    try:
        markup2=types.InlineKeyboardMarkup()
        markup2.add(types.InlineKeyboardButton("💬 Chat Now →",callback_data=f"openchat_{lid}"))
        bot.send_message(rp.get("chat_id"),
            f"🎉 <b>New Match!</b> 🎉\n\n<b>{lname}</b> liked you!\n\n"
            f"💬 Icebreaker: <i>{random.choice(ICEBREAKERS)}</i>\n\nTap <b>Chat Now</b> to start!",
            reply_markup=markup2,parse_mode="HTML")
    except Exception as e: logger.error(f"Match notify: {e}")
    safe_answer(call.id,"💕 Matched!"); analytics["matches_made"]+=1

@bot.callback_query_handler(func=lambda call: call.data.startswith("skip_"))
def skip_match(call):
    safe_answer(call.id,"⏭ Skipped")
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💞 Find Next Match",callback_data="goto_findmatch"))
    bot.send_message(call.message.chat.id,"⏭ Skipped! Keep looking 💞",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("report_"))
def report_user(call):
    rid=call.data.split("_")[1]
    markup=types.InlineKeyboardMarkup(row_width=2)
    for r in ["Fake Profile","Spam","Inappropriate","Harassment","Other"]:
        markup.add(types.InlineKeyboardButton(r,callback_data=f"reportreason_{rid}_{r}"))
    safe_answer(call.id)
    bot.send_message(call.message.chat.id,"🚩 <b>Why are you reporting?</b>",reply_markup=markup,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reportreason_"))
def report_reason(call):
    parts=call.data.split("_",2); reported_id=parts[1]; reason=parts[2]
    rp=get_user_profile(call.from_user.id)
    try:
        bot.send_message(ADMIN_ID,
            f"🚩 <b>Report</b>\nFrom: {esc(rp.get('name','?'))} ({call.from_user.id})\nAgainst: {reported_id}\nReason: {reason}")
    except Exception: pass
    safe_answer(call.id,"✅ Reported!",show_alert=True)
    bot.send_message(call.message.chat.id,"✅ Report submitted. We review all reports within 24h.")
# ═══════════════════ BOOST ═══════════════════
@bot.message_handler(func=lambda msg: msg.text and get_text(msg.from_user.id,'boost') in msg.text)
def boost_profile(message):
    uid=message.from_user.id; limits=get_plan_limits(uid)
    if not limits["can_boost"]:
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬆️ Upgrade to Gold/Platinum",callback_data="cb_upgrade"))
        bot.send_message(message.chat.id,
            "🚀 <b>Profile Boost</b>\n\nBe at the top of everyone's match list for 30 mins!\n\nAvailable on 💎 Gold & 👑 Platinum.",
            reply_markup=markup,parse_mode="HTML"); return
    et=(datetime.now()+timedelta(minutes=BOOST_DURATION_MINUTES)).isoformat()
    with data_lock: boosted_users[str(uid)]=et
    invalidate_match_cache()
    bot.send_message(message.chat.id,
        f"🚀 <b>Boosted for {BOOST_DURATION_MINUTES} minutes!</b>\n\n"
        f"You're at the top of matches for everyone nearby.\n"
        f"Ends at: {(datetime.now()+timedelta(minutes=BOOST_DURATION_MINUTES)).strftime('%H:%M')}",parse_mode="HTML")
    analytics["boosts_used"]+=1

# ═══════════════════ LEADERBOARD ═══════════════════
@bot.message_handler(func=lambda msg: msg.text and get_text(msg.from_user.id,'leaderboard') in msg.text)
def show_leaderboard(message):
    scored=sorted([(uid,get_profile_score(p),p) for uid,p in user_data.items()
        if p.get("profile_complete") and p.get("active")],key=lambda x:x[1],reverse=True)[:10]
    medals=["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    msg="🏆 <b>Top Profiles</b>\n\n"
    for i,(uid,sc,p) in enumerate(scored):
        v=" ✅" if p.get("verified") else ""
        msg+=f"{medals[i]} <b>{esc(p.get('name','User'))}</b>{v} — {sc}%\n"
    uid=message.from_user.id; my=get_profile_score(get_user_profile(uid))
    msg+=f"\n📊 Your score: <b>{my}%</b>\n\n💡 Add photos & hobbies to climb up!"
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👤 Improve My Profile",callback_data="goto_profile"))
    bot.send_message(message.chat.id,msg,reply_markup=markup,parse_mode="HTML")

# ═══════════════════ MESSAGES ═══════════════════
@bot.message_handler(func=lambda msg: msg.text and get_text(msg.from_user.id,'messages') in msg.text)
def messages_menu(message):
    uid=message.from_user.id
    chats=[info for cid,info in active_chats.items() if uid in [info.get("user1"),info.get("user2")]]
    if not chats:
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💞 Find Your First Match",callback_data="goto_findmatch"))
        bot.send_message(message.chat.id,"💬 <b>No matches yet!</b>\n\nGo find your first match! 💞",reply_markup=markup,parse_mode="HTML"); return
    bot.send_message(message.chat.id,f"💬 <b>Your Matches ({len(chats)})</b>",parse_mode="HTML")
    for info in chats[:10]:
        oid=info["user2"] if uid==info["user1"] else info["user1"]
        op=get_user_profile(oid); name=esc(op.get('name') or f"User {oid}")
        msgs=info.get("messages",0)
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f"💬 Chat with {name}",callback_data=f"openchat_{oid}"))
        try:
            bot.send_message(message.chat.id,
                f"👤 <b>{name}</b> — {op.get('age','?')} yrs, {esc(op.get('city',''))}\n"
                f"💬 {msgs} message{'s' if msgs!=1 else ''} exchanged",
                reply_markup=markup,parse_mode="HTML")
        except Exception: continue

# ═══════════════════ IN-BOT CHAT ═══════════════════
@bot.callback_query_handler(func=lambda call: call.data.startswith("openchat_"))
def open_chat_cb(call):
    safe_answer(call.id); uid=call.from_user.id
    try: oid=int(call.data.split("_")[1])
    except Exception: bot.send_message(call.message.chat.id,"❌ Invalid chat."); return
    p=get_user_profile(uid); other=get_user_profile(oid)
    p['chatting_with']=oid; update_user(uid,p)
    oname=esc(other.get('name') or f"User {oid}"); cname=esc(p.get('name') or f"User {uid}")
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    markup.add(types.KeyboardButton("🔴 End Chat"))
    bot.send_message(call.message.chat.id,
        f"💬 <b>Chat opened with {oname}</b>\n\n🔒 Private in-app chat\n✉️ Type your message!\n\n<i>/endchat to end</i>",
        reply_markup=markup,parse_mode="HTML")
    try:
        if other and other.get('is_seed'):
            sname=esc(other.get('name') or f"Seed {oid}")
            for at in ADMIN_IDS:
                try:
                    ikm=types.InlineKeyboardMarkup()
                    ikm.add(types.InlineKeyboardButton(f"✏️ Reply as {sname}",callback_data=f"replyas_prompt_{oid}_{uid}"))
                    bot.send_message(at,
                        f"💌 <b>User opened chat with seed!</b>\n\n"
                        f"👤 User: <b>{cname}</b> (ID: <code>{uid}</code>)\n"
                        f"🎭 Seed: <b>{sname}</b> (ID: <code>{oid}</code>)\n\n"
                        f"<code>/replyas {oid} {uid} your message</code>",
                        parse_mode="HTML",reply_markup=ikm)
                except Exception as e: logger.error(f"seed notify {at}: {e}")
        elif other and other.get('chat_id') and not is_admin(oid):
            other['chatting_with']=uid; update_user(oid,other)
            markup2=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
            markup2.add(types.KeyboardButton("🔴 End Chat"))
            bot.send_message(other.get('chat_id'),
                f"💬 <b>{cname}</b> started a chat!\n\n🔒 Private in-app chat\n✉️ Type to reply!\n\n<i>/endchat to end</i>",
                reply_markup=markup2,parse_mode="HTML")
        elif is_admin(oid):
            mkup=types.InlineKeyboardMarkup()
            mkup.row(types.InlineKeyboardButton("🟢 Accept",callback_data=f"admin_accept_{uid}"),
                     types.InlineKeyboardButton("❌ Reject",callback_data=f"admin_reject_{uid}"))
            for at in ADMIN_IDS:
                try: bot.send_message(at,f"🔔 <b>User wants chat</b>\n\n{cname} (ID: {uid})",parse_mode="HTML",reply_markup=mkup)
                except Exception as e: logger.error(f"admin notify {at}: {e}")
    except Exception as e: logger.error(f"openchat notify: {e}")

@bot.message_handler(commands=['endchat'])
def end_chat_cmd(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    if p.get('chatting_with'):
        target=p.pop('chatting_with',None); update_user(uid,p)
        bot.send_message(message.chat.id,"✅ Chat ended.",reply_markup=types.ReplyKeyboardRemove())
        try:
            if target and not is_admin(target) and not get_user_profile(target).get('is_seed'):
                op=get_user_profile(target)
                if op.get('chatting_with')==uid:
                    op.pop('chatting_with',None); update_user(target,op)
                    bot.send_message(op.get('chat_id'),"✅ Chat ended.",reply_markup=types.ReplyKeyboardRemove())
        except Exception: pass
        send_main_menu(message.chat.id,uid)
    else:
        bot.send_message(message.chat.id,"ℹ️ You are not in a chat right now.")
        send_main_menu(message.chat.id,uid)

@bot.message_handler(func=lambda msg: msg.text and msg.text.startswith("🔴 End Chat"))
def end_chat_btn(message): end_chat_cmd(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_accept_"))
def admin_accept(call):
    if not is_admin(call.from_user.id): safe_answer(call.id,"❌ Not authorized"); return
    safe_answer(call.id)
    try:
        aid=call.from_user.id; tid=int(call.data.split("_")[-1])
        ap=get_user_profile(aid); ap['chatting_with']=tid; update_user(aid,ap)
        up=get_user_profile(tid); up['chatting_with']=aid; update_user(tid,up)
        try: bot.edit_message_text("🟢 Accepted.",call.message.chat.id,call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id,f"🟢 Connected to user {tid}.")
        if up.get('chat_id'): bot.send_message(up.get('chat_id'),"🟢 Support has joined!")
    except Exception as e: logger.error(f"admin_accept: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_reject_"))
def admin_reject(call):
    if not is_admin(call.from_user.id): safe_answer(call.id,"❌ Not authorized"); return
    safe_answer(call.id)
    try:
        aid=call.from_user.id; tid=int(call.data.split("_")[-1])
        ap=get_user_profile(aid); ap.pop('chatting_with',None); update_user(aid,ap)
        up=get_user_profile(tid); up.pop('chatting_with',None); update_user(tid,up)
        try: bot.edit_message_text("❌ Declined.",call.message.chat.id,call.message.message_id)
        except Exception: pass
        if up.get('chat_id'): bot.send_message(up.get('chat_id'),"❌ Chat requires Premium.")
    except Exception as e: logger.error(f"admin_reject: {e}")

# ── Proxy chat (registered AFTER admin_character_message at top of file) ──
@bot.message_handler(func=lambda msg: (
    msg.text and not msg.text.startswith('/') and not msg.text.startswith("🔴") and
    get_user_profile(msg.from_user.id).get('chatting_with') and
    not admin_in_wizard(msg.from_user.id)
))
def proxy_chat_message(message):
    sid=message.from_user.id; p=get_user_profile(sid)
    tid=p.get('chatting_with')
    if not tid: return
    text=message.text.strip()
    ck=f"chat_{min(sid,int(tid))}_{max(sid,int(tid))}"
    with data_lock:
        if ck not in active_chats:
            active_chats[ck]={"user1":min(sid,int(tid)),"user2":max(sid,int(tid)),"started_at":datetime.now().isoformat(),"messages":0}
        active_chats[ck]["messages"]=active_chats[ck].get("messages",0)+1; save_all_data()
    try:
        sname=esc(p.get('name') or f"User {sid}"); tp=get_user_profile(int(tid))
        if tp.get('is_seed'):
            sdn=esc(tp.get('name') or f"Seed {tid}")
            for at in ADMIN_IDS:
                try:
                    ikm=types.InlineKeyboardMarkup()
                    ikm.add(types.InlineKeyboardButton(f"✏️ Reply as {sdn}",callback_data=f"replyas_prompt_{tid}_{sid}"))
                    bot.send_message(at,
                        f"💬 <b>Message → {sdn}</b>\n\nFrom: <b>{sname}</b> (ID: <code>{sid}</code>)\n\n"
                        f"<i>{esc(text)}</i>\n\n<code>/replyas {tid} {sid} your reply</code>",
                        parse_mode="HTML",reply_markup=ikm)
                except Exception as e: logger.error(f"seed proxy {at}: {e}")
            bot.send_message(message.chat.id,"✅ Sent!")
        elif is_admin(tid):
            bot.send_message(int(tid),
                f"💬 <b>From {sname}</b> (ID: <code>{sid}</code>)\n\n{esc(text)}\n\n/reply {sid} your message",
                parse_mode="HTML")
        else:
            tc=tp.get('chat_id')
            if tc:
                bot.send_message(tc,text)   # plain text, no header
                bot.send_message(message.chat.id,"✅ Sent!")
            else:
                bot.send_message(message.chat.id,"❌ User unavailable right now.")
    except Exception as e:
        logger.error(f"Proxy error: {e}"); bot.send_message(message.chat.id,"❌ Could not send.")
# ═══════════════════ PROFILE VIEW ═══════════════════
@bot.message_handler(func=lambda msg: msg.text and get_text(msg.from_user.id,'profile') in msg.text)
def view_profile(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    if not p: bot.send_message(message.chat.id,"⚠️ No profile. Send /start"); return
    score=get_profile_score(p); hobbies=", ".join(p.get("hobbies",[])[:5]) or "None"
    v=" ✅" if p.get("verified") else ""; exp=p.get("plan_expires","N/A")
    filled=int(score/10); bar="█"*filled+"░"*(10-filled)
    msg=(f"👤 <b>Your Profile</b>{v}\n\n"
         f"🧑 <b>{esc(p.get('name',p.get('username','?')))}</b>\n"
         f"{esc(p.get('gender_display',''))} • {p.get('age','?')} yrs • 📍 {esc(p.get('city','?'))}\n"
         f"{esc(p.get('looking_for_display',''))}\n\n"
         f"🎯 Hobbies: {hobbies}\n📝 Bio: {esc(p.get('bio','Not set'))}\n\n"
         f"💳 Plan: {p.get('plan','?')}\n"
         f"📅 Expires: {exp[:10] if exp!='N/A' else 'N/A'}\n"
         f"📸 Photos: {len(p.get('photos',[]))}/{MAX_PHOTOS}\n\n"
         f"📊 Score: <b>{score}%</b>  [{bar}]")
    markup=types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("✏️ Edit Bio",callback_data="edit_bio"),
               types.InlineKeyboardButton("📸 Add Photos",callback_data="goto_photos"))
    markup.add(types.InlineKeyboardButton("📍 Edit City",callback_data="cb_editcity"),
               types.InlineKeyboardButton("💫 Edit Looking For",callback_data="cb_editlf"))
    markup.add(types.InlineKeyboardButton("🎯 Edit Hobbies",callback_data="cb_edithobbies"),
               types.InlineKeyboardButton("⬆️ Upgrade Plan",callback_data="cb_upgrade"))
    markup.add(types.InlineKeyboardButton("🗑 Delete Account",callback_data="confirm_delete"))
    bot.send_message(message.chat.id,msg,reply_markup=markup,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data=="edit_bio")
def edit_bio_cb(call):
    uid=call.from_user.id; p=get_user_profile(uid)
    p["editing_bio"]=True; update_user(uid,p); safe_answer(call.id)
    bot.send_message(call.message.chat.id,"✏️ Send your new bio (max 150 chars):\n\n/cancel to cancel")

@bot.callback_query_handler(func=lambda call: call.data=="goto_photos")
def goto_photos_cb(call):
    uid=call.from_user.id; p=get_user_profile(uid)
    p["waiting_for_photo"]="profile"; update_user(uid,p); safe_answer(call.id)
    n=len(p.get("photos",[])); markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Done",callback_data="done_photos"))
    bot.send_message(call.message.chat.id,f"📸 Send photos ({n}/{MAX_PHOTOS}):",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data=="cb_editcity")
def cb_editcity(call):
    uid=call.from_user.id; p=get_user_profile(uid)
    p["editing_city"]=True; update_user(uid,p); safe_answer(call.id)
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=2)
    for c in CITIES: markup.add(c)
    bot.send_message(call.message.chat.id,"📍 Select your new city:",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data=="cb_editlf")
def cb_editlf(call):
    uid=call.from_user.id; p=get_user_profile(uid)
    p["editing_lf"]=True; update_user(uid,p); safe_answer(call.id)
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=2)
    for lf in LOOKING_FOR.keys(): markup.add(lf)
    bot.send_message(call.message.chat.id,"💫 What are you looking for now?",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data=="cb_edithobbies")
def cb_edithobbies(call):
    safe_answer(call.id); uid=call.from_user.id; p=get_user_profile(uid)
    _hobby_temp[uid]=list(p.get("hobbies",[])); p["editing_hobbies"]=True; update_user(uid,p)
    _send_hobby_picker(call.message.chat.id,uid,_hobby_temp[uid])

@bot.callback_query_handler(func=lambda call: call.data=="cb_upgrade")
def cb_upgrade(call):
    safe_answer(call.id); markup=types.InlineKeyboardMarkup(row_width=1)
    for pname,pi in PLANS.items():
        if pi["price"]>0:
            markup.add(types.InlineKeyboardButton(f"{pname} — ₹{pi['price']} — {pi['description']}",callback_data=f"selectplan_{pname}"))
    bot.send_message(call.message.chat.id,"⬆️ <b>Upgrade Plan</b>\n\nChoose below:",reply_markup=markup,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data=="goto_profile")
def goto_profile_cb(call):
    safe_answer(call.id); view_profile(call.message)

@bot.callback_query_handler(func=lambda call: call.data=="goto_findmatch")
def goto_findmatch_cb(call):
    safe_answer(call.id); find_matches(call.message)

@bot.callback_query_handler(func=lambda call: call.data=="confirm_delete")
def confirm_delete(call):
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Yes, Delete",callback_data="do_delete"),
               types.InlineKeyboardButton("❌ Cancel",callback_data="cancel_delete"))
    safe_answer(call.id)
    bot.send_message(call.message.chat.id,"⚠️ Delete your account permanently?",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data=="do_delete")
def do_delete(call):
    uid=str(call.from_user.id)
    with data_lock: user_data.pop(uid,None); save_all_data()
    safe_answer(call.id)
    bot.send_message(call.message.chat.id,"❌ Account deleted. Goodbye! 👋\n\nSend /start to rejoin.")

@bot.callback_query_handler(func=lambda call: call.data=="cancel_delete")
def cancel_delete(call):
    safe_answer(call.id,"✅ Account safe!"); bot.send_message(call.message.chat.id,"✅ Your account is safe! 💕")

@bot.callback_query_handler(func=lambda call: call.data=="ignore")
def ignore_cb(call): safe_answer(call.id)

# ── Edit state message handlers ────────────────────────────────
@bot.message_handler(func=lambda msg: (
    msg.text and not msg.text.startswith("/") and
    get_user_profile(msg.from_user.id).get("editing_bio") and not admin_in_wizard(msg.from_user.id)
))
def save_bio(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    p["bio"]=message.text[:150]; p.pop("editing_bio",None); update_user(uid,p)
    bot.send_message(message.chat.id,"✅ Bio updated!"); send_main_menu(message.chat.id,uid)

@bot.message_handler(func=lambda msg: (
    msg.text in CITIES and get_user_profile(msg.from_user.id).get("editing_city") and not admin_in_wizard(msg.from_user.id)
))
def save_city(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    p["city"]=message.text; p.pop("editing_city",None); update_user(uid,p)
    bot.send_message(message.chat.id,f"✅ City updated to {message.text}!"); send_main_menu(message.chat.id,uid)

@bot.message_handler(func=lambda msg: (
    msg.text in LOOKING_FOR and get_user_profile(msg.from_user.id).get("editing_lf") and not admin_in_wizard(msg.from_user.id)
))
def save_lf(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    p["looking_for"]=LOOKING_FOR[message.text]; p["looking_for_display"]=message.text
    p.pop("editing_lf",None); update_user(uid,p)
    bot.send_message(message.chat.id,f"✅ Updated to: {message.text}"); send_main_menu(message.chat.id,uid)

# ═══════════════════ SETTINGS ═══════════════════
@bot.message_handler(func=lambda msg: msg.text and get_text(msg.from_user.id,'settings') in msg.text)
def settings_menu(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    markup=types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🌐 Language",callback_data="set_lang"),
               types.InlineKeyboardButton("⬆️ Upgrade",callback_data="cb_upgrade"))
    markup.add(types.InlineKeyboardButton("💎 My Plan",callback_data="set_myplan"),
               types.InlineKeyboardButton("💰 Referral",callback_data="set_referral"))
    markup.add(types.InlineKeyboardButton("🚫 Block List",callback_data="set_blocklist"),
               types.InlineKeyboardButton("📋 Recap",callback_data="set_recap"))
    markup.add(types.InlineKeyboardButton("🆘 Support",callback_data="set_support"))
    bot.send_message(message.chat.id,
        f"⚙️ <b>Settings</b>\n\nPlan: {p.get('plan','?')}\nCity: {esc(p.get('city','?'))}\nScore: {get_profile_score(p)}%",
        reply_markup=markup,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data=="set_lang")
def set_lang_cb(call):
    safe_answer(call.id); markup=types.InlineKeyboardMarkup(row_width=1)
    for code,li in LANGUAGES.items():
        markup.add(types.InlineKeyboardButton(li['name'],callback_data=f"lang_{code}"))
    bot.send_message(call.message.chat.id,"🌐 Select language:",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_lang_choice(call):
    uid=call.from_user.id; code=call.data[5:]
    if code in LANGUAGES:
        set_user_language(uid,code); safe_answer(call.id,f"✅ {LANGUAGES[code]['name']}")
        bot.send_message(call.message.chat.id,f"✅ Language: {LANGUAGES[code]['name']}")
        send_main_menu(call.message.chat.id,uid)

@bot.callback_query_handler(func=lambda call: call.data=="set_myplan")
def set_myplan_cb(call):
    safe_answer(call.id); uid=call.from_user.id; p=get_user_profile(uid)
    plan=PLANS.get(p.get("plan","🆓 Free"),PLANS["🆓 Free"]); u=get_daily_usage(uid)
    exp=p.get("plan_expires","N/A")
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬆️ Upgrade Plan",callback_data="cb_upgrade"))
    bot.send_message(call.message.chat.id,
        f"💎 <b>{p.get('plan')}</b>\n\n"
        f"📅 Expires: {exp[:10] if exp!='N/A' else 'N/A'}\n"
        f"💞 Matches: {u['matches_used']}/{plan['matches_per_day']} today\n"
        f"⭐ Super Likes: {u['super_likes_used']}/{plan['super_likes_per_day']} today\n"
        f"🚀 Boost: {'✅' if plan['can_boost'] else '❌'}\n"
        f"👁 See who liked: {'✅' if plan['see_who_liked'] else '❌'}\n"
        f"✅ Verified badge: {'✅' if plan['verified_badge'] else '❌'}",
        reply_markup=markup,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data=="set_referral")
def set_referral_cb(call):
    safe_answer(call.id); uid=call.from_user.id; p=get_user_profile(uid)
    if "referral_code" not in p: p["referral_code"]=f"REF{uid}"; update_user(uid,p)
    bot.send_message(call.message.chat.id,
        f"🎁 <b>Your Referral Code</b>\n\nCode: <code>{p['referral_code']}</code>\n\n"
        f"Share with friends!\n├─ Friend gets: +3 days free\n├─ You get: +5 matches/day\n└─ Both: 10% off upgrade\n\n"
        f"💰 Earned: ₹{p.get('affiliate_earnings',0)}\n👥 Referrals: {p.get('total_referrals',0)}",
        parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data=="set_blocklist")
def set_blocklist_cb(call):
    safe_answer(call.id); uid=call.from_user.id; p=get_user_profile(uid)
    blocked=p.get("blocked_users",[])
    if not blocked: bot.send_message(call.message.chat.id,"✅ Block list is empty."); return
    msg="🚫 <b>Blocked Users:</b>\n\n"
    for bid in blocked:
        bp=get_user_profile(bid); name=esc(bp.get('name',str(bid)) if bp else str(bid))
        msg+=f"• {name} — /unblock {bid}\n"
    bot.send_message(call.message.chat.id,msg,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data=="set_recap")
def set_recap_cb(call):
    safe_answer(call.id); _daily_recap_inner(call.message.chat.id,call.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data=="set_support")
def set_support_cb(call):
    safe_answer(call.id); uid=call.from_user.id; p=get_user_profile(uid)
    p['support_mode']=True; update_user(uid,p)
    bot.send_message(call.message.chat.id,
        "🆘 <b>Support</b>\n\nDescribe your issue and we'll reply here.\n\n/cancel to cancel",
        parse_mode="HTML",reply_markup=types.ReplyKeyboardRemove())

def _daily_recap_inner(chat_id,uid):
    u=get_daily_usage(uid); limits=get_plan_limits(uid); p=get_user_profile(uid)
    ml=max(0,limits["matches_per_day"]-u["matches_used"])
    sl=max(0,limits["super_likes_per_day"]-u["super_likes_used"])
    total=sum(1 for c in active_chats.values() if uid in [c.get("user1"),c.get("user2")])
    score=get_profile_score(p)
    tips=[]
    if not p.get("bio"): tips.append("✏️ Add a bio to get 2x more matches")
    if len(p.get("photos",[]))<2: tips.append("📸 Add photos (2 recommended)")
    if len(p.get("hobbies",[]))<4: tips.append("🎯 Add more hobbies")
    if not p.get("verified"): tips.append("💎 Upgrade for verified badge")
    bot.send_message(chat_id,
        f"📋 <b>Daily Recap</b> — {datetime.now().strftime('%d %B %Y')}\n\n"
        f"📊 Profile Score: {score}%\n"
        f"💞 Matches: {u['matches_used']}/{limits['matches_per_day']} ({ml} left)\n"
        f"⭐ Super Likes: {u['super_likes_used']}/{limits['super_likes_per_day']} ({sl} left)\n"
        f"🤝 Total Connections: {total}\n\n"
        f"💡 <b>Tips:</b>\n"+("\n".join(tips) if tips else "🌟 Profile looks great!"),parse_mode="HTML")
# ═══════════════════ PAYMENT ═══════════════════
def handle_payment_screenshot(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    if "selected_plan" not in p: return
    bot.send_message(message.chat.id,"⏳ Screenshot received! Verifying payment...")
    with data_lock:
        pending_payments[str(uid)]={"user_id":uid,"username":p.get("username"),
            "plan":p.get("selected_plan"),"price":p.get("selected_price"),
            "timestamp":datetime.now().isoformat(),"chat_id":message.chat.id}
        save_all_data()
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ APPROVE",callback_data=f"approve_{uid}"),
               types.InlineKeyboardButton("❌ REJECT",callback_data=f"reject_{uid}"))
    for at in ADMIN_IDS:
        try:
            bot.send_message(at,
                f"💰 <b>Payment: {esc(p.get('selected_plan'))} — ₹{p.get('selected_price')}</b>\n\n"
                f"{esc(p.get('name','?'))}, {p.get('age','?')} yrs, {esc(p.get('city','?'))}",parse_mode="HTML")
            bot.forward_message(at,message.chat.id,message.message_id)
            bot.send_message(at,"Approve?",reply_markup=markup)
        except Exception as e:
            logger.error(f"payment notify {at}: {e}")
            if "403" in str(e):
                bot.send_message(message.chat.id,"✅ Screenshot received! Verification may take up to 24 hours.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve_payment(call):
    if not is_admin(call.from_user.id): safe_answer(call.id,"❌ Not authorized!"); return
    try:
        uid=int(call.data.split("_")[1]); p=get_user_profile(uid)
        pend=pending_payments.get(str(uid))
        if not pend: safe_answer(call.id,"❌ Not found!",show_alert=True); return
        pname=pend["plan"]; pi=PLANS.get(pname,{})
        p.update({"plan":pname,"plan_price":pend["price"],"active":True,
            "subscribed_at":datetime.now().isoformat(),
            "plan_expires":(datetime.now()+timedelta(days=pi.get("duration_days",30))).isoformat(),
            "verified":pi.get("verified_badge",False),"selected_plan":None,"selected_price":None})
        update_user(uid,p)
        with data_lock: pending_payments.pop(str(uid),None); save_all_data()
        bot.edit_message_text("✅ APPROVED",call.message.chat.id,call.message.message_id)
        safe_answer(call.id,"✅ Approved!"); analytics["payments_approved"]+=1
        start_profile_setup(pend["chat_id"],uid,pname,pi)
    except Exception as e: logger.error(f"approve: {e}"); safe_answer(call.id,f"❌ {e}",show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_payment(call):
    if not is_admin(call.from_user.id): safe_answer(call.id,"❌ Not authorized!"); return
    try:
        uid=int(call.data.split("_")[1]); pend=pending_payments.get(str(uid))
        if pend:
            with data_lock: pending_payments.pop(str(uid),None); save_all_data()
            bot.send_message(pend["chat_id"],"❌ Payment not verified.\n\nPlease send a clearer screenshot with UPI transaction ID.")
        bot.edit_message_text("❌ REJECTED",call.message.chat.id,call.message.message_id)
        safe_answer(call.id,"❌ Rejected")
    except Exception as e: logger.error(f"reject: {e}")

# ═══════════════════ POST-PAYMENT SETUP WIZARD ═══════════════════
SETUP_STEPS=["name","age","city","gender","looking_for","hobbies","bio","photos"]

def start_profile_setup(chat_id,uid,pname,pi):
    p=get_user_profile(uid)
    p["setup_step"]="name"; p["setup_active"]=True; update_user(uid,p)
    bot.send_message(chat_id,
        f"🎉 <b>Payment Approved!</b>\n\n<b>{pname}</b> is now active!\n"
        f"💞 {pi.get('matches_per_day',3)} matches/day unlocked\n"
        f"{'✅ Verified badge included!' if pi.get('verified_badge') else ''}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n📋 <b>Let's set up your profile!</b>\n\n"
        f"<b>Step 1/8 — What's your name?</b>\n(First name or nickname)",parse_mode="HTML")

def ask_setup_step(chat_id,uid,step):
    idx=SETUP_STEPS.index(step)+1 if step in SETUP_STEPS else 1
    prog=f"{idx}/8"
    if step=="name":
        bot.send_message(chat_id,f"<b>Step 1/8</b>\n\n👤 <b>Your name?</b>",parse_mode="HTML")
    elif step=="age":
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=6)
        for a in range(18,61): markup.add(str(a))
        bot.send_message(chat_id,f"<b>Step 2/8</b>\n\n🎂 <b>Your age?</b>",reply_markup=markup,parse_mode="HTML")
    elif step=="city":
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=2)
        for c in CITIES: markup.add(c)
        bot.send_message(chat_id,f"<b>Step 3/8</b>\n\n📍 <b>Your city?</b>",reply_markup=markup,parse_mode="HTML")
    elif step=="gender":
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=2)
        for g in GENDERS.keys(): markup.add(g)
        bot.send_message(chat_id,f"<b>Step 4/8</b>\n\n🙋 <b>Your gender?</b>",reply_markup=markup,parse_mode="HTML")
    elif step=="looking_for":
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=2)
        for lf in LOOKING_FOR.keys(): markup.add(lf)
        bot.send_message(chat_id,f"<b>Step 5/8</b>\n\n💫 <b>What are you looking for?</b>",reply_markup=markup,parse_mode="HTML")
    elif step=="hobbies":
        # Only init if not already set (don't wipe tapped selections)
        if uid not in _hobby_temp:
            _hobby_temp[uid]=[]
        _send_hobby_picker(chat_id,uid,_hobby_temp.get(uid,[]))
    elif step=="bio":
        bot.send_message(chat_id,
            f"<b>Step 7/8</b>\n\n✏️ <b>Short bio</b> (max 150 chars):\n<i>Example: \"Loves chai, sunsets and long walks!\"</i>",
            parse_mode="HTML",reply_markup=types.ReplyKeyboardRemove())
    elif step=="photos":
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Skip — Done",callback_data="done_photos"))
        bot.send_message(chat_id,
            f"<b>Step 8/8</b>\n\n📸 <b>Add photos!</b>\n\n• Up to {MAX_PHOTOS} photos\n"
            f"• Clear photos get 3x more matches\n\nSend photos or tap Skip.",
            parse_mode="HTML",reply_markup=markup)

@bot.message_handler(func=lambda msg: (
    msg.text and not msg.text.startswith("/") and
    get_user_profile(msg.from_user.id).get("setup_active") and not admin_in_wizard(msg.from_user.id)
))
def handle_setup_wizard(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    step=p.get("setup_step"); text=message.text.strip(); cid=message.chat.id
    if step=="name":
        if len(text)<2 or len(text)>30: bot.send_message(cid,"⚠️ Name must be 2–30 chars:"); return
        p["name"]=text; p["setup_step"]="age"; update_user(uid,p); ask_setup_step(cid,uid,"age")
    elif step=="age":
        if not text.isdigit() or not (18<=int(text)<=65): bot.send_message(cid,"⚠️ Valid age 18–65:"); return
        p["age"]=int(text); p["setup_step"]="city"; update_user(uid,p); ask_setup_step(cid,uid,"city")
    elif step=="city":
        if text not in CITIES: bot.send_message(cid,"⚠️ Select from the list:"); return
        p["city"]=text; p["setup_step"]="gender"; update_user(uid,p); ask_setup_step(cid,uid,"gender")
    elif step=="gender":
        if text not in GENDERS: bot.send_message(cid,"⚠️ Choose from options:"); return
        p["gender"]=GENDERS[text]; p["gender_display"]=text; p["setup_step"]="looking_for"
        update_user(uid,p); ask_setup_step(cid,uid,"looking_for")
    elif step=="looking_for":
        if text not in LOOKING_FOR: bot.send_message(cid,"⚠️ Choose from options:"); return
        p["looking_for"]=LOOKING_FOR[text]; p["looking_for_display"]=text; p["setup_step"]="hobbies"
        update_user(uid,p); ask_setup_step(cid,uid,"hobbies")
    elif step=="hobbies":
        bot.send_message(cid,"👆 Tap the hobby buttons above, then tap ✔️ Done.")
    elif step=="bio":
        if len(text)<5: bot.send_message(cid,"⚠️ Too short! Min 5 chars:"); return
        p["bio"]=text[:150]; p["setup_step"]="photos"; p["waiting_for_photo"]="profile"
        update_user(uid,p); bot.send_message(cid,"✅ Bio saved!"); ask_setup_step(cid,uid,"photos")
    elif step=="photos":
        if text.lower() in ("done","/done"): _finalize_user_setup(cid,uid,p)
        else: bot.send_message(cid,"📸 Send photos or tap Done button above.")
    else:
        ask_setup_step(cid,uid,"photos")

def _finalize_user_setup(chat_id,uid,p):
    p.pop("waiting_for_photo",None); p.pop("setup_active",None); p.pop("setup_step",None)
    p["profile_complete"]=True; p["last_active"]=datetime.now().isoformat()
    update_user(uid,p)
    score=get_profile_score(p); photos=len(p.get("photos",[])); v=" ✅" if p.get("verified") else ""
    bot.send_message(chat_id,
        f"🎉 <b>Profile Complete!</b>{v}\n\n"
        f"👤 <b>{esc(p.get('name','User'))}</b>\n"
        f"{esc(p.get('gender_display',''))} • {p.get('age')} yrs • 📍 {esc(p.get('city',''))}\n\n"
        f"🎯 {', '.join(p.get('hobbies',[])[:4])}\n"
        f"📝 <i>{esc(p.get('bio',''))}</i>\n"
        f"📸 {photos}/{MAX_PHOTOS} photos\n\n"
        f"📊 Score: <b>{score}%</b>\n"
        f"{'💡 Add photos for more matches!' if photos<2 else '🌟 Looking great!'}",
        parse_mode="HTML",reply_markup=types.ReplyKeyboardRemove())
    analytics["profiles_created"]+=1
    send_main_menu(chat_id,uid,"💞 You're all set! Start finding matches:")
# ═══════════════════ ADMIN FEATURED PHOTOS ═══════════════════
@bot.message_handler(commands=["addfeatured"])
def admin_add_featured(message):
    if not is_admin(message.from_user.id): bot.send_message(message.chat.id,"❌ Not authorized!"); return
    admin_featured_temp[message.from_user.id]=[]
    bot.send_message(message.chat.id,"📸 Send featured photos. /savefeatured when done, /cancelfeature to cancel.")

@bot.message_handler(commands=["savefeatured"])
def admin_save_featured(message):
    if not is_admin(message.from_user.id): return
    temp=admin_featured_temp.get(message.from_user.id,[])
    if not temp: bot.send_message(message.chat.id,"No photos. Use /addfeatured first."); return
    global featured_photos
    featured_photos=temp.copy(); save_all_data()
    admin_featured_temp.pop(message.from_user.id,None)
    bot.send_message(message.chat.id,f"✅ Saved {len(featured_photos)} featured photos.")

@bot.message_handler(commands=["cancelfeature"])
def admin_cancel_featured(message):
    if not is_admin(message.from_user.id): return
    admin_featured_temp.pop(message.from_user.id,None)
    bot.send_message(message.chat.id,"Cancelled.")

# ═══════════════════ ADMIN SEED PROFILE MANAGER ═══════════════════
def get_next_seed_id():
    existing=[int(k) for k in user_data if k.isdigit() and int(k)>=SEED_ID_PREFIX]
    return max(existing,default=SEED_ID_PREFIX-1)+1

@bot.message_handler(commands=["addprofile"])
def admin_add_profile(message):
    if not is_admin(message.from_user.id): bot.send_message(message.chat.id,"❌ Not authorized!"); return
    sid=get_next_seed_id()
    admin_creating_seed[message.from_user.id]={"seed_id":sid,"step":"name"}
    total=sum(1 for k in user_data if k.isdigit() and int(k)>=SEED_ID_PREFIX)
    bot.send_message(message.chat.id,
        f"👤 <b>Create Seed Profile</b>\n\nExisting: {total} | New ID: <code>{sid}</code>\n\n"
        f"<b>Step 1 — Name</b>\nEnter display name:",parse_mode="HTML",reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=["addlady"])
def admin_add_lady(message):
    if not is_admin(message.from_user.id): bot.send_message(message.chat.id,"❌ Not authorized!"); return
    aid=message.from_user.id; sid=get_next_seed_id()
    admin_creating_lady[aid]={"seed_id":sid,"step":"name"}
    user_data[str(sid)]={"photos":[]}
    bot.send_message(message.chat.id,"👩 Add Lady — Step 1: Send full name:",reply_markup=types.ReplyKeyboardRemove())

# ── Seed wizard text (priority over generic handlers via tight lambda) ──
@bot.message_handler(func=lambda msg: (
    msg.text and is_admin(msg.from_user.id) and
    msg.from_user.id in admin_creating_seed and not msg.text.startswith("/")
))
def handle_seed_wizard(message):
    aid=message.from_user.id; text=message.text.strip()
    state=admin_creating_seed.get(aid)
    if not state: return
    step=state["step"]; sid=state["seed_id"]; cid=message.chat.id
    p=user_data.get(str(sid),{})

    if step=="name":
        if len(text)<2 or len(text)>30: bot.send_message(cid,"⚠️ Name 2–30 chars:"); return
        p["name"]=text; state["step"]="age"; admin_creating_seed[aid]=state; user_data[str(sid)]=p
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=6)
        for a in range(18,61): markup.add(str(a))
        bot.send_message(cid,f"✅ Name: <b>{esc(text)}</b>\n\n<b>Step 2 — Age</b>",reply_markup=markup,parse_mode="HTML")
    elif step=="age":
        if not text.isdigit() or not (18<=int(text)<=65): bot.send_message(cid,"⚠️ Valid age 18–65:"); return
        p["age"]=int(text); state["step"]="city"; admin_creating_seed[aid]=state; user_data[str(sid)]=p
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=2)
        for c in CITIES: markup.add(c)
        bot.send_message(cid,f"✅ Age: <b>{text}</b>\n\n<b>Step 3 — City</b>",reply_markup=markup,parse_mode="HTML")
    elif step=="city":
        if text not in CITIES: bot.send_message(cid,"⚠️ Select from list:"); return
        p["city"]=text; state["step"]="gender"; admin_creating_seed[aid]=state; user_data[str(sid)]=p
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=2)
        for g in GENDERS.keys(): markup.add(g)
        bot.send_message(cid,f"✅ City: <b>{esc(text)}</b>\n\n<b>Step 4 — Gender</b>",reply_markup=markup,parse_mode="HTML")
    elif step=="gender":
        if text not in GENDERS: bot.send_message(cid,"⚠️ Choose from options:"); return
        p["gender"]=GENDERS[text]; p["gender_display"]=text; state["step"]="looking_for"
        admin_creating_seed[aid]=state; user_data[str(sid)]=p
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,row_width=2)
        for lf in LOOKING_FOR.keys(): markup.add(lf)
        bot.send_message(cid,f"✅ Gender: <b>{esc(text)}</b>\n\n<b>Step 5 — Looking For</b>",reply_markup=markup,parse_mode="HTML")
    elif step=="looking_for":
        if text not in LOOKING_FOR: bot.send_message(cid,"⚠️ Choose from options:"); return
        p["looking_for"]=LOOKING_FOR[text]; p["looking_for_display"]=text; state["step"]="hobbies"
        admin_creating_seed[aid]=state; user_data[str(sid)]=p
        hmsg="<b>Step 6 — Hobbies</b>\nType numbers e.g. <code>1,3,6</code>:\n\n"
        for i,hn in enumerate(HOBBIES.keys(),1): hmsg+=f"{i}. {hn}\n"
        bot.send_message(cid,hmsg,parse_mode="HTML",reply_markup=types.ReplyKeyboardRemove())
    elif step=="hobbies":
        hl=list(HOBBIES.keys())
        try:
            idx=[int(x.strip())-1 for x in (text.split(",") if "," in text else [text])]
            sel=[hl[i] for i in idx if 0<=i<len(hl)]
            if not sel: raise ValueError()
        except Exception: bot.send_message(cid,"⚠️ Type like <code>1,3,5</code>:",parse_mode="HTML"); return
        p["hobbies"]=sel; state["step"]="bio"; admin_creating_seed[aid]=state; user_data[str(sid)]=p
        bot.send_message(cid,f"✅ Hobbies: {esc(', '.join(sel))}\n\n<b>Step 7 — Bio</b> (5–150 chars):",
            parse_mode="HTML",reply_markup=types.ReplyKeyboardRemove())
    elif step=="bio":
        if len(text)<5: bot.send_message(cid,"⚠️ Too short! Min 5 chars:"); return
        p["bio"]=text[:150]; state["step"]="photo"; admin_creating_seed[aid]=state; user_data[str(sid)]=p
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⏭ Skip photo",callback_data=f"seed_skip_{sid}"))
        bot.send_message(cid,"✅ Bio saved!\n\n<b>Step 8 — Photo</b>\nSend a photo or tap Skip.",
            parse_mode="HTML",reply_markup=markup)
    elif step=="photo" and text.lower()=="skip":
        _finalize_seed_profile(aid,sid,p,cid)
    else:
        bot.send_message(cid,f"⚠️ Unexpected input for step <b>{step}</b>. Follow the prompts.",parse_mode="HTML")

# ── Lady wizard text ──
@bot.message_handler(func=lambda msg: (
    msg.text and is_admin(msg.from_user.id) and
    msg.from_user.id in admin_creating_lady and not msg.text.startswith("/")
))
def handle_lady_flow(message):
    aid=message.from_user.id; state=admin_creating_lady.get(aid)
    if not state: return
    sid=state["seed_id"]; p=user_data.get(str(sid),{}); text=message.text.strip()
    if state["step"]=="name":
        if not text: bot.send_message(message.chat.id,"⚠️ Name required:"); return
        p["name"]=text[:100]; state["step"]="age"; admin_creating_lady[aid]=state; user_data[str(sid)]=p
        bot.send_message(message.chat.id,"✅ Name saved.\n\nStep 2: Send age:")
    elif state["step"]=="age":
        try:
            age=int(text)
            if not 18<=age<=120: raise ValueError()
            p["age"]=age; state["step"]="photo"; admin_creating_lady[aid]=state; user_data[str(sid)]=p
            markup=types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⏭ Skip photos",callback_data=f"seed_skip_{sid}"))
            bot.send_message(message.chat.id,"✅ Age saved.\n\nStep 3: Send photos or tap Skip.",reply_markup=markup)
        except ValueError: bot.send_message(message.chat.id,"⚠️ Valid age 18–120:")

# ── Admin pending actions ──
@bot.message_handler(func=lambda msg: (
    msg.text and is_admin(msg.from_user.id) and
    msg.from_user.id in admin_pending_actions and not msg.text.startswith("/")
))
def handle_admin_pending(message):
    aid=message.from_user.id; state=admin_pending_actions.get(aid)
    if not state: return
    try: target=int(message.text.strip())
    except ValueError: bot.send_message(aid,"Please send a numeric Telegram ID."); return
    action=state.get('action')
    if action=='add_admin':
        if target in ADMIN_IDS: bot.send_message(aid,"Already admin.")
        else: ADMIN_IDS.append(target); save_admins(); bot.send_message(aid,f"✅ Added {target} as admin.")
    elif action=='remove_admin':
        if target not in ADMIN_IDS: bot.send_message(aid,"Not an admin.")
        elif target==ADMIN_ID: bot.send_message(aid,"❌ Cannot remove primary admin.")
        else:
            try: ADMIN_IDS.remove(target); save_admins(); bot.send_message(aid,f"✅ Removed {target}.")
            except ValueError: bot.send_message(aid,"Error.")
    admin_pending_actions.pop(aid,None)

# ── Seed photo handlers ──
def _handle_seed_photo_inner(message):
    aid=message.from_user.id; state=admin_creating_seed.get(aid)
    if not state: return
    sid=state["seed_id"]; p=user_data.get(str(sid),{})
    if "photos" not in p: p["photos"]=[]
    p["photos"].append(message.photo[-1].file_id); n=len(p["photos"])
    if n<MAX_PHOTOS:
        user_data[str(sid)]=p
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Done — Save",callback_data=f"seedsave_{sid}"),
                   types.InlineKeyboardButton("📸 Add Another",callback_data=f"seedmore_{sid}"))
        bot.send_message(message.chat.id,f"📸 Photo {n} added! Save or add another.",reply_markup=markup)
    else:
        _finalize_seed_profile(aid,sid,p,message.chat.id)

def _handle_lady_photo_inner(message):
    aid=message.from_user.id; state=admin_creating_lady.get(aid)
    if not state: return
    sid=state["seed_id"]; p=user_data.get(str(sid),{})
    if "photos" not in p: p["photos"]=[]
    p["photos"].append(message.photo[-1].file_id); user_data[str(sid)]=p; n=len(p.get("photos",[]))
    if n>=MAX_PHOTOS: _finalize_seed_profile(aid,sid,p,message.chat.id)
    else:
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Done — Save",callback_data=f"seedsave_{sid}"))
        bot.send_message(message.chat.id,f"📸 Photo {n} added! Send more or tap Done.",reply_markup=markup)

@bot.message_handler(commands=["skiplady","donelady"])
def finish_lady_cmd(message):
    if not is_admin(message.from_user.id): return
    aid=message.from_user.id; state=admin_creating_lady.get(aid)
    if not state: return
    sid=state["seed_id"]; p=user_data.get(str(sid),{})
    _finalize_seed_profile(aid,sid,p,message.chat.id); admin_creating_lady.pop(aid,None)

@bot.callback_query_handler(func=lambda call: call.data.startswith("seed_skip_") and is_admin(call.from_user.id))
def seed_skip_cb(call):
    safe_answer(call.id); sid=int(call.data.split("_")[-1])
    p=user_data.get(str(sid),{})
    _finalize_seed_profile(call.from_user.id,sid,p,call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("seedsave_") and is_admin(call.from_user.id))
def seedsave_cb(call):
    sid=int(call.data.split("_")[1]); p=user_data.get(str(sid),{})
    safe_answer(call.id); _finalize_seed_profile(call.from_user.id,sid,p,call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("seedmore_") and is_admin(call.from_user.id))
def seedmore_cb(call):
    safe_answer(call.id); bot.send_message(call.message.chat.id,"📸 Send the next photo:")

def _finalize_seed_profile(aid,sid,p,chat_id):
    p.update({"user_id":sid,"username":f"seed_{sid}","chat_id":None,"active":True,"verified":True,
        "plan":"👑 Platinum","plan_price":0,"profile_complete":True,"is_seed":True,
        "joined_at":datetime.now().isoformat(),"last_active":datetime.now().isoformat(),
        "blocked_users":[],"language":DEFAULT_LANG})
    with data_lock: user_data[str(sid)]=p; save_all_data()
    admin_creating_seed.pop(aid,None); admin_creating_lady.pop(aid,None)
    score=get_profile_score(p); photos=len(p.get("photos",[]))
    markup=types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🟢 Toggle Active",callback_data=f"seedtoggle_{sid}"),
               types.InlineKeyboardButton("🗑 Delete",callback_data=f"seeddelete_{sid}"))
    markup.add(types.InlineKeyboardButton("📋 List All",callback_data="seed_list_all"),
               types.InlineKeyboardButton("➕ Add Another",callback_data="seed_add_another"))
    bot.send_message(chat_id,
        f"✅ <b>Seed Profile Created!</b>\n\n"
        f"👤 <b>{esc(p.get('name'))}</b> ✅\n"
        f"{esc(p.get('gender_display',''))} • {p.get('age')} yrs • 📍 {esc(p.get('city',''))}\n"
        f"{esc(p.get('looking_for_display',''))}\n\n"
        f"🎯 {esc(', '.join(p.get('hobbies',[])[:4]))}\n"
        f"📝 <i>{esc(p.get('bio',''))}</i>\n"
        f"📸 {photos} photos | 📊 Score: {score}%\n"
        f"ID: <code>{sid}</code>\n\n"
        f"This profile now appears in matches! 💕",
        parse_mode="HTML",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("seedtoggle_") and is_admin(call.from_user.id))
def seedtoggle_cb(call):
    safe_answer(call.id); sid=int(call.data.split("_")[1]); p=get_user_profile(sid)
    if not p: bot.send_message(call.message.chat.id,"❌ Not found."); return
    p["active"]=not p.get("active",True); update_user(sid,p)
    status="🟢 Active" if p["active"] else "🔴 Hidden"
    bot.send_message(call.message.chat.id,f"✅ {esc(p.get('name'))} is now {status}.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("seeddelete_") and is_admin(call.from_user.id))
def seeddelete_cb(call):
    safe_answer(call.id); sid=int(call.data.split("_")[1])
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Yes, delete",callback_data=f"seeddelconfirm_{sid}"),
               types.InlineKeyboardButton("❌ Cancel",callback_data="ignore"))
    bot.send_message(call.message.chat.id,f"Delete seed <code>{sid}</code>?",reply_markup=markup,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("seeddelconfirm_") and is_admin(call.from_user.id))
def seeddelconfirm_cb(call):
    safe_answer(call.id); sid=int(call.data.split("_")[1])
    with data_lock: user_data.pop(str(sid),None); save_all_data()
    bot.send_message(call.message.chat.id,f"🗑 Seed {sid} deleted.")

@bot.callback_query_handler(func=lambda call: call.data=="seed_list_all" and is_admin(call.from_user.id))
def seed_list_all_cb(call):
    safe_answer(call.id)
    seeds={k:v for k,v in user_data.items() if k.isdigit() and int(k)>=SEED_ID_PREFIX}
    if not seeds: bot.send_message(call.message.chat.id,"No seed profiles yet."); return
    msg=f"📋 <b>Seed Profiles ({len(seeds)})</b>\n\n"
    for uid,p in seeds.items():
        act="🟢" if p.get("active") else "🔴"
        msg+=f"{act} <b>{esc(p.get('name','?'))}</b> ✅ (ID: <code>{uid}</code>)\n   {esc(p.get('gender_display',''))} • {p.get('age')} yrs • {esc(p.get('city',''))}\n   Photos: {len(p.get('photos',[]))} | Score: {get_profile_score(p)}%\n\n"
    bot.send_message(call.message.chat.id,msg,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data=="seed_add_another" and is_admin(call.from_user.id))
def seed_add_another_cb(call):
    safe_answer(call.id)
    sid=get_next_seed_id(); admin_creating_seed[call.from_user.id]={"seed_id":sid,"step":"name"}
    bot.send_message(call.message.chat.id,
        f"👤 <b>Create Another Seed Profile</b>\n\nNew ID: <code>{sid}</code>\n\n<b>Step 1 — Name:</b>",
        parse_mode="HTML",reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=["listprofiles"])
def admin_list_profiles(message):
    if not is_admin(message.from_user.id): return
    seeds={k:v for k,v in user_data.items() if k.isdigit() and int(k)>=SEED_ID_PREFIX}
    if not seeds: bot.send_message(message.chat.id,"📋 No seed profiles.\n\nUse /addprofile to create one."); return
    msg=f"📋 <b>Seed Profiles ({len(seeds)})</b>\n\n"
    markup=types.InlineKeyboardMarkup()
    for uid,p in seeds.items():
        act="🟢" if p.get("active") else "🔴"
        msg+=f"{act} <b>{esc(p.get('name','?'))}</b> ✅ (ID: <code>{uid}</code>)\n   {esc(p.get('gender_display',''))} • {p.get('age')} yrs • {esc(p.get('city',''))}\n   Photos: {len(p.get('photos',[]))} | Score: {get_profile_score(p)}%\n\n"
    markup.add(types.InlineKeyboardButton("➕ Add Profile",callback_data="seed_add_another"))
    bot.send_message(message.chat.id,msg,reply_markup=markup,parse_mode="HTML")

# ── Admin options menu ──
@bot.message_handler(func=lambda msg: msg.text and msg.text.strip().lower()=='options' and is_admin(msg.from_user.id))
def admin_options_menu(message):
    markup=types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("➕ Add Admin",callback_data="opt_add_admin"),
               types.InlineKeyboardButton("➖ Remove Admin",callback_data="opt_remove_admin"))
    markup.add(types.InlineKeyboardButton("👩 Add Lady",callback_data="opt_addlady"),
               types.InlineKeyboardButton("📋 List Profiles",callback_data="seed_list_all"))
    markup.add(types.InlineKeyboardButton("📜 List Admins",callback_data="opt_list_admins"),
               types.InlineKeyboardButton("📊 Stats",callback_data="opt_stats"))
    bot.send_message(message.chat.id,"⚙️ <b>Admin Panel</b>",reply_markup=markup,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("opt_") and is_admin(call.from_user.id))
def handle_opt_cb(call):
    aid=call.from_user.id; safe_answer(call.id)
    if call.data=="opt_add_admin":
        admin_pending_actions[aid]={"action":"add_admin"}
        bot.send_message(aid,"Send numeric Telegram ID to add as admin:")
    elif call.data=="opt_remove_admin":
        admin_pending_actions[aid]={"action":"remove_admin"}
        bot.send_message(aid,"Send numeric Telegram ID to remove from admins:")
    elif call.data=="opt_addlady":
        bot.send_message(aid,"Use /addlady to quickly add a lady profile.")
    elif call.data=="opt_list_admins":
        bot.send_message(aid,"👑 Admins:\n"+"\n".join(f"• {x}" for x in ADMIN_IDS))
    elif call.data=="opt_stats":
        admin_stats_inner(aid)

@bot.callback_query_handler(func=lambda call: call.data=="ignore")
def ignore_cb2(call): safe_answer(call.id)
# ═══════════════════ ADMIN COMMANDS ═══════════════════
def admin_stats_inner(chat_id):
    total=len(user_data); seeds=sum(1 for u in user_data.values() if u.get("is_seed"))
    paid=sum(1 for u in user_data.values() if u.get("plan_price",0)>0 and not u.get("is_seed"))
    revenue=sum(u.get("plan_price",0) for u in user_data.values())
    complete=sum(1 for u in user_data.values() if u.get("profile_complete") and not u.get("is_seed"))
    today=datetime.now().strftime("%Y-%m-%d")
    active=sum(1 for u in user_data.values() if u.get("last_active","")[:10]==today and not u.get("is_seed"))
    bot.send_message(chat_id,
        f"📊 <b>Bot Statistics</b>\n\n"
        f"👥 Real Users: {total-seeds} | 🎭 Seeds: {seeds}\n"
        f"✅ Complete Profiles: {complete}\n"
        f"💰 Paid Users: {paid}\n"
        f"💵 Revenue: ₹{revenue}\n"
        f"🟢 Active Today: {active}\n"
        f"⏳ Pending Payments: {len(pending_payments)}\n\n"
        f"📈 Analytics:\n"
        f"  Signups: {analytics['free_signups']}\n"
        f"  Profiles Created: {analytics['profiles_created']}\n"
        f"  Matches Shown: {analytics['matches_shown']}\n"
        f"  Matches Made: {analytics['matches_made']}\n"
        f"  Super Likes: {analytics['super_likes']}\n"
        f"  Boosts: {analytics['boosts_used']}\n"
        f"  Approved Payments: {analytics['payments_approved']}",
        parse_mode="HTML")

@bot.message_handler(commands=['stats'])
def admin_stats(message):
    if not is_admin(message.from_user.id): return
    admin_stats_inner(message.chat.id)

@bot.message_handler(commands=['broadcast'])
def admin_broadcast(message):
    if not is_admin(message.from_user.id): return
    text=message.text.replace("/broadcast","").strip()
    if not text: bot.send_message(message.chat.id,"Usage: /broadcast message"); return
    sent=failed=0
    for uid,p in user_data.items():
        if p.get("is_seed"): continue
        try:
            bot.send_message(p.get("chat_id"),f"📢 <b>Announcement</b>\n\n{text}",parse_mode="HTML")
            sent+=1; time.sleep(0.05)
        except Exception: failed+=1
    bot.send_message(message.chat.id,f"📢 Done!\n✅ Sent: {sent}\n❌ Failed: {failed}")

@bot.message_handler(commands=['pending'])
def admin_pending(message):
    if not is_admin(message.from_user.id): return
    if not pending_payments: bot.send_message(message.chat.id,"✅ No pending payments!"); return
    msg="⏳ <b>Pending Payments:</b>\n\n"
    for uid,p in pending_payments.items():
        msg+=f"{esc(p.get('username','?'))} — {p.get('plan')} — ₹{p.get('price')}\n"
    bot.send_message(message.chat.id,msg,parse_mode="HTML")

@bot.message_handler(commands=['reply'])
def admin_reply(message):
    if not is_admin(message.from_user.id): return
    parts=message.text.split(maxsplit=2)
    if len(parts)<3: bot.send_message(message.chat.id,"Usage: /reply <user_id> <message>"); return
    try: tid=int(parts[1])
    except ValueError: bot.send_message(message.chat.id,"❌ Numeric user ID required."); return
    tp=get_user_profile(tid)
    if not tp: bot.send_message(message.chat.id,f"❌ No user {tid}."); return
    tc=tp.get('chat_id')
    if not tc: bot.send_message(message.chat.id,f"❌ No chat_id for {tid}."); return
    bot.send_message(tc,parts[2].strip())
    bot.send_message(message.chat.id,f"✅ Sent to user {tid}.")
    support_requests.pop(str(tid),None)

@bot.message_handler(commands=['replyas'])
def admin_replyas(message):
    if not is_admin(message.from_user.id): return
    parts=message.text.split(maxsplit=3)
    if len(parts)<4:
        bot.send_message(message.chat.id,
            "Usage: <code>/replyas &lt;seed_id&gt; &lt;user_id&gt; &lt;message&gt;</code>",parse_mode="HTML"); return
    try: sid,uid=int(parts[1]),int(parts[2])
    except ValueError: bot.send_message(message.chat.id,"❌ Numeric IDs required."); return
    sp=get_user_profile(sid); up=get_user_profile(uid)
    if not sp or not sp.get('is_seed'): bot.send_message(message.chat.id,f"❌ No seed {sid}."); return
    if not up: bot.send_message(message.chat.id,f"❌ No user {uid}."); return
    tc=up.get('chat_id')
    if not tc: bot.send_message(message.chat.id,f"❌ No chat_id for {uid}."); return
    bot.send_message(tc,parts[3].strip())  # plain text, no header
    sname=esc(sp.get('name') or f"Seed {sid}")
    bot.send_message(message.chat.id,f"✅ Sent as <b>{sname}</b>",parse_mode="HTML")
    ck=f"chat_{min(sid,uid)}_{max(sid,uid)}"
    with data_lock:
        if ck not in active_chats:
            active_chats[ck]={"user1":min(sid,uid),"user2":max(sid,uid),"started_at":datetime.now().isoformat(),"messages":0}
        active_chats[ck]["messages"]=active_chats[ck].get("messages",0)+1; save_all_data()

@bot.callback_query_handler(func=lambda call: call.data.startswith("replyas_prompt_") and is_admin(call.from_user.id))
def replyas_prompt_cb(call):
    safe_answer(call.id)
    try:
        parts=call.data.split("_")
        sid=int(parts[2]); uid=int(parts[3])
    except Exception: bot.send_message(call.message.chat.id,"❌ Could not parse IDs."); return
    sp=get_user_profile(sid); up=get_user_profile(uid)
    sname=esc(sp.get('name') or f"Seed {sid}"); uname=esc(up.get('name') or f"User {uid}")
    admin_replyas_context[call.from_user.id]={"seed_id":sid,"user_id":uid,"seed_name":sname}
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔴 Exit character mode",callback_data="stopreplyas_btn"))
    bot.send_message(call.message.chat.id,
        f"🎭 <b>Character mode ON</b>\n\n"
        f"Replying as: <b>{sname}</b>\nTalking to: <b>{uname}</b>\n\n"
        f"Every message you type → sent as {sname}.\n\n"
        f"Tap button below to exit.",parse_mode="HTML",reply_markup=markup)

@bot.message_handler(commands=['stopreplyas'])
def stopreplyas_cmd(message):
    if not is_admin(message.from_user.id): return
    ctx=admin_replyas_context.pop(message.from_user.id,None)
    if ctx: bot.send_message(message.chat.id,f"✅ Exited character mode for <b>{ctx['seed_name']}</b>.",parse_mode="HTML")
    else: bot.send_message(message.chat.id,"ℹ️ Not in character mode.")

# ═══════════════════ BLOCK / UNBLOCK ═══════════════════
@bot.message_handler(commands=['block'])
def block_cmd(message):
    uid=message.from_user.id; parts=message.text.strip().split()
    if len(parts)<2: bot.send_message(message.chat.id,"Usage: /block <user_id>"); return
    try: tid=int(parts[1])
    except ValueError: bot.send_message(message.chat.id,"❌ Numeric user ID."); return
    p=get_user_profile(uid); bl=p.get("blocked_users",[])
    if tid not in bl:
        bl.append(tid); p["blocked_users"]=bl; update_user(uid,p)
        bot.send_message(message.chat.id,"🚫 User blocked. They won't appear in your matches.")
    else: bot.send_message(message.chat.id,"ℹ️ Already blocked.")

@bot.message_handler(commands=['unblock'])
def unblock_cmd(message):
    uid=message.from_user.id; parts=message.text.strip().split()
    if len(parts)<2: bot.send_message(message.chat.id,"Usage: /unblock <user_id>"); return
    try: tid=int(parts[1])
    except ValueError: bot.send_message(message.chat.id,"❌ Numeric user ID."); return
    p=get_user_profile(uid); bl=p.get("blocked_users",[])
    if tid in bl:
        bl.remove(tid); p["blocked_users"]=bl; update_user(uid,p)
        bot.send_message(message.chat.id,"✅ Unblocked.")
    else: bot.send_message(message.chat.id,"ℹ️ Not in block list.")

# ═══════════════════ WHO LIKED ME ═══════════════════
@bot.message_handler(commands=['wholikedme'])
def who_liked_me(message):
    uid=message.from_user.id; limits=get_plan_limits(uid)
    if not limits.get("see_who_liked"):
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬆️ Upgrade to Gold/Platinum",callback_data="cb_upgrade"))
        bot.send_message(message.chat.id,"👁 <b>Who Liked Me</b>\n\nAvailable on 💎 Gold & 👑 Platinum only.",
            reply_markup=markup,parse_mode="HTML"); return
    likers=[]
    for luid,ld in pending_likes.items():
        if str(uid) in ld:
            lp=get_user_profile(int(luid))
            if lp: likers.append(lp)
    if not likers: bot.send_message(message.chat.id,"💔 No likes yet. Keep matching!"); return
    msg=f"👁 <b>{len(likers)} people liked you!</b>\n\n"
    for lp in likers[:10]:
        v=" ✅" if lp.get("verified") else ""
        msg+=f"• <b>{esc(lp.get('name','User'))}</b>{v} — {lp.get('age')} yrs, {esc(lp.get('city',''))}\n"
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💞 Find Matches Now",callback_data="goto_findmatch"))
    bot.send_message(message.chat.id,msg,reply_markup=markup,parse_mode="HTML")

# ═══════════════════ SUPPORT ═══════════════════
@bot.message_handler(commands=['support'])
def support_cmd(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    p['support_mode']=True; update_user(uid,p)
    bot.send_message(message.chat.id,
        "🆘 <b>Support</b>\n\nDescribe your issue and we'll reply here in the app.\n\n/cancel to cancel",
        parse_mode="HTML",reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda msg: (
    msg.text and not msg.text.startswith('/') and
    get_user_profile(msg.from_user.id).get('support_mode') and not admin_in_wizard(msg.from_user.id)
))
def handle_support(message):
    uid=message.from_user.id; p=get_user_profile(uid)
    p.pop('support_mode',None); update_user(uid,p)
    support_requests[str(uid)]={'chat_id':message.chat.id,'message':message.text,'time':datetime.now().isoformat()}
    bot.send_message(message.chat.id,"✅ Support request sent! We'll reply here soon.")
    name=esc(p.get('name','?'))
    for at in ADMIN_IDS:
        try:
            bot.send_message(at,
                f"🆘 <b>Support Request</b>\n\nFrom: <b>{name}</b> (ID: <code>{uid}</code>)\n\n"
                f"{esc(message.text)}\n\nReply: /reply {uid} your message",parse_mode="HTML")
        except Exception as e: logger.error(f"support notify {at}: {e}")

# ═══════════════════ HELP ═══════════════════
@bot.message_handler(commands=['help'])
def help_cmd(message):
    markup=types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("💞 Find Match",callback_data="goto_findmatch"),
               types.InlineKeyboardButton("👤 My Profile",callback_data="goto_profile"))
    markup.add(types.InlineKeyboardButton("💬 Messages",callback_data="set_recap"),
               types.InlineKeyboardButton("⚙️ Settings",callback_data="set_myplan"))
    markup.add(types.InlineKeyboardButton("⬆️ Upgrade Plan",callback_data="cb_upgrade"),
               types.InlineKeyboardButton("🆘 Support",callback_data="set_support"))
    bot.send_message(message.chat.id,
        "🆘 <b>Help — Real Dating Bot</b>\n\n"
        "<b>Keyboard buttons:</b>\n"
        "💞 Find Match — Browse & like profiles\n"
        "⭐ Super Like — Send a special like\n"
        "📸 Add Photos — Upload profile photos\n"
        "💬 Messages — Chat with your matches\n"
        "🚀 Boost — Be seen by more people (Gold+)\n"
        "🏆 Leaderboard — Top profiles\n"
        "👤 My Profile — View & edit everything\n"
        "⚙️ Settings — Plan, language, referral\n\n"
        "<b>Commands:</b>\n"
        "/start — Restart the bot\n"
        "/cancel — Cancel any current action\n"
        "/endchat — End an in-app chat\n"
        "/wholikedme — See who liked you (Gold+)\n"
        "/block &lt;id&gt; — Block a user\n"
        "/unblock &lt;id&gt; — Unblock a user\n"
        "/support — Contact support\n"
        "/icebreaker — Get a conversation starter\n"
        "/recap — Today's activity summary\n"
        "/help — This message\n\n"
        f"Support: {ADMIN_USERNAME}",
        reply_markup=markup,parse_mode="HTML")

@bot.message_handler(commands=['icebreaker'])
def icebreaker_cmd(message):
    q=random.choice(ICEBREAKERS)
    bot.send_message(message.chat.id,f"💬 <b>Icebreaker</b>\n\n<i>{q}</i>\n\nShare with your match!",parse_mode="HTML")

@bot.message_handler(commands=['recap'])
def recap_cmd(message):
    _daily_recap_inner(message.chat.id,message.from_user.id)

# ═══════════════════ ACTIVITY TRACKING ═══════════════════
def update_last_active(uid):
    p=get_user_profile(uid)
    if p: p["last_active"]=datetime.now().isoformat(); update_user(uid,p)

@bot.middleware_handler(update_types=['message'])
def track_activity(bot_instance,message):
    if message.from_user:
        threading.Thread(target=update_last_active,args=(message.from_user.id,),daemon=True).start()

# ═══════════════════ BACKGROUND TASKS ═══════════════════
def match_expiry_task():
    while True:
        now=datetime.now()
        to_del=[k for k,info in list(active_chats.items())
            if info.get("messages",0)==0 and
            (now-datetime.fromisoformat(info.get("started_at",now.isoformat()))).total_seconds()>MATCH_EXPIRY_HOURS*3600]
        if to_del:
            with data_lock:
                for k in to_del: active_chats.pop(k,None)
                save_all_data()
            logger.info(f"Cleaned {len(to_del)} expired matches")
        time.sleep(3600)

def weekly_reminder_task():
    while True:
        now=datetime.now()
        if now.weekday()==0 and now.hour==9 and now.minute==0:
            for uid,p in list(user_data.items()):
                if not p.get("active") or not p.get("profile_complete") or p.get("is_seed"): continue
                try:
                    last=datetime.fromisoformat(p.get("last_active",""))
                    if (now-last).days>=7:
                        bot.send_message(p.get("chat_id"),
                            f"👋 <b>Hey {esc(p.get('name','there'))}!</b>\n\nNew people are waiting to match with you! 💕\n\nTap 💞 Find Match to get back!",
                            parse_mode="HTML")
                except Exception: pass
            time.sleep(61)
        else: time.sleep(30)

def daily_icebreaker_task():
    while True:
        now=datetime.now()
        if now.hour==10 and now.minute==0:
            q=random.choice(ICEBREAKERS)
            for uid,p in user_data.items():
                if not p.get("active") or p.get("is_seed"): continue
                if any(int(uid) in [c.get("user1"),c.get("user2")] for c in active_chats.values()):
                    try: bot.send_message(p.get("chat_id"),f"💬 <b>Daily Icebreaker</b>\n\n<i>{q}</i>\n\nShare with your match!",parse_mode="HTML")
                    except Exception: pass
            time.sleep(61)
        else: time.sleep(30)

def expiry_reminder_task():
    while True:
        now=datetime.now()
        for uid,p in user_data.items():
            if p.get("is_seed"): continue
            es=p.get("plan_expires")
            if not es: continue
            try:
                dl=(datetime.fromisoformat(es)-now).days
                if dl in (3,1):
                    today=now.strftime("%Y-%m-%d")
                    if p.get("last_expiry_reminder","")!=today:
                        bot.send_message(p.get("chat_id"),
                            f"⏰ <b>Plan expires in {dl} day(s)!</b>\n\nRenew to keep matching 💕",parse_mode="HTML")
                        p["last_expiry_reminder"]=today; update_user(int(uid),p)
            except Exception: pass
        time.sleep(3600)

# ═══════════════════ LAUNCH ═══════════════════
if __name__=="__main__":
    load_all_data()
    for task in [daily_icebreaker_task,expiry_reminder_task,match_expiry_task,weekly_reminder_task]:
        threading.Thread(target=task,daemon=True).start()
    logger.info(f"✅ Dating Bot v5.0 started | {len(user_data)} users")
    print(f"""
╔══════════════════════════════════════════════════════╗
║       💕 REAL DATING BOT v5.0 — LIVE!               ║
║                                                      ║
║  Users   : {len(user_data):<6}  Seeds: {sum(1 for u in user_data.values() if u.get('is_seed')):<6}              ║
║  Revenue : ₹{sum(u.get('plan_price',0) for u in user_data.values()):<6}                             ║
║  Pending : {len(pending_payments):<6}                              ║
║                                                      ║
║  v5.0 Key Fixes:                                     ║
║  • Character mode registered first (no interception) ║
║  • Plain text delivery in all chat paths             ║
║  • Inline hobby picker (no typing numbers)           ║
║  • /cancel to unstick any state                      ║
║  • All management via inline buttons                 ║
║  • Seed profiles route to admin perfectly            ║
╚══════════════════════════════════════════════════════╝
    """)
    try:
        bot.infinity_polling(timeout=60,long_polling_timeout=20,interval=0,
            allowed_updates=['message','callback_query'])
    except Exception as e: logger.error(f"Bot error: {e}")
