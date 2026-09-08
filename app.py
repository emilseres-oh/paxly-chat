import os
import streamlit as st
from google import genai

st.set_page_config(page_title="Paxly Support", page_icon="💬", layout="centered")

# Anpassad CSS för mörk bakgrund (#080D42), centrerad logga och ljus text
st.markdown("""
    <style>
    /* Huvudbakgrund */
    .stApp {
        background-color: #080D42;
        color: #FFFFFF;
    }
    
    /* Dölj Streamlit-menyer för renare känsla */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Centrera logotypen */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 30px;
        margin-top: 20px;
    }
    .logo-container img {
        max-width: 250px;
        height: auto;
    }
    
    /* Anpassa chattmeddelanden för mörk bakgrund */
    .stChatMessage {
        background-color: #12195E !important;
        border-radius: 12px;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# Visa centrerad logotyp istället för textrubrik
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("API-nyckel saknas. Lägg till GEMINI_API_KEY i dina Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# SYSTEMINSTRUKTIONER OCH KÄLLMATERIAL
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

# Initiera chatthistorik
if "messages" not in st.session_state:
    st.session_state.messages = []

# Visa tidigare meddelanden
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Hantera användarens input
if prompt := st.chat_input("Skriv din fråga här..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    try:
        # Använder gemini-2.0-flash för att undvika 404-felet
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={"system_instruction": SYSTEM_INSTRUCTION}
        )
        bot_response = response.text
    except Exception as e:
        bot_response = f"Ett fel uppstod vid kontakt med AI-tjänsten: {e}"

    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(bot_response)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
