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

    /* Logotypens storlek och avstånd */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 60px;
        margin-top: 20px;
    }
    .logo-container img {
        max-width: 200px !important;
        height: auto;
    }

    /* Vit text i allmänhet samt i meddelanderutorna */
    p, .stChatMessage p {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* Meddelanderutor med border-radius 16px */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border-radius: 16px !important;
        padding: 12px 24px !important;
        margin-bottom: 15px !important;
    }

    /* Input-fältets behållare */
    .stChatInputContainer {
        border-radius: 16px !important;
        background-color: #FFFFFF !important;
    }

    /* Svart text enbart inne i input-fältet med genomskinlig bakgrund */
    .stChatInputContainer textarea,
    .stChatInputContainer p,
    .stChatInputContainer span,
    [data-testid="stChatInput"] textarea {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border-radius: 16px !important;
        background-color: transparent !important;
        background: transparent !important;
    }

    /* Placeholder-text */
    .stChatInputContainer textarea::placeholder {
        color: #666666 !important;
        -webkit-text-fill-color: #666666 !important;
    }

    /* Aktiv ram när man klickar i fältet */
    .stChatInputContainer:focus-within {
        border: 2px solid #AD87FC !important;
        box-shadow: 0 0 8px rgba(173, 135, 252, 0.5) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Visa logotypen
if os.path.exists("logo.png"):
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
