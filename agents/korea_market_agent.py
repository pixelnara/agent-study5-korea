"""
한국 시장 데이터 수집 에이전트
- KOSPI, KOSDAQ, 주요 종목, 환율, 원자재, 거시지표를 수집합니다
"""

import yfinance as yf
import requests
from datetime import datetime
import pytz

KST = pytz.timezone('Asia/Seoul')


class KoreaMarketAgent:

    def fetch_all(self):
        print("  📊 국내 지수 수집 중...")
        kr_indices = self._fetch_yf_group({
            'KOSPI': '^KS11',
            'KOSDAQ': '^KQ11',
            'KOSPI 200': '^KS200',
        })

        print("  🏢 주요 대형주 수집 중...")
        kr_stocks = self._fetch_yf_group({
            '삼성전자': '005930.KS',
            'SK하이닉스': '000660.KS',
            'LG에너지솔루션': '373220.KS',
            '삼성바이오로직스': '207940.KS',
            '현대차': '005380.KS',
            'POSCO홀딩스': '005490.KS',
            'KB금융': '105560.KS',
            '셀트리온': '068270.KS',
        })

        print("  🚀 테마주 수집 중...")
        kr_theme = self._fetch_yf_group({
            'KODEX 반도체': '091160.KS',
            'KODEX 2차전지': '305720.KS',
            'KODEX AI반도체핵심장비': '396500.KS',
            'KODEX 방산': '305720.KS',
        })

        print("  💱 환율/외환 수집 중...")
        forex = self._fetch_yf_group({
            'USD/KRW': 'USDKRW=X',
            'JPY/KRW': 'JPYKRW=X',
            'EUR/KRW': 'EURKRW=X',
            'CNY/KRW': 'CNYKRW=X',
        })

        print("  🛢️ 원자재 수집 중...")
        commodities = self._fetch_yf_group({
            '금 (Gold)': 'GC=F',
            'WTI 원유': 'CL=F',
            '천연가스': 'NG=F',
            '구리': 'HG=F',
        })

        print("  📉 거시지표 수집 중...")
        macro = self._fetch_yf_group({
            '한국 3년 국채금리': '^KR3YT=RR',
            '미국 10년 국채금리': '^TNX',
            '공포지수 (VIX)': '^VIX',
            '달러지수 (DXY)': 'DX-Y.NYB',
        })

        return {
            'kr_indices': kr_indices,
            'kr_stocks': kr_stocks,
            'kr_theme': kr_theme,
            'forex': forex,
            'commodities': commodities,
            'macro': macro,
            'timestamp': datetime.now(KST).strftime('%Y년 %m월 %d일 %H:%M KST'),
        }

    def _fetch_yf_group(self, symbols: dict) -> dict:
        result = {}
        for name, symbol in symbols.items():
            data = self._get_ticker(symbol, name)
            if data:
                result[name] = data
        return result

    def _get_ticker(self, symbol: str, name: str):
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='5d')
            if hist.empty or len(hist) < 1:
                return None

            latest = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) >= 2 else hist.iloc[-1]

            price = float(latest['Close'])
            prev_price = float(prev['Close'])
            change = price - prev_price
            change_pct = (change / prev_price) * 100 if prev_price else 0

            return {
                'name': name,
                'price': price,
                'change': change,
                'change_pct': change_pct,
                'date': hist.index[-1].strftime('%m/%d'),
            }
        except Exception as e:
            print(f"    ⚠️ {name} ({symbol}) 수집 실패: {e}")
            return None
