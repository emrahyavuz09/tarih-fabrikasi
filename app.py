import streamlit as st
from groq import Groq
import re
import urllib.parse

# 1. OTURUM KONTROLÜ
if 'authed' not in st.session_state:
    st.session_state['authed'] = False

# 2. PREMIUM UI ARCHITECTURE
st.set_page_config(page_title="Tarih Haber AI", page_icon="🏛️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; color: #e3e3e3 !important; font-family: 'Inter', sans-serif; }
    @keyframes pulseGlow {
        0% { text-shadow: 0 0 10px #FFCC00; opacity: 1; }
        50% { text-shadow: 0 0 25px #FF8C00; opacity: 0.9; }
        100% { text-shadow: 0 0 10px #FFCC00; opacity: 1; }
    }
    .main-header {
        font-size: 3rem !important; font-weight: 800; text-align: center;
        background: linear-gradient(90deg, #FFCC00, #FF8C00);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: pulseGlow 3s infinite ease-in-out; margin-top: 1rem; margin-bottom: 0.5rem;
    }
    .sub-text { color: #8e918f !important; text-align: center; font-size: 0.9rem; letter-spacing: 2px; margin-bottom: 2rem; }
    div[data-testid="stRadio"] > div { justify-content: center; gap: 20px; background: #1e1f20; padding: 10px; border-radius: 15px; border: 1px solid #333; }
    div[data-testid="stRadio"] label p { color: #ffffff !important; font-weight: 500 !important; }
    .stTextInput > div > div > input {
        background-color: #1e1f20 !important; color: white !important;
        border: 1px solid #444 !important; border-radius: 12px !important;
        padding: 12px 20px !important; text-align: center;
    }
    div.stButton { display: flex; justify-content: center; margin-top: 25px; }
    div.stButton > button {
        background: linear-gradient(90deg, #FFCC00, #FF8C00) !important;
        color: #000000 !important; border: none !important; border-radius: 12px !important;
        padding: 14px 40px !important; font-weight: 700 !important; font-size: 1.1rem !important;
        min-width: 280px !important; transition: 0.3s; white-space: nowrap !important;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(255, 204, 0, 0.4); }
    .content-card {
        background-color: #1a1c23; padding: 30px; border-radius: 20px;
        border-left: 5px solid #FFCC00; margin: 30px auto; line-height: 1.9;
        font-size: 1.15rem; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: justify;
    }
    div[data-testid="stCodeBlock"] { background-color: #000000 !important; border: 1px solid #333 !important; border-radius: 12px !important; }
    .source-box { background: #1e1f20; border-radius: 16px; padding: 20px; margin: 15px auto; border: 1px solid #333; text-align: center; }
    .source-btn { text-decoration: none; color: #FFCC00 !important; font-size: 0.85rem; margin: 0 8px; font-weight: 600; padding: 6px 12px; border: 1px solid #FFCC00; border-radius: 20px; transition: 0.3s; }
    .source-btn:hover { background-color: #FFCC00; color: #000 !important; }
    h2, h3 { text-align: center !important; margin-top: 40px !important; color: #FFCC00 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. GİRİŞ EKRANI (Şifreler Streamlit Secrets'tan Geliyor)
def login_screen():
    st.markdown('<div class="main-header">TARİH HABER</div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">YETKİLİ ERİŞİM PANELİ</p>', unsafe_allow_html=True)
    
    # Şifreleri Streamlit Secrets'tan çekiyoruz
    try:
        valid_users = st.secrets["users"]
    except:
        st.error("Sistem hatası: Kullanıcı veritabanı bulunamadı. Lütfen Streamlit ayarlarını kontrol edin.")
        return

    with st.container():
        st.write("---")
        email = st.text_input("E-Posta Adresi")
        password = st.text_input("Şifre", type="password")
        
        if st.button("SİSTEME GİRİŞ YAP"):
            if email in valid_users and str(valid_users[email]) == password:
                st.session_state['authed'] = True
                st.session_state['user_email'] = email
                st.rerun()
            else:
                st.error("Hatalı giriş! Lütfen bilgilerinizi kontrol edin.")

# 4. ANA UYGULAMA
if not st.session_state['authed']:
    login_screen()
else:
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("Çıkış Yap", key="logout"):
            st.session_state['authed'] = False
            st.rerun()

    st.markdown('<div class="main-header">TARİH HABER</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-text">Hoş geldiniz, {st.session_state["user_email"]}</p>', unsafe_allow_html=True)

    mod = st.radio("", ["🎲 Otomatik", "✍️ Manuel"], horizontal=True, label_visibility="collapsed")
    ozel_konu = ""
    if mod == "✍️ Manuel":
        ozel_konu = st.text_input("", placeholder="Merak ettiğiniz bir konuyu buraya yazın...", label_visibility="collapsed")

    # API Key de Secrets'tan alınabilir (Daha güvenli)
    client = Groq(api_key=st.secrets.get("GROQ_API_KEY", "BURAYA_API_KEY_GELECEK_VEYA_BOŞ_BIRAKIN"))

    SYSTEM_PROMPT = (
        "Sen bir tarih profesörü ve sinematik hikaye anlatıcısısın. "
        "ŞU KURALLARA KESİNLİKLE UY:\n\n"
        "1. SARSICI KANCA: Metne ASLA klasik başlama. İlk 2 cümlen provokatif, ters köşe ve şok edici bir iddia olsun.\n"
        "2. METİN: Akademik gerçekleri akıcı bir dille anlat. En az 450-500 kelime olsun.\n"
        "3. KAYNAKLAR: Metin bitince 'KAYNAKLAR:' başlığı altında kaynakları ver.\n"
        "4. PROMPTLAR: En sona '---PROMPTLAR---' yaz. 10 adet numaralı sinematik İngilizce prompt üret."
    )

    if st.button("ARAŞTIRMAYI BAŞLAT"):
        konu = ozel_konu if (mod == "✍️ Manuel" and ozel_konu) else "Tarihten sarsıcı bir olay seç."
        with st.spinner(""):
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": konu}],
                    temperature=0.75
                )
                output = completion.choices[0].message.content
                if "---PROMPTLAR---" in output:
                    story_part, prompts = output.split("---PROMPTLAR---")
                else:
                    story_part, prompts = output, ""
                if "KAYNAKLAR:" in story_part:
                    main_story, sources_raw = story_part.split("KAYNAKLAR:")
                else:
                    main_story, sources_raw = story_part, ""

                st.markdown("---")
                st.subheader("📝 Araştırma Metni")
                st.markdown(f'<div class="content-card">{main_story.strip()}</div>', unsafe_allow_html=True)
                with st.expander("📋 Metni Kopyalamak İçin Tıkla"):
                    st.code(main_story.strip(), language="text")

                if sources_raw:
                    st.subheader("📚 Çok Yönlü Doğrulama")
                    for s in sources_raw.strip().split('\n'):
                        s_clean = re.sub(r'^[0-9\-\.\*\s]+', '', s.strip())
                        if s_clean:
                            q = urllib.parse.quote(s_clean)
                            st.markdown(f"""
                            <div class="source-box">
                                <div style="margin-bottom:12px; font-weight:500;">{s_clean}</div>
                                <a href="https://www.google.com/search?q={q}" target="_blank" class="source-btn">🔍 Google</a>
                                <a href="https://scholar.google.com/scholar?q={q}" target="_blank" class="source-btn">🎓 Akademik</a>
                                <a href="https://www.google.com/search?q={q}+wikipedia" target="_blank" class="source-btn">🌐 Wikipedia</a>
                            </div>
                            """, unsafe_allow_html=True)
                if prompts:
                    st.subheader("🖼️ Sahne Bazlı Görsel Promptlar")
                    st.code(prompts.strip(), language="text")
            except Exception as e:
                st.error(f"Sistemsel Hata: {e}")
