"""Allow the creator's public name while protecting school and personal details."""
import re
import unicodedata


DEFAULT_MEMORY = ('Your name is Karen. Your creator is Sreehari V. You are a friendly Malayalam science exhibition assistant. '
                  'Explain things simply. An ESP32 can record and play audio while a Python server '
                  'uses online speech recognition, Gemini and speech synthesis.')
CREATOR_REPLY = 'എന്നെ നിർമ്മിച്ചത് ശ്രീഹരി ആണ്. ഞാൻ ഒരു മലയാളം ശാസ്ത്രപ്രദർശന സഹായിയാണ്.'
PRIVATE_REPLY = ('നിർമ്മാതാവിന്റെ സ്കൂൾ, ക്ലാസ്, താമസസ്ഥലം തുടങ്ങിയ വ്യക്തിവിവരങ്ങൾ പങ്കിടുന്നില്ല. '
                 'കാരെൻ എങ്ങനെ പ്രവർത്തിക്കുന്നു എന്ന് വിശദീകരിക്കാം.')
PRIVATE_QUESTION = 'നിർമ്മാതാവിന്റെ വ്യക്തിവിവരങ്ങളെക്കുറിച്ചുള്ള ചോദ്യം.'

# The creator's name is public. Recognize its variants only to route questions;
# school/locality and complete class-section combinations stay private. General
# places (Kerala/Malappuram) and class numbers remain useful science-fair facts.
_NAME = (r'(?<!\w)(?:' + '|'.join(r'[\W_]*'.join(name) for name in
         ('sreehari', 'shreehari', 'srihari', 'shrihari')) + r')(?:[\W_]*v)?(?!\w)')
# Require the complete protected grade and section together. A grade number
# alone and ordinary duration units remain useful non-identifying science text.
_CLASS_LABEL = r'(?:class|section|standard|grade|ക്ലാസ്|ക്ലാസ്സ്|ഗ്രേഡ്|സ്റ്റാൻഡേർഡ്)'
_CLASS_NUMBER = r'(?:9(?:th)?|ix|nine|ninth|ഒമ്പത്|ഒൻപത്|ഒമ്പതാം|ഒൻപതാം)'
_CLASS_ORDINAL = r'(?:9th|ninth|ഒമ്പതാം|ഒൻപതാം)'
_SECTION_SUFFIX = (r'\s*(?:[.\-]\s*|[,;:]?\s*(?:section|sec\.?|division|സെക്ഷൻ|വിഭാഗം)'
                   r'\s*[:.\-]?\s*)?(?:s|എസ്)(?!\w)')
_IDENTIFIERS = re.compile(
    r'(?<!\w)p[\W_]*k[\W_]*m[\W_]*m(?:[\W_]*h[\W_]*s[\W_]*s|\s+higher\s+secondary\s+school)?(?:[\W_]*edarikk?ode)?(?!\w)'
    r'|പി[\s.\-]*കെ[\s.\-]*എം[\s.\-]*എം'
    r'|(?<!\w)edarikk?ode(?!\w)|എടരിക്കോ[ടഡ]'
    r'|(?<!\w)thottasheri(?:yar|y|ya|ar)?(?!\w)|തോട്ടശ്ശേരി|തോട്ടശേരി'
    r'|' + _CLASS_LABEL + r'\s*[:.\-]?\s*' + _CLASS_NUMBER + _SECTION_SUFFIX +
    r'|(?<!\w)' + _CLASS_ORDINAL + r'\s+' + _CLASS_LABEL + _SECTION_SUFFIX,
    re.I,
)
_CREATOR_NAME = re.compile(_NAME + r'|ശ്രീ\s*ഹരി', re.I)
_PRIVATE_DETAIL_QUESTION = re.compile(
    r'\b(?:school|class|grade|section|standard|home|hometown|village|address|district|personal\s+details|lives?|living)\b'
    r'|സ്കൂൾ|വിദ്യാലയ|ക്ലാസ്|ക്ലാസ്സ്|ഗ്രേഡ്|സ്റ്റാൻഡേർഡ്|നാട്|വീട്|താമസ|വിലാസ|പഠി|വ്യക്തിവിവര', re.I,
)

