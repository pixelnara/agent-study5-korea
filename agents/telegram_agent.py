"""
텔레그램 전송 에이전트
- 생성된 브리핑 메시지를 텔레그램으로 전송합니다
"""

import requests
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

MAX_MSG_LEN = 4000  # 텔레그램 최대 4096자, 여유 있게 4000으로 설정


class TelegramAgent:

    def __init__(self):
        self.url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'

    def send_all(self, messages):
        """메시지 목록을 순서대로 전송합니다."""
        for msg in messages:
            chunks = self._split(msg)
            for chunk in chunks:
                self._send(chunk)

    def send_text(self, text: str):
        """단일 텍스트 메시지를 전송합니다 (오류 알림 등)."""
        chunks = self._split(text)
        for chunk in chunks:
            self._send(chunk)

    def _send(self, text: str):
        payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': text}
        try:
            resp = requests.post(self.url, json=payload, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"  ⚠️ 텔레그램 전송 실패: {e}")
            raise

    def _split(self, text: str) -> list[str]:
        if len(text) <= MAX_MSG_LEN:
            return [text]

        chunks = []
        lines = text.split('\n')
        current = ''
        for line in lines:
            candidate = (current + '\n' + line).lstrip('\n')
            if len(candidate) > MAX_MSG_LEN:
                if current:
                    chunks.append(current)
                current = line
            else:
                current = candidate
        if current:
            chunks.append(current)
        return chunks
