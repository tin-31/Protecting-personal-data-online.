import streamlit as st
from supabase import create_client
from groq import Groq

# ==========================================
# CẤU HÌNH TRANG & SIÊU GIAO DIỆN (ULTRA UI)
# ==========================================
st.set_page_config(page_title="Security Ecosystem", page_icon="🛡️", layout="wide")

# CSS Cao cấp: Tự động thích ứng màu sắc (Light/Dark Mode)
st.markdown("""
    <style>
    /* 1. ĐỊNH NGHĨA BIẾN VÀ PHÔNG CHỮ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* 2. LÀM ĐẸP CÁC TAB (GLASSMORPHISM) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(150, 150, 150, 0.05);
        padding: 8px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    /* 3. THIẾT KẾ CÁC KHỐI NỘI DUNG NỔI (CARD UI) */
    div[data-testid="stForm"], .stChatMessage, div[data-testid="stExpander"] {
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 24px !important;
        padding: 30px !important;
        background: var(--background-secondary-color); /* Tự động đổi màu theo Mode */
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05) !important;
        transition: transform 0.3s ease;
    }
    
    div[data-testid="stForm"]:hover {
        transform: translateY(-5px);
        border-color: var(--primary-color) !important;
    }

    /* 4. NÚT BẤM HIỆU ỨNG GRADIENT TĨNH */
    .stButton>button {
        border-radius: 14px;
        border: none;
        padding: 15px 30px;
        background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%);
        color: white;
        font-weight: 800;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        box-shadow: 0 8px 20px rgba(31, 111, 235, 0.3);
    }

    /* 5. CẢI TIẾN KHUNG CHAT */
    .stChatMessage {
        border-radius: 18px !important;
        animation: fadeIn 0.5s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* 6. THANH TRƯỢT & INPUT */
    .stSelectbox, .stRadio, .stTextInput {
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KẾT NỐI HỆ THỐNG ---
@st.cache_resource
def init_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

@st.cache_resource
def init_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY")
    return Groq(api_key=api_key) if api_key else None

supabase = init_connection()
client = init_groq_client()

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
tab1, tab2 = st.tabs(["📊 PHÂN TÍCH RỦI RO", "🤖 CHUYÊN GIA AI"])

# --- TAB 1: ĐÁNH GIÁ RỦI RO ---
with tab1:
    st.markdown("<h1 style='text-align: center;'>🛡️ Cybersecurity Diagnostics</h1>", unsafe_allow_html=True)
    
    with st.form("risk_form"):
        st.markdown("### 🗝️ Identity & Devices")
        c1, c2 = st.columns(2)
        with c1:
            age = st.selectbox("Độ tuổi", ["Dưới 15", "15 - 18", "19 - 25", "Trên 25"])
            pw = st.radio("Cấu trúc mật khẩu thường dùng:", 
                         ["Chỉ chữ/số đơn giản", "Kết hợp chữ và số", "Siêu cấp (Chữ hoa, số, ký tự đặc biệt)"])
        with c2:
            update = st.radio("Cập nhật hệ thống:", 
                             ["Khi máy hỏng mới làm", "Tháng một lần", "Tự động/Ngay lập tức"])

        st.divider()
        st.markdown("### 🌐 Online Behavior")
        c3, c4 = st.columns(2)
        with c3:
            two_fa = st.radio("Bảo mật 2 lớp (2FA):", 
                             ["Không dùng", "Vài trang quan trọng", "Tất cả tài khoản"])
            phish = st.radio("Ứng xử với tin nhắn lạ:", 
                            ["Click xem thử", "Xóa/Lờ đi", "Báo cáo Spam ngay"])
        with c4:
            wifi = st.radio("Sử dụng mạng công cộng:", 
                           ["Thoải mái sử dụng", "Hạn chế/Chỉ đọc tin", "Dùng VPN/4G riêng"])
            piracy = st.radio("Phần mềm lậu (Crack):", 
                             ["Dùng thường xuyên", "Thỉnh thoảng", "Nói không với Crack"])

        st.markdown("<br>", unsafe_allow_html=True)
        btn = st.form_submit_button("KHỞI CHẠY PHÂN TÍCH HỆ THỐNG")
        
        if btn:
            score = 100
            if pw == "Siêu cấp (Chữ hoa, số, ký tự đặc biệt)": score -= 15
            elif pw == "Kết hợp chữ và số": score -= 5
            if update == "Tự động/Ngay lập tức": score -= 10
            if two_fa == "Tất cả tài khoản": score -= 25
            elif two_fa == "Vài trang quan trọng": score -= 10
            if phish == "Báo cáo Spam ngay": score -= 15
            if wifi == "Dùng VPN/4G riêng": score -= 20
            elif wifi == "Hạn chế/Chỉ đọc tin": score -= 10
            if piracy == "Nói không với Crack": score -= 15
            
            risk_score = max(0, min(100, score))
            
            st.markdown(f"## Mức độ rủi ro: `{risk_score}%`")
            st.progress(risk_score / 100)
            
            if risk_score > 60: st.error("🚨 Trạng thái: **NGUY HIỂM CAO**")
            elif risk_score > 30: st.warning("⚠️ Trạng thái: **CÓ RỦI RO**")
            else: st.success("✅ Trạng thái: **AN TOÀN TUYỆT ĐỐI**")
            
            if supabase:
                try: supabase.table('survey_results').insert({"age_group": age, "risk_score": risk_score}).execute()
                except: pass

# --- TAB 2: TRỢ LÝ AI ---
with tab2:
    st.markdown("<h2 style='text-align: center;'>🤖 AI Security Consultant</h2>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Hỏi tôi bất cứ điều gì về bảo mật..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Bạn là chuyên gia an ninh mạng quốc tế. Trả lời tiếng Việt, học thuật, cấu trúc rõ ràng."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3, stream=True,
                )
                res = st.write_stream(c.choices[0].delta.content for c in stream if c.choices[0].delta.content)
                st.session_state.messages.append({"role": "assistant", "content": res})
            except:
                st.error("Kết nối gián đoạn. Thử lại sau.")
