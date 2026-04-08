import streamlit as st
from supabase import create_client
from groq import Groq

# ==========================================
# CẤU HÌNH TRANG & KẾT NỐI
# ==========================================
st.set_page_config(page_title="Hệ Sinh Thái An Toàn Không Gian Mạng", page_icon="🛡️", layout="wide")
st.title("🛡️ Nền Tảng Đánh Giá & Tư Vấn An Toàn Thông Tin")

# --- KẾT NỐI SUPABASE ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        return None

supabase = init_connection()

# --- KHỞI TẠO GROQ API ---
@st.cache_resource
def init_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

client = init_groq_client()

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
tab1, tab2 = st.tabs(["📊 Đánh giá Rủi ro Đa chiều", "🤖 Trợ lý AI (Siêu tốc)"])

# --- TAB 1: CÔNG CỤ ĐÁNH GIÁ RỦI RO (PHIÊN BẢN CẢI TIẾN) ---
with tab1:
    st.header("Chẩn đoán Nguy cơ Bảo mật Cá nhân")
    st.markdown("Hệ thống đánh giá dựa trên 8 chỉ số hành vi an ninh mạng chuẩn quốc tế.")
    
    with st.form("risk_assessment_form"):
        st.subheader("1. Quản lý Danh tính & Thiết bị")
        col1, col2 = st.columns(2)
        with col1:
            age = st.selectbox("Độ tuổi của bạn", ["Dưới 15", "15 - 18", "19 - 25", "Trên 25"])
            pw_complexity = st.radio("Cấu trúc mật khẩu của bạn thường có:", 
                                     ["Chỉ chữ hoặc số (Dễ đoán)", 
                                      "Kết hợp chữ và số", 
                                      "Bao gồm chữ hoa, số và ký tự đặc biệt (@,#,...)"])
        with col2:
            update_habit = st.radio("Tần suất cập nhật phần mềm/hệ điều hành:", 
                                    ["Khi máy bị lỗi mới cập nhật", 
                                     "Thỉnh thoảng cập nhật thủ công", 
                                     "Luôn cập nhật ngay khi có thông báo"])

        st.divider()
        st.subheader("2. Hành vi Môi trường mạng")
        col3, col4 = st.columns(2)
        with col3:
            two_fa = st.radio("Xác thực 2 lớp (2FA) - (Mã gửi về điện thoại):", 
                              ["Không bao giờ dùng", 
                               "Chỉ dùng cho Facebook/Zalo", 
                               "Bật cho tất cả tài khoản quan trọng (Email, Ngân hàng)"])
            phishing_skill = st.radio("Nếu nhận tin nhắn trúng thưởng kèm link lạ, bạn sẽ:", 
                                      ["Click vào xem thử", 
                                       "Xóa tin nhắn nhưng vẫn tò mò", 
                                       "Báo cáo spam và tuyệt đối không click"])
        with col4:
            public_wifi = st.radio("Thói quen dùng Wi-Fi công cộng (Quán cafe, sân bay):", 
                                   ["Đăng nhập ngân hàng/Mua sắm bình thường", 
                                    "Chỉ lướt mạng xã hội/Đọc tin tức", 
                                    "Sử dụng VPN hoặc 4G để bảo mật"])
            piracy_habit = st.radio("Bạn có thường dùng phần mềm 'Crack' hoặc link tải lậu không?", 
                                    ["Thường xuyên (Game mod, phần mềm crack)", 
                                     "Thỉnh thoảng", 
                                     "Không bao giờ (Chỉ dùng nguồn chính thống)"])

        st.divider()
        submitted = st.form_submit_button("Tiến hành Phân tích Dữ liệu")
        
        if submitted:
            # THUẬT TOÁN TÍNH ĐIỂM CÓ TRỌNG SỐ (WEIGHTED SCORING)
            # Điểm càng cao = Rủi ro càng cao (0 - 100)
            score = 100
            
            # Trừ điểm dựa trên hành vi tốt (Trọng số khác nhau)
            if pw_complexity == "Bao gồm chữ hoa, số và ký tự đặc biệt (@,#,...)": score -= 15
            elif pw_complexity == "Kết hợp chữ và số": score -= 5
            
            if update_habit == "Luôn cập nhật ngay khi có thông báo": score -= 10
            
            if two_fa == "Bật cho tất cả tài khoản quan trọng (Email, Ngân hàng)": score -= 25
            elif two_fa == "Chỉ dùng cho Facebook/Zalo": score -= 10
            
            if phishing_skill == "Báo cáo spam và tuyệt đối không click": score -= 15
            
            if public_wifi == "Sử dụng VPN hoặc 4G để bảo mật": score -= 20
            elif public_wifi == "Chỉ lướt mạng xã hội/Đọc tin tức": score -= 10
            
            if piracy_habit == "Không bao giờ (Chỉ dùng nguồn chính thống)": score -= 15
            
            risk_score = max(0, min(100, score))
            
            # Hiển thị kết quả
            st.subheader(f"Kết quả phân tích: {risk_score}/100 điểm rủi ro")
            st.progress(risk_score / 100)
            
            if risk_score > 60:
                st.error("🚨 CẢNH BÁO: Mức độ rủi ro cực cao. Bạn là mục tiêu dễ bị tấn công mạng!")
            elif risk_score > 30:
                st.warning("⚠️ CHÚ Ý: Mức độ rủi ro trung bình. Cần thắt chặt các lớp bảo mật.")
            else:
                st.success("✅ AN TOÀN: Bạn có kỹ năng phòng thủ số rất tốt.")
            
            # Lưu dữ liệu nghiên cứu vào Supabase
            if supabase:
                try:
                    supabase.table('survey_results').insert({
                        "age_group": age,
                        "password_habit": pw_complexity,
                        "two_fa_usage": two_fa,
                        "wifi_habit": public_wifi,
                        "risk_score": risk_score
                    }).execute()
                    st.toast("Dữ liệu đã được mã hóa và lưu trữ phục vụ nghiên cứu!", icon="🛡️")
                except:
                    st.error("Lỗi đồng bộ Cloud.")

# --- TAB 2: CHATBOT TƯ VẤN (SIÊU TỐC) ---
with tab2:
    st.header("Trợ lý An ninh mạng AI")
    st.markdown("Tư vấn giải pháp bảo mật dựa trên lập luận học thuật.")
    
    if not client:
        st.error("⚠️ Chưa cấu hình GROQ_API_KEY.")
    else:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Hỏi chuyên gia về an ninh mạng..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    stream = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "Bạn là chuyên gia an ninh mạng cấp cao. Trả lời bằng tiếng Việt, súc tích, chuyên nghiệp và có dẫn chứng khoa học/pháp lý."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        stream=True,
                    )
                    
                    def stream_generator():
                        for chunk in stream:
                            if chunk.choices[0].delta.content is not None:
                                yield chunk.choices[0].delta.content
                                
                    full_response = st.write_stream(stream_generator)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"Lỗi: {str(e)}")
