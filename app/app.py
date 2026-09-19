from dotenv import load_dotenv

load_dotenv()
import streamlit as st
import requests
from time import sleep


API_URL = "http://127.0.0.1:8000"


if "vector_db" not in st.session_state:
    st.session_state.vector_db = None

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None


st.subheader("📃 Document Q & A ChatBot - Ask Anything")

if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False

### Document Uploaded
if not st.session_state.document_uploaded:
    file = st.file_uploader("Select your pdf file",type="pdf")
    if file:
        try:
            files = {"file":(file.name,file.getvalue(),"application/json")}
            response = requests.post(f"{API_URL}/upload", files=files)

            if response.status_code == 200:
                data = response.json()
                st.session_state.session_id = data['session_id']

                st.session_state.messages = []
                st.session_state.document_uploaded = True
                st.success("Document processed successfully!")
                st.rerun()
            else:
                st.error(response.json().get("detail","Something went wrong."))
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the FastAPI server."
                      "Make sure uvicorn is running.")


if st.session_state.document_uploaded:

    for oneMessage in st.session_state.messages:
        with st.chat_message(oneMessage["role"]):
            st.write(oneMessage["content"])

    query = st.chat_input("Ask Anything...")
    if query:

        st.session_state.messages.append({"role":"user","content":query})
        with st.chat_message("user"):
            st.write(query)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents..."):
                try:
                    payload = {"session_id":st.session_state.session_id, "question":query}
                    response = requests.post(f"{API_URL}/ask",json=payload)

                    if response.status_code == 200:
                        answer = response.json()["answer"]
                        st.write(answer)

                        # Save conversation
                        st.session_state.messages.append({
                            "role":"assistant",
                            "content":answer
                        })
                    else:
                        st.error(response.json().get("detail","Something went wrong."))

                except requests.exceptions.ConnectionError:
                    st.error(
                        "Could not connect to the FastAPI server."
                    )
