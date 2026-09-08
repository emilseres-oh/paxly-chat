import os
import streamlit as st
from google import genai

st.set_page_config(page_title="Paxly Support", page_icon="💬")

st.title("Paxly Support")
st.write("Välkommen! Ställ dina frågor om Paxly här.")

# Hämta API-nyckel från secrets
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
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Hantera användarens input
if prompt := st.chat_input("Skriv din fråga här..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"system_instruction": SYSTEM_INSTRUCTION}
        )
        bot_response = response.text
    except Exception as e:
        bot_response = f"Ett fel uppstod vid kontakt med AI-tjänsten: {e}"

    with st.chat_message("assistant"):
        st.markdown(bot_response)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
