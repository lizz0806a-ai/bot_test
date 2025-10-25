
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

TOKEN = "8460671823:AAEWD0YzQu_0uo1ZdCnokSvD7u2V8D8FCO8"

team_data = {}
current_break = {}  # To remember what break the user is on

def record_time(user, category=None):
    now = datetime.now()

    if user not in team_data:
        team_data[user] = {"in": None, "out": None, "food": [], "washroom": []}

    if category == "in":
        team_data[user]["in"] = now.strftime("%H:%M:%S")
        return f"🟢 {user} **arrived at** {team_data[user]['in']} 🎉 Welcome!"
    elif category == "out":
        team_data[user]["out"] = now.strftime("%H:%M:%S")
        return f"🔴 {user} **left at** {team_data[user]['out']} 💼 Good work today!"
    elif category in ["food", "washroom"]:
        if user in current_break:
            return f"⚠️ {user}, you are already on a break ({current_break[user]})!"
        current_break[user] = category
        if category == "food":
            team_data[user]["food"].append({"start": now, "end": None, "minutes": 0})
            return f"🍴 {user} **started food break at** {now.strftime('%H:%M:%S')} 😋 Enjoy your meal!"
        else:
            team_data[user]["washroom"].append({"start": now, "end": None, "minutes": 0})
            return f"🚻 {user} **started washroom break at** {now.strftime('%H:%M:%S')} ⏱️"
    elif category == "back":
        if user not in current_break:
            return f"⚠️ {user}, you are not on any break!"
        btype = current_break[user]
        if btype == "food":
            start_time = team_data[user]["food"][-1]["start"]
            team_data[user]["food"][-1]["end"] = now
            minutes = int((now - start_time).total_seconds() / 60)
            team_data[user]["food"][-1]["minutes"] = minutes
            del current_break[user]
            total_food = sum(b["minutes"] for b in team_data[user]["food"])
            return (f"✅ {user} **back from food break at** {now.strftime('%H:%M:%S')} 💪 Time spent: {minutes} min\n"
                    f"📊 Total food today: {total_food} min")
        else:
            start_time = team_data[user]["washroom"][-1]["start"]
            team_data[user]["washroom"][-1]["end"] = now
            minutes = int((now - start_time).total_seconds() / 60)
            team_data[user]["washroom"][-1]["minutes"] = minutes
            del current_break[user]
            total_washroom = sum(b["minutes"] for b in team_data[user]["washroom"])
            return (f"✅ {user} **back from washroom at** {now.strftime('%H:%M:%S')} 👍 Time spent: {minutes} min\n"
                    f"📊 Total washroom today: {total_washroom} min")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **Welcome to Team Tracker Bot!**\n\n"
        "Commands:\n"
        "🟢 /in - Punch in\n"
        "🔴 /out - Punch out\n"
        "🍴 /food - Start food break\n"
        "🚻 /washroom - Start washroom break\n"
        "✅ /back - Back from break (food or washroom, auto-report total time)",
        parse_mode='Markdown'
    )

async def punch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text[1:]
    user = update.message.from_user.first_name

    if cmd in ["in", "out"]:
        msg = record_time(user, cmd)
    elif cmd in ["food", "washroom"]:
        msg = record_time(user, cmd)
    elif cmd == "back":
        msg = record_time(user, "back")
    else:
        msg = "⚠️ Unknown command!"

    await update.message.reply_text(msg, parse_mode='Markdown')

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler(["in","out","food","washroom","back"], punch))

print("Bot is running…")
app.run_polling()

