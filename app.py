import streamlit as st
import json
from src.utils import load_and_split_pdfs, get_or_create_vectorstore
from src.quiz import generate_questions   

st.set_page_config(page_title="PDF Quiz", page_icon="📝")
st.title("📝 QuizMaker from PDF")

pdf_dir = st.text_input("📁 Path to PDF folder", value="documents")
num_q = st.slider("Number of questions", 1, 20, 5)

if st.button("Generate Quiz"):
    with st.spinner("Loading PDFs & creating vectors…"):
        chunks = load_and_split_pdfs(pdf_dir)
        vs = get_or_create_vectorstore(chunks)
        questions = generate_questions(vs, num_q)

    st.session_state["questions"] = questions
    st.session_state["score"] = 0
    st.session_state["idx"] = 0

total = len(st.session_state.questions)
q = st.session_state.questions[st.session_state.idx]
st.subheader(f"Q{st.session_state.idx+1}) {q['question']}")

choice = st.radio("Choose", q["options"], index=None, key=f"q{st.session_state.idx}")

# checkk
if "answered" not in st.session_state:
    st.session_state.answered = False
    st.session_state.feedback = ""

if not st.session_state.answered:
    if st.button("Submit"):
        if choice is None:
            st.warning("Pick an answer first")
        else:
            idx_letter = "ABCD"[q["options"].index(choice)]
            st.session_state.answered = True
            if idx_letter == q["answer"]:
                st.session_state.feedback = "✅ Correct!"
                st.session_state.score += 1
            else:
                st.session_state.feedback = f"❌ Wrong – correct: **{q['answer']}**"
            st.rerun()

else:
    st.markdown(st.session_state.feedback)

    if st.button("Next ➡️"):
        st.session_state.answered = False
        st.session_state.feedback = ""
        if st.session_state.idx < total - 1:
            st.session_state.idx += 1
            st.rerun()
        else:
            st.balloons()
            pct = st.session_state.score / total
            if pct < 0.30:
                st.markdown(
                    "<h1 style='text-align:center; color:red;'>YOU ARE A LOSER 😭</h1>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"### 🎯 Final score: **{st.session_state.score}/{total}**",
                    unsafe_allow_html=True,
                )