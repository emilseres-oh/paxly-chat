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

    /* Styling för Segmented Control (Växlare) överst */
    [data-testid="stSegmentedControl"], div[role="radiogroup"] {
        display: flex !important;
        justify-content: center !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        padding: 6px !important;
        border-radius: 30px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        margin: 0 auto 30px auto !important;
        max-width: 320px !important;
    }

    [data-testid="stSegmentedControl"] button, div[role="radiogroup"] label {
        flex: 1 !important;
        border-radius: 24px !important;
        border: none !important;
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        background: transparent !important;
    }

    [data-testid="stSegmentedControl"] button[aria-selected="true"], 
    div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        background-color: #9C6EF9 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(156, 110, 249, 0.4) !important;
    }

    /* Vit bakgrund på bottenkontrollern i chattläget */
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

    /* Animationer */
    @keyframes slideUpInput {
        0% { transform: translateY(40px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }

    @keyframes popScale {
        0% { transform: scale(0.85); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }

    @keyframes popInCenter {
        0% { transform: scale(0.85); opacity: 0; }
        60% { transform: scale(1.02); opacity: 1; }
        100% { transform: scale(1); opacity: 1; }
    }

    /* Inputbox & Logotyp */
    [data-testid="stChatInput"] {
        border: 2px solid #9C6EF9 !important;
        border-radius: 24px !important;
        background-color: #FFFFFF !important;
        box-shadow: none !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        animation: slideUpInput 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
    }

    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
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
        .logo-container img {
            width: 200px !important;
            max-width: 70% !important;
        }
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

    /* Användarens meddelanden = 0.05 opacitet */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 24px 32px !important;
        margin-bottom: 8px !important;
        animation: popInCenter 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards !important;
        transform-origin: center center !important;
    }

    /* AI-assistentens meddelanden = 0.15 opacitet */
    [data-testid="stChatMessageContainer"] > div:nth-child(even) .stChatMessage {
        background-color: rgba(255, 255, 255, 0.15) !important;
    }

    /* Onboarding-kort styling */
    .onboarding-card {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 28px !important;
        margin-bottom: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
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

# Visa logotypen överst
if os.path.exists("logo.png"):
    st.markdown('''
        <div class="logo-container">
            <img src="data:image/png;base64,{}" alt="Paxly Logo">
        </div>
    '''.format(get_base64_image("logo.png")), unsafe_allow_html=True)

# Controlled segment (Flipväljare överst)
if hasattr(st, "segmented_control"):
    selected_page = st.segmented_control("", ["Chatt", "Onboarding"], default="Chatt")
else:
    selected_page = st.radio("", ["Chatt", "Onboarding"], horizontal=True, label_visibility="collapsed")

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
            <p>Här hittar du allt du behöver för att komma igång med ditt smarta bokningssystem. Följ stegen nedan för att konfigurera dina första resurser och ta emot bokningar.</p>
        </div>
    ''', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('''
            <div class="onboarding-card">
                <h3>1. Registrera Resurser</h3>
                <p>En resurs kan vara vad som helst – allt från mötesrum och fordon till rådgivare och utrustning.</p>
                <ul>
                    <li>Ställ in maxkapacitet</li>
                    <li>Bestäm ställtid och bufferttid</li>
                    <li>Länk till extern kalendersynkning</li>
                </ul>
            </div>
        ''', unsafe_allow_html=True)
        if os.path.exists("logo.png"):
            st.image("logo.png", caption="Paxly Resource Engine", use_container_width=True)

    with col2:
        st.markdown('''
            <div class="onboarding-card">
                <h3>2. Hantera Bokningar</h3>
                <p>Användarna kan boka direct via din kundanpassade portal eller via widgeten på din hemsida.</p>
                <ul>
                    <li>Automatisk bekräftelse via e-post</li>
                    <li>Inbyggd påminnelelse 24h innan</li>
                    <li>Smidig avbokningshantering</li>
                </ul>
            </div>
        ''', unsafe_allow_html=True)
        if os.path.exists("bg.jpg"):
            st.image("bg.jpg", caption="Paxly Bokningsvy", use_container_width=True)

    st.markdown('''
        <div class="onboarding-card">
            <h3>📖 Dokumentation & Guider</h3>
            <p>För mer ingående instruktioner och detaljerade guider om alla funktioner, se den fullständiga dokumentationen:</p>
            <p><a href="https://docs.google.com/document/d/1lJpjo_v3nFn7KDMughZDHtKrTWyL42E2NW5hAR_ATaw/edit?usp=drive_web" target="_blank" style="color: #9C6EF9; font-weight: bold; font-size: 18px;">📄 Öppna Paxly Onboarding & Dokumentation (Google Doc)</a></p>
        </div>
    ''', unsafe_allow_html=True)
