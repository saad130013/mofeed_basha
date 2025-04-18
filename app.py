import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import requests
import os
from langchain.llms import LlamaCpp
from langchain.chains import load_qa_chain
from langchain.docstore.document import Document

# إعدادات التطبيق
st.set_page_config(
    page_title="مفيد باشا - مساعدك الذكي",
    layout="wide",
    page_icon="🤖",
    menu_items={"About": "تم التطوير بواسطة فريق مفيد باشا"}
)

# إعدادات النموذج (بدون ملف config.yml)
MODEL_CONFIG = {
    "url": "https://drive.usercontent.google.com/download?id=11ARnFAX2I6a-OSSOTtPqvaP41qwe4UHw&export=download",
    "path": "model.bin",
    "settings": {
        "temperature": 0.1,
        "max_tokens": 512,
        "n_ctx": 2048,
        "verbose": False
    }
}

# ─── وظائف أساسية ─────────────────────────────────────────────────
def download_model():
    """تنزيل النموذج من Google Drive"""
    if not os.path.exists(MODEL_CONFIG["path"]):
        with st.spinner("🔄 جاري تحميل النموذج..."):
            try:
                response = requests.get(MODEL_CONFIG["url"], stream=True)
                with open(MODEL_CONFIG["path"], "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            except Exception as e:
                st.error(f"❌ فشل في التحميل: {e}")
                st.stop()

def process_file(uploaded_file):
    """معالجة الملفات المرفوعة"""
    if uploaded_file.type == "application/pdf":
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            return "\n".join([page.get_text() for page in doc])
    else:
        df = pd.read_excel(uploaded_file)
        return df.to_string()

# ─── واجهة المستخدم ───────────────────────────────────────────────
st.title("🤖 مفيد باشا - مساعدك الذكي")
uploaded_file = st.file_uploader("📁 ارفع ملف PDF أو Excel", type=["pdf", "xlsx"])

if uploaded_file:
    text_data = process_file(uploaded_file)
    st.subheader("📄 المحتوى المستخرج")
    st.text_area("النص", text_data, height=250)

    if st.text_input("💬 اكتب سؤالك:"):
        download_model()  # تأكيد وجود النموذج
        
        llm = LlamaCpp(
            model_path=MODEL_CONFIG["path"],
            **MODEL_CONFIG["settings"]
        )
        
        chain = load_qa_chain(llm, chain_type="stuff")
        docs = [Document(page_content=text_data)]
        
        try:
            answer = chain.run(input_documents=docs, question=st.session_state.question)
            st.subheader("✅ الإجابة:")
            st.write(answer)
        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
else:
    st.info("👆 الرجاء رفع ملف لبدء التحليل")
