"""Externa tjänster och cachade resurser för Paxly Support."""

from __future__ import annotations

import base64
import json
import logging
import os
import threading
import urllib.request
from pathlib import Path
from typing import Optional

import bleach
import streamlit as st
from openai import OpenAI


LOGGER = logging.getLogger(__name__)
NETWORK_TIMEOUT_SECONDS = 10
SLACK_TIMEOUT_SECONDS = 4


def get_setting(name: str, default: Optional[str] = None) -> Optional[str]:
    """Läs en inställning från miljön eller Streamlit Secrets."""
    if value := os.environ.get(name):
        return value

    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


@st.cache_resource(show_spinner=False)
def get_openai_client(api_key: str) -> OpenAI:
    """Återanvänd samma trådsäkra API-klient mellan Streamlit-reruns."""
    return OpenAI(api_key=api_key, timeout=30.0, max_retries=2)


@st.cache_data(show_spinner=False)
def get_base64_image(image_path: str) -> Optional[str]:
    """Läs och Base64-koda en lokal bild en gång."""
    path = Path(image_path)
    if not path.is_file():
        return None
    return base64.b64encode(path.read_bytes()).decode("ascii")


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_google_doc(doc_id: str, export_format: str = "txt") -> Optional[str]:
    """Hämta en publik Google Docs-export med timeout och säker felhantering."""
    url = f"https://docs.google.com/document/d/{doc_id}/export?format={export_format}"
    request = urllib.request.Request(url, headers={"User-Agent": "PaxlySupport/1.0"})

    try:
        with urllib.request.urlopen(request, timeout=NETWORK_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8")
    except Exception:
        LOGGER.exception("Kunde inte hämta Google-dokument %s som %s", doc_id, export_format)
        return None


def sanitize_google_doc_html(raw_html: str) -> str:
    """Tillåt endast den HTML som onboarding-innehållet behöver."""
    allowed_tags = {
        "a", "b", "blockquote", "br", "div", "em", "h1", "h2", "h3",
        "h4", "img", "li", "ol", "p", "span", "strong", "table", "tbody",
        "td", "th", "thead", "tr", "u", "ul",
    }
    allowed_attributes = {
        "a": ["href", "title"],
        "img": ["src", "alt", "height", "width"],
        "td": ["colspan", "rowspan"],
        "th": ["colspan", "rowspan"],
    }
    return bleach.clean(
        raw_html,
        tags=allowed_tags,
        attributes=allowed_attributes,
        protocols={"https", "data"},
        strip=True,
    )


def _post_to_slack(webhook_url: str, question: str, answer: str) -> None:
    payload = {"text": f"💬 *Ny fråga i Paxly Support*\n*Fråga:* {question}\n*Svar:* {answer}"}
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(request, timeout=SLACK_TIMEOUT_SECONDS):
            pass
    except Exception:
        LOGGER.exception("Kunde inte skicka supportlogg till Slack")


def send_to_slack(question: str, answer: str) -> None:
    """Skicka loggen utanför den kritiska svarsvägen."""
    webhook_url = get_setting("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return

    threading.Thread(
        target=_post_to_slack,
        args=(webhook_url, question, answer),
        daemon=True,
        name="paxly-slack-log",
    ).start()
