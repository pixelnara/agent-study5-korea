"""
한국 시장 AI 요약 에이전트
- Claude API를 사용해 국내 시장 데이터를 브리핑 형식으로 요약합니다
"""

import anthropic
from datetime import datetime
import pytz
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANTHROPIC_API_KEY

KST = pytz.timezone('Asia/Seoul')


class KoreaSummaryAgent:

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate(self, market_data: dict, news_data: dict):
        """시장 데이터와 뉴스를 받아 텔레그램 메시지 목록을 반환합니다."""

        # 메시지 1: 시장 현황 (구조화된 숫자 데이터)
        market_msg = self._build_market_message(market_data)

        # 메시지 2: AI 뉴스 요약
        news_msg = self._generate_news_summary(market_data, news_data)

        return [market_msg, news_msg]

    # ──────────────────────────────────────────────
    # 시장 현황 메시지 빌더
    # ──────────────────────────────────────────────

    def _build_market_message(self, market_data: dict) -> str:
        now = datetime.now(KST)
        lines = [
            f"🇰🇷 한국 주식 일일 브리핑  {now.strftime('%Y.%m.%d %H:%M')}",
            "━━━━━━━━━━━━━━━━━━━━━",
            "[ 시장 현황 ]",
            "━━━━━━━━━━━━━━━━━━━━━",
        ]

        # 국내 지수
        if market_data.get('kr_indices'):
            lines.append('')
            lines.append('📈 국내 지수 (당일 종가)')
            for name, d in market_data['kr_indices'].items():
                lines.append(self._fmt_price_line(name, d))

        # 주요 대형주
        if market_data.get('kr_stocks'):
            lines.append('')
            lines.append('🏢 주요 대형주')
            for name, d in market_data['kr_stocks'].items():
                lines.append(self._fmt_price_line(name, d, unit='원', comma=True))

        # 테마 ETF
        if market_data.get('kr_theme'):
            lines.append('')
            lines.append('🚀 테마 ETF')
            for name, d in market_data['kr_theme'].items():
                lines.append(self._fmt_price_line(name, d, unit='원', comma=True))

        # 환율
        if market_data.get('forex'):
            lines.append('')
            lines.append('💱 환율 (원화 기준)')
            for name, d in market_data['forex'].items():
                lines.append(self._fmt_price_line(name, d, show_pct=False))

        # 원자재
        if market_data.get('commodities'):
            lines.append('')
            lines.append('🛢️ 원자재')
            for name, d in market_data['commodities'].items():
                lines.append(self._fmt_price_line(name, d))

        # 거시지표
        if market_data.get('macro'):
            lines.append('')
            lines.append('📉 거시지표')
            for name, d in market_data['macro'].items():
                lines.append(self._fmt_price_line(name, d))

        return '\n'.join(lines)

    def _fmt_price_line(self, name: str, d, show_pct: bool = True,
                        unit: str = '', comma: bool = False) -> str:
        if not d:
            return f"  • {name}: 데이터 없음"
        emoji = '🟢' if d['change_pct'] >= 0 else '🔴'
        arrow = '▲' if d['change_pct'] >= 0 else '▼'
        price = d['price']
        if comma:
            price_str = f"{price:,.0f}{unit}"
        else:
            price_str = f"{price:,.2f}{unit}"
        if show_pct:
            return f"{emoji} {name}: {price_str} {arrow}{abs(d['change_pct']):.2f}%"
        return f"  • {name}: {price_str}"

    # ──────────────────────────────────────────────
    # Claude AI 뉴스 요약 생성
    # ──────────────────────────────────────────────

    def _generate_news_summary(self, market_data: dict, news_data: dict) -> str:
        market_text = self._market_to_text(market_data)
        news_text = self._news_to_text(news_data)

        prompt = f"""당신은 한국 개인 투자자에게 오늘 국내 주식 시장을 설명해주는 애널리스트입니다.
아래 데이터를 보고 핵심만 짧고 명확하게 설명해주세요.

=== 오늘의 시장 데이터 ===
{market_text}

=== 지난 24시간 주요 뉴스 ===
{news_text}

작성 목표:
"국내 투자자에게 직접 영향을 주는 뉴스만"
"쉬운 말로 흐름이 보이게"
"투자 판단에 도움이 되는 인사이트 포함"

작성 규칙:
어려운 전문 용어는 괄호로 쉽게 설명 추가
뉴스 원문을 그대로 복사하지 말고 핵심만 재구성
각 섹션은 실제 관련 뉴스가 있을 때만 작성 (없으면 섹션 생략)
같은 표현 반복 금지
"왜 주가에 영향을 주는지" 한 줄 추가
외국인/기관 수급 흐름이 뉴스에 있으면 반드시 포함
전체 600자 이내

출력 스타일:
한 줄에 한 내용만
모바일에서 읽기 쉽게 짧게
뉴스 나열이 아니라 "오늘 시장 흐름 설명" 느낌으로

출력 형식:
━━━━━━━━━━━━━━━━━━━━━
[ 오늘의 한국 시장 이야기 ]
━━━━━━━━━━━━━━━━━━━━━

🧠 반도체 / AI

🔋 2차전지 / 에너지

💊 바이오 / 헬스케어

🏦 금융 / 부동산

🌏 대외 변수 (환율·수출)

━━━━━━━━━━━━━━━━━━━━━
📌 오늘 이것만 기억하세요
━━━━━━━━━━━━━━━━━━━━━
(오늘 국내 시장 핵심을 한 문장으로 정리)"""

        message = self.client.messages.create(
            model='claude-sonnet-4-6', // 최신 모델로 변경
            max_tokens=2500,
            messages=[{'role': 'user', 'content': prompt}],
        )

        return message.content[0].text

    def _market_to_text(self, market_data: dict) -> str:
        lines = []
        sections = [
            ('국내 지수', 'kr_indices'),
            ('주요 대형주', 'kr_stocks'),
            ('테마 ETF', 'kr_theme'),
            ('환율', 'forex'),
            ('원자재', 'commodities'),
            ('거시지표', 'macro'),
        ]
        for label, key in sections:
            group = market_data.get(key, {})
            if group:
                lines.append(f'[{label}]')
                for name, d in group.items():
                    if d:
                        pct = d.get('change_pct', 0)
                        price = d.get('price', 0)
                        lines.append(f'  {name}: {price:,.2f} ({pct:+.2f}%)')
        return '\n'.join(lines)

    def _news_to_text(self, news_data: dict) -> str:
        lines = []
        for sector, articles in news_data.items():
            if articles:
                lines.append(f'\n[{sector}]')
                for article in articles[:8]:
                    lines.append(f'  - [{article["source"]}] {article["title"]}')
                    if article.get('summary'):
                        lines.append(f'    {article["summary"][:200]}')
        return '\n'.join(lines)
