"""
CLI / Streamlit-ready quiz generator for PDF(s)
"""
import argparse
import json
import random
import os
from typing import List, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain.schema import Document

# NOTE: relative import so it works both CLI and Streamlit
from .utils import load_and_split_pdfs, get_or_create_vectorstore

# --------------------------------------------------
# Prompt template (French, strict JSON)
# --------------------------------------------------
PROMPT = PromptTemplate(
    input_variables=["context", "k"],
    template="""
Tu es un générateur de quiz en français.
Renvoie UNIQUEMENT du JSON valide, sans commentaire.

Crée exactement {k} questions à choix multiples répondables uniquement d’après le texte ci-dessous.

Chaque objet doit avoir les clés exactes :
{{
  "question": "...",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "answer": "A"
}}

Texte :
{context}

JSON :
"""
)

# --------------------------------------------------
# Core generation logic
# --------------------------------------------------
def generate_questions(
    vectorstore,
    num_questions: int,
    questions_per_call: int = 3
) -> List[Dict]:
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-1.5-flash-8b",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.0,
        response_mime_type="application/json",
        transport="rest",
    )

    chain = PROMPT | llm | JsonOutputParser()

    all_chunks = vectorstore.similarity_search(" ", k=500)
    random.shuffle(all_chunks)

    questions = []
    for i in range(0, num_questions, questions_per_call):
        ctx_docs = all_chunks[i*2 : (i+1)*2]   # small window so text is never empty
        context = "\n\n".join([c.page_content for c in ctx_docs])
        try:
                raw = chain.invoke({"context": context,
                                    "k": min(questions_per_call, num_questions - len(questions))})

                # Accept dict or list
                if isinstance(raw, dict):
                    raw = [raw]
                if not isinstance(raw, list):
                    continue

                # Keep only objects that have the 3 required keys
                for item in raw:
                    if all(k in item for k in ("question", "options", "answer")):
                        questions.append(item)
        except Exception as e:
                print("⚠️ Skipping malformed batch:", e)

    return questions


# --------------------------------------------------
# CLI entry-point (optional)
# --------------------------------------------------
def run_quiz_cli(questions: List[Dict]) -> None:
    score = 0
    for idx, q in enumerate(questions, 1):
        print(f"\nQ{idx}) {q['question']}")
        for opt in q["options"]:
            print("   ", opt)
        choice = input("Your choice (A/B/C/D): ").strip().upper()
        if choice == q["answer"]:
            print("✅ Correct!")
            score += 1
        else:
            print(f"❌ Wrong. Correct: {q['answer']}")
    print(f"\nFinal score: {score}/{len(questions)}")


def main_cli():
    import argparse
    parser = argparse.ArgumentParser(description="Generate a quiz from PDFs.")
    parser.add_argument("pdf_dir", help="Directory containing PDF files")
    parser.add_argument("-n", "--num", type=int, default=10, help="Number of questions")
    args = parser.parse_args()

    chunks = load_and_split_pdfs(args.pdf_dir)
    vs = get_or_create_vectorstore(chunks)
    questions = generate_questions(vs, args.num)

    if not questions:
        print("❌ No questions generated.")
        return

    run_quiz_cli(questions)


if __name__ == "__main__":
    main_cli()