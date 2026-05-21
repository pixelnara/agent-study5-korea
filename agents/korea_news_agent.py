"""
한국 뉴스 수집 에이전트
- 한국 경제/증시/산업 RSS 피드를 사용해 24시간 이내 기사를 수집합니다
- 추가 API 키 없이 동작합니다
"""

import feedparser
import calendar
from datetime import datetime, timedelta, timezone
import pytz
import re

KST = pytz.timezone('Asia/Seoul')

# 섹터별 RSS 피드 목록 (한국 중심)
RSS_FEEDS = {
    '증시_시황': [
        ('연합뉴스 경제', 'https://www.yna.co.kr/rss/economy.xml'),
        ('한국경제', 'https://www.hankyung.com/feed/economy'),
        ('매일경제', 'https://www.mk.co.kr/rss/40300001/'),
        ('머니투데이', 'https://news.mt.co.kr/mtview.php?no=&type=1&sec=rss'),
        ('이데일리 증권', 'https://www.edaily.co.kr/rss/edaily_stock.xml'),
    ],
    '반도체_AI': [
        ('전자신문', 'https://www.etnews.com/rss'),
        ('한국경제 IT', 'https://www.hankyung.com/feed/it'),
        ('매일경제 IT', 'https://www.mk.co.kr/rss/50300000/'),
        ('아이뉴스24', 'https://www.inews24.com/rss'),
        ('디지털타임스', 'https://www.dt.co.kr/rss/rss.xml'),
    ],
    '2차전지_에너지': [
        ('에너지경제', 'https://www.ekn.kr/rss/allArticle.xml'),
        ('이데일리 산업', 'https://www.edaily.co.kr/rss/edaily_industry.xml'),
        ('한경 바이오헬스', 'https://www.hankyung.com/feed/bio'),
        ('뉴스1 경제', 'https://www.news1.kr/rss/economy'),
    ],
    '바이오_헬스': [
        ('한국경제 바이오', 'https://www.hankyung.com/feed/bio'),
        ('청년의사', 'https://www.docdocdoc.co.kr/rss/allArticle.xml'),
        ('히트뉴스', 'https://www.hitnews.co.kr/rss/allArticle.xml'),
        ('팜뉴스', 'https://www.pharmnews.com/rss/allArticle.xml'),
    ],
    '부동산_금융': [
        ('한국경제 금융', 'https://www.hankyung.com/feed/finance'),
        ('매일경제 부동산', 'https://www.mk.co.kr/rss/50200011/'),
        ('머니투데이 부동산', 'https://news.mt.co.kr/mtview.php?no=&type=2&sec=rss'),
        ('뉴스핌', 'https://www.newspim.com/rss/allArticle.xml'),
    ],
    '대외_경제': [
        ('연합뉴스 국제', 'https://www.yna.co.kr/rss/international.xml'),
        ('KBS 경제', 'https://news.kbs.co.kr/rss/rss_economy.xml'),
        ('SBS 경제', 'https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER'),
        ('한국무역신문', 'https://www.weeklytrade.co.kr/rss/allArticle.xml'),
    ],
}


class KoreaNewsAgent:

    def __init__(self, hours_back: int = 24):
        now = datetime.now(KST)
        self.cutoff = now - timedelta(hours=hours_back)

    def fetch_all(self) -> dict:
        all_news = {}
        for sector, feeds in RSS_FEEDS.items():
            articles = []
            for source_name, url in feeds:
                fetched = self._fetch_feed(url, source_name)
                articles.extend(fetched)
            # 날짜 기준 최신순 정렬 후 섹터당 최대 15개
            articles.sort(key=lambda x: x.get('pub_ts', 0), reverse=True)
            all_news[sector] = articles[:15]
            print(f"  📰 {sector}: {len(all_news[sector])}개 기사 수집")
        return all_news

    def _fetch_feed(self, url: str, source_name: str) -> list:
        try:
            feed = feedparser.parse(url)
            articles = []
            for entry in feed.entries[:12]:
                pub_date, pub_ts = self._parse_date(entry)

                # 24시간 이내 기사만 포함
                if pub_date and pub_date < self.cutoff:
                    continue

                title = entry.get('title', '').strip()
                if not title:
                    continue

                summary = (
                    entry.get('summary', '')
                    or entry.get('description', '')
                ).strip()
                summary = re.sub(r'<[^>]+>', '', summary)[:400]

                articles.append({
                    'title': title,
                    'summary': summary,
                    'link': entry.get('link', ''),
                    'source': source_name,
                    'published': pub_date.strftime('%m/%d %H:%M') if pub_date else '날짜불명',
                    'pub_ts': pub_ts,
                })
            return articles
        except Exception as e:
            print(f"    ⚠️ {source_name} 피드 실패: {e}")
            return []

    def _parse_date(self, entry) -> tuple:
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                ts = calendar.timegm(entry.published_parsed)
                dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(KST)
                return dt, ts
        except Exception:
            pass
        return None, 0
