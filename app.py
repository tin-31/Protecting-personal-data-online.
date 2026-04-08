import streamlit as st
from supabase import create_client

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ Sinh Thái An Toàn Không Gian Mạng", page_icon="🛡️", layout="wide")
st.title("🛡️ Nền Tảng Đánh Giá & Tư Vấn An Toàn Thông Tin")

# --- KẾT NỐI SUPABASE (CƠ SỞ DỮ LIỆU) ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        return None

supabase = init_connection()

# --- TẠO CÁC TAB CHỨC NĂNG ---
# Đã lược bỏ Tab 3 để tập trung hiệu năng cho hệ thống lõi
tab1, tab2 = st.tabs(["📊 Đánh giá Rủi ro", "🤖 Chatbot Tư vấn RAG (Tốc độ cao)"])

# ==========================================
# TAB 1: CÔNG CỤ ĐÁNH GIÁ RỦI RO (RISK ASSESSMENT)
# ==========================================
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
            # Thuật toán chấm điểm rủi ro cơ bản
            risk_score = 100
            if pw_habit == "Mật khẩu ngẫu nhiên, khác nhau cho từng web": risk_score -= 30
            elif pw_habit == "Có đổi nhưng vẫn dùng tên/ngày sinh": risk_score -= 10
            
            if two_fa == "Luôn luôn": risk_score -= 40
            elif two_fa == "Chỉ vài tài khoản quan trọng": risk_score -= 15
            
            if public_wifi == "Sử dụng VPN để bảo mật": risk_score -= 30
            elif public_wifi == "Chỉ lướt web đọc tin tức": risk_score -= 10
            
            # Đảm bảo điểm nằm trong khoảng 0-100
            risk_score = max(0, min(100, risk_score))
            
            st.progress(risk_score / 100)
            if risk_score > 60:
                st.error(f"🚨 Nguy cơ cao: {risk_score}% - Bạn đang đối mặt với rủi ro rò rỉ dữ liệu lớn!")
            elif risk_score > 30:
                st.warning(f"⚠️ Nguy cơ trung bình: {risk_score}% - Cần cải thiện thói quen bảo mật.")
            else:
                st.success(f"✅ An toàn: {risk_score}% - Bạn có kỹ năng bảo vệ dữ liệu rất tốt!")
            
            # Gửi dữ liệu lên Supabase để làm Data nghiên cứu
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
            else:
                st.info("Chưa cấu hình Supabase API Key. Dữ liệu không được lưu trữ.")


# ==========================================
# TAB 2: CHATBOT TƯ VẤN (RAG TỐC ĐỘ CAO - STREAMING)
# ==========================================
with tab2:
    st.header("Trợ lý An ninh mạng AI")
    st.markdown("Bot được huấn luyện trên dữ liệu Luật An ninh mạng và các kết quả nghiên cứu độc quyền. **Tốc độ phản hồi đã được tối ưu hóa.**")
    
    # Khởi tạo lịch sử chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Hiển thị lịch sử
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Xử lý input người dùng
    if prompt := st.chat_input("Nhập câu hỏi của bạn về an toàn thông tin..."):
        # Thêm câu hỏi vào UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                
                api_key = st.secrets.get("GOOGLE_API_KEY")
                if not api_key:
                    st.warning("⚠️ Hệ thống Chatbot đang tạm ngưng do chưa cấu hình GOOGLE_API_KEY trong Streamlit Secrets.")
                    st.stop()
                    
                # Khởi tạo mô hình
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=api_key)
                
                # Ép khuôn chuyên gia bảo mật
                expert_prompt = f"Bạn là một chuyên gia an ninh mạng. Hãy trả lời ngắn gọn, học thuật và chính xác câu hỏi sau dựa trên bối cảnh tại Việt Nam: {prompt}"
                
                # Áp dụng cơ chế Streaming (Gõ từng chữ)
                response_stream = llm.stream(expert_prompt)
                
                # Streamlit 1.31+ hỗ trợ write_stream giúp hiển thị mượt mà
                full_response = st.write_stream(chunk.content for chunk in response_stream)
                
                # Lưu lại toàn bộ câu trả lời vào lịch sử session
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Hệ thống đang bảo trì: {str(e)}")
