"""Fresh facts use native search; citations stay out of spoken prose."""
from datetime import date
import json

import httpx
import pytest

from exhibition_identity import PRIVATE_REPLY
from openai_provider import answer_prose, citation_sources, needs_live_information
from test_openai_provider import mocked_openai, text_result


TODAY = date(2026, 11, 2)
SOURCE = {'url': 'https://www.icc-cricket.com/news/final', 'title': 'ICC final result'}


@pytest.mark.parametrize('question', [
    'Who won 2026 t20 world cup men', 'Who won nobel price last year',
    '2026 പുരുഷ ടി20 ലോകകപ്പ് വിജയി ആരാണ്?', 'കഴിഞ്ഞ വർഷത്തെ നോബൽ സമാധാന സമ്മാനം ആര് നേടി?',
    'Who is the current president of India?', 'Who is the chief minister of Kerala?',
    'What is the weather today?', 'What is the latest news?',
    'Who will win the 2040 World Cup?', '2025ലെ രസതന്ത്ര നോബൽ ജേതാക്കൾ ആരാണ്?',
])
def test_time_sensitive_questions_require_search(question):
    assert needs_live_information(question, [], TODAY)


@pytest.mark.parametrize('question', ['How does rain form?', 'Explain an ESP32.', 'What is gravity?'])
def test_ordinary_science_does_not_force_a_search(question):
    assert not needs_live_information(question, [], TODAY)


def test_freshness_year_rolls_with_actual_calendar():
    assert needs_live_information('Who won in 2026?', [], TODAY)
    assert not needs_live_information('Who won in 2026?', [], date(2030, 1, 1))
    previous = [('user', 'Who won the Nobel prize last year?'), ('model', 'Which category?')]
    assert needs_live_information('Peace prize', previous, TODAY)
    assert not needs_live_information('How does rain form?', previous, TODAY)


def annotated_result(reply='ഇന്ത്യ വിജയിച്ചു. citeturn0search0', sources=(SOURCE,)):
    result = text_result(reply)
    result['output'].insert(0, {'type': 'web_search_call', 'status': 'completed'})
    result['output'][-1]['content'][0]['annotations'] = [
        {'type': 'url_citation', **source} for source in sources]
    return result


def test_search_request_uses_current_indian_date_and_retains_configured_model(mocked_openai, monkeypatch):
    app, provider, calls, responses, options = mocked_openai
    monkeypatch.setattr('openai_provider.today_in_india', lambda: TODAY)
    responses.append(httpx.Response(200, json=annotated_result()))
    reply, sources = provider.answer_with_sources('Public science facts', [], 'Who won 2026 t20 world cup men')
    body = json.loads(calls[0].content)
    assert body['model'] == 'gpt-6-luna'
    assert body['tools'] == [{'type': 'web_search'}]
    assert body['tool_choice'] == {'type': 'web_search'}
    assert body['max_tool_calls'] == 2
    assert body['reasoning'] == {'effort': 'low'}
    assert body['store'] is False
    assert '2026-11-02' in body['instructions'] and 'Last year means 2025' in body['instructions']
    assert sources == [SOURCE] and reply == 'ഇന്ത്യ വിജയിച്ചു.'
    assert calls[0].extensions['timeout']['read'] == 45


def test_ordinary_question_has_optional_search_and_fast_reasoning(mocked_openai):
    app, provider, calls, responses, options = mocked_openai
    provider.answer('facts', [], 'How does rain form?')
    body = json.loads(calls[0].content)
    assert body['tool_choice'] == 'auto' and body['reasoning'] == {'effort': 'none'}


@pytest.mark.parametrize('url', [
    'javascript:alert(1)', '//example.com/source', 'https://',
    'https://username:password@example.com/', 'https://example.com/\nheader',
    'https://example.com/path with spaces', 'https://[invalid',
])
def test_untrusted_citation_urls_are_not_rendered(url):
    assert not citation_sources([{'annotations': [{'type': 'url_citation', 'url': url}]}])


def test_sources_are_bounded_deduplicated_and_missing_titles_have_real_hostnames():
    annotations = [{'type': 'url_citation', 'url': f'https://example.com/{i}'} for i in range(12)]
    sources = citation_sources([{'annotations': annotations + annotations}])
    assert len(sources) == 8
    assert sources[0]['title'] == 'example.com'
    assert len({source['url'] for source in sources}) == 8


def test_citations_never_reuse_previous_answer_sources(mocked_openai):
    app, provider, calls, responses, options = mocked_openai
    responses.append(httpx.Response(200, json=annotated_result()))
    assert provider.answer_with_sources('facts', [], 'Who won in 2026?')[1] == [SOURCE]
    assert provider.answer_with_sources('facts', [], 'Explain gravity.')[1] == []


def test_private_generated_answers_and_private_source_titles_are_filtered(mocked_openai):
    app, provider, calls, responses, options = mocked_openai
    responses.append(httpx.Response(200, json=annotated_result('The school is PKMMHSS Edarikode.')))
    assert provider.answer_with_sources('facts', [], 'Explain a science project.') == (PRIVATE_REPLY, [])
    assert not citation_sources([{'annotations': [{'type': 'url_citation',
        'url': 'https://example.com/result', 'title': 'PKMMHSS Edarikode'}]}])


def test_verified_source_markdown_and_urls_are_not_read_aloud():
    url = SOURCE['url']
    assert answer_prose(f'ഇന്ത്യ വിജയിച്ചു. ([icc-cricket.com]({url}))', [SOURCE]) == 'ഇന്ത്യ വിജയിച്ചു.'
    assert answer_prose(f'[ഇന്ത്യ വിജയിച്ചു]({url}).', [SOURCE]) == 'ഇന്ത്യ വിജയിച്ചു.'
    assert answer_prose(f'ഇന്ത്യ വിജയിച്ചു. ({url})', [SOURCE]) == 'ഇന്ത്യ വിജയിച്ചു.'
    assert answer_prose('Read [the project](https://example.com/project).', [SOURCE]) == 'Read [the project](https://example.com/project).'


def test_percent_encoded_private_citation_urls_are_filtered_before_direct_provider_delivery():
    assert not citation_sources([{'annotations': [{'type': 'url_citation',
        'url': 'https://example.com/?q=PKMMHSS%20Edarikode', 'title': 'A source'}]}])