# Match the relationship to Karen, rather than a loose combination of "you"
# and a creation word. This keeps "Who built your ESP32?" and questions about
# other inventions available to the normal science/technology answer path.
_EN_TARGET = (r'\b(?:you|u|karen(?:\s+ai)?|this\s+'
              r'(?:(?:school|class|science|exhibition|ai|malayalam)\s+)*(?:assistant|robot|bot|project|device|machine))\b'
              r'(?![\'’]s\b)')
_EN_ACTION = (r'\b(?:creat(?:e[ds]?|ing)|ma(?:de|kes?|king)|buil(?:t|ds?|ding)|'
              r'develop(?:ed|s|ing)?|design(?:ed|s|ing)?|invent(?:ed|s|ing)?|'
              r'program(?:m?ed|m?ing|s)?|cod(?:e[ds]?|ing)|construct(?:ed|s|ing)?|'
              r'assembl(?:e[ds]?|ing)|engineer(?:ed|s|ing)?|manufactur(?:e[ds]?|ing)|conceiv(?:e[ds]?|ing))\b')
_EN_ROLE = (r'(?:creator|maker|builder|developer|designer|programmer|inventor|'
            r'author|coder|engineer|manufacturer|architect)s?')
_EN_POSSESSIVE = r'\b(?:your|karen(?:\s+ai)?[’\']s)\s+'
_EN_ROLE_RELATION = re.compile(
    _EN_POSSESSIVE + r'(?:(?:original|real|actual|project)\s+)*' + _EN_ROLE + r'\b'
    r'|\b' + _EN_ROLE + r'\s+(?:of|for)\s+' + _EN_TARGET,
)
_EN_BUILD_RELATION = re.compile(
    _EN_ACTION + r'\s+(?:(?:originally|really|actually|first)\s+)*' + _EN_TARGET +
    r'(?!\s+(?:laugh|cry|smile|happy|sad|think|work|feel|believe|say|do|an?\s+(?!reality\b))\b)'
    r'|' + _EN_TARGET + r'\s+(?:(?:has|have|had)\s+)?'
    r'(?:(?:not|never|really|originally|actually)\s+)*(?:was|were|is|are|be|been|being)\s+'
    r'(?:(?:not|never|really|originally|actually|first)\s+)*' + _EN_ACTION +
    r'|\b(?:was|were|is|are)\s+' + _EN_TARGET +
    r'\s+(?:(?:not|never|really|originally|actually|first)\s+)*' + _EN_ACTION +
    r'|\b(?:programming|construction|design|development)\s+(?:of|for)\s+' + _EN_TARGET +
    r'|\b(?:behind|responsible\s+for|came\s+up\s+with)\s+' + _EN_TARGET +
    r'|\b(?:brought|bring)\s+' + _EN_TARGET + r'\s+(?:to\s+life|into\s+existence)'
    r'|\bput\s+' + _EN_TARGET + r'\s+together'
    r'|\b(?:wrote|writes?|written)\s+your\s+(?:source\s+)?(?:code|software|program)\b'
    r'|\bwhose\s+(?:creation|invention|project|work)\s+(?:is|are|was|were)\s+' + _EN_TARGET,
)
_EN_NOMINAL_RELATION = re.compile(
    _EN_POSSESSIVE + r'(?:creation|development|design|construction|invention|programming)\b'
    r'|' + _EN_TARGET + r'\s+(?:(?:is|are)\s+)?(?:a|an)\s+(?:creation|invention|project)\s+of\b',
)
_EN_ATTRIBUTION = re.compile(
    r'\b(?:who(?:se|m)?|(?:which|what)\s+(?:person|student|team|company|individual|organisation|organization))\b'
    r'|\bperson\s+behind\b|\bname\s+of\s+(?:the\s+)?(?:person|student|team|creator|maker|developer)\b',
)

