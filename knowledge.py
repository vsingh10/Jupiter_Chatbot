import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def create_chunks(json_file_path, chunk_size = 1000, chunk_overlap = 200):
    with open(json_file_path, "r", encoding = "utf-8") as f:
        data = json.load(f)

    langchain_doc = []

    for i, entry in enumerate(data):
        doc = Document(
            page_content = entry['text'],
            metadata = entry['metadata']
        )
        langchain_doc.append(doc)

    print(f"Total entries loaded: {len(langchain_doc)}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        length_function = len,
        add_start_index = True
    ) 

    chunks = text_splitter.split_documents(langchain_doc)

    return chunks   


data_chunks = create_chunks("dataset/cleaned_data.json")
print(f"Total chunks created: {len(data_chunks)}")


def embedding_model():
    emb_model = HuggingFaceEmbeddings(model_name = 'sentence-transformers/all-mpnet-base-v2')
    return emb_model

embed_model = embedding_model()


DB_FAISS_PATH = "knowledge_base/db_faiss"

db = FAISS.from_documents(
    data_chunks,
    embed_model
)

db.save_local(DB_FAISS_PATH)
