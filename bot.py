from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram import Update
from datetime import time, timezone
import uuid
from transcribe import transcribe_voice
import os
from dotenv import load_dotenv
from huggingface_wrapper import get_roast_hf as get_roast
import random
from tts import text_to_speech
from telegram import Voice

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

user_contexts = {} # stores / setup descriptions per user
registered_users = set()  # users who want daily motivational roasts

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_messages = [
        "Welcome to Penguin. This isn't therapy. It's a roast session with consequences.",
        "You really hit /start? Bold. Let’s see if you can handle what’s coming.",
        "This bot was built to make you cry. Glad you're here."
    ]
    await update.message.reply_text(random.choice(welcome_messages))
    
async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_context = " ".join(context.args)
    user_contexts[user_id] = user_context
    await update.message.reply_text("Context saved. Penguin will use this to roast you more personally.")


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
    except Exception as e:
        await update.message.reply_text(f"Failed to process voice message: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_input = update.message.text
    context_info = user_contexts.get(user_id, "")
    roast = get_roast(user_input, context_info)
    
    await update.message.reply_text(roast)

    try:
        audio_file = text_to_speech(roast)
        with open(audio_file, "rb") as audio:
            await update.message.reply_voice(audio)
        os.remove(audio_file)
    except Exception as e:
        await update.message.reply_text(f"[Penguin voice failed: {str(e)}]")


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

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setup", setup))
app.add_handler(CommandHandler("notifyme", notifyme))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))

job_queue = app.job_queue
job_queue.run_daily(
    send_daily_roasts, time=time(hour=0, minute=30, tzinfo=timezone.utc)
)

if __name__ == "__main__":
    import asyncio
    from telegram.ext import ApplicationBuilder

    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Add your handlers like app.add_handler(...)

    app.run_polling()

app.run_polling()