_ML_POSSESSIVE = r'(?:നിന്റെ|നിങ്ങളുടെ|താങ്കളുടെ|അങ്ങയുടെ|കാരെന്റെ|കാരന്റെ|കരന്റെ)'
_ML_OBJECT = (r'(?:നിന്നെ|നിങ്ങളെ|താങ്കളെ|അങ്ങയെ|കാരെനെ|കാരെനിനെ|കാരനെ|കരെനെ|കരനെ|'
              r'കാരെൻ|കാരൻ|കരെൻ|കരൻ|'
              r'ഈ\s*(?:(?:ശാസ്ത്ര|സ്കൂൾ)\s*)?(?:റോബോട്ടിനെ|സഹായിയെ|പ്രോജക്ടിനെ)|'
              r'\bkaren(?:\s*നെ)?\b)')
_ML_SUBJECT = r'(?:നീ|നിങ്ങൾ|താങ്കൾ|അങ്ങ്|കാരെൻ|കാരൻ|കരെൻ|കരൻ|\bkaren\b)'
_ML_ACTION = (r'(?:നിർമ|(?:ഉ|ു)ണ്ടാക്ക|(?:ഉ|ു)ണ്ടാക്കി|സൃഷ്ടി|വികസിപ്പി|രൂപകൽപ|രൂപകല്പ|'
              r'പ്രോഗ്രാം|പ്രോഗ്രാമി|കോഡിങ്|കോഡിംഗ്|ഡിസൈൻ|അസംബിൾ|കൂട്ടിച്ചേർ|'
              r'തയ്യാറാക്ക|പണിത|പണിയ|രൂപം\s*നൽകി|' + _EN_ACTION + r')')
_ML_ROLE = (r'(?:നിർമാതാ|സൃഷ്ടാ|സ്രഷ്ടാ|ഡെവലപ്പ|ഡിസൈന|പ്രോഗ്രാമ|'
            + _EN_ROLE + r')')
_ML_ROLE_RELATION = re.compile(
    _ML_POSSESSIVE + r'\s*' + _ML_ROLE +
    r'|(?:കാരെൻ|കാരൻ|കരെൻ|കരൻ)\s*എന്ന\s*(?:റോബോട്ടിന്റെ|പ്രോജക്ടിന്റെ|സഹായിയുടെ)\s*' + _ML_ROLE,
)
_ML_BUILD_RELATION = re.compile(
    _ML_OBJECT + r'.{0,100}' + _ML_ACTION +
    r'|' + _ML_ACTION + r'.{0,100}' + _ML_OBJECT +
    r'|' + _ML_SUBJECT + r'.{0,25}ആരുടെ.{0,25}(?:സൃഷ്ടി|നിർമിതി|പ്രോജക്ട|കണ്ടുപിടി)'
    r'|' + _ML_SUBJECT + r'.{0,15}പിന്നിൽ.{0,40}(?:വ്യക്തി|ആൾ|പ്രവർത്തി)'
    r'|' + _ML_POSSESSIVE + r'\s*(?:കോഡ്|പ്രോഗ്രാം|സോഫ്റ്റ്\s*വെയർ).{0,25}(?:എഴുത|രചി)'
    r'|' + _ML_POSSESSIVE + r'.{0,35}(?:നിർമാണ|സൃഷ്ടി|പിന്നിൽ).{0,35}(?:ആര|ക്രെഡിറ്റ്)'
    r'|ആർക്ക്.{0,20}' + _ML_POSSESSIVE + r'.{0,35}(?:നിർമാണ|സൃഷ്ടി).{0,25}ക്രെഡിറ്റ്'
    r'|നിനക്ക്\s*രൂപം\s*നൽകി',
)
_ML_ATTRIBUTION = re.compile(r'ആര(?:ാ|ാണ്|ുടെ|്)|ആർക്ക്|വ്യക്തി|ആള|വിദ്യാർഥി|വിദ്യാർത്ഥി|കമ്പനി|\bwho\b')

