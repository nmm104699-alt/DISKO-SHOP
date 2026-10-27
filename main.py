import os
import telebot
from telebot import types
from datetime import datetime

TOKEN = os.environ.get("TOKEN", "ضع_التوكن_هنا")
bot = telebot.TeleBot(TOKEN)

# قواعد البيانات المؤقتة في الذاكرة
user_data = {}

# أسعار الخطط لمنتج AIM DISKO (الساعة أصبحت بـ 6 نقاط)
PLANS = {
    "1 hour": {"name": "1 hour", "points": 6, "stock": 5},
    "3 hours": {"name": "3 hours", "points": 12, "stock": 2},
    "6 hours": {"name": "6 hours", "points": 20, "stock": 1},
    "1 DAY": {"name": "1 DAY", "points": 35, "stock": 1},
    "3 DAY": {"name": "3 DAY", "points": 45, "stock": 0}
}

def get_user(user_id, username="User"):
    user_id = str(user_id)
    if user_id not in user_data:
        user_data[user_id] = {
            "name": username,
            "points": 10,  # رصيد ابتدائي للتجربة
            "orders": [],
            "referrals": 0,
            "rewards_earned": 0,
            "joined": datetime.now().strftime("%Y-%m-%d")
        }
    return user_data[user_id]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split()
    user_id = str(message.from_user.id)
    username = message.from_user.first_name or "User"
    
    user = get_user(user_id, username)

    # نظام الإحالة (عضو جديد عبر رابط صديقه)
    if len(args) > 1:
        ref_id = args[1]
        if ref_id in user_data and ref_id != user_id:
            # التأكد أن المستخدم جديد ولم يسجل من قبل عبر إحالة
            if "referred_by" not in user:
                user["referred_by"] = ref_id
                user_data[ref_id]["points"] += 1  # يربح المعزُّز نقطة واحدة
                user_data[ref_id]["referrals"] += 1
                user_data[ref_id]["rewards_earned"] += 1
                try:
                    bot.send_message(ref_id, "🎉 **مرحباً! لقد انضم شخص جديد عبر رابط الدعوة الخاص بك وحصلت على +1 نقطة!**", parse_mode="Markdown")
                except:
                    pass

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_shop = types.KeyboardButton("🛍️ SHOP")
    btn_profile = types.KeyboardButton("👤 PROFILE")
    btn_myshop = types.KeyboardButton("📦 MY SHOP")
    btn_points = types.KeyboardButton("⭐ MY POINTS")
    btn_ref = types.KeyboardButton("🎁 REFERRAL")
    markup.add(btn_shop, btn_profile, btn_myshop, btn_points, btn_ref)

    welcome_text = (
        "🛒 **DISKO SHOP**\n\n"
        "✨ **Available Products**\n\n"
        "💎 **AIM DISKO**\n"
        "⚡ Instant Delivery\n"
        "🔒 Secure Payment\n"
        "📞 24/7 Support\n\n"
        "👇 Select an option below to continue:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = str(message.from_user.id)
    username = message.from_user.first_name or "User"
    user = get_user(user_id, username)

    if message.text == "🛍️ SHOP":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🎯 AIM DISKO | 🛒 View Plans", callback_data="view_aim_plans"))
        bot.send_message(message.chat.id, "🛒 **CHOOSE YOUR GAME / PRODUCT:**", reply_markup=markup, parse_mode="Markdown")

    elif message.text == "👤 PROFILE":
        profile_text = (
            f"👤 **— YOUR PROFILE —**\n\n"
            f"🆔 **User ID:** `{user_id}`\n"
            f"👑 **Name:** {user['name']}\n\n"
            f"💰 **— POINTS —**\n"
            f"Current Balance: **{user['points']} Points**\n\n"
            f"📊 **— STATISTICS —**\n"
            f"📦 Orders: {len(user['orders'])}\n"
            f"👥 Referrals: {user['referrals']}\n"
            f"🎁 Rewards Earned: {user['rewards_earned']}\n\n"
            f"📅 Joined: {user['joined']}"
        )
        bot.send_message(message.chat.id, profile_text, parse_mode="Markdown")

    elif message.text == "📦 MY SHOP":
        orders = user["orders"]
        if not orders:
            bot.send_message(message.chat.id, "📦 **MY ORDERS**\n\nليس لديك أي طلبات سابقة حتى الآن.", parse_mode="Markdown")
        else:
            orders_text = "🛍️ **— MY ORDERS —**\n\n"
            for order in orders:
                status_icon = "🟢" if order['status'] == "Delivered" else "🔴"
                orders_text += (
                    f"📦 **AIM DISKO / APKMOD**\n"
                    f"⏱️ Plan: {order['plan']}\n"
                    f"💎 Order ID: `#{order['id']}`\n"
                    f"{status_icon} Status: {order['status']}\n"
                    f"🔑 Product Key\n`{order['key']}`\n"
                    f"🕒 Date: {order['date']}\n"
                    f"-----------------------------------\n"
                )
            bot.send_message(message.chat.id, orders_text, parse_mode="Markdown")

    elif message.text == "⭐ MY POINTS":
        bot.send_message(message.chat.id, f"💰 **YOUR BALANCE**\n\nCurrent Balance: **{user['points']} Points**", parse_mode="Markdown")

    elif message.text == "🎁 REFERRAL":
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        ref_text = (
            f"🔗 **YOUR REFERRAL LINK**\n\n"
            f"Invite friends using your personal link.\n\n"
            f"🎁 **Reward**\n"
            f"**1 Point** for each eligible referral.\n\n"
            f"Your link:\n`{ref_link}`"
        )
        bot.send_message(message.chat.id, ref_text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = str(call.from_user.id)
    username = call.from_user.first_name or "User"
    user = get_user(user_id, username)

    if call.data == "view_aim_plans":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, plan in PLANS.items():
            stock_status = f"Stock: {plan['stock']}" if plan['stock'] > 0 else "OUT OF STOCK"
            btn_text = f"🔴 {plan['name']} — {stock_status} | 💰 {plan['points']} Points" if plan['stock'] == 0 else f"🟢 {plan['name']} — Stock: {plan['stock']} | 💰 {plan['points']} Points"
            markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"buy_{key}"))
        
        markup.add(types.InlineKeyboardButton("🔙 BACK TO STORE", callback_data="back_to_store"))
        
        text = "🎯 **AIM DISKO — SELECT YOUR PLAN**\nSelect the plan you want below:"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("buy_"):
        plan_key = call.data.replace("buy_", "")
        plan = PLANS.get(plan_key)

        if not plan:
            return

        if plan["stock"] <= 0:
            bot.answer_callback_query(call.id, "❌ عذراً، هذا المنتج غير متوفر حالياً (Out of Stock)!", show_alert=True)
            return

        if user["points"] < plan["points"]:
            bot.answer_callback_query(call.id, f"❌ رصيدك غير كافي! تحتاج إلى {plan["points"]} نقاط.", show_alert=True)
            return

