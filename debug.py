import os, json
from src.utils import load_and_split_pdfs, get_or_create_vectorstore
from src.quiz import PROMPT   # use the same prompt
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough

pdf_dir = "documents"
chunks  = load_and_split_pdfs(pdf_dir)
vs      = get_or_create_vectorstore(chunks)

llm   = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.0,
    response_mime_type="application/json",
    transport="rest",
)

chain = PROMPT | llm | JsonOutputParser()

ctx = "\n\n".join([c.page_content for c in chunks[:2]])
print("----- CONTEXT GIVEN TO GEMINI -----")
print(ctx[:500] + " …" if len(ctx) > 500 else ctx)
print("-----------------------------------")

try:
    raw = chain.invoke({"context": ctx, "k": 1})
    print("----- RAW GEMINI RESPONSE -----")
    print(json.dumps(raw, ensure_ascii=False, indent=2))
except Exception as e:
    print("❌ LLM error:", e)