import streamlit as st
from groq import Groq
import re
import urllib.parse

# 1. OTURUM VE BENİ HATIRLA KONTROLÜ
if 'authed' not in st.session_state:
    st.session_state['authed'] = False

# 2. PREMIUM UI ARCHITECTURE
st.set_page_config(page_title="Tarih Haber AI", page_icon="🏛️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: #ffffff !important; font-family: 'Inter', sans-serif; }
    
    [data-testid="stWidgetLabel"] p, .stMarkdown p, div[data-testid="stRadio"] label p {
        color: #ffffff !important; font-size: 1.1rem !important; font-weight: 600 !important;
    }

    input::placeholder { color: #bbbbbb !important; }

    @keyframes pulseGlow {
        0% { text-shadow: 0 0 10px #FFCC00; opacity: 1; }
        50% { text-shadow: 0 0 25px #FF8C00; opacity: 0.9; }
        100% { text-shadow: 0 0 10px #FFCC00; opacity: 1; }
    }
    .main-header {
        font-size: 3.5rem !important; font-weight: 800; text-align: center;
        background: linear-gradient(90deg, #FFCC00, #FF8C00);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: pulseGlow 3s infinite ease-in-out; margin-top: 1rem; margin-bottom: 0.5rem;
    }

    .sub-text { color: #cccccc !important; text-align: center; font-size: 0.95rem; margin-bottom: 2rem; }

    .stTextInput > div > div > input {
        background-color: #1a1a1a !important; color: #ffffff !important;
        border: 1px solid #444 !important; border-radius: 12px !important; text-align: center;
    }

    div[data-testid="stRadio"] > div {
        justify-content: center; gap: 10px; background: #1a1a1a; padding: 15px; border-radius: 15px; border: 1px solid #333;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #FFCC00, #FF8C00) !important;
        color: #000000 !important; border: none !important; border-radius: 12px !important;
        padding: 14px 40px !important; font-weight: 800; min-width: 280px !important;
    }

    /* Beni Hatırla Checkbox Rengi */
    div[data-testid="stCheckbox"] label p { color: #FFCC00 !important; font-size: 0.9rem !important; }

    .content-card {
        background-color: #0a0a0a; padding: 35px; border-radius: 20px;
        border-left: 5px solid #FFCC00; margin: 30px auto; line-height: 2.1;
        font-size: 1.2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.6); text-align: justify;
        white-space: pre-wrap;
    }

    .source-box { background: #111; border-radius: 16px; padding: 20px; margin: 15px auto; border: 1px solid #333; text-align: center; }
    .source-btn {
        text-decoration: none; color: #FFCC00 !important; font-size: 0.85rem;
        margin: 5px; font-weight: 700; padding: 8px 18px; border: 2px solid #FFCC00;
        border-radius: 25px; display: inline-block;
    }
    
    h2, h3 { text-align: center !important; color: #FFCC00 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. GİRİŞ SİSTEMİ (Beni Hatırla Dahil)
def login_screen():
    st.markdown('<div class="main-header">TARİH HABER</div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">YETKİLİ ERİŞİM PANELİ</p>', unsafe_allow_html=True)
    try:
        valid_users = st.secrets["users"]
    except:
        st.error("Secrets ayarı bulunamadı!")
        return

    with st.container():
        email = st.text_input("E-Posta Adresi")
        password = st.text_input("Şifre", type="password")
        remember_me = st.checkbox("Beni Hatırla")
        
        if st.button("SİSTEME GİRİŞ YAP"):
            if email in valid_users and str(valid_users[email]) == password:
                st.session_state['authed'] = True
                st.session_state['user_email'] = email
                if remember_me:
                    st.info("Beni Hatırla özelliği bu oturum için aktif edildi.")
                st.rerun()
            else: st.error("Hatalı giriş!")

if not st.session_state['authed']:
    login_screen()
else:
    col_l, col_r = st.columns([8, 2])
    with col_r:
        if st.button("Güvenli Çıkış"):
            st.session_state['authed'] = False
            st.rerun()

    st.markdown('<div class="main-header">TARİH HABER</div>', unsafe_allow_html=True)

    kategoriler = ["Osmanlı Tarihi", "Roma Tarihi", "Mısır Tarihi", "Pers Tarihi", "Cumhuriyet Tarihi", "Bizans Tarihi", "Avrupa Tarihi"]
    secilen_kat = st.radio("Bir Tarih Kategorisi Seçin", kategoriler, horizontal=True)
    
    manuel_konu = st.text_input("Özel Konu Araştır", placeholder="Sadece tarihsel konuları kabul eder...")

    try:
        api_key = st.secrets["GROQ_API_KEY"]
        client = Groq(api_key=api_key)
    except:
        st.error("API Anahtarı bulunamadı!")
        st.stop()

    # 4. EN SERT FİLTRELEME TALİMATI
    SYSTEM_PROMPT = (
        f"Sen sadece TARİH üzerine uzmanlaşmış, çok katı bir yapay zekasın. SADECE TÜRKÇE KARAKTERLER KULLAN.\n"
        f"ASLA CEVAP VERMEYECEĞİN DURUMLAR:\n"
        f"- Küfür, argo, hakaret içeren her türlü girdi.\n"
        f"- Sadece özel isimlerden oluşan anlamsız aramalar (Örn: Sadece 'Ahmet', 'Mehmet' yazıp bırakmak).\n"
        f"- Tarih dışı her şey (Selam, nasılsın, yemek tarifi, siyaset, spor, teknoloji, kodlama vb.).\n"
        f"BU DURUMLARDA ŞUNU SÖYLE: 'Bu sistem yalnızca derinlemesine tarih araştırmaları için tasarlanmıştır. Lütfen tarihsel bir konu belirtin.'\n\n"
        f"EĞER KONU CİDDİ BİR TARİH ARAŞTIRMASI İSE:\n"
        f"1. GİRİŞ (KANCA): Metne 'Biliyor musun?' veya 'Sanılanın aksine...' ile başlayan sarsıcı bir soruyla başla.\n"
        f"2. OKUMA METNİ: Başlıklar olmadan tek bir akıcı senaryo olarak yaz. En az 450-500 kelime.\n"
        f"3. KAYNAKLAR: En sona 'KAYNAKLAR:' ekle.\n"
        f"4. PROMPTLAR: En sona '---PROMPTLAR---' yazıp 10 adet numaralı İngilizce prompt üret."
    )

    if st.button("ARAŞTIRMAYI BAŞLAT"):
        konu = manuel_konu if manuel_konu else f"{secilen_kat} kategorisinden en sarsıcı olay."
        with st.spinner("Tarih Muhafızı kontrol ediyor..."):
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": konu}],
                    temperature=0.7
                )
                output = completion.choices[0].message.content
                output = re.sub(r'[^\x00-\x7FğüşıöçĞÜŞİÖÇ\n\r\t ]+', '', output)

                if "KAYNAKLAR:" in output:
                    if "---PROMPTLAR---" in output: story_part, prompts = output.split("---PROMPTLAR---")
                    else: story_part, prompts = output, ""
                    
                    main_story, sources_raw = story_part.split("KAYNAKLAR:")

                    st.markdown("---")
                    st.subheader(f"🎙️ Araştırma Sonucu")
                    st.markdown(f'<div class="content-card">{main_story.strip()}</div>', unsafe_allow_html=True)
                    with st.expander("📋 Kopyala"): st.code(main_story.strip(), language="text")

                    if sources_raw:
                        st.subheader("📚 Üçlü Doğrulama")
                        for s in sources_raw.strip().split('\n'):
                            s_clean = re.sub(r'^[0-9\-\.\*\s]+', '', s.strip())
                            if s_clean:
                                q = urllib.parse.quote(s_clean)
                                st.markdown(f"""
                                <div class="source-box">
                                    <div style="margin-bottom:12px; font-weight:600;">{s_clean}</div>
                                    <a href="https://www.google.com/search?q={q}" target="_blank" class="source-btn">🔍 Google</a>
                                    <a href="https://scholar.google.com/scholar?q={q}" target="_blank" class="source-btn">🎓 Akademik</a>
                                    <a href="https://www.google.com/search?q={q}+wikipedia" target="_blank" class="source-btn">🌐 Wikipedia</a>
                                </div>
                                """, unsafe_allow_html=True)

                    if prompts:
                        st.subheader("🖼️ Sahne Bazlı Promptlar")
                        st.code(prompts.strip(), language="text")
                else:
                    # Filtreye takılan cevaplar için
                    st.warning(output.strip())
                
            except Exception as e:
                st.error(f"Hata: {e}")