خصم النقاط وإنشاء مفتاح وهمي
        user["points"] -= plan["points"]
        plan["stock"] -= 1
        
        dummy_key = f"DISKO-{user_id}-{int(datetime.now().timestamp())}"
        order_id = len(user["orders"]) + 50
        
        order_info = {
            "id": order_id,
            "plan": plan["name"],
            "key": dummy_key,
            "status": "Delivered",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        user["orders"].append(order_info)

        bot.answer_callback_query(call.id, "✅ تم الشراء بنجاح!")
        success_msg = (
            f"✅ **SUCCESSFUL PURCHASE!**\n\n"
            f"📦 Product: AIM DISKO\n"
            f"⏱️ Plan: {plan['name']}\n"
            f"🔑 Key:\n`{dummy_key}`\n\n"
            f"تم حفظ المفتاح في قسم (📦 MY SHOP)."
        )
        bot.send_message(call.message.chat.id, success_msg, parse_mode="Markdown")

    elif call.data == "back_to_store":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🎯 AIM DISKO | 🛒 View Plans", callback_data="view_aim_plans"))
        text = (
            "🛒 **DISKO SHOP**\n\n"
            "✨ **Available Products**\n\n"
            "💎 **AIM DISKO**\n"
            "⚡ Instant Delivery\n"
            "🔒 Secure Payment\n"
            "📞 24/7 Support\n\n"
            "👇 Select an option below to continue:"
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

print("Bot is running...")
bot.infinity_polling()