# Common Romanized Malayalam and mixed-script questions occur in both typing
# and speech transcripts. These are explicit stems, not fuzzy spelling guesses.
_ROMAN_OBJECT = r'\b(?:ninney?|ningaley?|thankaley?|thangaley?|angaye|karen(?:ne)?)\b'
_ROMAN_POSSESSIVE = r'\b(?:ninte|ningalude|thankalude|thangalude|angayude|kareninte)\s+'
_ROMAN_ACTION = r'\b(?:nirmi\w*|undaa?k\w*|srishti\w*|vikasippi\w*|roopakalp\w*|' + _EN_ACTION + r')'
_ROMAN_RELATION = re.compile(
    _ROMAN_OBJECT + r'.{0,70}' + _ROMAN_ACTION +
    r'|' + _ROMAN_ACTION + r'.{0,70}' + _ROMAN_OBJECT +
    r'|' + _ROMAN_POSSESSIVE + r'(?:nirmath\w*|srisht\w*|pinnil|' + _EN_ROLE + r')',
)
_ROMAN_ATTRIBUTION = re.compile(r'\b(?:aar\w*|aranu|who|whose|whom)\b')
_ROMAN_LANGUAGE = re.compile(r'\b(?:aar\w*|aranu|ninney?|ningaley?|thankaley?|thangaley?|angaye|'
                             r'ninte|ningalude|thankalude|thangalude|angayude|kareninte|nirmi\w*|undaa?k\w*)\b')

_TECHNICAL_QUESTION = re.compile(
    r'\b(?:how|when|why|what|which)\b'
    r'|എങ്ങനെ|എന്ത്|എന്തൊക്കെ|എന്തെല്ലാം|എപ്പോൾ|എന്തിനാ|എന്തിന്|ഏത്|എത്ര|ഏതൊക്കെ|കഴിയു|സാധിക്കു'
    r'|\b(?:engane|enganeyanu|eppol|enthinu)\b',
)
_NESTED_TECHNICAL_SUBJECT = re.compile(
    r'\b(?:chip|processor|board|esp32|model|language|book)\b.{0,45}'
    r'\b(?:used|required|needed|chosen|selected)\s+(?:to|for)\b'
    r'|(?:നിർമിക്കാൻ|ഉണ്ടാക്കാൻ|സൃഷ്ടിക്കാൻ).{0,45}ഉപയോഗി.{0,35}(?:ബോർഡ്|ചിപ്പ്|മോഡൽ|ഭാഷ|ഉപകരണം)',
)
_PERSONAL_QUESTION = re.compile(
    _EN_POSSESSIVE + r'(?:school|class|home|hometown|village|personal\s+details)\b'
    r'|\bwhere\s+(?:are\s+you|is\s+karen)(?:\s+from)?\s*$'
    r'|\b(?:which|what)\s+(?:school|class|village|town)\s+(?:are\s+you|is\s+karen)\b'
    r'|' + _ML_POSSESSIVE + r'\s*(?:സ്കൂൾ|വിദ്യാലയം|ക്ലാസ്|നാട്|വീട്|വ്യക്തിവിവര)',
)
_PERSONAL_DETAIL_REQUEST = re.compile(
    r'\b(?:what|which)\s+(?:school|class|grade|section|standard|home|hometown|village|address|district)\b'
    r'|(?:' + _EN_ROLE + r'|' + _NAME + r')[\'’]s\s+(?:school|class|grade|section|home|address|village|district)\b'
    r'|\b(?:his|her|their)\s+(?:school|class|grade|section|home|address|village|district)\b'
    r'|\b(?:home\s+address|personal\s+details|lives?|living)\b'
    r'|(?:ഏത്\s*(?:സ്കൂൾ|വിദ്യാലയം|ക്ലാസ്|ഗ്രേഡ്|നാട്)|'
    r'(?:സ്കൂൾ|വിദ്യാലയം|ക്ലാസ്|ഗ്രേഡ്).{0,8}ഏത്|'
    r'(?:ന്റെ|യുടെ|റുടെ|വിന്റെ|യാളുടെ|വ്യക്തിയുടെ)\s*(?:സ്കൂൾ|വിദ്യാലയം|ക്ലാസ്|നാട്|വീട്|വിലാസ|താമസ)|പഠി)',
)
_IMPLICIT_CREATOR = re.compile(
    r'^(?:who\s+(?:(?:has|had|really|originally|actually)\s+)*' + _EN_ACTION + r'\s+(?:it|this)'
    r'|who\s+(?:is|are|was|were)\s+the\s+' + _EN_ROLE +
    r'|(?:ഇത്|ഇതിനെ).{0,45}' + _ML_ACTION + r'.{0,25}(?:ആര|വ്യക്തി)[^.!?;]*'
    r'|(?:ഇത്|ഇതിനെ).{0,25}ആര.{0,30}' + _ML_ACTION + r'[^.!?;]*'
    r'|ആര.{0,15}(?:ഇത്|ഇതിനെ).{0,35}' + _ML_ACTION + r'[^.!?;]*)[ .!?;]*$',
)
_SELF_TOPIC = re.compile(
    r'(?:how\s+(?:do\s+you|does\s+karen)\s+(?:work|function|operate)'
    r'|tell\s+me\s+about\s+(?:karen|you|yourself|this\s+assistant)'
    r'|what\s+can\s+you\s+do|who\s+(?:are\s+you|is\s+karen)'
    r'|' + _ML_SUBJECT + r'\s*എങ്ങനെ\s*പ്രവർത്തി\S*'
    r'|' + _ML_OBJECT + r'\s*ക്കുറിച്ച്\s*പറയ\S*)[ .!?;]*',
)


