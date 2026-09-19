from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
parser = StrOutputParser()

QA_PROMPT = PromptTemplate(
    template="""
    Answer the question using ONLY the context below. 
    If the answer isn't in the context, say you don't know.\n\n
    Context:\n{context}\n\n
    Question: {question}\n\n
    Answer:
    """,
    input_variables = ['context','question']
)

def build_vectorstore(chunks: list[str]) -> FAISS:

    vectorstore = FAISS.from_documents(documents=chunks,embedding=embeddings)
    return vectorstore

def answer_question(vectorstore: FAISS, question: str, k: int = 3) -> str:

    relevant_docs = vectorstore.similarity_search(question,k=k)
    context = "\n\n".join(doc.page_content for doc in relevant_docs)

    chain = QA_PROMPT | llm | parser
    result = chain.invoke({"context":context,"question":question})
    return result
