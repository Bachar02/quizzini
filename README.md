```markdown
# 📄 PDF Quizzer  
**Turn any PDF into an interactive quiz in seconds.**

---

## 🚀 Quick start
```bash
git clone https://github.com/<you>/pdf-quizzer.git
cd pdf-quizzer
pip install -r requirements.txt
streamlit run app.py
```
Navigate to the **Local URL** and you’re ready to quiz.

---


## 📂 How it works
1. Drop **any PDF** into `documents/`.  
2. Choose how many questions you want.  
3. Click **Generate Quiz**.  
4. Answer one-by-one, get instant feedback.  

---

## 🛠️ Tech stack
- **Streamlit** – slick web UI  
- **LangChain** – prompt & chain management  
- **Google Gemini 1.5-flash-8b** –  quiz generation  
- **Pinecone** – vector store for semantic retrieval  
- **RecursiveCharacterTextSplitter** – PDF chunking  

---

## 🔧 Environment
Create `.env` at the root:

```bash
PINECONE_API_KEY=your_pinecone_key
GEMINI_API_KEY=your_gemini_key
```

---

## 🧪 CLI alternative
```bash
python src/quiz.py documents/ -n 10
```

---

## 🤝 Contributions
Pull-requests welcome. Open an issue for bugs or ideas.


## 📸 Demo
Watch the 58-second clip below to see the flow:  
[Demo GIF / Video link](https://github.com/<you>/pdf-quizzer/blob/main/demo.gif)

---


```

