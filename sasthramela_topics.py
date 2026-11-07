"""Bilingual concept groups and source-bound answers; no question-template matching."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import json
import re
import unicodedata

BASE=Path(__file__).parent
ROOT=BASE/'docs/research/kerala-school-science'

@lru_cache(maxsize=1)
def config():
    return json.loads((BASE/'sasthramela_topics.json').read_text(encoding='utf-8'))['topics']

@lru_cache(maxsize=8)
def dataset(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8'))

def normalized(text):
    it_event=bool(re.search(r'\bIT\b|ഐടി|information.technology|\bit\s+(?:fair|fest|event|project|quiz|categor|item)|science\s+(?:and|&)\s+it',text))
    text=unicodedata.normalize('NFKC',text).lower()
    if not it_event:
        text=re.sub(r'\bit\b','itself',text)
    text=re.sub('[\u200b\u200c\u200d\u2060\ufeff]','',text)
    return re.sub(r'\s+',' ',text).strip()

def choose(question):
    q=normalized(question)
    years=set(map(int,re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',q)))
    matches=[]
    for t in config():
        if t.get('exclude') and re.search(t['exclude'],q):continue
        if t.get('years') and not years<=set(t['years']):continue
        if all(re.search(group,q) for group in t['concept_groups']):
            matches.append((len(t['concept_groups'])*100+t['priority'],t))
    if not matches:return None
    best=max(matches,key=lambda x:x[0])[1]
    preparation={'working-team','construction-video','working-rubric','working-display'}
    parts=[t for _,t in matches if t['id'] in preparation]
    if best['id'] in preparation and len(parts)>1:
        combined=dict(best,id='working-preparation')
        combined['fact_ids']=list(dict.fromkeys(fid for t in parts for fid in t['fact_ids']))
        return combined
    return best

def lookup(question, history, facts, sources):
    topic=choose(question)
    query=question
    if topic is None and re.search(r'^(?:and |what about |how long|how many|did it |can it |can i |can we |do we |should i |when |where |which year |അതിന്റെ|അതിൽ|അതിന്|പിന്നെ|എത്ര)',unicodedata.normalize('NFKC',question).lower().strip()):
        prior=next((text for role,text in reversed(history) if role=='user'),'')
        if choose(prior) or re.search(r'sasthr|sastra|shastra|science.*(?:fair|exhib)|ശാസ്ത്ര.*മേള',prior,re.I):
            query=prior+' '+question
            topic=choose(query)
    if topic is None:return None
    by_id={f['id']:f for f in facts}
    refs=list(topic['source_refs'])
    for fid in topic['fact_ids']:refs.extend(by_id[fid]['sources'])
    handler=topic.get('handler')
    spoken=topic.get('spoken_ml')
    if handler=='standings':
        from sasthramela_results import lookup as standings
        scope='school' if re.search(r'school|സ്കൂ[ൾള]',normalized(query)) else 'district'
        answer=standings(query+' overall '+scope+' table',history)
        if answer is None:return None
        answer['topic_id']=topic['id']
        return answer
    if handler=='consistency':
        tables=[t for t in dataset('result-snapshots.json')['snapshots'] if t['table_scope']=='overall_district']
        counts=Counter(r['district_name'] for t in tables for r in t['records'][:3])
        values=sorted(counts.items(),key=lambda x:(-x[1],x[0]))[:4]
        text='2019, 2022–25 വർഷങ്ങളിലെ ശേഖരിച്ച ജില്ലാ പട്ടികകളുടെ ആദ്യ മൂന്ന് വരികളിൽ വന്ന തവണകൾ: '+ '; '.join(f'{name}: {n}/5' for name,n in values)+'. ഇത് അഞ്ച് പ്രസിദ്ധീകരിച്ച snapshotകളുടെ താരതമ്യമാണ്; എല്ലാ വർഷങ്ങളുടെയും അന്തിമ championship ranking അല്ല. പഴയ പട്ടികകളിലെ റിപ്പോർട്ട് വ്യത്യാസങ്ങൾ പരിഹരിച്ചിട്ടില്ല.'
        refs.extend({'id':t['source_id'],'locator':f"{t['portal_year']} overall district table; first three displayed rows"} for t in tables)
    elif handler=='catalogue':
        changes=dataset('catalogue-changes.json')['transitions']
        text='ശേഖരിച്ച subdistrict catalogue മാറ്റങ്ങൾ: '+'; '.join(f"{t['from_portal_year']}–{t['to_portal_year']}: ചേർത്തത് {len(t['added_catalogue_rows'])}, നീക്കിയത് {len(t['removed_catalogue_rows'])}, മാറ്റിയ വരികൾ {len(t['changed_catalogue_rows'])}" for t in changes)+'. ഇവ പേരുകൾ, codes, capacities തുടങ്ങിയ catalogue വ്യത്യാസങ്ങളാണ്; യഥാർഥ ഹാജറോ എല്ലാ വർഷങ്ങളിലെയും മത്സരനടത്തിപ്പോ തെളിയിക്കുന്നില്ല.'
        urls={t[k] for t in changes for k in ['from_source_url','to_source_url']}
        refs.extend({'id':s['id'],'locator':'Compared published subdistrict catalogue rows'} for s in sources.values() if s['url'] in urls)
    elif handler=='streams':
        years=set(re.findall(r'2017|2018',query))
        tables=[t for t in dataset('historical-stream-results.json')['district_snapshots'] if t['edition_context'][:4] in years]
        lines=[]
        for t in tables:
            row=t['rows'][0]
            lines.append(f"{t['edition_context'][:4]} {t['stream'].upper()}: {row['district_as_published']} {row['published_total']}")
            refs.append({'id':t['source_id'],'locator':'First row of the published stream-specific district table'})
        text='; '.join(lines)+'. ഇവ Science/IT വിഭാഗങ്ങളുടെ വേറിട്ട ജില്ലാ പോയിന്റുകളാണ്; മൊത്തം ശാസ്ത്രോത്സവ championship അല്ല. ഒഴിഞ്ഞ വിഭാഗക്കോളങ്ങളെയും പഴയ തലക്കെട്ടുകളെയും അന്തിമ സർട്ടിഫിക്കേഷനായി കാണരുത്.'
    elif handler=='national':
        rows=[r for r in dataset('national-selection-index.json')['selection_records'] if r['event_year']==2025 and r['selection_group_heading_as_published']=='KERALA']
        text='NCERT 2025 കേരള selected-exhibit പട്ടിക: '+'; '.join(f"{r['exhibit_code_as_published']}: {r['title_as_published']}" for r in rows)+'. ഇത് ദേശീയ പങ്കാളിത്തത്തിനുള്ള തിരഞ്ഞെടുപ്പാണ്; സമ്മാനമോ സ്ഥിരീകരിച്ച ഹാജറോ അല്ല. പട്ടിക/ഫോം പേരുകളിലെ പതിപ്പുവ്യത്യാസങ്ങൾ വേർതിരിക്കണം.'
        refs.extend({'id':r['source_id'],'locator':f"PDF{r['pdf_page_1based']}; exhibit {r['exhibit_code_as_published']}"} for r in rows)
    else:
        text=topic.get('answer_ml') or '\n\n'.join(by_id[fid]['claim_ml'] for fid in topic['fact_ids'])
    links=[]
    for ref in refs:
        source=sources[ref['id']]
        if not any(x['id']==source['id'] for x in links):
            links.append({'id':source['id'],'title':source['title'],'url':source['url'],'locator':ref.get('locator','')})
    if not links:raise ValueError('Research topic lacks a resolved source: '+topic['id'])
    return {'reply':text,'spoken_reply':spoken or text,'sources':links,'fact_ids':topic['fact_ids'] or ['topic:'+topic['id']],'topic_id':topic['id']}
