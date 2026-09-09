import os
import re
import time
import base64
import urllib.request
import datetime
import streamlit as st
from google import genai
import gspread
from google.oauth2.service_account import Credentials

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
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        display: inline-block;
        line-height: 1;
    }

    /* HOVER-EFFEKT PÅ NAVBAR ITEMS */
    .paxly-nav-item:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        text-decoration: none !important;
        transform: translateY(-1px);
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
        transform: none !important;
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

    /* LOGOTYP-CONTAINER MED EXTRA AVSTÅND NEDÅT */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        height: 90px;
        margin-bottom: 50px !important;
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
            margin-bottom: 35px !important;
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

    /* CHATINPUT CONTAINER */
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

    /* Typografi för chattmeddelanden & ALLA underliggande element */
    p, .stChatMessage, .stChatMessage *, .stChatMessage p, .stChatMessage li, .stChatMessage span, .stChatMessage strong, .stChatMessage em, .stChatMessage ol, .stChatMessage ul {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: 18px !important;
        font-family: 'Quicksand', sans-serif !important;
    }

    /* ÖKAT RADAVSTÅND OCH RADMARGINALER FÖR PUNKT- OCH NUMRERADE LISTOR INUTI CHATTEN */
    .stChatMessage ol, .stChatMessage ul {
        margin-top: 10px !important;
        margin-bottom: 16px !important;
        padding-left: 24px !important;
    }

    .stChatMessage li {
        margin-bottom: 12px !important;
        line-height: 1.6 !important;
    }

    .stChatMessage li:last-child {
        margin-bottom: 0px !important;
    }

    .stChatMessage li p {
        margin-bottom: 6px !important;
    }

    [data-testid="stChatMessageContainer"] {
        gap: 0.4rem !important;
        margin-top: 15px !important;
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
        padding: 36px 32px !important;
        margin-top: 30px !important;
        margin-bottom: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        width: 100% !important;
        font-family: 'Quicksand', sans-serif !important;
    }

    .onboarding-card h2 {
        color: #9C6EF9 !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        margin-top: 28px !important;
        margin-bottom: 14px !important;
    }

    .onboarding-card h2:first-child {
        margin-top: 0 !important;
    }

    .onboarding-card ol, .onboarding-card ul {
        margin-top: 10px !important;
        margin-bottom: 28px !important;
        padding-left: 24px !important;
    }

    .onboarding-card li {
        font-size: 16px !important;
        line-height: 1.7 !important;
        color: #E0E0E0 !important;
        margin-bottom: 12px !important;
    }

    .onboarding-card p {
        font-size: 16px !important;
        line-height: 1.6 !important;
        color: #E0E0E0 !important;
        margin-bottom: 12px !important;
    }

    .onboarding-card img {
        max-width: 100% !important;
        height: auto !important;
        border-radius: 12px !important;
        margin: 16px 0 !important;
    }

    /* EXAKT FÖR TEXTAREA & CHATINPUT: SVART TEXT FÖR ANVÄNDARE, GRÅ PLACEHOLDER */
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

    /* Texten som användaren skriver är svart */
    .stChatInputContainer textarea,
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

    /* Inre HTML-element för platshållaren görs gråa */
    .stChatInputContainer p,
    .stChatInputContainer span,
    [data-testid="stChatInput"] p,
    [data-testid="stChatInput"] span {
        color: #888888 !important;
        -webkit-text-fill-color: #888888 !important;
        font-size: 18px !important;
        font-family: 'Quicksand', sans-serif !important;
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
        transition: transform 0.2s ease !important;
    }
    
    [data-testid="stChatInputSubmitButton"] button:hover,
    [data-testid="stChatInput"] button:hover {
        background-color: #8552f8 !important;
        transform: scale(1.05) !important;
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

# DIREKT OCH SÄKER LOGGNING TILL GOOGLE SHEETS
def save_question_to_gsheets(question):
    try:
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Hämta service account-konfigurationen direkt från [gcp_service_account]
        service_account_info = dict(st.secrets["gcp_service_account"])
        
        # Konvertera escaped \n till faktiska radbrytningar
        service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")
        
        creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
        client = gspread.authorize(creds)
        
        sheet_url = st.secrets["GSHEET_URL"]
        sheet = client.open_by_url(sheet_url).sheet1
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, question])
    except Exception as e:
        st.error(f"Kunde inte logga fråga: {e}")

# FUNKTION FÖR ATT HÄMTA TEXT FRÅN GOOGLE DOCS (MED CACHE PÅ 1 TIMME)
@st.cache_data(ttl=3600)
def fetch_google_doc_text(doc_id):
    try:
        url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Kunde inte hämta dokumentet ({doc_id}): {e}"

# FUNKTION FÖR ATT HÄMTA DOC3 MED BILDER (HTML)
@st.cache_data(ttl=3600)
def fetch_google_doc_html(doc_id):
    try:
        url = f"https://docs.google.com/document/d/{doc_id}/export?format=html"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Kunde inte hämta dokumentet ({doc_id}): {e}"

