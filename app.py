import streamlit as st
from groq import Groq
import re
import urllib.parse

# 1. GEMINI UI ARCHITECTURE (CSS)
st.set_page_config(page_title="Tarih Fabrikası AI", page_icon="✨", layout="centered")

st.markdown("""
    <style>
    /* Gemini Temel Renk Paleti */
    .stApp {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* Ana Başlık: Gradient ve Zarif */
    .gemini-header {
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 500;
        text-align: center;
        margin-top: 2rem;
        letter-spacing: -1px;
    }
    
    .gemini-subtitle {
        color: #8e918f;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 3rem;
    }

    /* Giriş Alanı: Modern Pill Design */
    .stTextInput > div > div > input {
        background-color: #1e1f20 !important;
        color: #e3e3e3 !important;
        border: 1px solid #444746 !important;
        border-radius: 28px !important;
        padding: 14px 24px !important;
        font-size: 1rem !important;
        transition: border 0.3s ease;
    }
    .stTextInput > div > div > input:focus {
        border: 1px solid #a8c7fa !important;
        box-shadow: none !important;
    }

    /* Mod Seçimi (Radio): Minimalist Butonlar */
    div[data-testid="stRadio"] > div {
        justify-content: center;
        gap: 12px;
    }
    div[data-testid="stRadio"] label {
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
        padding: 8px 18px !important;
        border-radius: 20px !important;
        color: #c4c7c5 !important;
        font-size: 0.9rem !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child { display: none; } /* Yuvarlakları gizle */

    /* Ana Aksiyon Butonu */
    div.stButton > button {
        background-color: #a8c7fa !important;
        color: #062e6f !important;
        border: none !important;
        border-radius: 24px !important;
        padding: 10px 32px !important;
        font-weight: 600 !important;
        margin: 20px auto !important;
        display: block !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #d3e3fd !important;
        transform: scale(1.02);
    }

    /* Sonuç Alanı: Chat Bubble Style */
    .result-bubble {
        background-color: transparent;
        max-width: 700px;
        margin: 20px auto;
        line-height: 1.8;
        font-size: 1.1rem;
        color: #e3e3e3;
    }

    /* Kaynak Kartları */
    .source-box {
        background-color: #1e1f20;
        border: 1px solid #444746;
        border-radius: 16px;
        padding: 16px;
        margin-top: 15px;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    .source-btn {
        text-decoration: none;
        color: #a8c7fa !important;
        font-size: 0.85rem;
        margin-right: 15px;
        font-weight: 500;
    }
    .source-btn:hover { text-decoration: underline; }

    /* Bekleme Animasyonu */
    .loader-text {
        color: #8e918f;
        text-align: center;
        font-style: italic;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. UI ELEMENTS
st.markdown('<div class="gemini-header">Tarih Fabrikası</div>', unsafe_allow_html=True)
st.markdown('<div class="gemini-subtitle">Derinlemesine, gerçek ve doğrulanabilir tarih araştırması</div>', unsafe_allow_html=True)

# Central Input Area
mod = st.radio("", ["🎲 Otomatik", "✍️ Manuel"], horizontal=True, label_visibility="collapsed")
ozel_konu = ""
if mod == "✍️ Manuel":
    ozel_konu = st.text_input("", placeholder="Neyi keşfetmek istersin?", label_visibility="collapsed")

# 3. ENGINE (Llama 3.3 70B)
client = Groq(api_key="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")

if st.button("Araştırmayı Başlat"):
    input_text = ozel_konu if (mod == "✍️ Manuel" and ozel_konu) else "Dünya tarihinden sarsıcı ve kanıtlanmış bir olay seç."
    
    with st.spinner(""):
        st.markdown('<p class="loader-text">Veriler taranıyor, kaynaklar doğrulanıyor. Lütfen bekleyin...</p>', unsafe_allow_html=True)
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Akademik bir tarihçisin. Metni sade, akıcı ve başlık kullanmadan yaz. En az 450 kelime olsun. Sonunda 'KAYNAKLAR:' ve '---PROMPTLAR---' ekle."},
                    {"role": "user", "content": input_text}
                ],
                temperature=0.6
            )
            
            output = completion.choices[0].message.content
            
            # Content Logic
            if "---PROMPTLAR---" in output:
                main_part, prompts = output.split("---PROMPTLAR---")
            else:
                main_part, prompts = output, ""

            if "KAYNAKLAR:" in main_part:
                story, sources_raw = main_part.split("KAYNAKLAR:")
            else:
                story, sources_raw = main_part, ""

            # DISPLAY
            st.markdown("---")
            
            # Story Text
            st.markdown(f'<div class="result-bubble">{story.strip()}</div>', unsafe_allow_html=True)

            # Sources
            if sources_raw:
                st.markdown('<p style="text-align:center; color:#8e918f; margin-top:50px;">Referans Alınan Kaynaklar</p>', unsafe_allow_html=True)
                for s in sources_raw.strip().split('\n'):
                    s_clean = re.sub(r'^[0-9\-\.\*\s]+', '', s.strip())
                    if s_clean:
                        q = urllib.parse.quote(s_clean)
                        st.markdown(f"""
                        <div class="source-box">
                            <div style="margin-bottom:8px; font-size:0.95rem;">{s_clean}</div>
                            <a href="https://www.google.com/search?q={q}" target="_blank" class="source-btn">Google'da Doğrula</a>
                            <a href="https://scholar.google.com/scholar?q={q}" target="_blank" class="source-btn">Akademik Kaynağa Git</a>
                        </div>
                        """, unsafe_allow_html=True)

            # Image Prompts
            if prompts:
                st.markdown('<p style="text-align:center; color:#8e918f; margin-top:50px;">Görsel Üretim Promptları</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-bubble" style="color:#a8c7fa; font-family:monospace; font-size:0.9rem;">{prompts.strip()}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Teknik bir sorun oluştu: {e}")
