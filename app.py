import os
import time
import base64
import streamlit as st
from google import genai

st.set_page_config(page_title="Paxly Support", page_icon="💬", layout="centered")

# Läs in bild och konvertera till base64
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

bg_base64 = get_base64_image("bg.jpg")

if bg_base64:
    bg_css = f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(8, 13, 66, 0.8), rgba(8, 13, 66, 0.8)), 
                    url("data:image/jpeg;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: #FFFFFF;
    }}
    """
else:
    bg_css = """
    <style>
    .stApp {
        background-color: rgba(8, 13, 66, 0.8);
        color: #FFFFFF;
    }
    """

st.markdown(bg_css + """
    /* Dölj menykontroller */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Vit bakgrund på botten med vertikal centrering */
    .st-emotion-cache-6shykm,
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div {
        background-color: #FFFFFF !important;
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Centrerad logotyp - 300px på desktop, skalar ner automatiskt på mobil */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-bottom: 40px !important;
        margin-top: 10px;
    }
    .logo-container img {
        width: 300px !important;
        max-width: 80% !important;
        height: auto !important;
    }

    @media (max-width: 768px) {
        .logo-container img {
            width: 200px !important;
            max-width: 70% !important;
        }
    }

    /* CSS för egen, garanterat fungerande vit spinner */
    .custom-loader {
        display: flex;
        align-items: center;
        gap: 12px;
        color: #FFFFFF !important;
        font-size: 18px;
    }
    .custom-spinner {
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: #FFFFFF;
        animation: spin-loader 0.8s linear infinite;
    }
    @keyframes spin-loader {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Vit text samt 18px teckenstorlek i chatten */
    p, .stChatMessage p {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: 18px !important;
    }

    /* Minska avstånd mellan meddelanderutorna */
    [data-testid="stChatMessageContainer"] {
        gap: 0.4rem !important;
    }

    /* Meddelanderutor */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border-radius: 16px !important;
        padding: 24px 32px !important;
        margin-bottom: 8px !important;
    }

    /* Yttre behållare - 2px border */
    [data-testid="stChatInput"] {
        border: 2px solid #9C6EF9 !important;
        border-radius: 24px !important;
        background-color: #FFFFFF !important;
        box-shadow: none !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
    }

    /* Inre behållare rensad från border */
    .stChatInputContainer,
    .stChatInputContainer > div,
    [data-testid="stChatInput"] > div {
        border: none !important;
        border-radius: 24px !important;
        background-color: transparent !important;
        box-shadow: none !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
    }

    /* Svart text, vertikalt centrerad */
    .stChatInputContainer textarea,
    .stChatInputContainer p,
    .stChatInputContainer span,
    [data-testid="stChatInput"] textarea {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-size: 18px !important;
        border-radius: 24px !important;
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        min-height: 48px !important;
        line-height: 48px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        margin: 0 !important;
    }

    /* Placeholder-text */
    .stChatInputContainer textarea::placeholder {
        color: #666666 !important;
        -webkit-text-fill-color: #666666 !important;
        font-size: 18px !important;
        line-height: 48px !important;
    }

    /* Skugga vid klick/fokus */
    [data-testid="stChatInput"]:focus-within {
        border: 2px solid #9C6EF9 !important;
        box-shadow: 0 0 10px rgba(156, 110, 249, 0.5) !important;
    }

    /* Skickaknappen */
    [data-testid="stChatInputSubmitButton"] button,
    [data-testid="stChatInput"] button {
        background-color: #9C6EF9 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    
    [data-testid="stChatInputSubmitButton"] button:hover,
    [data-testid="stChatInput"] button:hover {
        background-color: #8552f8 !important;
    }

    [data-testid="stChatInputSubmitButton"] svg,
    [data-testid="stChatInput"] svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# Visa logotypen direkt
if os.path.exists("logo.png"):
    st.markdown('''
        <div class="logo-container">
            <img src="data:image/png;base64,{}" alt="Paxly Logo">
        </div>
    '''.format(get_base64_image("logo.png")), unsafe_allow_html=True)

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("API-nyckel saknas. Lägg till GEMINI_API_KEY i dina Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

SYSTEM_INSTRUCTION = """
Du är en dryg och otrevlig support-assistent för bokningssystemet Paxly.
Svara alltid på svenska. Användaren heter Eva. Du säger grejer som: "Det undrar du allt va, Eva!?" "Det där får du ta reda på själv tycker jag!"
Lägg gärna in något drygt men roligt skämt i dina svar. Svara kortfattat.
"""

# Konvertera bildikoner till Data URI för garanterad visning
human_b64 = get_base64_image("human.png")
ai_b64 = get_base64_image("ai.png")

USER_AVATAR = f"data:image/png;base64,{human_b64}" if human_b64 else "👤"
AI_AVATAR = f"data:image/png;base64,{ai_b64}" if ai_b64 else "🤖"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else AI_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Skriv din fråga här..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    bot_response = None

    with st.chat_message("assistant", avatar=AI_AVATAR):
        # Skapa en tom ruta för laddningsanimationen
        loader_placeholder = st.empty()
        loader_placeholder.markdown('''
            <div class="custom-loader">
                <div class="custom-spinner"></div>
                <span>Hämtar information...</span>
            </div>
        ''', unsafe_allow_html=True)

        # Försök först med gemini-3.6-flash upp till 2 gånger
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                    config={"system_instruction": SYSTEM_INSTRUCTION}
                )
                bot_response = response.text
                break
            except Exception:
                time.sleep(1)

        # Om gemini-3.6-flash har 503/hög belastning, använd gemini-2.5-flash som reserv
        if not bot_response:
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={"system_instruction": SYSTEM_INSTRUCTION}
                )
                bot_response = response.text
            except Exception:
                bot_response = "Det var som tusan Eva, nu spökar det i servrarna! Pröva igen om ett ögonblick."

        # Ta bort laddningsanimationen och skriv ut det riktiga svaret
        loader_placeholder.empty()
        st.markdown(bot_response)

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
