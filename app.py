import streamlit as st
from groq import Groq
import re
import urllib.parse

# 1. GEMINI-STYLE MINIMALIST CSS
st.set_page_config(page_title="Tarih Fabrikası AI", page_icon="✨", layout="centered")

st.markdown("""
    <style>
    /* Gemini Karanlık Tema Arka Planı */
    .stApp {
        background-color: #131314;
        color: #e3e3e3;
        font-family: 'Google Sans', sans-serif;
    }

    /* Başlık Alanı */
    .main-title {
        font-size: 2.5rem !important;
        font-weight: 500;
        text-align: center;
        background: linear-gradient(45deg, #4285f4, #9b72cb, #d96570, #ff8c00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #8e918f;
        font-size: 1rem;
        margin-bottom: 40px;
    }

    /* Radyo Butonları (Mod Seçimi) */
    div[data-testid="stRadio"] > div {
        justify-content: center;
        gap: 20px;
    }
    div[data-testid="stRadio"] label {
        background-color: #1e1f20;
        padding: 10px 20px;
        border-radius: 20px;
        color: #e3e3e3 !important;
        border: 1px solid #444746;
    }

    /* Giriş Kutusu (Gemini Tarzı Oval) */
    .stTextInput > div > div > input {
        background-color: #1e1f20 !important;
        color: white !important;
        border: 1px solid #444746 !important;
        border-radius: 24px !important;
        padding: 12px 24px;
        font-size: 1rem;
    }

    /* Gemini-Style Buton */
    div.stButton > button {
        background: linear-gradient(90deg, #1a73e8, #4285f4) !important;
        color: white !important;
        border: none !important;
        border-radius: 24px !important;
        padding: 12px 40px !important;
        font-weight: 500;
        display: block;
        margin: 0 auto;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3);
    }

    /* Metin Akışı (Sohbet gibi alt alta) */
    .chat-bubble {
        max-width: 800px;
        margin: 20px auto;
        line-height: 1.6;
        font-size: 1.1rem;
        color: #e3e3e3;
        white-space: pre-wrap;
    }

    /* Kaynaklar (Minimalist Linkler) */
    .source-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 20px;
        align-items: center;
    }
    .source-link {
        text-decoration: none;
        color: #8ab4f8 !important;
        font-size: 0.95rem;
        padding: 8px 16px;
        border-radius: 12px;
        background-color: #1e1f20;
        border: 1px solid #444746;
        width: fit-content;
        transition: background 0.2s;
    }
    .source-link:hover {
        background-color: #333537;
    }

    /* Animasyonlu Bekleme Yazısı */
    @keyframes pulse { 50% { opacity: 0.5; } }
    .loading-text {
        text-align: center;
        color: #8e918f;
        animation: pulse 1.5s infinite;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. UI BAŞLANGIÇ
st.markdown('<h1 class="main-title">Tarih Fabrikası AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Yapay zeka ile doğrulanabilir tarih yolculuğu</p>', unsafe_allow_html=True)

# 3. MOD SEÇİMİ VE INPUT
mod = st.radio("Bir mod seçin", ["🎲 Otomatik", "✍️ Manuel"], horizontal=True, label_visibility="collapsed")
ozel_konu = ""
if mod == "✍️ Manuel":
    ozel_konu = st.text_input("", placeholder="Neyi merak ediyorsun?", label_visibility="collapsed")

# 4. API & ÜRETİM
client = Groq(api_key="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")

if st.button("Araştır"):
    konu = ozel_konu if (mod == "✍️ Manuel" and ozel_konu) else "Tarihten sarsıcı, kanıtlanmış bir olay seç."
    
    with st.spinner(""):
        st.markdown('<p class="loading-text">Biraz uzun sürebilir; çünkü bu araştırma kapsamında her şeyi gerçek ve doğrulanabilir kaynaklardan inceliyoruz. Lütfen Bekleyin...</p>', unsafe_allow_html=True)
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sen akademik bir tarihçi ve minimalist bir içerik yazarıısın. Metni başlık kullanmadan, bir anlatı gibi akıcı yaz. En az 400 kelime olsun. Sonunda 'KAYNAKLAR:' ve '---PROMPTLAR---' bölümleri olsun."},
                    {"role": "user", "content": konu}
                ],
                temperature=0.7
            )
            
            cevap = completion.choices[0].message.content
            
            # Parçalara ayır
            if "---PROMPTLAR---" in cevap:
                ust, promptlar = cevap.split("---PROMPTLAR---")
            else:
                ust, promptlar = cevap, ""

            if "KAYNAKLAR:" in ust:
                metin, kaynaklar_ham = ust.split("KAYNAKLAR:")
            else:
                metin, kaynaklar_ham = ust, ""

            # 5. GEMINI TARZI GÖSTERİM
            st.markdown("---")
            
            # Video Metni
            st.markdown(f'<div class="chat-bubble">{metin.strip()}</div>', unsafe_allow_html=True)

            # Kaynaklar
            if kaynaklar_ham:
                st.markdown('<p style="text-align:center; color:#8e918f; margin-top:40px;">Doğrulama Kaynakları</p>', unsafe_allow_html=True)
                kaynak_listesi = kaynaklar_ham.strip().split('\n')
                for k in kaynak_listesi:
                    k_cleaned = re.sub(r'^[0-9\-\.\*\s]+', '', k.strip())
                    if k_cleaned:
                        query = urllib.parse.quote(k_cleaned)
                        st.markdown(f'''
                        <div class="source-container">
                            <span style="font-size:0.9rem; color:#e3e3e3;">{k_cleaned}</span>
                            <div style="display:flex; gap:10px;">
                                <a href="https://www.google.com/search?q={query}" target="_blank" class="source-link">🔍 Google</a>
                                <a href="https://scholar.google.com/scholar?q={query}" target="_blank" class="source-link">🎓 Akademik</a>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)

            # Promptlar
            if promptlar:
                st.markdown('<p style="text-align:center; color:#8e918f; margin-top:40px;">Sinematik Promptlar</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="chat-bubble" style="color:#8ab4f8; font-family:monospace; font-size:0.9rem;">{promptlar.strip()}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Bir sorun oluştu: {e}")
