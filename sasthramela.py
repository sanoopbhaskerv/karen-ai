"""Bounded extractive answers from the checked bilingual research, never eval data."""
from functools import lru_cache
from pathlib import Path
import json
import math
import re
import unicodedata

ROOT = Path(__file__).parent / 'docs/research/kerala-school-science'
NOTICE = '2026 നവംബർ 1 വരെ പരിശോധിച്ച രേഖകളെ അടിസ്ഥാനമാക്കിയുള്ള വിവരം. പുതിയ പ്രാദേശിക നിർദേശങ്ങൾ സംഘാടകരുമായി ഉറപ്പാക്കുക.'
UNKNOWN = 'ഈ ചോദ്യത്തിന് പരിശോധിച്ച ശാസ്ത്രമേള രേഖകളിൽ ഉറപ്പുള്ള ഉത്തരം കണ്ടെത്താനായില്ല. വർഷവും മേളയുടെ വിഭാഗവും ഇനവും വ്യക്തമാക്കുക; നിലവിലെ പ്രാദേശിക നിർദേശങ്ങൾ സംഘാടകരുമായി ഉറപ്പാക്കുക.'
FAIR = re.compile(r'sasthr|sasthra|sasthrol|shasthr|science\s*(?:fair|exhibition)|working\s*model|ശാസ്ത്ര.*മേള|ശാസ്ത്ര.*പ്രദർശന|വർക്കി|പ്രവർത്തനമാതൃക', re.I)
STOP = set('the a an is are was were what when where who how many much does do did in of for to and about kerala science fair exhibition sasthramela sasthrolsavam please tell me working model'.split())
ROUTES = [
 (r'how many.*(?:pupil|student|child|participant)|team|individual|ഒറ്റ|എത്ര.*(?:കുട്ടി|വിദ്യാർ|പങ്ക)|രണ്ട് കുട്ടി', ['working-two-pupils']),
 (r'video|വീഡിയോ', ['working-video']),
 (r'rubric|marks|scor|judg|മാർക്ക്|മൂല്യനിർണ', ['working-rubric']),
 (r'dimension|size|വലിപ്പ|അളവ്', ['working-size']),
 (r'chart|ചാർട്ട്', ['working-charts']),
 (r'uniform|badge|യൂണിഫോം|ബാഡ്ജ്', []),
 (r'origin|first.*(?:fair|exhibition)|beg[ai]n|start|history|ചരിത്ര|ആരംഭ|ആദ്യ', ['history-1962-63-regional-fairs', 'history-2009-integration']),
]

def normalize(text):
    return unicodedata.normalize('NFKC', text).lower()

def tokens(text):
    return set(re.findall(r'[a-z0-9]+|[\u0d00-\u0d7f]+', normalize(text))) - STOP

@lru_cache(maxsize=1)
def corpus():
    facts = [json.loads(line) for line in (ROOT / 'knowledge.jsonl').read_text().splitlines() if line.strip()]
    # Historical descriptions of Karen's provider are stale, not exhibition evidence.
    facts = [f for f in facts if f['topic'] != 'karen-project']
    sources = {s['id']: s for s in json.loads((ROOT / 'sources.json').read_text())}
    for f in facts:
        assert all(s['id'] in sources for s in f['sources'])
    return facts, sources

def lookup(question, history=()):
    """None means unrelated; unknown fair questions fail closed rather than guess."""
    q = normalize(question)
    followup = re.search(r'^(?:and |what about |how (?:long|many|much)|what (?:is|are) (?:its|the)|അതിന്റെ|അതിൽ|എത്ര|വീഡിയോ|മാർക്ക്)', q)
    contextual = bool(followup and history and FAIR.search(history[-2][1] if len(history)>1 else history[-1][1]))
    if not FAIR.search(q) and not contextual:
        return None
    facts, sources = corpus()
    by_id = {f['id']:f for f in facts}
    selected = None
    years = set(re.findall(r'\b(?:19|20)\d{2}\b', q))
    working = bool(re.search(r'working\s*model|വർക്കി|പ്രവർത്തനമാതൃക', q))
    if contextual and not working:
        working = any(re.search(r'working\s*model|വർക്കി|പ്രവർത്തനമാതൃക', normalize(text)) for role,text in history[-4:] if role=='user')
    # Avoid transferring HS working-model directions into other event streams.
    other_stream = re.search(r'\bit\b|technical|ടെക്നിക്കൽ|ഐടി|electronics|robotics|iot|ഇലക്ട്രോണി|റോബോട്ടി',q)
    if other_stream and working and re.search(r'\bit\b|ഐടി',q):
        selected=[by_id['it-no-working-model']]
    if re.search(r'2026',q) and re.search(r'when|date|venue|എപ്പോൾ|തീയതി|എവിടെ',q) and not working:
        selected=[by_id['state-2026-scheduled']]
    if not other_stream and selected is None:
        for pattern, ids in ROUTES:
            if (re.search(pattern,q) and (not ids or (ids[0].startswith('working-') and working and (not years or years <= {'2025','2026'})) or (ids[0].startswith('history-') and not years))):
                selected = [by_id[i] for i in ids]
                break
    if selected is None and working and not other_stream and (not years or years <= {'2025','2026'}) and re.search(r'rules|requirements|ചട്ട|നിയമ|നിബന്ധന',q):
        selected=[by_id[i] for i in ['working-two-pupils','working-video','working-rubric']]
    if selected is None:
        query = tokens(q)
        documents, frequencies = search_index()
        scored=[]
        for f, document in zip(facts, documents):
            if years and not years <= set(re.findall(r'\b(?:19|20)\d{2}\b', f['claim_en']+' '+f['scope'])):
                continue
            overlap=query & document
            score=sum(math.log(1+len(facts)/frequencies[t]) for t in overlap)
            if len(overlap)>=2:scored.append((score,f))
        scored.sort(key=lambda x:x[0],reverse=True)
        selected=[scored[0][1]] if scored else []
    links=[]
    for f in selected:
        for ref in f['sources']:
            s=sources[ref['id']]
            if not any(x['id']==s['id'] for x in links):
                links.append({'id':s['id'],'title':s['title'],'url':s['url'],'locator':ref.get('locator','')})
    reply = '\n\n'.join(f['claim_ml'] for f in selected) if selected else UNKNOWN
    if selected: reply += '\n\n'+NOTICE
    return {'reply':reply,'sources':links,'fact_ids':[f['id'] for f in selected]}


@lru_cache(maxsize=1)
def search_index():
    from collections import Counter
    documents = [tokens(f['id']+' '+f['topic']+' '+f['claim_en']+' '+f['claim_ml']) for f in corpus()[0]]
    frequencies = Counter(t for document in documents for t in document)
    return documents, frequencies

def history_sources(history):
    result = {}
    for i,(role,text) in enumerate(history):
        if role=='model' and i and history[i-1][0]=='user':
            match = lookup(history[i-1][1],history[:i-1])
            if match and match['reply']==text:
                result[i]=match['sources']
    return result
