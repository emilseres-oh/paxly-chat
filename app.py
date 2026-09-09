@st.cache_data(ttl=60)  # Sänkt cache så att ändringar syns snabbare
def fetch_google_doc_html(doc_id):
    try:
        url = f"https://docs.google.com/document/d/{doc_id}/export?format=html"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Kunde inte hämta dokumentet ({doc_id}): {e}"
