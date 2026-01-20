import streamlit as st
from groq import Groq
import re
import urllib.parse

# 1. GEMINI UI ARCHITECTURE (Görsel Tasarım)
st.set_page_config(page_title="Tarih Fabrikası AI", page_icon="✨", layout="centered")

st.markdown("""
    <style>
    /* Gemini Teması */
    .stApp {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Başlık */
    .gemini-header {
        font-size: 2.8rem;
        font-weight: 500;
        text-align: center;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 2rem;
    }
    
    .gemini-subtitle {
        color: #8e918f;
        text-align: center;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Mod Seçimi Butonları (Ortalı ve Beyaz) */
    div[data-testid="stRadio"] {
        display: flex;
        justify-content: center;
        width: 100%;
    }
    div[data-testid="stRadio"] > div {
        flex-direction: row;
        justify-content: center;
        gap: 15px;
    }
    div[data-testid="stRadio"] label p {
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    div[data-testid="stRadio"] label {
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
        padding: 10px 24px !important;
        border-radius: 24px !important;
    }

    /* Input */
    .stTextInput > div > div > input {
        background-color: #1e1f20 !important;
        color: #ffffff !important;
        border: 1px solid #444746 !important;
        border-radius: 28px !important;
        padding: 12px 24px !important;
        text-align: center;
    }

    /* Araştır Butonu */
    div.stButton {
        display: flex;
        justify-content: center;
        margin-top: 15px;
    }
    div.stButton > button {
        background-color: #a8c7fa !important;
        color: #062e6f !important;
        border: none !important;
        border-radius: 24px !important;
        padding: 10px 40px !important;
        font-weight: 600 !important;
    }

    /* Metin Alanları */
    .chat-bubble {
        max-width: 750px;
        margin: 20px auto;
        line-height: 1.8;
        font-size: 1.1rem;
        color: #e3e3e3;
    }
    .prompt-bubble {
        max-width: 750px;
        margin: 20px auto;
        line-height: 1.6;
        font-size: 0.95rem;
        color: #a8c7fa;
        font-family: monospace;
        white-space: pre-wrap;
    }

    /* Kaynaklar */
    .source-box {
        background-color: #1e1f20;
        border: 1px solid #444746;
        border-radius: 16px;
        padding: 16px;
        margin: 15px auto;
        max-width: 600px;
        text-align: center;
    }
    .source-btn {
        text-decoration: none;
        color: #a8c7fa !important;
        font-size: 0.9rem;
        margin: 0 10px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="gemini-header">Tarih Fabrikası</div>', unsafe_allow_html=True)
st.markdown('<div class="gemini-subtitle">Gerçek zamanlı akademik doğrulama ve vurucu içerik üretimi</div>', unsafe_allow_html=True)

mod = st.radio("", ["🎲 Otomatik", "✍️ Manuel"], horizontal=True, label_visibility="collapsed")
ozel_konu = ""
if mod == "✍️ Manuel":
    ozel_konu = st.text_input("", placeholder="Neyi merak ediyorsun?", label_visibility="collapsed")

# 2. GÜÇLENDİRİLMİŞ MOTOR (SYSTEM PROMPT GÜNCELLENDİ)
client = Groq(api_key="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")

SYSTEM_PROMPT = (
    "Sen akademik bir tarih profesörü ve viral içerik uzmanısın. "
    "Çıktılarında teknik başlık kullanma. ŞU KURALLARA KESİNLİKLE UY:\n\n"
    "1. KANCA (HOOK): Metne en başta, konuyla %100 bağlantılı, sarsıcı ve 'Bunu biliyor muydunuz?' havasında "
    "inanılmaz merak uyandırıcı 2-3 cümleyle başla. Okuyucuyu ilk saniyede yakalamalısın.\n"
    "2. METİN: Sade, akıcı bir Türkçe ile en az 450-500 kelime uzunluğunda derin bir anlatım yap.\n"
    "3. KAYNAKLAR: Metnin sonuna 'KAYNAKLAR:' ekle ve gerçek kitap/makale isimlerini listele.\n"
    "4. PROMPTLAR: En sona '---PROMPTLAR---' yazıp 8-15 adet numaralı, sinematik İNGİLİZCE promptlar üret."
)

if st.button("Araştır"):
    konu = ozel_konu if (mod == "✍️ Manuel" and ozel_konu) else "Tarihten çok sarsıcı ve kanıtlanmış bir olay seç."
    
    with st.spinner(""):
        st.markdown('<p style="text-align:center; color:#8e918f;">Biraz uzun sürebilir; çünkü bu araştırma kapsamında her şeyi gerçek ve doğrulanabilir kaynaklardan inceliyoruz. Lütfen Bekleyin...</p>', unsafe_allow_html=True)
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": konu}
                ],
                temperature=0.7
            )
            
            output = completion.choices[0].message.content
            
            # İçerik Ayrıştırma
            if "---PROMPTLAR---" in output:
                main_part, prompts = output.split("---PROMPTLAR---")
            else:
                main_part, prompts = output, ""

            if "KAYNAKLAR:" in main_part:
                story, sources_raw = main_part.split("KAYNAKLAR:")
            else:
                story, sources_raw = main_part, ""

            # GÖSTERİM
            st.markdown("---")
            
            # Kancalı Ana Metin
            st.markdown(f'<div class="chat-bubble">{story.strip()}</div>', unsafe_allow_html=True)

            # Kaynaklar
            if sources_raw:
                st.markdown('<p style="text-align:center; color:#8e918f; margin-top:40px;">Doğrulama Kaynakları</p>', unsafe_allow_html=True)
                for s in sources_raw.strip().split('\n'):
                    s_clean = re.sub(r'^[0-9\-\.\*\s]+', '', s.strip())
                    if s_clean:
                        q = urllib.parse.quote(s_clean)
                        st.markdown(f"""
                        <div class="source-box">
                            <div style="margin-bottom:8px;">{s_clean}</div>
                            <a href="https://www.google.com/search?q={q}" target="_blank" class="source-btn">🔍 Google</a>
                            <a href="https://scholar.google.com/scholar?q={q}" target="_blank" class="source-btn">🎓 Akademik</a>
                        </div>
                        """, unsafe_allow_html=True)

            # Promptlar
            if prompts:
                st.markdown('<p style="text-align:center; color:#8e918f; margin-top:40px;">Görsel Üretim Promptları</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="prompt-bubble">{prompts.strip()}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Sistemsel Hata: {e}")
