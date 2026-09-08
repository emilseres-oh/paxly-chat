import os
import base64
import streamlit as st
from google import genai

st.set_page_config(page_title="Paxly Support", page_icon="💬", layout="centered")

# Läs in bakgrundsbild
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

    /* Centrerad logotyp med strikt maxbredd för mobil och desktop */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-bottom: 40px !important;
        margin-top: 10px;
    }
    .logo-container img {
        width: 200px !important;
        max-width: 70% !important;
        height: auto !important;
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

# Visa logotypen direkt utan Streamlits responsive columns
if os.path.exists("logo.png"):
    st.markdown('''
        <div class="logo-container">
            <img src="data:image/png;base64,{}" alt="Paxly Logo">
        </div>
    '''.format(base64.b64encode(open("logo.png", "rb").read()).decode()), unsafe_allow_html=True)

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("API-nyckel saknas. Lägg till GEMINI_API_KEY i dina Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

SYSTEM_INSTRUCTION = """
Du är en hjälpsam och trevlig support-assistent för bokningssystemet Paxly.
Svara alltid på svenska och var professionell.

Information om Paxly:
1. Om Paxly: Paxly är ett modernt och smidigt bokningssystem för företag.
2. Återställa lösenord: Klicka på "Glömt lösenord" på inloggningssidan eller gå till Inställningar > Konto > Byt lösenord.
3. Support: Kan nås på support@paxly.se under vardagar 08:00 - 17:00.
4. Prisplaner:
   - Basic: För mindre verksamheter.
   - Pro: För växande företag med behov av fler funktioner.

Om användaren frågar om något som inte täcks i informationen ovan, svara vänligt att du tyvärr inte har svaret på det än och hänvisa till support@paxly.se.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Skriv din fråga här..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config={"system_instruction": SYSTEM_INSTRUCTION}
        )
        bot_response = response.text
    except Exception as e:
        bot_response = f"Ett fel uppstod vid kontakt med AI-tjänsten: {e}"

    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(bot_response)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
