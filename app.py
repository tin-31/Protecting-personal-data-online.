import streamlit as st
from supabase import create_client
import google.generativeai as genai

# ==========================================
# CẤU HÌNH TRANG & KẾT NỐI
# ==========================================
st.set_page_config(page_title="Hệ Sinh Thái An Toàn Không Gian Mạng", page_icon="🛡️", layout="wide")
st.title("🛡️ Nền Tảng Đánh Giá & Tư Vấn An Toàn Thông Tin")

@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        return None

supabase = init_connection()

# Khởi tạo API Google ngay từ đầu
api_key = st.secrets.get("GOOGLE_API_KEY")
model = None

if api_key:
    genai.configure(api_key=api_key)
    
    # CHIẾN THUẬT BULLETPROOF: Tự động quét và khóa mục tiêu (Model Scanner)
    try:
        # Ưu tiên 1: Quét tìm mô hình dòng 'Flash' để đảm bảo tốc độ tên lửa
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name.lower():
                    model = genai.GenerativeModel(m.name)
                    break
                    
        # Ưu tiên 2: Phương án dự phòng (Fallback) nếu tài khoản chưa được cấp Flash
        if model is None:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    model = genai.GenerativeModel(m.name)
                    break
    except Exception as e:
        st.error(f"Lỗi truy xuất danh sách mô hình từ Google: {e}")

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
tab1, tab2 = st.tabs(["📊 Đánh giá Rủi ro", "🤖 Trợ lý AI (Tốc độ tối đa)"])

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

# --- TAB 2: CHATBOT TƯ VẤN (NATIVE SDK + STREAM) ---
with tab2:
    st.header("Trợ lý An ninh mạng AI")
    st.markdown("Hệ thống kết nối trực tiếp (Point-to-Point) mang lại tốc độ phản hồi thời gian thực.")
    
    if not model:
        st.error("⚠️ Lỗi cấu hình API. Vui lòng kiểm tra lại GOOGLE_API_KEY trong Secrets.")
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
                    expert_prompt = f"Bạn là chuyên gia an ninh mạng. Trả lời ngắn gọn, học thuật dựa trên pháp luật Việt Nam: {prompt}"
                    
                    # Gọi API với cơ chế stream=True trực tiếp từ Google
                    response = model.generate_content(expert_prompt, stream=True)
                    
                    # Hàm generator để tương thích hoàn hảo với st.write_stream
                    def stream_generator():
                        for chunk in response:
                            yield chunk.text
                            
                    full_response = st.write_stream(stream_generator)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                except Exception as e:
                    st.error(f"Hệ thống đang bảo trì: {str(e)}")
