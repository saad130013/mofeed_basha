
# مفيد باشا - مساعد الذكاء الصناعي للعمل
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from langchain.llms import LlamaCpp
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document

st.set_page_config(page_title="مفيد باشا - مساعدك الذكي في العمل", layout="wide")

st.title("🤖 مفيد باشا - مساعدك الذكي في العمل")
st.markdown("مرحبا بك! ارفع ملف **PDF** أو **Excel** وسأقوم بتحليل المحتوى، الإجابة على أسئلتك، وتوليد تقرير لك باستخدام نموذج ذكاء صناعي يعمل محليًا.")

uploaded_file = st.file_uploader("📂 ارفع الملف هنا", type=["pdf", "xlsx", "xls"])
text = ""
df = None

if uploaded_file:
    file_type = uploaded_file.type
    st.success(f"✅ تم رفع الملف: {uploaded_file.name}")

    if file_type == "application/pdf":
        with st.spinner("📖 جاري قراءة ملف PDF..."):
            pdf_reader = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            for page in pdf_reader:
                text += page.get_text()
            st.subheader("📄 محتوى الملف:")
            st.text_area("نص مستخرج من PDF", text, height=300)

    elif file_type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
        with st.spinner("📊 جاري قراءة ملف Excel..."):
            df = pd.read_excel(uploaded_file)
            text = df.to_string()
            st.subheader("📋 بيانات Excel:")
            st.dataframe(df)

    st.subheader("❓ اسأل مفيد باشا عن محتوى الملف")
    question = st.text_input("🗨️ اكتب سؤالك هنا:")

    if question and text:
        with st.spinner("🤔 مفيد باشا يفكر..."):
            llm = LlamaCpp(
                model_path="./models/ggml-model-q4_0.bin",
                temperature=0.1,
                max_tokens=512,
                top_p=0.95,
                n_ctx=2048,
                verbose=False
            )
            chain = load_qa_chain(llm, chain_type="stuff")
            docs = [Document(page_content=text)]
            answer = chain.run(input_documents=docs, question=question)
            st.success("✅ الإجابة:")
            st.write(answer)
else:
    st.warning("🔺 الرجاء رفع ملف PDF أو Excel للبدء")
