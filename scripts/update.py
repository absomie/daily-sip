#!/usr/bin/env python3
"""Daily Sip: free news RSS + optional Gemini summaries (server-side only)."""
import datetime as dt
import email.utils
import html
import json
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
TZ = dt.timezone(dt.timedelta(hours=7))
MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
QUERIES = [
    ('World', 'world politics diplomacy international'),
    ('World', 'Ukraine Russia peace talks'),
    ('Money', 'global economy markets inflation'),
    ('Money', 'technology artificial intelligence business'),
    ('Thailand & Asia', 'Thailand ASEAN Southeast Asia'),
    ('Culture', 'film music arts culture entertainment'),
]

def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', value or ''))).strip()

def fetch(query):
    q = urllib.parse.quote(query + ' when:2d')
    url = f'https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en'
    req = urllib.request.Request(url, headers={'User-Agent': 'DailySipPersonalReader/1.1'})
    with urllib.request.urlopen(req, timeout=25) as resp:
        body = resp.read(2_000_000)
    root = ET.fromstring(body)
    results = []
    for item in root.findall('.//channel/item')[:14]:
        title = clean(item.findtext('title'))
        source = clean(item.findtext('source'))
        link = (item.findtext('link') or '').strip()
        description = clean(item.findtext('description'))[:1600]
        published = item.findtext('pubDate') or ''
        try:
            pub = email.utils.parsedate_to_datetime(published)
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=dt.timezone.utc)
            if (dt.datetime.now(dt.timezone.utc) - pub.astimezone(dt.timezone.utc)).total_seconds() > 60 * 60 * 55:
                continue
        except (ValueError, TypeError):
            continue
        if source and title.endswith(' - ' + source):
            title = title[:-(len(source) + 3)].strip()
        if len(title) < 25 or not link.startswith('https://'):
            continue
        results.append({'title': title[:200], 'source': source or 'Google News', 'url': link,
                        'published': pub.isoformat(), 'feed_context': description})
    return results

def choose(feeds):
    chosen, seen = [], set()
    for category, candidates in feeds:
        for story in candidates:
            key = re.sub(r'[^a-z0-9]+', '', story['title'].lower())[:90]
            if key in seen:
                continue
            seen.add(key)
            chosen.append({'category': category, **story})
            break
    return chosen[:6]

def summarize(story, api_key):
    # RSS often supplies only a headline and related links, not article body.
    # Explicitly forbid turning insufficient evidence into invented reporting.
    context = story.get('feed_context', '')
    prompt = f'''You are a cautious news editor for a personal daily briefing.
Only use the supplied headline and RSS feed context. You cannot browse the article.
Do not invent figures, quotes, locations, causes, consequences, or confirmation.
If there is insufficient factual information for a useful summary, return summary as an empty string.
Output ONLY a JSON object with exactly three string keys: summary, why_it_matters, uncertainty.
summary: 1-2 short plain-English sentences describing confirmed facts supported by input, not simply repeating the headline.
why_it_matters: one short sentence of general significance, only if safely inferable.
uncertainty: one short sentence describing what cannot be established from the feed, when appropriate.
No speculation framed as fact. No markdown.
Category: {story['category']}
Source: {story['source']}
Headline: {story['title']}
RSS context: {context[:1400]}'''
    endpoint = f'https://generativelanguage.googleapis.com/v1beta/models/{urllib.parse.quote(MODEL)}:generateContent'
    payload = json.dumps({'contents': [{'parts': [{'text': prompt}]}],
                          'generationConfig': {'responseMimeType': 'application/json', 'temperature': 0.1,
                                               'maxOutputTokens': 550}}).encode()
    req = urllib.request.Request(endpoint, data=payload, method='POST', headers={
        'Content-Type': 'application/json', 'x-goog-api-key': api_key})
    with urllib.request.urlopen(req, timeout=45) as response:
        data = json.load(response)
    raw = ''.join(p.get('text', '') for c in data.get('candidates', [])
                  for p in c.get('content', {}).get('parts', []))
    parsed = json.loads(raw)
    return {k: clean(str(parsed.get(k, '')))[:450] for k in ('summary', 'why_it_matters', 'uncertainty')}

def main():
    today = dt.datetime.now(TZ).date().isoformat()
    feeds = []
    for category, query in QUERIES:
        try:
            items = fetch(query)
            print(f'{category}: {len(items)} candidates')
        except Exception as exc:
            print(f'WARNING: {category} feed unavailable: {exc}')
            items = []
        feeds.append((category, items))
    stories = choose(feeds)
    if len(stories) < 3:
        raise SystemExit('Insufficient news feeds; previous edition preserved.')
    key = os.getenv('GEMINI_API_KEY', '').strip()
    ai_count = 0
    for story in stories:
        story['summary'] = ''
        story['why_it_matters'] = ''
        story['uncertainty'] = ''
        if key:
            try:
                result = summarize(story, key)
                story.update(result)
                if story['summary']:
                    ai_count += 1
            except Exception as exc:
                print(f"WARNING: Gemini unavailable for {story['category']}: {type(exc).__name__}: {exc}")
            time.sleep(1)
        story.pop('feed_context', None)
    edition = {'date': today, 'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(),
               'mode': 'ai' if ai_count else 'feed', 'stories': stories}
    DATA.mkdir(exist_ok=True)
    (DATA / f'{today}.json').write_text(json.dumps(edition, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    existing = json.loads((DATA / 'index.json').read_text(encoding='utf-8')) if (DATA / 'index.json').exists() else []
    dates = sorted(set([today] + existing), reverse=True)[:90]
    (DATA / 'index.json').write_text(json.dumps(dates, indent=2) + '\n', encoding='utf-8')
    print(f'Published {today} with {len(stories)} stories; AI summaries: {ai_count}/{len(stories)}')
    if key and ai_count == 0:
        print('WARNING: No AI summaries generated. Check Gemini model, quota, and key access.')

if __name__ == '__main__':
    main()