def _matching_view(text):
    """Return matching text and offsets into the untouched original characters."""
    ignored = '\u200b\u200c\u200d\u2060\ufeff'
    starts = [0] + [i for i, char in enumerate(text) if i and
                    not unicodedata.category(char).startswith('M') and char not in ignored]
    pieces, offsets = [], []
    for start, end in zip(starts, starts[1:] + [len(text)]):
        # Keep combining marks with their base when comparing Malayalam. Offset
        # tracking lets us retain superscripts (10³), units and joiners verbatim.
        piece = unicodedata.normalize('NFKC', text[start:end]).translate(dict.fromkeys(map(ord, ignored)))
        pieces.append(piece)
        offsets.extend([(start, end)] * len(piece))
    return ''.join(pieces), offsets


def _normalized(text):
    return _matching_view(text)[0]


def _intent_text(text):
    """Canonicalize only the matching view, keeping stored/spoken text intact."""
    text = _normalized(text).casefold().replace('ര്', 'ർ')
    text = text.replace('നിർമ്മ', 'നിർമ').replace('നിൻ്റെ', 'നിന്റെ').replace('കാരെൻ്റെ', 'കാരെന്റെ')
    text = re.sub(r'കാരെന്(?=\s|$)', 'കാരെൻ', text)
    text = text.replace('’', "'")
    for contraction, expanded in (("who's", 'who is'), ("who're", 'who are'),
                                  ("you're", 'you are'), ("you've", 'you have')):
        text = re.sub(r'\b' + contraction + r'\b', expanded, text)
    # Retain sentence boundaries and possessives. Dashes and other punctuation
    # can separate words; Malayalam combining marks must never be stripped.
    text = ''.join(' ' if unicodedata.category(char).startswith('P') and char not in "'.!?;"
                   else char for char in text)
    return ' '.join(text.split())


def _build_relation(text):
    if _EN_BUILD_RELATION.search(text) or _EN_NOMINAL_RELATION.search(text):
        return True
    if re.search(r'[\u0d00-\u0d7f]', text) and _ML_BUILD_RELATION.search(text):
        return True
    return bool(_ROMAN_LANGUAGE.search(text) and _ROMAN_RELATION.search(text))


def _role_attribution(text):
    for match in _EN_ROLE_RELATION.finditer(text):
        before = text[:match.start()].strip()
        if (not before or re.match(r'^(?:is|was|are|were)\b', before) or
                re.search(r'\b(?:is|are|was|were|about|names?(?:\s+of)?|identify|describe|confirm|tell\s+me)'
                          r'\s*(?:the\s*)?$', before)):
            return True
    return bool(_ML_ROLE_RELATION.search(text))


def _creator_relation(text):
    return bool(_build_relation(text) or _EN_ROLE_RELATION.search(text) or _ML_ROLE_RELATION.search(text))


