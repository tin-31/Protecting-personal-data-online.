import streamlit as st
from supabase import create_client
from groq import Groq

# ==========================================
# CẤU HÌNH TRANG & GIAO DIỆN (UI/UX CUSTOM)
# ==========================================
st.set_page_config(page_title="Hệ Sinh Thái An Toàn Không Gian Mạng", page_icon="🛡️", layout="wide")

# CSS tùy chỉnh để làm đẹp giao diện
st.markdown("""
    <style>
    /* Tổng thể phông nền và màu chữ */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Làm đẹp các Tab */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #161b22;
        padding: 10px 20px;
        border-radius: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 10px;
        color: #8b949e;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f6feb !important;
        color: white !important;
    }

    /* Bo góc và làm nổi các khối nội dung (Glassmorphism) */
    div[data-testid="stForm"], .stChatMessage, div[data-testid="stExpander"] {
        background: rgba(22, 27, 34, 0.7) !important;
        border: 1px solid rgba(48, 54, 61, 1) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }

    /* Làm đẹp nút bấm */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1f6feb 0%, #388bfd 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: bold;
        transition: transform 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(31, 111, 235, 0.4);
    }

    /* Thanh Progress bar chuyên nghiệp */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #f85149 , #e3b341, #2ea043);
    }
    
    /* Khung chat */
    .stChatMessage {
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KẾT NỐI HỆ THỐNG ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except: return None

@st.cache_resource
def init_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY")
    return Groq(api_key=api_key) if api_key else None

supabase = init_connection()
client = init_groq_client()

# ==========================================
# GIAO DIỆN CHÍNH (TỐI GIẢN & SANG TRỌNG)
# ==========================================
tab1, tab2 = st.tabs(["📊 Đánh giá Rủi ro", "🤖 Trợ lý AI"])

# --- TAB 1: CÔNG CỤ ĐÁNH GIÁ ---
with tab1:
    st.header("Chẩn đoán Nguy cơ Bảo mật")
    
    with st.form("risk_assessment_form"):
        st.subheader("🛡️ Danh tính & Thiết bị")
        col1, col2 = st.columns(2)
        with col1:
            age = st.selectbox("Độ tuổi", ["Dưới 15", "15 - 18", "19 - 25", "Trên 25"])
            pw = st.radio("Cấu trúc mật khẩu thường dùng:", 
                         ["Chỉ chữ/số đơn giản", "Kết hợp chữ và số", "Phức tạp (Chữ hoa, số, ký tự đặc biệt)"])
        with col2:
            update = st.radio("Cập nhật phần mềm:", 
                             ["Khi có lỗi mới làm", "Thỉnh thoảng", "Ngay khi có thông báo"])

        st.divider()
        st.subheader("🌐 Môi trường mạng & Hành vi")
        col3, col4 = st.columns(2)
        with col3:
            two_fa = st.radio("Sử dụng xác thực 2 lớp (2FA):", 
                             ["Không bao giờ", "Chỉ một số ít", "Cho tất cả tài khoản"])
            phish = st.radio("Phản ứng với đường link lạ:", 
                            ["Click xem thử", "Xóa nhưng vẫn tò mò", "Báo cáo và chặn ngay"])
        with col4:
            wifi = st.radio("Wi-Fi công cộng:", 
                           ["Dùng mọi lúc", "Chỉ lướt web giải trí", "Luôn dùng VPN/4G"])
            piracy = st.radio("Sử dụng phần mềm lậu/bẻ khóa:", 
                             ["Thường xuyên", "Thỉnh thoảng", "Tuyệt đối không"])

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("TIẾN HÀNH PHÂN TÍCH")
        
        if submitted:
            # Thuật toán tính điểm trọng số
            score = 100
            if pw == "Phức tạp (Chữ hoa, số, ký tự đặc biệt)": score -= 15
            elif pw == "Kết hợp chữ và số": score -= 5
            if update == "Ngay khi có thông báo": score -= 10
            if two_fa == "Cho tất cả tài khoản": score -= 25
            elif two_fa == "Chỉ một số ít": score -= 10
            if phish == "Báo cáo và chặn ngay": score -= 15
            if wifi == "Luôn dùng VPN/4G": score -= 20
            elif wifi == "Chỉ lướt web giải trí": score -= 10
            if piracy == "Tuyệt đối không": score -= 15
            
            risk_score = max(0, min(100, score))
            
            st.markdown(f"### Chỉ số rủi ro: `{risk_score}/100`")
            st.progress(risk_score / 100)
            
            if risk_score > 60: st.error("🚨 Mức độ rủi ro: **NGUY HIỂM**")
            elif risk_score > 30: st.warning("⚠️ Mức độ rủi ro: **TRUNG BÌNH**")
            else: st.success("✅ Mức độ rủi ro: **AN TOÀN**")
            
            if supabase:
                try: supabase.table('survey_results').insert({"age_group": age, "risk_score": risk_score}).execute()
                except: pass

# --- TAB 2: CHATBOT AI ---
with tab2:
    st.header("Trợ lý An ninh mạng")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Gửi câu hỏi cho chuyên gia..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Bạn là chuyên gia an ninh mạng cấp cao. Trả lời bằng tiếng Việt chuyên nghiệp, học thuật."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3, stream=True,
                )
                full_response = st.write_stream(chunk.choices[0].delta.content for chunk in stream if chunk.choices[0].delta.content)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error("Hệ thống đang bận. Vui lòng thử lại sau.")
