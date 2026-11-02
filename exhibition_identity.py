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
# Keep the same object forms in every Malayalam word order, including the
# formal pronouns commonly returned by speech recognition.
_SELF_OBJECT = r'(?:നിന്നെ|നിങ്ങളെ|താങ്കളെ|അങ്ങയെ|കാരെനെ|കാരെനിനെ)'
_CREATION_ACTION = r'(?:നിർമ|ഉണ്ടാക്ക|സൃഷ്ടി|വികസിപ്പി|രൂപകൽപ്പന)'
_IDENTITY_QUESTION = re.compile(
    r'\b(?:your|karen[’\']s)\s+(?:creator|maker|builder|developer|author|school|class|home|hometown|village|personal\s+details)\b'
    r'|\b(?:who|which\s+(?:student|person|team))\s+(?:really\s+)?(?:created|built|made|developed|invented|designed)\s+(?:you|karen|this\s+(?:assistant|project))\b'
    r'|\b(?:creator|maker|builder|developer)\s+of\s+(?:karen|this\s+(?:assistant|project))\b'
    r'|\b(?:where\s+(?:are|is)|(?:which|what)\s+(?:school|class|village|town)\s+(?:are|is))\s+(?:you|karen)\b'
    r'|(?:നിന്റെ|നിങ്ങളുടെ|താങ്കളുടെ|അങ്ങയുടെ|കാരെന്റെ)\s*(?:നിർമ്മാതാ|നിർമാതാ|സൃഷ്ടാവ|സ്കൂൾ|വിദ്യാലയം|ക്ലാസ്|നാട്|വീട്|വ്യക്തിവിവര)'
    r'|' + _SELF_OBJECT + r'.{0,30}(?:ആരാണ്|ആരാ|ആര്).{0,20}' + _CREATION_ACTION +
    r'|' + _SELF_OBJECT + r'.{0,20}' + _CREATION_ACTION + r'.{0,20}(?:ആരാണ്|ആരാ|ആര്)'
    r'|(?:ആരാണ്|ആര്).{0,10}' + _SELF_OBJECT + r'.{0,20}' + _CREATION_ACTION, re.I,
)


_CREATOR_NAME = re.compile(_NAME + r'|ശ്രീ\s*ഹരി', re.I)
_PRIVATE_DETAIL_QUESTION = re.compile(
    r'\b(?:school|class|grade|section|standard|home|hometown|village|address|district|location|where|from|personal\s+details)\b'
    r'|സ്കൂൾ|വിദ്യാലയ|ക്ലാസ്|ക്ലാസ്സ്|ഗ്രേഡ്|സ്റ്റാൻഡേർഡ്|നാട്|വീട്|താമസ|വിലാസ|പഠി|വ്യക്തിവിവര', re.I,
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


def identity_question(message):
    text = _normalized(message)
    return contains_identity(text) or bool(_IDENTITY_QUESTION.search(text) or _CREATOR_NAME.search(text))


def identity_reply(message):
    """Answer name-only questions locally; never disclose school or home details."""
    text = _normalized(message)
    return PRIVATE_REPLY if contains_identity(text) or _PRIVATE_DETAIL_QUESTION.search(text) else CREATOR_REPLY


def anonymous_reply(text):
    """Protect generated text before it becomes speech, JSON or saved history."""
    return PRIVATE_REPLY if contains_identity(text) else text


def anonymous_history(history):
    return [(role, (PRIVATE_QUESTION if role == 'user' else PRIVATE_REPLY)
             if contains_identity(text) else text) for role, text in history]
