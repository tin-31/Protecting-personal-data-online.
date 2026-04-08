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

# --- KHỞI TẠO GROQ API (TỐC ĐỘ LPU SIÊU TỐC) ---
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
tab1, tab2 = st.tabs(["📊 Đánh giá Rủi ro", "🤖 Trợ lý AI (Tốc độ ánh sáng)"])

# --- TAB 1: CÔNG CỤ ĐÁNH GIÁ RỦI RO ---
with tab1:
    st.header("Kiểm tra mức độ an toàn tài khoản của bạn")
    st.markdown("Bài test này giúp đánh giá nguy cơ rò rỉ dữ liệu cá nhân dựa trên thói quen sử dụng internet.")
    
    with st.form("risk_assessment_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.selectbox("Độ tuổi của bạn", ["Dưới 15", "15 - 18", "19 - 25", "Trên 25"])
            pw_habit = st.radio("Thói quen đặt mật khẩu:", 
                                ["Dùng 1 mật khẩu cho mọi tài khoản", 
                                 "Có đổi nhưng vẫn dùng tên/ngày sinh", 
                                 "Mật khẩu ngẫu nhiên, khác nhau cho từng web"])
        with col2:
            two_fa = st.radio("Bạn có sử dụng xác thực 2 bước (2FA) không?", ["Không bao giờ", "Chỉ vài tài khoản quan trọng", "Luôn luôn"])
            public_wifi = st.radio("Khi dùng Wi-Fi quán cafe, bạn thường:", 
                                   ["Đăng nhập ngân hàng, mua sắm", 
                                    "Chỉ lướt web đọc tin tức", 
                                    "Sử dụng VPN để bảo mật"])
        
        submitted = st.form_submit_button("Chẩn đoán Rủi ro")
        
        if submitted:
            risk_score = 100
            if pw_habit == "Mật khẩu ngẫu nhiên, khác nhau cho từng web": risk_score -= 30
            elif pw_habit == "Có đổi nhưng vẫn dùng tên/ngày sinh": risk_score -= 10
            
            if two_fa == "Luôn luôn": risk_score -= 40
            elif two_fa == "Chỉ vài tài khoản quan trọng": risk_score -= 15
            
            if public_wifi == "Sử dụng VPN để bảo mật": risk_score -= 30
            elif public_wifi == "Chỉ lướt web đọc tin tức": risk_score -= 10
            
            risk_score = max(0, min(100, risk_score))
            
            st.progress(risk_score / 100)
            if risk_score > 60:
                st.error(f"🚨 Nguy cơ cao: {risk_score}% - Bạn đang đối mặt với rủi ro rò rỉ dữ liệu lớn!")
            elif risk_score > 30:
                st.warning(f"⚠️ Nguy cơ trung bình: {risk_score}% - Cần cải thiện thói quen bảo mật.")
            else:
                st.success(f"✅ An toàn: {risk_score}% - Bạn có kỹ năng bảo vệ dữ liệu rất tốt!")
            
            if supabase:
                try:
                    data, count = supabase.table('survey_results').insert({
                        "age_group": age,
                        "password_habit": pw_habit,
                        "two_fa_usage": two_fa,
                        "wifi_habit": public_wifi,
                        "risk_score": risk_score
                    }).execute()
                    st.toast("Đã lưu dữ liệu nghiên cứu ẩn danh thành công!", icon="✅")
                except Exception as e:
                    st.error("Lỗi kết nối cơ sở dữ liệu. Kết quả chỉ hiển thị cục bộ.")

# --- TAB 2: CHATBOT TƯ VẤN (GROQ API + LLAMA 3) ---
with tab2:
    st.header("Trợ lý An ninh mạng AI")
    st.markdown("Hệ thống kết nối trực tiếp với chip xử lý LPU của Groq, mang lại tốc độ phản hồi tính bằng mili-giây.")
    
    if not client:
        st.error("⚠️ Lỗi cấu hình API. Vui lòng kiểm tra lại GROQ_API_KEY trong Secrets.")
    else:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Nhập câu hỏi của bạn về an toàn thông tin..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    # Gọi API của Groq với mô hình Llama 3 70B siêu mạnh
                    stream = client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=[
                            {"role": "system", "content": "Bạn là một chuyên gia an ninh mạng. Trả lời ngắn gọn, lập luận chặt chẽ, học thuật và dựa trên bối cảnh pháp luật Việt Nam. Viết hoàn toàn bằng tiếng Việt."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.2,
                        stream=True,
                    )
                    
                    # Hàm bóc tách dữ liệu Stream từ Groq
                    def stream_generator():
                        for chunk in stream:
                            if chunk.choices[0].delta.content is not None:
                                yield chunk.choices[0].delta.content
                                
                    full_response = st.write_stream(stream_generator)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                except Exception as e:
                    st.error(f"⚠️ Hệ thống đang bảo trì: {str(e)}")