def _private_question(text):
    if contains_identity(text) or _PERSONAL_QUESTION.search(text.rstrip(' .!?;')):
        return True
    related = _creator_relation(text) or _CREATOR_NAME.search(text)
    if related and _PRIVATE_DETAIL_QUESTION.search(text) and _PERSONAL_DETAIL_REQUEST.search(text):
        return True
    role = _EN_ROLE_RELATION.search(text) or _ML_ROLE_RELATION.search(text) or _CREATOR_NAME.search(text)
    return bool(role and re.search(r'\bwhere\b|എവിട|\bevide\b', text))


def _creator_question(text):
    # Keep a question about another invention from borrowing a "who" cue in a
    # separate sentence. Mixed creator/how-it-works questions retain the credit.
    for clause in re.split(r'[.!?;]|\b(?:and|but)\b|കൂടാതെ', text):
        role = _role_attribution(clause)
        if not (_build_relation(clause) or role) or _NESTED_TECHNICAL_SUBJECT.search(clause):
            continue
        attribution = any(pattern.search(clause) for pattern in (
            _EN_ATTRIBUTION, _ML_ATTRIBUTION, _ROMAN_ATTRIBUTION,
        ))
        if role and re.search(r'\bnames?\b|പേര്', clause):
            attribution = True
        if attribution or not _TECHNICAL_QUESTION.search(clause):
            return True
    return bool(_CREATOR_NAME.search(text) and not _TECHNICAL_QUESTION.search(text))


def _implicit_creator_question(text, history):
    if not _IMPLICIT_CREATOR.fullmatch(text):
        return False
    if not history:
        # At the beginning of an exhibit conversation, "this" is Karen. After
        # another topic has been discussed, resolve the short question from the
        # last completed user turn instead of attributing that invention to him.
        return True
    previous = next((_intent_text(value) for role, value in reversed(history) if role == 'user'), '')
    last_reply = next((value for role, value in reversed(history) if role == 'model'), '')
    return bool(previous and (
        _private_question(previous) or _creator_question(previous) or
        (_build_relation(previous) and not _NESTED_TECHNICAL_SUBJECT.search(previous)) or
        _SELF_TOPIC.fullmatch(previous) or
        (_IMPLICIT_CREATOR.fullmatch(previous) and last_reply == CREATOR_REPLY)
    ))


def contains_identity(text):
    return bool(_IDENTIFIERS.search(_normalized(text)))


def anonymous_memory(text):
    """Remove identifying biography sentences, retaining unrelated saved facts."""
    text = text.strip()
    if not contains_identity(text):
        return text or DEFAULT_MEMORY
    # Replace complete identity spans before finding sentence boundaries, so
    # dotted school initials cannot be split apart and then silently rejoined.
    marker = '\x00private-identity\x00'
    view, offsets = _matching_view(text)
    parts, cursor = [], 0
    for match in _IDENTIFIERS.finditer(view):
        start, end = offsets[match.start()][0], offsets[match.end() - 1][1]
        if start >= cursor:
            parts.extend((text[cursor:start], marker))
        cursor = max(cursor, end)
    parts.append(text[cursor:])
    masked = ''.join(parts)
    sentences = re.split(r'(?<=[.!?])\s+|\n+', masked)
    kept = [part for part in sentences if marker not in part]
    clean = ' '.join(kept).strip()
    return clean if clean and not contains_identity(clean) else DEFAULT_MEMORY


def identity_question(message, history=()):
    text = _intent_text(message)
    return _private_question(text) or _creator_question(text) or _implicit_creator_question(text, history)


def identity_reply(message):
    """Answer name-only questions locally; never disclose school or home details."""
    return PRIVATE_REPLY if _private_question(_intent_text(message)) else CREATOR_REPLY


def anonymous_reply(text):
    """Protect generated text before it becomes speech, JSON or saved history."""
    return PRIVATE_REPLY if contains_identity(text) else text


def anonymous_history(history):
    return [(role, (PRIVATE_QUESTION if role == 'user' else PRIVATE_REPLY)
             if contains_identity(text) else text) for role, text in history]
