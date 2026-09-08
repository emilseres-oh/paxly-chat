import os
import time
import base64
import streamlit as st
from google import genai

st.set_page_config(page_title="Paxly Support", page_icon="💬", layout="centered")

# LÄGG CSS HÖGST UPP SÅ ATT SIDAN RITARS UT RÄTT DIREKT
st.markdown("""
    <!-- IMPORT GOOGLE FONT: QUICKSAND -->
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');

    /* Global typografi */
    html, body, [class*="css"], .stApp, p, span, div, h1, h2, h3, h4, h5, h6, a, button, input, textarea {
        font-family: 'Quicksand', sans-serif !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Stoppa skrollhopp vid sidbyte */
    html, body, .stAppContainer, .stApp {
        scroll-behavior: auto !important;
        overflow-y: scroll !important;
    }

    .stMainBlockContainer {
        padding-top: 5.5rem !important;
        padding-bottom: 7rem !important;
    }

    /* RENSAD & FIXERAD NAVBAR */
    .paxly-navbar-container {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 999999;
        display: flex;
        gap: 8px;
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 6px 10px;
        border-radius: 40px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        height: 48px;
        box-sizing: border-box;
    }

    /* ALLTID VIT TEXT OCH INGEN UNDERLINE */
    .paxly-nav-item,
    .paxly-nav-item:hover,
    .paxly-nav-item:visited,
    .paxly-nav-item:active,
    .paxly-nav-item:focus {
        background: transparent;
        border: none;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        padding: 8px 24px;
        border-radius: 30px;
        font-size: 15px;
        font-weight: 500;
        font-family: 'Quicksand', sans-serif !important;
        cursor: pointer;
        text-decoration: none !important;
        transition: background-color 0.15s ease;
        display: inline-block;
        line-height: 1;
    }

    /* AKTIV FLIK */
    .paxly-nav-active,
    .paxly-nav-active:hover,
    .paxly-nav-active:visited,
    .paxly-nav-active:active,
    .paxly-nav-active:focus {
        background-color: #9C6EF9 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(156, 110, 249, 0.5);
        text-decoration: none !important;
    }

    /* ANIMATIONER */
    @keyframes popScale {
        0% { transform: scale(0.85); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }

    @keyframes popInCenter {
        0% { transform: scale(0.85); opacity: 0; }
        60% { transform: scale(1.02); opacity: 1; }
        100% { transform: scale(1); opacity: 1; }
    }

    /* LOGOTYP-CONTAINER MED ANIMATION */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        height: 90px;
        margin-bottom: 25px !important;
        margin-top: 10px;
        animation: popScale 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
    }
    .logo-container img {
        width: 300px !important;
        max-width: 80% !important;
        height: auto !important;
    }

    @media (max-width: 768px) {
        .logo-container {
            height: 60px;
        }
        .logo-container img {
            width: 200px !important;
            max-width: 70% !important;
        }
    }

    /* BOTTENPANEL */
    [data-testid="stBottom"] > div,
    [data-testid="stBottom"] .stChatInputContainer,
    .st-emotion-cache-6shykm {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        margin: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        display: flex !important;
        align-items: center !important;
    }

    [data-testid="stBottom"] {
        background-color: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
        padding-top: 1.2rem !important;
        padding-bottom: 1.2rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* CHATINPUT */
    [data-testid="stChatInput"] {
        border: 2px solid #9C6EF9 !important;
        border-radius: 24px !important;
        background-color: #FFFFFF !important;
        box-shadow: none !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        margin: 0 !important;
    }

    /* Loader */
    .custom-loader {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-family: 'Quicksand', sans-serif !important;
        line-height: 1 !important;
        margin-top: -18px !important;
        padding: 0 !important;
    }
    .custom-spinner {
        width: 20px !important;
        height: 20px !important;
        min-width: 20px !important;
        min-height: 20px !important;
        border: 3px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 50% !important;
        border-top-color: #FFFFFF !important;
        animation: spin-loader 0.8s linear infinite !important;
        box-sizing: border-box !important;
    }
    @keyframes spin-loader {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Typografi */
    p, .stChatMessage p {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: 18px !important;
        font-family: 'Quicksand', sans-serif !important;
    }

    [data-testid="stChatMessageContainer"] {
        gap: 0.4rem !important;
    }

    /* GLAS-KÄNSLA PÅ CHATTMEDDELANDEN MED ANIMATION */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
        border-radius: 16px !important;
        padding: 24px 32px !important;
        margin-bottom: 8px !important;
        animation: popInCenter 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards !important;
        transform-origin: center center !important;
    }

    [data-testid="stChatMessageContainer"] > div:nth-child(even) .stChatMessage {
        background-color: rgba(255, 255, 255, 0.14) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2) !important;
    }

    /* Onboarding-kort */
    .onboarding-card {
        background-color: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 20px !important;
        padding: 28px !important;
        margin-bottom: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        width: 100% !important;
    }
    .onboarding-card h2 {
        color: #9C6EF9 !important;
        font-size: 24px !important;
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 700 !important;
        margin-top: 0 !important;
    }
    .onboarding-card h3 {
        color: #FFFFFF !important;
        font-size: 20px !important;
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 600 !important;
    }
    .onboarding-card p, .onboarding-card li {
        font-size: 16px !important;
        font-family: 'Quicksand', sans-serif !important;
        line-height: 1.6 !important;
        color: #E0E0E0 !important;
    }

    /* EXAKT FÖR TEXTAREA & CHATINPUT */
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

    .stChatInputContainer textarea,
    .stChatInputContainer p,
    .stChatInputContainer span,
    [data-testid="stChatInput"] textarea {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-size: 18px !important;
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 500 !important;
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

    .stChatInputContainer textarea::placeholder {
        color: #666666 !important;
        -webkit-text-fill-color: #666666 !important;
        font-size: 18px !important;
        font-family: 'Quicksand', sans-serif !important;
        line-height: 48px !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border: 2px solid #9C6EF9 !important;
        box-shadow: 0 0 10px rgba(156, 110, 249, 0.5) !important;
    }

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
    </style>
    """
else:
    bg_css = """
    <style>
    .stApp {
        background-color: rgba(8, 13, 66, 0.8);
        color: #FFFFFF;
    }
    </style>
    """

st.markdown(bg_css, unsafe_allow_html=True)

# Safari adressfält/flikrad färg
st.markdown("""
    <meta name="theme-color" content="#080d42">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
""", unsafe_allow_html=True)

# Läs URL-parametrar för navigeringen
query_params = st.query_params
selected_page = query_params.get("page", "Chatt")

# Renders ren HTML/CSS Navbar
chatt_class = "paxly-nav-item paxly-nav-active" if selected_page == "Chatt" else "paxly-nav-item"
onboarding_class = "paxly-nav-item paxly-nav-active" if selected_page == "Onboarding" else "paxly-nav-item"

st.markdown(f'''
    <div class="paxly-navbar-container">
        <a href="?page=Chatt" target="_self" class="{chatt_class}">Chatt</a>
        <a href="?page=Onboarding" target="_self" class="{onboarding_class}">Onboarding</a>
    </div>
''', unsafe_allow_html=True)

# 2. LOGOTYPEN UNDER NAVBAR
if os.path.exists("logo.png"):
    st.markdown('''
        <div class="logo-container">
            <img src="data:image/png;base64,{}" alt="Paxly Logo">
        </div>
    '''.format(get_base64_image("logo.png")), unsafe_allow_html=True)

# --- SIDA 1: CHATT ---
if selected_page == "Chatt":
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
            loader_placeholder = st.empty()
            loader_placeholder.markdown('''
                <div class="custom-loader">
                    <div class="custom-spinner"></div>
                    <span>Hämtar information...</span>
                </div>
            ''', unsafe_allow_html=True)

            try:
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                    config={"system_instruction": SYSTEM_INSTRUCTION}
                )
                bot_response = response.text
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    bot_response = "Tror du att jag jobbar dygnet runt gratis eller, Eva!? Dagsgränsen för gratiskvoten har nåtts! Prova igen om en stund eller imorgon."
                elif "503" in err_msg or "UNAVAILABLE" in err_msg:
                    bot_response = "Nu är trycket hårt på servrarna Eva! Prova att ställa din fråga igen om ett ögonblick."
                else:
                    bot_response = f"Det var som tusan Eva, nu spökar det i servrarna! (Fel: {e})"

            loader_placeholder.empty()
            st.markdown(bot_response)

        st.session_state.messages.append({"role": "assistant", "content": bot_response})

