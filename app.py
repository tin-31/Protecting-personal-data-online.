import streamlit as st
from supabase import create_client, Client
from PIL import Image, ImageDraw, ImageFont
import io
import os

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
tab1, tab2, tab3 = st.tabs(["📊 Đánh giá Rủi ro", "🤖 Chatbot Tư vấn RAG", "🏆 Thử tài & Nhận Chứng chỉ"])

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
# TAB 2: CHATBOT TƯ VẤN (RAG VỚI GEMINI & FAISS)
# ==========================================
with tab2:
    st.header("Trợ lý An ninh mạng AI")
    st.markdown("Bot được huấn luyện trên dữ liệu Luật An ninh mạng và các kết quả nghiên cứu độc quyền.")
    
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
                # KIẾN TRÚC RAG MẪU (Sử dụng Google Gemini)
                import google.generativeai as genai
                from langchain_google_genai import ChatGoogleGenerativeAI
                
                api_key = st.secrets.get("GOOGLE_API_KEY")
                if not api_key:
                    st.warning("⚠️ Hệ thống Chatbot đang tạm ngưng do chưa cấu hình GOOGLE_API_KEY trong Streamlit Secrets.")
                    st.stop()
                    
                # Khởi tạo mô hình
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=api_key)
                
                # Trong thực tế, bạn sẽ chèn FAISS Retriever vào đây
                # retriever = vector_store.as_retriever()
                # answer = qa_chain.run(prompt)
                
                # Tạm thời gọi trực tiếp LLM với System Prompt ép khuôn chuyên gia
                expert_prompt = f"Bạn là một chuyên gia an ninh mạng. Hãy trả lời ngắn gọn, học thuật và chính xác câu hỏi sau dựa trên Luật pháp Việt Nam: {prompt}"
                response = llm.invoke(expert_prompt)
                
                st.markdown(response.content)
                st.session_state.messages.append({"role": "assistant", "content": response.content})
                
            except Exception as e:
                st.error(f"Hệ thống đang bảo trì: {str(e)}")


# ==========================================
# TAB 3: TRÒ CHƠI HÓA (GAMIFICATION) & CẤP CHỨNG CHỈ
# ==========================================
with tab3:
    st.header("Thử tài Nhận diện Phishing")
    st.markdown("Phân tích email sau đây và cho biết nó có an toàn không?")
    
    # Giả lập một bài test trực quan
    st.info("**Từ:** admin@facebook-security-update.com\n\n**Tiêu đề:** TÀI KHOẢN CỦA BẠN SẼ BỊ KHÓA TRONG 24H!\n\n**Nội dung:** Vui lòng click vào đường link sau để xác minh danh tính: http://bit.ly/fb-verify-998")
    
    test_answer = st.radio("Đánh giá của bạn:", ["Đây là email thật của Facebook", "Đây là email lừa đảo (Phishing)"])
    
    if st.button("Kiểm tra kết quả"):
        if test_answer == "Đây là email lừa đảo (Phishing)":
            st.success("🎉 Chính xác! Tên miền email sai lệch và link rút gọn là dấu hiệu của Phishing.")
            st.session_state['passed_test'] = True
        else:
            st.error("❌ Rất tiếc! Đây là email lừa đảo. Bạn không nên click vào các link rút gọn từ email lạ.")
            st.session_state['passed_test'] = False

    st.divider()
    
    # Cấp chứng chỉ nếu đã qua bài test
    if st.session_state.get('passed_test', False):
        st.subheader("🎓 Nhận Chứng Chỉ Công Dân Mạng An Toàn")
        user_name = st.text_input("Nhập Họ và Tên của bạn để in lên chứng chỉ:")
        
        if st.button("Tạo Chứng Chỉ"):
            if user_name:
                # Xử lý ảnh bằng Pillow
                # Lưu ý: Trong thực tế, bạn tải một ảnh phôi 'template.jpg' lên GitHub cùng file app.py
                # img = Image.open('template.jpg')
                
                # Tạm thời tạo một ảnh nền gradient cơ bản để demo code chạy được ngay
                img = Image.new('RGB', (800, 600), color = (10, 36, 99))
                draw = ImageDraw.Draw(img)
                
                # Lấy font mặc định (Hoặc tải font .ttf lên repo)
                # font = ImageFont.truetype("arial.ttf", 40)
                try:
                    font_title = ImageFont.truetype("arial.ttf", 45)
                    font_name = ImageFont.truetype("arial.ttf", 60)
                except IOError:
                    font_title = font_name = ImageFont.load_default()
                
                # Ghi chữ lên ảnh
                draw.text((150, 150), "CHỨNG NHẬN HOÀN THÀNH", fill=(255, 255, 255), font=font_title)
                draw.text((150, 250), user_name.upper(), fill=(255, 215, 0), font=font_name)
                draw.text((150, 400), "Đã hoàn thành xuất sắc bài kiểm tra An toàn Không gian mạng.", fill=(255, 255, 255))
                
                # Xuất ảnh ra bộ nhớ đệm để tải về
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.image(img, caption="Chứng chỉ của bạn")
                st.download_button(
                    label="Tải Chứng Chỉ Về Máy",
                    data=byte_im,
                    file_name="chung_chi_an_toan_mang.png",
                    mime="image/png"
                )
            else:
                st.warning("Vui lòng nhập tên của bạn!")
