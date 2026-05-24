import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

missing = []
if not OPENAI_API_KEY:
    missing.append("OPENAI_API_KEY")
if not TELEGRAM_BOT_TOKEN:
    missing.append("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_CHAT_ID:
    missing.append("TELEGRAM_CHAT_ID")

if missing:
    raise ValueError(f"❌ .env 파일에 다음 항목이 없습니다: {', '.join(missing)}\n.env.example 파일을 참고해서 .env 파일을 만들어주세요.")
