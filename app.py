from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import InMemoryVectorStore
import streamlit as st
from time import sleep


## LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

if "vector_db" not in st.session_state:
    st.session_state.vector_db = None

if "messages" not in st.session_state:
    st.session_state.messages = []

def document_process(path):
    ## Document Loading
    loader = PyPDFLoader(path)
    docs = loader.load()

    ## Splitting
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    splitted_docs = splitter.split_documents(docs)

    ## Embeddings and Vector Store
    embedding_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
    vector_db = InMemoryVectorStore.from_documents(documents=splitted_docs,embedding=embedding_model)

    st.session_state.vector_db = vector_db
    st.session_state.document_uploaded = True

st.subheader("📃 Document Q & A ChatBot - Ask Anything")

if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False

### Document Uploaded
if not st.session_state.document_uploaded:
    file = st.file_uploader("Select your pdf file",type="pdf")
    if file:
        with open("uploaded_document.pdf","wb") as f:
            f.write(file.getvalue())

        with st.spinner("Processing..."):
            document_process("uploaded_document.pdf")

        st.markdown("Document Uploaded Succesfully")
        sleep(2)
        st.rerun()

if st.session_state.document_uploaded and st.session_state.vector_db:

    for oneMessage in st.session_state.messages:
        role = oneMessage["role"]
        content = oneMessage["content"]

        st.chat_message(role).markdown(content)

    query = st.chat_input("Ask Anything...")
    if query:

        st.session_state.messages.append({"role":"user","content":query})
        st.chat_message("user").markdown(query)
        documents = st.session_state.vector_db.similarity_search(query, k=2)
        context = "\n\n".join(doc.page_content for doc in documents)
        ## Prompt
        prompt = PromptTemplate(
            template="""
                You are a helpful assistant and provide answer based on the provided context.
                context:{context} , question:{query}
            """,
            input_variables=['context','query']
        )

        final_prompt = prompt.invoke({"context":context,"query":query})
        result = llm.invoke(final_prompt)

        st.session_state.messages.append({"role":"ai","content":result.content})
        st.chat_message("ai").markdown(result.content)

