"""Read published overall standings without turning archive order into final ranks."""
from functools import lru_cache
from pathlib import Path
import json
import re
import unicodedata

ROOT = Path(__file__).parent / 'docs/research/kerala-school-science'
MISSING = 'ശേഖരിച്ച മൊത്തം സ്കൂൾ/ജില്ല പട്ടികകൾ 2019, 2022, 2023, 2024, 2025 വർഷങ്ങളുടേതാണ്. ആവശ്യമായ വർഷവും സ്കൂൾ പട്ടികയാണോ ജില്ലാ പട്ടികയാണോ വ്യക്തമാക്കുക.'
SCOPE = 'ഇത് ശേഖരിച്ച KITE മൊത്തം പോയിന്റ് പട്ടികയിലെ പ്രസിദ്ധീകരണക്രമമാണ്; ഒരു പ്രത്യേക മത്സരയിനത്തിന്റെ വിജയിയെയോ സർട്ടിഫൈ ചെയ്ത അന്തിമ റാങ്കിനെയോ സൂചിപ്പിക്കുന്നില്ല.'
CONFLICT = 'ഈ വർഷത്തെ ആർക്കൈവ് പട്ടികയും സമകാലിക റിപ്പോർട്ടുകളും തമ്മിൽ രേഖപ്പെടുത്തിയ വ്യത്യാസങ്ങളുണ്ട്; അവ ഒത്തുതീർത്ത അന്തിമഫലമായി ഈ സംഖ്യകൾ കാണരുത്.'

@lru_cache(maxsize=1)
def tables():
    data=json.loads((ROOT/'result-snapshots.json').read_text())['snapshots']
    sources={s['id']:s for s in json.loads((ROOT/'sources.json').read_text())}
    for table in data:
        assert table['source_id'] in sources
        assert len(table['records'])==table['record_count']
    return data,sources

def domain(q):
    entity=re.search(r'school|district|സ്കൂൾ|വിദ്യാലയ|ജില്ല',q)
    table=re.search(r'overall|champion|school\s*(?:table|standings|points)|district\s*(?:table|standings|points)|മൊത്തം|ചാമ്പ്യ|പോയിന്റ്|പട്ടിക',q)
    return bool(entity and table)

def lookup(question, history=()):
    q=unicodedata.normalize('NFKC',question).lower()
    if not domain(q):
        if history and re.search(r'^(?:and |what about |who came |which came |second|third|രണ്ടാം|മൂന്നാം|അടുത്ത)',q):
            prior=next((text for role,text in reversed(history) if role=='user'), '')
            if domain(prior.lower()):q=prior.lower()+' '+q
            else:return None
        else:return None
    # Item placements and named-pupil prizes belong to a different record type.
    if re.search(r'sisf|inspire|ncert|national|subdistrict|sub-district|ഉപജില്ല|എസ്ഐഎസ്എഫ്|ദേശീയ|robotics|working\s*model|റോബോട്ടി|വർക്കി',q):return None
    data,sources=tables()
    years=sorted(set(int(y) for y in re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',q)))
    school=bool(re.search(r'school|സ്കൂൾ|വിദ്യാലയ',q))
    district=bool(re.search(r'district|ജില്ല',q))
    scopes=(['overall_school'] if school else [])+(['overall_district'] if district else [])
    if len(years)==2 and re.search(r'\b(?:from|between|to|through)\b|മുതൽ|വരെ',q):
        years=[t for t in sorted({x['portal_year'] for x in data}) if years[0]<=t<=years[-1]]
    if not years or any(y not in {t['portal_year'] for t in data} for y in years):
        return {'reply':MISSING,'sources':[],'fact_ids':[]}
    if re.search(r'\brank\b|\bposition\b|റാങ്ക്',q) and not re.search(r'top|first|second|third|ഒന്നാം|രണ്ടാം|മൂന്നാം',q):
        return {'reply':'നിലവിൽ മൊത്തം പട്ടികയുടെ മുൻനിര വരികൾ, വർഷങ്ങളിലെ ഒന്നാം വരികൾ, വരികളുടെ എണ്ണം എന്നിവ പരിശോധിക്കാം. ഒരു സ്കൂളിന്റെ റാങ്കിനെക്കുറിച്ച് ഈ ചോദ്യരൂപത്തിൽ ഉറപ്പായ ഉത്തരം നൽകാനായില്ല.','sources':[],'fact_ids':[]}
    # Limit output for speech. A broad range returns one leader per table.
    number=re.search(r'(?:top|first|മുൻനിര)\s*(\d{1,2})(?!\d)',q)
    limit=min(int(number[1]),5) if number else 1
    position=3 if re.search(r'\bthird\b|മൂന്നാം',q) else 2 if re.search(r'\bsecond\b|രണ്ടാം',q) else 1
    count=bool(re.search(r'how many|number of|എത്ര',q))
    replies=[];links=[];ids=[];conflict=False
    for year in years:
        for scope in scopes:
            table=next(t for t in data if t['portal_year']==year and t['table_scope']==scope)
            label='സ്കൂൾ' if scope=='overall_school' else 'ജില്ല'
            if count:
                replies.append(f"{year}ലെ ശേഖരിച്ച മൊത്തം {label} പട്ടികയിൽ {table['record_count']} വരികളുണ്ട്; ഇത് പങ്കെടുത്ത വിദ്യാർത്ഥികളുടെ എണ്ണമല്ല.")
            else:
                rows=table['records'][position-1:position-1+limit]
                for row in rows:
                    name=row['school_name'] if scope=='overall_school' else row['district_name']
                    if scope=='overall_school' and row['school_code']=='15005':
                        name='Sacred Heart HSS Dwaraka (S H H S S Dwaraka, Wayanad)'
                    replies.append(f"{year}ലെ പ്രസിദ്ധീകരിച്ച മൊത്തം {label} പട്ടികയിലെ {row['display_order']}-ാം വരിയിൽ {name} ആണ്: {row['total_points']} പോയിന്റ്.")
            source=sources[table['source_id']]
            links.append({'id':source['id'],'title':source['title'],'url':table['source_url'],'locator':f"{year} {scope}; received {table['retrieved_at']}; published display order"})
            ids.append(f'overall-{scope}-{year}')
            conflict |= table['championship_status']=='observed_archive_view_unreconciled'
    replies.append(SCOPE)
    if conflict:replies.append(CONFLICT)
    return {'reply':'\n\n'.join(replies),'sources':links,'fact_ids':ids}
