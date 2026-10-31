"""Live model listing + inference, without printing keys or changing memory/history."""
import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import Providers, create_app, DEFAULT_MEMORY


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', help='Exact model ID returned by models.list')
    parser.add_argument('--list-only', action='store_true')
    args = parser.parse_args()
    # App startup can migrate a legacy identity. A diagnostic must never touch
    # the owner's real saved facts, even in --list-only or missing-key cases.
    with tempfile.TemporaryDirectory(prefix='karen-model-check-') as temporary:
        app = create_app({'MEMORY_PATH': str(Path(temporary) / 'memory.txt'), 'DEMO_MODE': False})
        return diagnose(app, args)


def diagnose(app, args):
    if not app.config['GEMINI_API_KEY']:
        print('GEMINI_API_KEY is missing; configure it locally.'); return 1
    from google import genai
    from google.genai import types
    try:
        with genai.Client(api_key=app.config['GEMINI_API_KEY'], http_options=types.HttpOptions(
                timeout=15000, retry_options=types.HttpRetryOptions(attempts=1))) as client:
            names = sorted(m.name.removeprefix('models/') for m in client.models.list()
                           if 'generateContent' in (m.supported_actions or []))
        print(json.dumps({'generateContent_models': names}, ensure_ascii=False))
    except Exception as exc:
        # Exception text/URLs may contain credentials. Never print them.
        print(json.dumps({'listing': 'failed', 'type': type(exc).__name__,
                          'provider_code': getattr(exc, 'code', None)})); return 1
    if args.list_only:
        print('Listing succeeded. Inference has NOT been tested.'); return 0
    model = args.model or app.config['GEMINI_MODEL']
    if model not in names:
        print('Selected model is absent from the API listing. No inference attempted.'); return 1
    app.config['GEMINI_MODEL'] = model
    try:
        # Isolated diagnostic: never add a conversation turn or update saved facts.
        reply = Providers(app).answer(DEFAULT_MEMORY, [], 'മഴ എങ്ങനെയാണ് ഉണ്ടാകുന്നത്?')
        print(json.dumps({'model': model, 'inference': 'succeeded', 'reply': reply}, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({'model': model, 'inference': 'failed', 'code': getattr(exc, 'code', 'internal_error')}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
