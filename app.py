import streamlit as st
import pandas as pd
import pdfplumber
from transformers import pipeline

# تهيئة التطبيق
st.set_page_config(
    page_title="مساعدك الذكي - النسخة المجانية",
    layout="wide",
    page_icon="🤖"
)

# تحميل نموذج خفيف الوزن من Hugging Face
@st.cache_resource
def load_ai_model():
    return pipeline(
        "question-answering",
        model="mrm8488/bert-tiny-5-finetuned-squadv2"  # نموذج صغير بحجم 15MB فقط
    )

# ─── وظائف معالجة الملفات ───────────────────────────────────
def extract_text(uploaded_file):
    """استخراج النص من PDF أو Excel"""
    try:
        if uploaded_file.type == "application/pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                return "\n".join([page.extract_text() for page in pdf.pages])
        else:
            df = pd.read_excel(uploaded_file)
            return df.to_string()
    except Exception as e:
        st.error(f"خطأ في معالجة الملف: {str(e)}")
        return None

# ─── واجهة المستخدم ─────────────────────────────────────────
st.title("🤖 مساعدك الذكي - النسخة المجانية")
uploaded_file = st.file_uploader("ارفع ملف PDF أو Excel", type=["pdf", "xlsx"])

if uploaded_file:
    extracted_text = extract_text(uploaded_file)
    
    if extracted_text:
        st.subheader("📄 المحتوى المستخرج")
        st.text_area("النص", extracted_text, height=250)
        
        question = st.text_input("💬 اكتب سؤالك هنا:")
        
        if question:
            qa_model = load_ai_model()
            with st.spinner("جاري البحث عن الإجابة..."):
                try:
                    answer = qa_model(question=question, context=extracted_text)
                    st.subheader("✅ الإجابة:")
                    st.markdown(f"**{answer['answer']}** (الثقة: {answer['score']:.2f})")
                except Exception as e:
                    st.error(f"فشل في الحصول على الإجابة: {str(e)}")
else:
    st.info("👋 الرجاء رفع ملف لبدء التحليل.")
