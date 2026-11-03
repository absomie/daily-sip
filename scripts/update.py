#!/usr/bin/env python3
"""Free, dependency-free Google News RSS collector. No AI, no fabricated summaries."""
import datetime as dt
import email.utils
import html
import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
TZ = dt.timezone(dt.timedelta(hours=7))
QUERIES = [
    ('World', 'world politics diplomacy international'),
    ('World', 'Ukraine Russia peace talks'),
    ('Money', 'global economy markets inflation'),
    ('Money', 'technology artificial intelligence business'),
    ('Thailand & Asia', 'Thailand ASEAN Southeast Asia'),
    ('Culture', 'film music arts culture entertainment'),
]
CONTEXT = {
    'World': 'A development in international affairs. Read the original reporting for the background and what remains uncertain.',
    'Money': 'A development that may affect businesses, markets or household costs. The original article has the figures and context.',
    'Thailand & Asia': 'A regional development worth following from Thailand. Check the source for details and implications.',
    'Culture': 'A story from entertainment and culture. Follow the source for the people, events and wider context.',
}

def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', value or ''))).strip()

def fetch(query):
    q = urllib.parse.quote(query + ' when:2d')
    url = f'https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en'
    req = urllib.request.Request(url, headers={'User-Agent':'DailySipPersonalReader/1.0'})
    with urllib.request.urlopen(req, timeout=25) as resp:
        body = resp.read(2_000_000)
    root = ET.fromstring(body)
    results=[]
    for item in root.findall('.//channel/item')[:14]:
        title = clean(item.findtext('title'))
        source = clean(item.findtext('source'))
        link = (item.findtext('link') or '').strip()
        published = item.findtext('pubDate') or ''
        try:
            pub = email.utils.parsedate_to_datetime(published)
            if pub.tzinfo is None: pub=pub.replace(tzinfo=dt.timezone.utc)
            if (dt.datetime.now(dt.timezone.utc)-pub.astimezone(dt.timezone.utc)).total_seconds()>60*60*55: continue
        except (ValueError, TypeError): continue
        if source and title.endswith(' - '+source): title=title[:-(len(source)+3)].strip()
        if len(title)<25 or not link.startswith('https://'):continue
        results.append({'title':title[:200],'source':source or 'Google News','url':link,'published':pub.isoformat()})
    return results

def choose(feeds):
    chosen=[];seen=set()
    # One story per query, then fill gaps from available feeds.
    for category, candidates in feeds:
        for s in candidates:
            key=re.sub(r'[^a-z0-9]+','',s['title'].lower())[:90]
            if key in seen: continue
            seen.add(key)
            chosen.append({'category':category,'title':s['title'],'summary':CONTEXT[category], 'source':s['source'],'url':s['url']})
            break
    return chosen[:6]

def main():
    today=dt.datetime.now(TZ).date().isoformat()
    feeds=[]
    for category, query in QUERIES:
        try:
            items=fetch(query)
            print(f'{category}: {len(items)} candidates')
        except Exception as exc:
            print(f'WARNING: {category} feed unavailable: {exc}')
            items=[]
        feeds.append((category,items))
    stories=choose(feeds)
    if len(stories)<3:
        raise SystemExit('Insufficient news feeds; preserving previous edition rather than publishing an incomplete one.')
    edition={'date':today,'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'mode':'feed','stories':stories}
    DATA.mkdir(exist_ok=True)
    (DATA/f'{today}.json').write_text(json.dumps(edition,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    existing=json.loads((DATA/'index.json').read_text(encoding='utf-8')) if (DATA/'index.json').exists() else []
    dates=sorted(set([today]+existing),reverse=True)[:90]
    (DATA/'index.json').write_text(json.dumps(dates,indent=2)+'\n',encoding='utf-8')
    print(f'Published {today} with {len(stories)} stories')

if __name__=='__main__':main()