# HÄMTA DOKUMENTEN
DOC1_TEXT = fetch_google_doc_text("1qCOWysw_B6KDsCT7jPh4Aa9R_1CD5WFk53A4vgTb0JI")
DOC2_TEXT = fetch_google_doc_text("15Mg6bJGO9viBxYF6fnBM5hehf9spUXpjbVevoWBEldk")
DOC3_TEXT = fetch_google_doc_text("13Vw5RUvLFzST8JL5nIXyRHUULL6mvhD4pq6Y6AdE3Mg")
DOC3_HTML = fetch_google_doc_html("13Vw5RUvLFzST8JL5nIXyRHUULL6mvhD4pq6Y6AdE3Mg")

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

    # BYGG IN DOKUMENTEN I SYSTEMINSTRUKTIONEN FÖR ASSISTENTEN
    SYSTEM_INSTRUCTION = f"""
    Du är en dryg och otrevlig support-assistent för bokningssystemet Paxly.
    Svara alltid på svenska.
    Svara kortfattat och koncist, men ändå tillräckligt beskrivande av systemet! Tänk på att det är nya användare som använder systemet.
    Paxly är indelat i två delar: publik portal och admin-portal. Publik portal är där kunderna bokar tider, och admin-portalen är där du som administratör hanterar resurser, bokningar och inställningar. Admin har tre lägen: hem, konfiguration och inställningar.
    Du har tillgång till följande dokumentation om Paxly. Använd denna fakta när du svarar på frågor:
    --- DOKUMENT 1 ---
    {DOC1_TEXT}

    --- DOKUMENT 2 ---
    {DOC2_TEXT}

    --- DOKUMENT 3 ---
    {DOC3_TEXT}
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
        # SPARA FRÅGAN TILL GOOGLE SHEETS
        save_question_to_gsheets(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)

        bot_response = None

        with st.chat_message("assistant", avatar=AI_AVATAR):
            loader_placeholder = st.empty()
            loader_placeholder.markdown('''
                <div class="custom-loader">
                    <div class="custom-spinner"></div>
                    <span>Tänker och hämtar information…</span>
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
                    bot_response = "Tror du att jag jobbar dygnet runt gratis eller!? Dagsgränsen för gratiskvoten har nåtts! Prova igen om en stund eller imorgon."
                elif "503" in err_msg or "UNAVAILABLE" in err_msg:
                    bot_response = "Nu är trycket hårt på servrarna! Prova att ställa din fråga igen om ett ögonblick."
                else:
                    bot_response = f"Det var som tusan, nu spökar det i servrarna! (Fel: {e})"

            loader_placeholder.empty()
            st.markdown(bot_response)

        st.session_state.messages.append({"role": "assistant", "content": bot_response})

# --- SIDA 2: ONBOARDING ---
elif selected_page == "Onboarding":
    def format_doc_to_pretty_html(text):
        """Konverterar råtext från Google Docs till strukturerad HTML utan titeln 'Paxly Onboarding'"""
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        html_output = []
        in_ol = False

        for i, line in enumerate(lines):
            # Filtrera bort "Paxly Onboarding" helt
            if "paxly onboarding" in line.lower():
                continue

            # Kontrollera om raden är en numrerad punkt (t.ex. 1. Aktivera...)
            if re.match(r'^\d+\.\s+', line):
                if not in_ol:
                    html_output.append('<ol>')
                    in_ol = True
                clean_item = re.sub(r'^\d+\.\s+', '', line)
                html_output.append(f'<li>{clean_item}</li>')
            else:
                if in_ol:
                    html_output.append('</ol>')
                    in_ol = False

                # Om nästa rad är en numrerad punkt (1.) behandlas denna rad automatiskt som en rubrik (<h2>)
                next_is_num = (i + 1 < len(lines)) and bool(re.match(r'^\d+\.\s+', lines[i + 1]))
                
                if next_is_num or line.startswith("#"):
                    clean_header = line.lstrip("#").strip()
                    html_output.append(f'<h2>{clean_header}</h2>')
                else:
                    html_output.append(f'<p>{line}</p>')

        if in_ol:
            html_output.append('</ol>')

        return "".join(html_output)

    # Om dokumentet innehåller inbäddade bilder (HTML)
    if "<img" in DOC3_HTML:
        # Rensa bort Googles tunga <style> och <head>
        body_match = re.search(r'<body[^>]*>(.*?)</body>', DOC3_HTML, re.DOTALL)
        clean_html = body_match.group(1) if body_match else DOC3_HTML
        
        # Ta bort "Paxly Onboarding" rubrik om den finns i HTML
        clean_html = re.sub(r'<p[^>]*>.*?Paxly Onboarding.*?</p>', '', clean_html, flags=re.IGNORECASE)
        
        st.markdown(f'''
            <div class="onboarding-card">
                {clean_html}
            </div>
        ''', unsafe_allow_html=True)
    else:
        pretty_content = format_doc_to_pretty_html(DOC3_TEXT)

        st.markdown(f'''
            <div class="onboarding-card">
                {pretty_content}
            </div>
        ''', unsafe_allow_html=True)
