# Paxly Support

Streamlit-app med en OpenAI-baserad supportchatt och en separat onboarding-sida.

## Konfiguration

Lägg hemligheter i Streamlit Cloud eller i `.streamlit/secrets.toml` lokalt:

```toml
OPENAI_API_KEY = "sk-..."
SLACK_WEBHOOK_URL = "https://hooks.slack.com/..." # valfri
```

`OPENAI_MODEL` kan sättas som miljövariabel eller Streamlit-hemlighet. Standardmodellen
är `gpt-5.5`.

## Lokal körning

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Chatten finns på `/` och onboardingen på `/onboarding`.

## Integritet

Frågor och svar skickas endast till Slack när användaren aktivt godkänner det för den
aktuella webbläsarsessionen. API-nycklar får aldrig checkas in i Git.

## Tester

```bash
python -m unittest discover -s tests
```
