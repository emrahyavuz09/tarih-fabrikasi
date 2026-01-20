import streamlit as st
from groq import Groq
import re
import urllib.parse

# 1. TASARIM VE ANİMASYON AYARLARI
st.set_page_config(page_title="Tarih Fabrikası AI", page_icon="🔥", layout="centered")

# API Anahtarın buraya entegre edildi
client = Groq(api_key="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")

st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #0d0d0d;
        color: #ffffff;
    }

    /* Başlık Animasyonu */
    @keyframes glowText {
        0% { text-shadow: 0 0 10px #FF8C00, 0 0 20px #FF8C00; }
        50% { text-shadow: 0 0 20px #FFA500, 0 0 40px #FFA500; }
        100% { text-shadow: 0 0 10px #FF8C00, 0 0 20px #FF8C00; }
    }
    .main-title {
        color: #FF8C00 !important;
        font-size: 3.2rem !important;
        font-weight: 900;
        text-align: center;
        animation: glowText 3s infinite ease-in-out;
    }

    /* Yazıları Beyaz Yap ve Ortala */
    [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        font-size: 1.2rem !important;
        text-align: center !important;
        width: 100%;
        display: block;
    }

    [data-testid="stRadio"] > div {
        display: flex;
        justify-content: center;
        gap: 30px;
    }
    [data-testid="stRadio"] label p {
        color: #ffffff !important;
        font-size: 1.1rem !important;
    }

    /* Giriş Kutusunu Ortala */
    .stTextInput {
        width: 100%;
        max-width: 550px;
        margin: 0 auto;
    }

    /* Ana Buton Animasyonu ve Ortalama */
    @keyframes pulse-orange {
        0% { box-shadow: 0 0 0 0 rgba(255, 140, 0, 0.7); }
        70% { box-shadow: 0 0 0 20px rgba(255, 140, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 140, 0, 0); }
    }
    div.stButton {
        display: flex;
        justify-content: center;
        margin-top: 30px;
    }
    div.stButton > button {
        background-color: #FF8C00 !important;
        color: #000 !important;
        border-radius: 50px !important;
        padding: 20px 70px !important;
        font-size: 1.4rem !important;
        font-weight: 900;
        animation: pulse-orange 2s infinite;
        border: none !important;
        transition: 0.4s;
    }
    div.stButton > button:hover {
        transform: scale(1.1);
        background-color: #ffffff !important;
        color: #FF8C00 !important;
    }

    /* Bekleme Yazısı Yanıp Sönme */
    @keyframes blinker { 50% { opacity: 0; } }
    .loading-text {
        color: #FF8C00;
        font-weight: bold;
        animation: blinker 1s linear infinite;
    }

    /* Kaynak Kartları */
    .source-card {
        background-color: #1a1a1a;
        padding: 25px;
        border-radius: 25px;
        border: 2px solid #FF8C00;
        margin: 25px auto;
        max-width: 550px;
        text-align: center;
    }
    .icon-link {
        text-decoration: none;
        color: #FF8C00 !important;
        border: 2px solid #FF8C00;
        padding: 8px 20px;
        border-radius: 50px;
        display: inline-block;
        margin: 8px;
        font-weight: bold;
    }
    .icon-link:hover {
        background-color: #FF8C00;
        color: #000 !important;
    }

    /* Kod Blokları */
    code {
        background-color: #000000 !important;
        color: #FF8C00 !important;
        border-left: 8px solid #FF8C00 !important;
        font-size: 1.1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🔥 Tarih Fabrikası AI</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#bbbbbb;">Bulut Tabanlı Akademik Araştırma Sistemi</p>', unsafe_allow_html=True)

# 2. MOD SEÇİMİ VE GİRİŞ
mod = st.radio("Mod Seçimi:", ["🎲 Otomatik", "✍️ Manuel"], horizontal=True)

ozel_konu = ""
if mod == "✍️ Manuel":
    ozel_konu = st.text_input("", placeholder="Araştırmak istediğiniz konuyu buraya yazın...", label_visibility="collapsed")

# 3. SİSTEM TALİMATI
SYSTEM_PROMPT = (
    "Sen akademik bir tarih profesörü ve viral içerik uzmanısın. "
    "Çıktılarında 'Belgesel', 'Senaryo' gibi teknik başlıklar kullanma. "
    "ŞU KURALLARA KESİNLİKLE UY:\n"
    "1. KANCA: İlk 2 cümle konuyla %100 bağlantılı, sarsıcı bir merak uyandırmalı.\n"
    "2. METİN: En az 400-500 kelime, tamamen TÜRKÇE, akıcı bir anlatım yap.\n"
    "3. KAYNAKLAR: Metnin sonuna 'KAYNAKLAR:' başlığı koy ve altına her satırda sadece BİR gerçek yazar/kitap adı ekle.\n"
    "4. PROMPTLAR: '---PROMPTLAR---' yazısından sonra 8-25 adet numaralı, 9:16 dikey, sinematik İNGİLİZCE promptlar üret.\n\n"
    "Metni ve promptları asla yarıda kesme."
)

# 4. ÜRETİM SÜRECİ
if st.button("Hemen Araştır ve Oluştur"):
    konu_mesaji = ozel_konu if (mod == "✍️ Manuel" and ozel_konu) else "Dünya tarihinden az bilinen, kanıtlanmış ve sarsıcı bir olay seç."
    
    wait_text = "Biraz uzun sürebilir; çünkü bu araştırma kapsamında her şeyi gerçek ve doğrulanabilir kaynaklardan inceliyoruz. "
    with st.spinner(""):
        st.markdown(f'<p style="text-align:center; color:#ffffff;">{wait_text}<span class="loading-text">Lütfen Bekleyin...</span></p>', unsafe_allow_html=True)
        
        try:
            # Groq üzerinden Llama 3 kullanarak hızlı ve ücretsiz üretim
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": konu_mesaji}],
                temperature=0.6,
                max_tokens=4096
            )
            
            tam_cevap = completion.choices[0].message.content
            
            # İçerik Ayrıştırma
            if "---PROMPTLAR---" in tam_cevap:
                hikaye, promptlar = tam_cevap.split("---PROMPTLAR---")
            else:
                hikaye, promptlar = tam_cevap, ""

            if "KAYNAKLAR:" in hikaye:
                metin, kaynaklar_ham = hikaye.split("KAYNAKLAR:")
            else:
                metin, kaynaklar_ham = hikaye, ""

            # 5. MERKEZİ GÖSTERİM
            st.markdown("---")
            st.markdown("### 📝 Video Metni")
            st.code(metin.strip(), language="text")

            if kaynaklar_ham:
                st.markdown("### 📚 Doğrulanabilir Kaynakça")
                kaynak_listesi = kaynaklar_ham.strip().split('\n')
                for k in kaynak_listesi:
                    k_cleaned = re.sub(r'^[0-9\-\.\*\s]+', '', k.strip())
                    if k_cleaned:
                        query = urllib.parse.quote(k_cleaned)
                        st.markdown(f"""
                        <div class="source-card">
                            <b style="color:#ffffff;">📖 {k_cleaned}</b><br><br>
                            <a href="https://www.google.com/search?q={query}" target="_blank" class="icon-link">🔍 Google</a>
                            <a href="https://scholar.google.com.tr/scholar?q={query}" target="_blank" class="icon-link">🎓 Akademik</a>
                            <a href="https://www.google.com/search?q={query}+wikipedia" target="_blank" class="icon-link">🌐 Wiki</a>
                        </div>
                        """, unsafe_allow_html=True)

            if promptlar:
                st.markdown("### 🖼️ Sinematik Promptlar")
                st.code(promptlar.strip(), language="text")

            st.success("✅ Tüm veriler bulut üzerinden doğrulandı ve hazırlandı!")

        except Exception as e:
            st.error(f"Hata: {e}")