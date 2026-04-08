import streamlit as st
from supabase import create_client
import google.generativeai as genai

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

# --- KHỞI TẠO AI MODEL (TỐI ƯU HÓA BẰNG CACHE) ---
# Điểm mấu chốt để tốc độ trở nên siêu tốc nằm ở đây
@st.cache_resource
def init_ai_model():
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        return None
        
    genai.configure(api_key=api_key)
    try:
        # Ưu tiên 1: Quét tìm Flash (Chỉ chạy 1 lần duy nhất)
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and 'flash' in m.name.lower():
                return genai.GenerativeModel(m.name)
                
        # Ưu tiên 2: Dự phòng
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
    except Exception as e:
        return None

model = init_ai_model()


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
        st.error("⚠️ Lỗi cấu hình API. Vui lòng kiểm tra lại GOOGLE_API_KEY hoặc hệ thống Google đang bảo trì.")
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
                    
                    response = model.generate_content(expert_prompt, stream=True)
                    
                    def stream_generator():
                        for chunk in response:
                            yield chunk.text
                            
                    full_response = st.write_stream(stream_generator)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                except Exception as e:
                    st.error(f"Hệ thống đang bảo trì: Quota bị vượt hoặc lỗi mạng. {str(e)}")