# --- SIDA 2: ONBOARDING ---
elif selected_page == "Onboarding":
    st.markdown('''
        <div class="onboarding-card">
            <h2>🚀 Välkommen till Paxly Onboarding</h2>
            <p>Här hittar du allt du behöver för att komma igång med ditt smarta bokningssystem. Följ guiden nedan för att konfigurera dina resurser och ta emot dina första bokningar.</p>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
        <div class="onboarding-card">
            <h3>1. Registrera dina Resurser</h3>
            <p>En resurs kan vara vad som helst som är bokningsbart – allt från mötesrum och fordon till rådgivare och utrustning.</p>
            <ul>
                <li>Ställ in maxkapacitet och lokaltyp</li>
                <li>Bestäm ställtid och bufferttid mellan bokningar</li>
                <li>Länka direkt till extern kalendersynkning (Outlook / Google Calendar)</li>
            </ul>
        </div>
    ''', unsafe_allow_html=True)

    if os.path.exists("logo.png"):
        st.markdown('''
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="data:image/png;base64,{}" style="max-width: 100%; border-radius: 12px;" alt="Resource Engine">
            </div>
        '''.format(get_base64_image("logo.png")), unsafe_allow_html=True)

    st.markdown('''
        <div class="onboarding-card">
            <h3>2. Hantera och Automatisera Bokningar</h3>
            <p>Användarna kan boka direkt via er kundanpassade portal eller via den inbäddade widgeten på er hemsida.</p>
            <ul>
                <li>Automatisk bokningsbekräftelse skickas direkt via e-post</li>
                <li>Inbyggda påminnelser 24 timmar innan bokad tid</li>
                <li>Smidiga avbokningsregler och kundanpassad schemaläggning</li>
            </ul>
        </div>
    ''', unsafe_allow_html=True)

    if os.path.exists("bg.jpg"):
        st.markdown('''
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="data:image/jpeg;base64,{}" style="max-width: 100%; border-radius: 12px;" alt="Bokningsvy">
            </div>
        '''.format(get_base64_image("bg.jpg")), unsafe_allow_html=True)

    st.markdown('''
        <div class="onboarding-card">
            <h3>📖 Fullständiga Användardokumentation</h3>
            <p>För mer ingående instruktioner, vanliga frågor och detaljerade guider om samtliga funktioner i Paxly, se vår fullständiga dokumentation:</p>
            <p><a href="https://docs.google.com/document/d/1lJpjo_v3nFn7KDMughZDHtKrTWyL42E2NW5hAR_ATaw/edit?usp=drive_web" target="_blank" style="color: #9C6EF9; font-weight: bold; font-size: 18px; font-family: 'Quicksand', sans-serif;">📄 Öppna Paxly Onboarding & Dokumentation (Google Doc)</a></p>
        </div>
    ''', unsafe_allow_html=True)
