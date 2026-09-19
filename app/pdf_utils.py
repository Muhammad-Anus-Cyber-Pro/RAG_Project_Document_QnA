from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_document(file_path: str):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    return docs

def splitting_docs(documents, chunk_size: int = 1500, chunk_overlap: int = 200) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    splitted_docs = splitter.split_documents(documents)
    return splitted_docs