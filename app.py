import streamlit as st
from groq import Groq
import re
import urllib.parse

# 1. OTURUM KONTROLÜ
if 'authed' not in st.session_state:
    st.session_state['authed'] = False

# 2. PREMIUM UI ARCHITECTURE (CSS GÜNCELLENDİ)
st.set_page_config(page_title="Tarih Haber AI", page_icon="🏛️", layout="centered")

st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }

    /* TÜM YAZI ETİKETLERİNİ (Label) BEYAZ YAP */
    /* Giriş ekranındaki 'E-posta', 'Şifre' ve mod seçimindeki yazıların görünmesini sağlar */
    [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }

    /* YANIP SÖNEN SARI-TURUNCU BAŞLIK */
    @keyframes pulseGlow {
        0% { text-shadow: 0 0 10px #FFCC00; opacity: 1; }
        50% { text-shadow: 0 0 25px #FF8C00; opacity: 0.9; }
        100% { text-shadow: 0 0 10px #FFCC00; opacity: 1; }
    }
    .main-header {
        font-size: 3.5rem !important;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #FFCC00, #FF8C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulseGlow 3s infinite ease-in-out;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    .sub-text {
        color: #8e918f !important;
        text-align: center;
        font-size: 0.9rem;
        letter-spacing: 2px;
        margin-bottom: 2rem;
    }

    /* Giriş Kutuları */
    .stTextInput > div > div > input {
        background-color: #111 !important; 
        color: white !important;
        border: 1px solid #333 !important; 
        border-radius: 12px !important;
        padding: 12px 20px !important; 
        text-align: center;
    }
    .stTextInput > div > div > input:focus {
        border: 1px solid #FFCC00 !important;
    }

    /* Radio/Mod Seçimi */
    div[data-testid="stRadio"] > div {
        justify-content: center; gap: 20px; background: #111; padding: 10px; border-radius: 15px; border: 1px solid #333;
    }

    /* Butonlar */
    div.stButton { display: flex; justify-content: center; margin-top: 25px; }
    div.stButton > button {
        background: linear-gradient(90deg, #FFCC00, #FF8C00) !important;
        color: #000000 !important; border: none !important; border-radius: 12px !important;
        padding: 14px 40px !important; font-weight: 700 !important; font-size: 1.1rem !important;
        min-width: 280px !important; transition: 0.3s;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(255, 204, 0, 0.4); }

    /* İçerik Kartı */
    .content-card {
        background-color: #0a0a0a; padding: 30px; border-radius: 20px;
        border-left: 5px solid #FFCC00; margin: 30px auto; line-height: 1.9;
        font-size: 1.15rem; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: justify;
    }
    
    div[data-testid="stCodeBlock"] { background-color: #000000 !important; border: 1px solid #333 !important; border-radius: 12px !important; }

    .source-box { background: #111; border-radius: 16px; padding: 20px; margin: 15px auto; border: 1px solid #333; text-align: center; }
    .source-btn {
        text-decoration: none; color: #FFCC00 !important; font-size: 0.85rem;
        margin: 5px; font-weight: 600; padding: 6px 15px; border: 1px solid #FFCC00;
        border-radius: 20px; display: inline-block; transition: 0.3s;
    }
    .source-btn:hover { background-color: #FFCC00; color: #000 !important; }
    
    h2, h3 { text-align: center !important; margin-top: 40px !important; color: #FFCC00 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. GİRİŞ EKRANI
def login_screen():
    st.markdown('<div class="main-header">TARİH HABER</div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">YETKİLİ ERİŞİM PANELİ</p>', unsafe_allow_html=True)
    
    try:
        valid_users = st.secrets["users"]
    except:
        st.error("Hata: Streamlit Secrets ayarlarında 'users' bulunamadı.")
        return

    with st.container():
        st.write("---")
        # Artık bu etiketler (E-Posta Adresi, Şifre) CSS sayesinde beyaz görünecek
        email = st.text_input("E-Posta Adresi", placeholder="E-postanızı girin")
        password = st.text_input("Şifre", type="password", placeholder="Şifrenizi girin")
        
        if st.button("SİSTEME GİRİŞ YAP"):
            if email in valid_users and str(valid_users[email]) == password:
                st.session_state['authed'] = True
                st.session_state['user_email'] = email
                st.rerun()
            else:
                st.error("Hatalı giriş!")

# 4. ANA PANEL
if not st.session_state['authed']:
    login_screen()
else:
    col_l, col_r = st.columns([8, 2])
    with col_r:
        if st.button("Çıkış"):
            st.session_state['authed'] = False
            st.rerun()

    st.markdown('<div class="main-header">TARİH HABER</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-text">Aktif Kullanıcı: {st.session_state["user_email"]}</p>', unsafe_allow_html=True)

    mod = st.radio("", ["🎲 Otomatik", "✍️ Manuel"], horizontal=True, label_visibility="collapsed")
    ozel_konu = ""
    if mod == "✍️ Manuel":
        ozel_konu = st.text_input("Araştırma Konusu", placeholder="Ne keşfetmek istersiniz?", label_visibility="collapsed")

    try:
        api_key = st.secrets["GROQ_API_KEY"]
        client = Groq(api_key=api_key)
    except:
        st.error("API Anahtarı eksik!")
        st.stop()

    SYSTEM_PROMPT = (
        "Sen bir tarih profesörü ve sinematik hikaye anlatıcısısın. "
        "ŞU KURALLARA KESİNLİKLE UY:\n"
        "1. SARSICI KANCA: Metne mutlaka şok edici, ters köşe bir iddiayla başla.\n"
        "2. METİN: Akademik gerçekleri akıcı anlat. En az 450-500 kelime.\n"
        "3. KAYNAKLAR: Sona 'KAYNAKLAR:' ekle.\n"
        "4. PROMPTLAR: En sona '---PROMPTLAR---' yazıp 10 adet numaralı İngilizce prompt üret."
    )

    if st.button("ARAŞTIRMAYI BAŞLAT"):
        konu = ozel_konu if (mod == "✍️ Manuel" and ozel_konu) else "Tarihten sarsıcı bir olay seç."
        with st.spinner("Araştırılıyor..."):
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
                with st.expander("📋 Kopyala"):
                    st.code(main_story.strip(), language="text")

                if sources_raw:
                    st.subheader("📚 Üçlü Doğrulama")
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
                    st.subheader("🖼️ Görsel Promptlar")
                    st.code(prompts.strip(), language="text")
            except Exception as e:
                st.error(f"Hata: {e}")
