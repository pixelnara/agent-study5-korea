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

        prompt = fprompt = f"""당신은 중학생 동생에게 오늘 한국 주식 시장을 카카오톡으로 설명해주는 친한 형/언니입니다.
딱딱한 뉴스 말고, 친구한테 말하듯 편하고 재미있게 설명해주세요.

=== 오늘의 시장 데이터 ===
{market_text}

=== 지난 24시간 주요 뉴스 ===
{news_text}

작성 목표:
"중학생도 바로 이해할 수 있게"
"왜 오르고 내렸는지 이유가 느껴지게"
"읽으면 오늘 시장 분위기가 머릿속에 그려지게"

작성 규칙:
어려운 말은 쓰지 말고, 꼭 써야 하면 바로 옆에 괄호로 쉽게 설명
뉴스 그대로 복사 금지 — 내 말로 다시 풀어쓰기
실제 관련 뉴스가 없는 섹션은 그냥 빼기
같은 표현 두 번 쓰지 않기
"그래서 주가에 어떤 영향?" 한 줄 꼭 추가
외국인·기관이 많이 샀는지 팔았는지 뉴스에 있으면 꼭 언급
전체 600자 이내

말투 예시 (이런 느낌으로!):
❌ "반도체 업종은 수급 개선으로 상승 압력이 예상됩니다"
✅ "삼성전자에 외국인들이 다시 사러 왔어! 오를 수도 있겠는데?"

❌ "바이오 섹터는 임상 결과 발표로 변동성이 확대될 전망입니다"
✅ "셀트리온이 신약 실험 결과 발표하는 날이라 주가가 널뛸 수 있어"

출력 형식:
━━━━━━━━━━━━━━━━━━━━━
[ 오늘의 한국 시장 이야기 ]
━━━━━━━━━━━━━━━━━━━━━

🧠 반도체 / AI

🔋 2차전지 / 에너지

💊 바이오 / 헬스케어

🏦 금융 / 부동산

🌏 환율이랑 수출은요?

━━━━━━━━━━━━━━━━━━━━━
📌 오늘 이것만 기억해!
━━━━━━━━━━━━━━━━━━━━━
(오늘 시장 핵심 한 문장 — 친구한테 말하듯)"""

        message = self.client.messages.create(
            model='claude-sonnet-4-6',
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
