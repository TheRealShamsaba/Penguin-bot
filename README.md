# 🐧 Penguin Bot

Penguin is your brutally honest, foul-mouthed Telegram bestie. It roasts you, swears at you, and motivates you — powered by open-source LLMs and voice tech.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Roast-Level](https://img.shields.io/badge/roast--level-🔥_100%-critical)
[![Model](https://img.shields.io/badge/model-zephyr--7b--beta-red?logo=huggingface)](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta)

---

> 🐧 **“Skipped gym again? Damn bro, at this point your discipline is on vacation too.”**

---

## 🔥 Features
- Savage replies powered by [Zephyr-7B](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta)
- Voice-to-text with Whisper
- Text-to-voice replies using gTTS
- Personalized roast logic with memory
- Works with text or voice messages

## 📦 Requirements
- Python 3.10+
- Telegram bot token
- HuggingFace access token

## 📁 Setup

1. Clone this repo  
2. Create a `.env` file:

```env
HF_TOKEN=your_huggingface_token_here
TELEGRAM_BOT_TOKEN=your_telegram_token_here
