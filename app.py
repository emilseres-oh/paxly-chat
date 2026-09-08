import os
import time
import base64
import streamlit as st
from google import genai

st.set_page_config(page_title="Paxly Support", page_icon="💬", layout="centered")

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

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Stoppa skrollhopp och lås sidhöjden */
    html, body, .stAppContainer, .stApp {
        scroll-behavior: auto !important;
    }

    /* Fast avstånd i toppen så innehållet inte hoppar under navbaren */
    .stMainBlockContainer {
        padding-top: 6.5rem !important;
    }

    /* EXAKT CENTRERING AV MENYN HÖGST UPP (FIXED) */
    [data-testid="stSegmentedControl"] {
        position: fixed !important;
        top: 20px !important;
        left: 0 !important;
        right: 0 !important;
        margin-left: auto !important;
        margin-right: auto !important;
        width: fit-content !important;
        z-index: 999999 !important;
    }

    /* Utseende på själva navbaren (Pill-design) */
    [data-testid="stSegmentedControl"] > div {
        background: rgba(15, 23, 42, 0.65) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        padding: 5px !important;
        border-radius: 9999px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4) !important;
        gap: 4px !important;
    }

    /* Styling av knapparna i menyn */
    [data-testid="stSegmentedControl"] button {
        border: none !important;
        background: transparent !important;
        padding: 8px 24px !important;
        border-radius: 9999px !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* Textstyling i knapparna */
    [data-testid="stSegmentedControl"] button p {
        color: rgba(255, 255, 255, 0.7) !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }

    /* Hover-effekt på icke-valda knappar */
    [data-testid="stSegmentedControl"] button:hover p {
        color: #FFFFFF !important;
    }

    /* Aktiv vald knapp */
    [data-testid="stSegmentedControl"] button[aria-selected="true"] {
        background-color: #9C6EF9 !important;
        box-shadow: 0 4px 12px rgba(156, 110, 249, 0.4) !important;
    }

    [data-testid="stSegmentedControl"] button[aria-selected="true"] p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Logotyp container */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-bottom: 25px !important;
        margin-top: 0px;
    }
    .logo-container img {
        width: 280px !important;
        max-width: 80% !important;
        height: auto !important;
    }

    @media (max-width: 768px) {
        .logo-container img {
            width: 180px !important;
            max-width: 70% !important;
        }
    }

    /* Vit bakgrund på bottenkontrollern i chattläget */
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div {
        background-color: #FFFFFF !important;
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Inputbox */
    [data-testid="stChatInput"] {
        border: 2px solid #9C6EF9 !important;
        border-radius: 24px !important;
        background-color: #FFFFFF !important;
        box-shadow: none !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
    }

    /* Loader */
    .custom-loader {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        color: #FFFFFF !important;
        font-size: 18px !important;
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
    }

    [data-testid="stChatMessageContainer"] {
        gap: 0.4rem !important;
    }

    /* Användarens meddelanden */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 24px 32px !important;
        margin-bottom: 8px !important;
    }

    /* AI-assistentens meddelanden */
    [data-testid="stChatMessageContainer"] > div:nth-child(even) .stChatMessage {
        background-color: rgba(255, 255, 255, 0.15) !important;
    }

    /* Onboarding-kort */
    .onboarding-card {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 28px !important;
        margin-bottom: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        width: 100% !important;
    }
    .onboarding-card h2 {
        color: #9C6EF9 !important;
        font-size: 24px !important;
        margin-top: 0 !important;
    }
    .onboarding-card h3 {
        color: #FFFFFF !important;
        font-size: 20px !important;
    }
    .onboarding-card p, .onboarding-card li {
        font-size: 16px !important;
        line-height: 1.6 !important;
        color: #E0E0E0 !important;
    }

    .stChatInputContainer textarea,
    [data-testid="stChatInput"] textarea {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-size: 18px !important;
    }

    [data-testid="stChatInputSubmitButton"] button {
        background-color: #9C6EF9 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    
    [data-testid="stChatInputSubmitButton"] button:hover {
        background-color: #8552f8 !important;
    }

    [data-testid="stChatInputSubmitButton"] svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# 1. FIXERAD OCH CENTRERAD NAVBAR
selected_page = st.segmented_control(
    "",
    ["Chatt", "Onboarding"],
    default="Chatt",
    label_visibility="collapsed"
)

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
            <h3>📖 Fullständig Användardokumentation</h3>
            <p>För mer ingående instruktioner, vanliga frågor och detaljerade guider om samtliga funktioner i Paxly, se vår fullständiga dokumentation:</p>
            <p><a href="https://docs.google.com/document/d/1lJpjo_v3nFn7KDMughZDHtKrTWyL42E2NW5hAR_ATaw/edit?usp=drive_web" target="_blank" style="color: #9C6EF9; font-weight: bold; font-size: 18px;">📄 Öppna Paxly Onboarding & Dokumentation (Google Doc)</a></p>
        </div>
    ''', unsafe_allow_html=True)
