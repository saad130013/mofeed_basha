import streamlit as st
import pandas as pd
import pdfplumber
from transformers import pipeline

# إعدادات واجهة التطبيق
st.set_page_config(
    page_title="مساعدك الذكي - تحليل ملفات PDF وExcel",
    layout="wide",
    page_icon="🤖"
)

# تحميل النموذج بذكاء
@st.cache_resource
def load_model():
    return pipeline("question-answering", model="mrm8488/bert-tiny-5-finetuned-squadv2")

# دالة استخراج النص من PDF أو Excel
def extract_text(file):
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            return "\n".join([page.extract_text() or "" for page in pdf.pages])
    elif file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(file)
        return df.to_string()
    return ""

# واجهة المستخدم
st.title("🤖 مساعدك الذكي")
st.markdown("ارفع ملف **PDF أو Excel** واستخرج منه المعلومات واسأل عنه بكل سهولة باستخدام الذكاء الصناعي.")

uploaded_file = st.file_uploader("📂 ارفع الملف هنا", type=["pdf", "xlsx"])

if uploaded_file:
    with st.spinner("📄 جاري معالجة الملف..."):
        text = extract_text(uploaded_file)

    if text.strip():
        st.subheader("📄 المحتوى المستخرج")
        st.text_area("النص:", text, height=250, label_visibility="collapsed")

        question = st.text_input("💬 اسأل عن المحتوى:")
        if question:
            with st.spinner("🤔 جاري توليد الإجابة..."):
                qa_pipeline = load_model()
                answer = qa_pipeline(question=question, context=text)
                st.subheader("✅ الإجابة:")
                st.markdown(f"**{answer['answer']}** (الثقة: {answer['score']:.2f})")
    else:
        st.warning("لم يتم استخراج نص من الملف. تأكد أن الملف يحتوي على محتوى قابل للقراءة.")
else:
    st.info("👋 الرجاء رفع ملف PDF أو Excel لبدء التحليل.")