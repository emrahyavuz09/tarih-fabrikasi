import streamlit as st
from groq import Groq
import re
import urllib.parse

# 1. PREMIUM UI ARCHITECTURE (CSS)
st.set_page_config(page_title="Tarih Haber AI", page_icon="🏛️", layout="centered")

st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #0e1117 !important;
        color: #e3e3e3 !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* YANIP SÖNEN SARI-TURUNCU BAŞLIK */
    @keyframes pulseGlow {
        0% { text-shadow: 0 0 10px #FFCC00; opacity: 1; }
        50% { text-shadow: 0 0 25px #FF8C00; opacity: 0.9; }
        100% { text-shadow: 0 0 10px #FFCC00; opacity: 1; }
    }
    .main-header {
        font-size: 3rem !important;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #FFCC00, #FF8C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulseGlow 3s infinite ease-in-out;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    /* Alt Başlık */
    .sub-text {
        color: #8e918f !important;
        text-align: center;
        font-size: 0.9rem;
        letter-spacing: 2px;
        margin-bottom: 2rem;
    }

    /* MOD SEÇİMİ (Kart Şeklinde) */
    div[data-testid="stRadio"] > div {
        justify-content: center;
        gap: 20px;
        background: #1e1f20;
        padding: 10px;
        border-radius: 15px;
        border: 1px solid #333;
    }
    div[data-testid="stRadio"] label p {
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    /* GİRİŞ KUTUSU (Belirgin ve Şık) */
    .stTextInput > div > div > input {
        background-color: #1e1f20 !important;
        color: white !important;
        border: 1px solid #444 !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        text-align: center;
    }
    .stTextInput > div > div > input:focus {
        border-color: #FFCC00 !important;
    }

    /* ARAŞTIR BUTONU (Görünür ve Canlı) */
    div.stButton {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
    div.stButton > button {
        background: linear-gradient(90deg, #FFCC00, #FF8C00) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 50px !important;
        font-weight: 700 !important;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(255, 204, 0, 0.3);
    }

    /* İÇERİK KARTLARI (Metinlerin Birbirine Girmesini Engeller) */
    .content-card {
        background-color: #1a1c23;
        padding: 30px;
        border-radius: 20px;
        border-left: 5px solid #FFCC00;
        margin: 30px auto;
        line-height: 1.8;
        font-size: 1.1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Kaynak Kartları */
    .source-box {
        background: #252833;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #3d4152;
    }
    .source-link {
        color: #FFCC00 !important;
        text-decoration: none;
        font-weight: 600;
        margin-right: 15px;
    }
    .source-link:hover { text-decoration: underline; }

    /* Bekleme Animasyonu */
    .loading-info {
        text-align: center;
        color: #FFCC00;
        font-style: italic;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ARAYÜZ KATMANI
st.markdown('<div class="main-header">TARİH HABER</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">DİJİTAL ARŞİV VE AKADEMİK ARAŞTIRMA SİSTEMİ</div>', unsafe_allow_html=True)

# Seçim ve Giriş Alanı
mod = st.radio("", ["🎲 Otomatik", "✍️ Manuel"], horizontal=True, label_visibility="collapsed")
ozel_konu = ""
if mod == "✍️ Manuel":
    ozel_konu = st.text_input("", placeholder="Merak ettiğiniz bir konuyu buraya yazın...", label_visibility="collapsed")

# 3. YAPAY ZEKA MOTORU (Llama-3.3-70b)
client = Groq(api_key="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")

# Sarsıcı Kanca Talimatı Sabitlendi
SYSTEM_PROMPT = (
    "Sen bir tarih profesörü ve viral içerik stratejistisin. "
    "Çıktılarında teknik başlık kullanma. ŞU KURALLARA KESİNLİKLE UY:\n\n"
    "1. SARSICI KANCA: Metne ASLA klasik cümlelerle başlama. İlk 2 cümlen ters köşe yapmalı, "
    "genel bilinen bir yanlışı iddia etmeli veya izleyiciyi şok edecek, 'Nasıl olur?' dedirtecek bir "
    "tespitle başlamalıdır. (Örn: 'Sanılanın aksine, Amerika'yı ilk keşfeden kişi Kristof Kolomb değildi' gibi.)\n"
    "2. METİN: Girişin ardından olayı akademik gerçeklerle en az 450-500 kelime anlat.\n"
    "3. KAYNAKLAR: Sona 'KAYNAKLAR:' başlığı ekle.\n"
    "4. PROMPTLAR: En sona '---PROMPTLAR---' yazıp 10 adet numaralı sinematik İngilizce prompt üret."
)

if st.button("ARAŞTIRMAYI BAŞLAT"):
    konu = ozel_konu if (mod == "✍️ Manuel" and ozel_konu) else "Tarihten çok sarsıcı ve yanlış bilinen bir olay seç."
    
    with st.spinner(""):
        st.markdown('<p class="loading-info">Arşivler taranıyor, sarsıcı gerçekler gün yüzüne çıkarılıyor...</p>', unsafe_allow_html=True)
        
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
            
            # İçerik Ayıklama
            if "---PROMPTLAR---" in output:
                story_part, prompts = output.split("---PROMPTLAR---")
            else:
                story_part, prompts = output, ""

            if "KAYNAKLAR:" in story_part:
                main_story, sources_raw = story_part.split("KAYNAKLAR:")
            else:
                main_story, sources_raw = story_part, ""

            # 4. GÖSTERİM KATMANI
            st.markdown("---")
            
            # Ana Metin Kartı
            st.markdown(f'<div class="content-card">{main_story.strip()}</div>', unsafe_allow_html=True)

            # Kaynaklar Bölümü
            if sources_raw:
                st.subheader("📚 Doğrulama Kaynakları")
                for s in sources_raw.strip().split('\n'):
                    s_clean = re.sub(r'^[0-9\-\.\*\s]+', '', s.strip())
                    if s_clean:
                        q = urllib.parse.quote(s_clean)
                        st.markdown(f"""
                        <div class="source-box">
                            <div style="margin-bottom:8px; font-weight:500;">{s_clean}</div>
                            <a href="https://www.google.com/search?q={q}" target="_blank" class="source-link">🔍 Google</a>
                            <a href="https://scholar.google.com/scholar?q={q}" target="_blank" class="source-link">🎓 Akademik</a>
                        </div>
                        """, unsafe_allow_html=True)

            # Görsel Promptlar Kartı
            if prompts:
                st.subheader("🖼️ Görsel Üretim Promptları")
                st.markdown(f'<div class="content-card" style="font-family:monospace; border-left-color:#8e918f; font-size:0.9rem;">{prompts.strip()}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Sistemsel Hata: {e}")
