import streamlit as st
from groq import Groq
import re
import urllib.parse

# 1. TASARIM: Siyah-Beyaz Minimalizm + Animasyonlu Sarı-Turuncu Başlık
st.set_page_config(page_title="Tarih Haber AI", page_icon="📜", layout="centered")

st.markdown("""
    <style>
    /* Ana Tema: Saf Siyah */
    .stApp {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }

    /* Yazıları Ortala */
    h1, h2, h3, p, span, label, div {
        text-align: center !important;
        color: #ffffff !important;
    }

    /* YANIP SÖNEN SARI-TURUNCU BAŞLIK ANİMASYONU */
    @keyframes pulseGlow {
        0% { text-shadow: 0 0 10px #FF8C00, 0 0 20px #FFCC00; opacity: 1; }
        50% { text-shadow: 0 0 30px #FFCC00, 0 0 50px #FF8C00; opacity: 0.8; }
        100% { text-shadow: 0 0 10px #FF8C00, 0 0 20px #FFCC00; opacity: 1; }
    }

    .animated-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FFCC00, #FF8C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulseGlow 2s infinite ease-in-out;
        letter-spacing: -2px;
        margin-top: 2rem;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
    }
    
    .minimal-subtitle {
        color: #666666 !important;
        font-size: 0.85rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 3rem;
    }

    /* MOD SEÇİMİ (Radio) - Ortalı ve Sade */
    div[data-testid="stRadio"] {
        display: flex;
        justify-content: center;
        margin-bottom: 25px;
    }
    div[data-testid="stRadio"] > div {
        flex-direction: row;
        justify-content: center;
        gap: 30px;
    }
    div[data-testid="stRadio"] label p {
        color: #ffffff !important;
        font-weight: 400 !important;
    }

    /* Giriş Kutusu (İnce Beyaz Çizgi) */
    .stTextInput > div > div > input {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 0px !important;
        padding: 15px;
        text-align: center;
        font-size: 1rem;
    }
    .stTextInput > div > div > input:focus {
        border: 1px solid #ffffff !important;
    }

    /* ARAŞTIR BUTONU: Beyaz Üstüne Siyah (Keskin ve Net) */
    div.stButton {
        display: flex;
        justify-content: center;
        margin-top: 2rem;
    }
    div.stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 12px 60px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.4s;
    }
    div.stButton > button:hover {
        background-color: #FFCC00 !important; /* Üstüne gelince sarı olsun */
        transform: scale(1.05);
    }

    /* Metin Alanı: Okunaklı ve Ferah */
    .content-text {
        max-width: 750px;
        margin: 40px auto;
        line-height: 2;
        font-size: 1.15rem;
        font-weight: 300;
        text-align: justify !important;
        color: #e0e0e0 !important;
    }

    /* Alt Bölümler İçin İnce Çizgi */
    hr {
        border: 0;
        border-top: 1px solid #222222;
        margin: 40px 0;
    }

    .minimal-link {
        color: #ffffff !important;
        text-decoration: underline;
        font-size: 0.75rem;
        margin: 0 15px;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ARAYÜZ
st.markdown('<div class="animated-header">Tarih Haber</div>', unsafe_allow_html=True)
st.markdown('<div class="minimal-subtitle">Dijital Arşiv ve Doğrulanabilir İçerik</div>', unsafe_allow_html=True)

# Seçim ve Giriş
mod = st.radio("", ["🎲 Otomatik", "✍️ Manuel"], horizontal=True, label_visibility="collapsed")
ozel_konu = ""
if mod == "✍️ Manuel":
    ozel_konu = st.text_input("", placeholder="ARAŞTIRILACAK KONUYU YAZIN", label_visibility="collapsed")

# 3. MOTOR (Sarsıcı Kancalı Sistem Talimatı)
client = Groq(api_key="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")

SYSTEM_PROMPT = (
    "Sen bir tarih profesörü ve içerik uzmanısın. "
    "Çıktılarında başlık kullanma. ŞU KURALLARA KESİNLİKLE UY:\n\n"
    "1. SARSICI KANCA: Metne mutlaka genel kanının aksine sarsıcı, provokatif ve 'ters köşe' bir iddiayla başla. "
    "Örn: 'Sanılanın aksine, İstanbul fethedilirken Akşemsettin gemilerin karadan yürütülmesine karşıydı.' gibi "
    "şok edici ama tarihsel temeli olan bir giriş yap.\n"
    "2. METİN: Girişin ardından olayı akademik gerçeklerle en az 450-500 kelime anlat.\n"
    "3. KAYNAKLAR: Sona 'KAYNAKLAR:' başlığı ekle.\n"
    "4. PROMPTLAR: En sona '---PROMPTLAR---' yazıp 10 adet sinematik İngilizce prompt üret."
)

# 4. ÇALIŞTIRMA
if st.button("ARAŞTIRMAYI BAŞLAT"):
    konu = ozel_konu if (mod == "✍️ Manuel" and ozel_konu) else "Tarihten çok sarsıcı ve yanlış bilinen bir olay seç."
    
    with st.spinner(""):
        st.markdown('<p style="text-align:center; color:#555555; font-size:0.8rem;">BELGELER İNCELENİYOR. LÜTFEN BEKLEYİN...</p>', unsafe_allow_html=True)
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": konu}
                ],
                temperature=0.75
            )
            
            output = completion.choices[0].message.content
            
            # İçerik Ayırma
            if "---PROMPTLAR---" in output:
                main_part, prompts = output.split("---PROMPTLAR---")
            else:
                main_part, prompts = output, ""

            if "KAYNAKLAR:" in main_part:
                story, sources_raw = main_part.split("KAYNAKLAR:")
            else:
                story, sources_raw = main_part, ""

            # GÖSTERİM
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(f'<div class="content-text">{story.strip()}</div>', unsafe_allow_html=True)

            if sources_raw:
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown('<p style="text-align:center; font-size:0.7rem; color:#555555; letter-spacing:2px;">REFERANS KAYNAKLAR</p>', unsafe_allow_html=True)
                for s in sources_raw.strip().split('\n'):
                    s_clean = re.sub(r'^[0-9\-\.\*\s]+', '', s.strip())
                    if s_clean:
                        q = urllib.parse.quote(s_clean)
                        st.markdown(f'<div style="margin:10px auto;"><span style="font-size:0.9rem;">{s_clean}</span><br><a href="https://www.google.com/search?q={q}" target="_blank" class="minimal-link">GOOGLE</a><a href="https://scholar.google.com/scholar?q={q}" target="_blank" class="minimal-link">SCHOLAR</a></div>', unsafe_allow_html=True)

            if prompts:
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown('<p style="text-align:center; font-size:0.7rem; color:#555555; letter-spacing:2px;">GÖRSEL PROMPTLAR</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="content-text" style="font-family:monospace; font-size:0.9rem; color:#888888;">{prompts.strip()}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"HATA: {e}")
