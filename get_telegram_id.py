#!/usr/bin/env python3
"""
텔레그램 채팅 ID 확인 도구
봇에게 메시지를 보낸 후 이 스크립트를 실행하면 채팅 ID를 알 수 있습니다.

사용법:
  1. .env 파일에 TELEGRAM_BOT_TOKEN 만 먼저 입력
  2. 텔레그램에서 내 봇에게 /start 메시지 전송
  3. 터미널에서 실행: python3 get_telegram_id.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('TELEGRAM_BOT_TOKEN')
if not token or '여기에' in token:
    print('❌ .env 파일에 TELEGRAM_BOT_TOKEN 을 먼저 입력해주세요.')
    exit(1)

print('📱 텔레그램 업데이트 확인 중...')
print('   (봇에게 /start 메시지를 보내셨나요?)\n')

url = f'https://api.telegram.org/bot{token}/getUpdates'
resp = requests.get(url, timeout=10)
data = resp.json()

if not data.get('ok'):
    print(f'❌ 봇 토큰이 올바르지 않습니다: {data}')
    exit(1)

updates = data.get('result', [])
if not updates:
    print('⚠️  메시지가 없습니다.')
    print('   텔레그램에서 내 봇을 찾아 /start 를 보내고 다시 실행하세요.')
    exit(1)

print('✅ 아래 정보를 .env 파일의 TELEGRAM_CHAT_ID 에 입력하세요:\n')
seen = set()
for update in updates:
    msg = update.get('message', {})
    chat = msg.get('chat', {})
    chat_id = chat.get('id')
    chat_type = chat.get('type', '')
    name = chat.get('first_name', '') or chat.get('title', '')
    if chat_id and chat_id not in seen:
        seen.add(chat_id)
        print(f'  채팅 ID : {chat_id}')
        print(f'  이름    : {name}')
        print(f'  타입    : {chat_type}')
        print(f'  → TELEGRAM_CHAT_ID={chat_id}')
        print()
