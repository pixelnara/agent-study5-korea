"""
한국 주식 일일 브리핑 - 메인 실행 파일
실행: python main.py
"""

import sys
import os
from datetime import datetime
import pytz

# agents 폴더를 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agents'))

from korea_market_agent import KoreaMarketAgent
from korea_news_agent import KoreaNewsAgent
from korea_summary_agent import KoreaSummaryAgent
from telegram_agent import TelegramAgent  # 기존 텔레그램 에이전트 재사용

KST = pytz.timezone('Asia/Seoul')


def run():
    start = datetime.now(KST)
    print(f"\n🇰🇷 한국 주식 브리핑 시작 [{start.strftime('%Y-%m-%d %H:%M')} KST]")
    print("=" * 50)

    telegram = TelegramAgent()

    try:
        # 1. 시장 데이터 수집
        print("\n[1/3] 시장 데이터 수집 중...")
        market_agent = KoreaMarketAgent()
        market_data = market_agent.fetch_all()

        # 2. 뉴스 수집
        print("\n[2/3] 뉴스 수집 중...")
        news_agent = KoreaNewsAgent(hours_back=24)
        news_data = news_agent.fetch_all()

        # 3. AI 요약 생성
        print("\n[3/3] AI 요약 생성 중...")
        summary_agent = KoreaSummaryAgent()
        messages = summary_agent.generate(market_data, news_data)

        # 4. 텔레그램 전송
        print("\n📤 텔레그램 전송 중...")
        telegram.send_all(messages)

        elapsed = (datetime.now(KST) - start).seconds
        print(f"\n✅ 완료! (소요 시간: {elapsed}초)")

    except Exception as e:
        error_msg = f"⚠️ 한국 브리핑 오류 발생\n{str(e)}"
        print(f"\n❌ {error_msg}")
        try:
            telegram.send_text(error_msg)
        except Exception:
            pass
        sys.exit(1)


if __name__ == '__main__':
    run()
