# مفيد باشا - مساعد الذكاء الصناعي للعمل (نسخة للرفع على GitHub مع تحميل النموذج من Google Drive)
import streamlit as st
import pandas as pd
import fitz
import yaml
import requests
import os
from langchain.llms import LlamaCpp
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document

st.set_page_config(page_title="مفيد باشا - مساعدك الذكي في العمل", layout="wide", page_icon="🤖")

# تحميل النموذج من Google Drive
MODEL_FILENAME = "ggml-model-q4_0.bin"
MODEL_URL = "https://drive.google.com/uc?export=download&id=11ARnFAX2I6a-OSSOTtPqvaP41qwe4UHw"

def download_model():
    if not os.path.exists(MODEL_FILENAME):
        with st.spinner("🔄 جاري تحميل نموذج الذكاء الصناعي..."):
            try:
                response = requests.get(MODEL_URL, stream=True)
                with open(MODEL_FILENAME, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                st.success("✅ تم تحميل النموذج بنجاح!")
            except Exception as e:
                st.error(f"❌ فشل في تحميل النموذج: {e}")
                st.stop()

download_model()

# تحميل الإعدادات
try:
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)
        MODEL_PATH = config["model"]["path"]
        MODEL_SETTINGS = config["model"]["settings"]
except Exception as e:
    st.error("❌ لم يتم العثور على ملف config.yml أو به مشكلة.")
    st.stop()

@st.cache_data
def read_pdf(file):
    pdf_reader = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in pdf_reader])

@st.cache_data
def read_excel(file):
    return pd.read_excel(file)

def initialize_model():
    try:
        return LlamaCpp(model_path=MODEL_PATH, **MODEL_SETTINGS)
    except FileNotFoundError:
        st.error("❌ لم يتم العثور على ملف النموذج.")
        return None

st.title("🤖 مفيد باشا - مساعدك الذكي في العمل")
st.markdown("ارفع ملف PDF أو Excel وسأقوم بتحليله والإجابة على أسئلتك.")

uploaded_file = st.file_uploader("📂 ارفع الملف هنا", type=["pdf", "xlsx", "xls"])
text = ""
df = None

if uploaded_file:
    try:
        if uploaded_file.type == "application/pdf":
            text = read_pdf(uploaded_file)
            st.subheader("📄 النص المستخرج")
            st.text_area("النص", text, height=300)
        else:
            df = read_excel(uploaded_file)
            st.subheader("📋 جدول البيانات")
            st.dataframe(df.head())
            text = df.to_string()
    except Exception as e:
        st.error(f"❌ خطأ: {str(e)}")

    question = st.text_input("❓ اكتب سؤالك عن المحتوى:")
    if question and text:
        llm = initialize_model()
        if llm:
            try:
                chain = load_qa_chain(llm, chain_type="stuff")
                docs = [Document(page_content=text)]
                answer = chain.run(input_documents=docs, question=question)
                st.subheader("✅ الإجابة:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"⚠️ فشل في توليد الإجابة: {str(e)}")
else:
    st.info("👆 الرجاء رفع ملف لبدء التحليل.")