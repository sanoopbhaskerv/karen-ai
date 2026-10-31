"""Keep the exhibition assistant separate from the student's personal identity."""
import re
import unicodedata


DEFAULT_MEMORY = ('Your name is Karen. You are a friendly Malayalam science exhibition assistant. '
                  'Explain things simply. An ESP32 can record and play audio while a Python server '
                  'uses online speech recognition, Gemini and speech synthesis.')
PRIVATE_REPLY = ('പ്രദർശനത്തിന്റെ ഭാഗമായി നിർമ്മാതാവിന്റെ പേര്, സ്കൂൾ, വ്യക്തിവിവരങ്ങൾ പങ്കിടുന്നില്ല. '
                 'കാരെൻ എങ്ങനെ പ്രവർത്തിക്കുന്നു എന്ന് വിശദീകരിക്കാം.')
PRIVATE_QUESTION = 'നിർമ്മാതാവിന്റെ വ്യക്തിവിവരങ്ങളെക്കുറിച്ചുള്ള ചോദ്യം.'

# Match the previously published biography, including spaced initials and common
# Malayalam spellings. General places (Kerala/Malappuram) and class numbers are
# deliberately retained: they are useful science-fair knowledge, not identities.
_NAME = (r'(?<!\w)(?:' + '|'.join(r'[\W_]*'.join(name) for name in
         ('sreehari', 'shreehari', 'srihari', 'shrihari')) + r')(?:[\W_]*v)?(?!\w)')
_IDENTIFIERS = re.compile(
    _NAME +
    r'|ശ്രീ\s*ഹരി'
    r'|(?<!\w)p[\W_]*k[\W_]*m[\W_]*m(?:[\W_]*h[\W_]*s[\W_]*s|\s+higher\s+secondary\s+school)?(?:[\W_]*edarikk?ode)?(?!\w)'
    r'|പി[\s.\-]*കെ[\s.\-]*എം[\s.\-]*എം'
    r'|(?<!\w)thottasheri(?:yar|y|ya|ar)?(?!\w)|തോട്ടശ്ശേരി|തോട്ടശേരി'
    r'|(?:class|section|standard|ക്ലാസ്|ക്ലാസ്സ്)\s*[:.\-]?\s*(?:9|ix|nine|ഒമ്പത്|ഒൻപത്)\s*[.\-]?\s*(?:s|എസ്)(?!\w)',
    re.I,
)
_CREATOR_FACT = re.compile(
    r'\byou\s+(?:(?:were|are)\s+)?(?:created|built|made|developed|designed)\s+by\b'
    r'|\b(?:your|karen[’\']s)\s+(?:creator|maker|builder|developer|author)\b'
    r'|(?:നിന്റെ|കാരെന്റെ)\s*(?:നിർമ്മാതാ|നിർമാതാ)', re.I,
)
_IDENTITY_QUESTION = re.compile(
    r'\b(?:your|karen[’\']s)\s+(?:creator|maker|builder|developer|author|school|class|home|hometown|village|personal\s+details)\b'
    r'|\b(?:who|which\s+(?:student|person|team))\s+(?:really\s+)?(?:created|built|made|developed|invented|designed)\s+(?:you|karen|this\s+(?:assistant|project))\b'
    r'|\b(?:creator|maker|builder|developer)\s+of\s+(?:karen|this\s+(?:assistant|project))\b'
    r'|\b(?:where\s+(?:are|is)|(?:which|what)\s+(?:school|class|village|town)\s+(?:are|is))\s+(?:you|karen)\b'
    r'|(?:നിന്റെ|നിങ്ങളുടെ|കാരെന്റെ)\s*(?:നിർമ്മാതാ|നിർമാതാ|സൃഷ്ടാവ|സ്കൂൾ|വിദ്യാലയം|ക്ലാസ്|നാട്|വീട്|വ്യക്തിവിവര)'
    r'|(?:നിന്നെ|നിങ്ങളെ|കാരെനെ|കാരെനിനെ).{0,30}(?:ആരാണ്|ആരാ|ആര്).{0,20}(?:നിർമ|ഉണ്ടാക്ക|സൃഷ്ടി)'
    r'|(?:നിന്നെ|നിങ്ങളെ|കാരെനെ|കാരെനിനെ).{0,20}(?:നിർമ|ഉണ്ടാക്ക|സൃഷ്ടി).{0,20}(?:ആരാണ്|ആരാ|ആര്)'
    r'|(?:ആരാണ്|ആര്).{0,10}(?:നിന്നെ|നിങ്ങളെ|കാരെനെ).{0,20}(?:നിർമ|ഉണ്ടാക്ക|സൃഷ്ടി)', re.I,
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
    if not (contains_identity(text) or _CREATOR_FACT.search(_normalized(text))):
        return text or DEFAULT_MEMORY
    # Replace complete identity spans before finding sentence boundaries, so
    # dotted names/initials cannot be split apart and then silently rejoined.
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
    kept = [part for part in sentences
            if marker not in part and not _CREATOR_FACT.search(_normalized(part))]
    clean = ' '.join(kept).strip()
    return clean if clean and not contains_identity(clean) else DEFAULT_MEMORY


def identity_question(message):
    text = _normalized(message)
    return contains_identity(text) or bool(_IDENTITY_QUESTION.search(text))


def anonymous_reply(text):
    """Protect generated text before it becomes speech, JSON or saved history."""
    return PRIVATE_REPLY if contains_identity(text) else text


def anonymous_history(history):
    return [(role, (PRIVATE_QUESTION if role == 'user' else PRIVATE_REPLY)
             if contains_identity(text) else text) for role, text in history]
