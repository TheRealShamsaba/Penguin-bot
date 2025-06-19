from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler,
)
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import time, timezone
import uuid
# from transcribe import transcribe_voice
import os
from dotenv import load_dotenv
from huggingface_wrapper import get_roast_hf as get_roast
import random
from tts import text_to_speech
from telegram import Voice
import asyncio

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

user_contexts = {} # stores / setup descriptions per user
registered_users = set()  # users who want daily motivational roasts


async def play_roast_voice(update, roast):
    try:
        audio_file = text_to_speech(roast)
        with open(audio_file, "rb") as audio:
            await update.message.reply_voice(audio)
        os.remove(audio_file)
    except Exception as e:
        await update.message.reply_text(f"[Penguin voice failed: {str(e)}]")
        print(f"[play_roast_voice ERROR] {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🔥 Roast me")],
        [KeyboardButton("🧠 Set context")],
        [KeyboardButton("🎯 Daily Motivation")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)
    await update.message.reply_text(
        "Welcome to Penguin. Pick your poison:", reply_markup=reply_markup
    )
    await update.message.reply_text("Before we begin… what's your name?")
    context.user_data["awaiting_name"] = True

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    context_info = user_contexts.get(user_id, "")

    if query.data == "roast":
        roast = get_roast("roast me", context_info)
        await query.edit_message_text(f"🐧 Penguin says:\n\n{roast}")
    elif query.data == "motivate":
        keyboard = [
            [InlineKeyboardButton("🔥 Brutal", callback_data="tone_brutal")],
            [InlineKeyboardButton("🧨 Degrading", callback_data="tone_degrading")],
            [InlineKeyboardButton("🧠 Straight Talk", callback_data="tone_straight")]
        ]
        await query.edit_message_text("Choose your motivation tone:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith("tone_"):
        context.user_data["tone"] = query.data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Every 30 min", callback_data="freq_30min")],
            [InlineKeyboardButton("Every hour", callback_data="freq_1hour")],
            [InlineKeyboardButton("Every day", callback_data="freq_daily")],
            [InlineKeyboardButton("Nevermind", callback_data="cancel_motivate")]
        ]
        await query.edit_message_text("How often do you want to be roasted?", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith("freq_"):
        freq = query.data.split("_")[1]
        await query.edit_message_text(f"You're all set. Penguin will roast you every {freq.replace('min', ' minutes').replace('hour', ' hour').replace('daily', 'day')}.")
    elif query.data == "cancel_motivate":
        await query.edit_message_text("Motivation setup cancelled. Coward.")
    elif query.data == "setup":
        await query.edit_message_text("Send /setup followed by your personality description.")
    elif query.data.startswith("persona_"):
        context.user_data["persona"] = query.data.split("_")[1]
        await query.edit_message_text(f"Penguin now speaks in {context.user_data['persona']} mode.")

async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_context = " ".join(context.args)
    user_contexts[user_id] = user_context
    await update.message.reply_text("Context saved. Penguin will use this to roast you more personally.")

async def chaosmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chaos"] = not context.user_data.get("chaos", False)
    status = "ON" if context.user_data["chaos"] else "OFF"
    await update.message.reply_text(f"💥 Chaos Mode is now {status}. Brace yourself.")

async def persona(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👑 Royal Penguin", callback_data="persona_royal")],
        [InlineKeyboardButton("😈 Demon Penguin", callback_data="persona_demon")],
        [InlineKeyboardButton("🤠 Cowboy Penguin", callback_data="persona_cowboy")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose Penguin's vibe:", reply_markup=reply_markup)

async def notifyme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    registered_users.add(user_id)
    await update.message.reply_text(
        "Penguin will drop a daily motivational roast in your DMs. Brace yourself."
    )

    
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    context_info = user_contexts.get(user_id, "")

    file = await context.bot.get_file(update.message.voice.file_id)
    ogg_path = f"temp_{uuid.uuid4()}.ogg"
    await file.download_to_drive(ogg_path)

    try:
        transcribed_text = transcribe_voice(ogg_path)
        os.remove(ogg_path)
        roast = get_roast(transcribed_text, context_info)
        await update.message.reply_text(f"🎙️ You said: {transcribed_text}\n\n🐧 Penguin says: {roast}")
        asyncio.create_task(play_roast_voice(update, roast))
    except Exception as e:
        await update.message.reply_text(f"🐧 Penguin froze: {str(e)}")
        print(f"[handle_voice ERROR] {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("conversation_mode", False):
        return  # ignore input unless in conversation

    text = update.message.text.lower()
    if "i love you" in text:
        await update.message.reply_text("Cringe. But ok. I love you too, loser.")
        return
    elif "kill me" in text:
        await update.message.reply_text("Already spiritually dead, but sure.")
        return
    elif "stop" in text:
        await update.message.reply_text("You came to a roast bot to quit now? That’s peak pathetic.")
        return

    if context.user_data.get("awaiting_name"):
        context.user_data["name"] = update.message.text.strip()
        context.user_data["awaiting_name"] = False
        context.user_data["conversation_mode"] = True
        await update.message.reply_text(f"Got it. I'll remember that, {context.user_data['name']}. Now talk to me like a human.")
        return

    user_id = str(update.message.from_user.id)
    user_input = update.message.text
    context_info = user_contexts.get(user_id, "")

    if user_input not in ["🔥 Roast me", "🧠 Set Context", "🎯 Motivation"]:
        try:
            persona = context.user_data.get("persona", "")
            chaos = context.user_data.get("chaos", False)
            persona_tag = f"[Persona: {persona}]" if persona else ""
            chaos_tag = "[CHAOS MODE]" if chaos else ""
            roast = get_roast(f"{chaos_tag} {user_input}", f"{context_info} {persona_tag}")
            name = context.user_data.get("name", "you")
            await update.message.reply_text(f"{roast} ({name})")
            audio_file = text_to_speech(roast)
            with open(audio_file, "rb") as audio:
                await update.message.reply_voice(audio)
            os.remove(audio_file)
        except Exception as e:
            await update.message.reply_text(f"🐧 Penguin choked: {str(e)}")
            print(f"[handle_message ERROR] {str(e)}")
    else:
        context.user_data["conversation_mode"] = True

async def send_daily_roasts(context: ContextTypes.DEFAULT_TYPE):
    for user_id in list(registered_users):
        roast = get_roast("motivation time", "")
        await context.bot.send_message(chat_id=user_id, text=roast)
        try:
            audio_file = text_to_speech(roast)
            with open(audio_file, "rb") as audio:
                await context.bot.send_voice(chat_id=user_id, voice=audio)
            os.remove(audio_file)
        except Exception as e:
            await context.bot.send_message(
                chat_id=user_id, text=f"[Penguin voice failed: {str(e)}]"
            )


if __name__ == "__main__":
    import asyncio

    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setup", setup))
    app.add_handler(CommandHandler("notifyme", notifyme))
    app.add_handler(CommandHandler("chaosmode", chaosmode))
    app.add_handler(CommandHandler("persona", persona))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(CallbackQueryHandler(menu_callback))

    if app.job_queue:
        app.job_queue.run_daily(
            send_daily_roasts, time=time(hour=0, minute=30, tzinfo=timezone.utc)
        )
    else:
        print("⚠️ JobQueue not available. Install with: pip install python-telegram-bot[job-queue]")

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8443)),
        webhook_url=os.getenv("WEBHOOK_URL")
    )
