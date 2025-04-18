# مفيد باشا - مساعد الذكاء الصناعي للعمل (الإصدار المطور)
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import yaml
from langchain.llms import LlamaCpp
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document

st.set_page_config(
    page_title="مفيد باشا - مساعدك الذكي في العمل",
    layout="wide",
    page_icon="🤖"
)

# تحميل الإعدادات
try:
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)
        MODEL_PATH = config["model"]["path"]
        MODEL_SETTINGS = config["model"]["settings"]
except Exception as e:
    st.error("❌ لم يتم العثور على ملف الإعدادات config.yml أو به مشكلة.")
    st.stop()

@st.cache_data
def read_pdf(file):
    max_file_size = 10 * 1024 * 1024
    if file.size > max_file_size:
        raise ValueError("حجم الملف كبير جداً (الحد الأقصى: 10MB)")
    pdf_reader = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in pdf_reader])

@st.cache_data
def read_excel(file):
    return pd.read_excel(file)

def initialize_model():
    try:
        return LlamaCpp(model_path=MODEL_PATH, **MODEL_SETTINGS)
    except FileNotFoundError:
        st.error("❌ نموذج الذكاء الصناعي غير موجود في المسار المحدد!")
        return None

st.title("🤖 مفيد باشا - مساعدك الذكي في العمل")
st.markdown("""
مرحبًا بك! ارفع ملف **PDF** أو **Excel** (بحد أقصى 10MB) وسأقوم بـ:
- تحليل المحتوى ⚙️
- الإجابة على أسئلتك ❓
- توليد تقارير مخصصة 📊
""")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("ما أهم النقاط في هذا الملف؟"):
        st.session_state.question = "لخص المحتوى في 5 نقاط رئيسية."
with col2:
    if st.button("ما الإحصائيات الأساسية؟"):
        st.session_state.question = "ما أبرز الإحصائيات في البيانات؟"
with col3:
    if st.button("ما التوصيات؟"):
        st.session_state.question = "ما التوصيات العملية بناءً على المحتوى؟"

uploaded_file = st.file_uploader(
    "📂 ارفع الملف هنا (PDF أو Excel)",
    type=["pdf", "xlsx", "xls"],
    help="الحد الأقصى لحجم الملف: 10MB"
)

text = ""
df = None

if uploaded_file:
    try:
        if uploaded_file.type == "application/pdf":
            with st.spinner("📖 جاري تحليل PDF..."):
                text = read_pdf(uploaded_file)
                st.subheader("📄 المحتوى المستخرج")
                st.text_area("النص", text, height=300, label_visibility="collapsed")

        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
            with st.spinner("📊 جاري تحليل Excel..."):
                df = read_excel(uploaded_file)
                st.subheader("📋 بيانات Excel")
                st.dataframe(df.head(10), use_container_width=True)
                text = df.to_string()

    except Exception as e:
        st.error(f"❌ خطأ في المعالجة: {str(e)}")

    st.divider()
    question = st.text_input(
        "🗨️ اكتب سؤالك هنا:",
        value=getattr(st.session_state, "question", ""),
        placeholder="مثال: ما أهم النتائج في هذا التقرير؟"
    )

    if question and text:
        with st.spinner("🤔 مفيد باشا يفكر بعمق..."):
            llm = initialize_model()
            if llm:
                try:
                    chain = load_qa_chain(llm, chain_type="stuff")
                    docs = [Document(page_content=text)]
                    answer = chain.run(input_documents=docs, question=question)
                    st.subheader("📝 الإجابة:")
                    st.markdown(f"```{answer}```")
                except Exception as e:
                    st.error(f"⚠️ فشل في توليد الإجابة: {str(e)}")
else:
    st.info("👆 ارفع ملف PDF أو Excel لبدء التحليل.")