# مفيد باشا – مساعد الذكاء الصناعي للعمل

🤖 تطبيق Streamlit لتحليل ملفات PDF وExcel باستخدام نموذج ذكاء صناعي يعمل محليًا عبر `llama-cpp-python`.

## المميزات
- دعم ملفات PDF وExcel
- تحليل المحتوى والإجابة على الأسئلة
- لا حاجة لاتصال إنترنت أو OpenAI API

## الاستخدام

```bash
pip install -r requirements.txt
streamlit run app.py
```

## تحميل النموذج
قم بتحميل نموذج مثل:
https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF

واختر ملف: `ggml-model-q4_0.bin` وضعه بجانب app.py
