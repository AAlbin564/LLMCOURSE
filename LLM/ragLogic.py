from google import genai
from dotenv import load_dotenv
from langchain_community.document_loaders.pdf import PyPDFLoader
import pydantic
import os
import gradio as gr
from google.genai import types
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from sentence_transformers import SentenceTransformer
from langchain.schema import Document
import torch

 # chunk object
class chunkObject: 
    def __init__(self,chunk,title, url,index):
        self.chunk = chunk
        self.title = title 
        self.url = url
        self.index = index
        self.embedding = None
    def textExpose(self):
        return self.chunk
    def set_embedding(self, embedding_vector):
        self.embedding = embedding_vector
    def embeddingExpose(self):
        return self.embedding
#setup and config
def setup():
    load_dotenv()
    print(torch.__version__)
    print(torch.cuda.is_available())
    device = "cuda" if torch.cuda.is_available() else "cpu"  # safe
    #need to wrap this in langchain to use chroma db
    embeddingModel = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    #load and fix
    print(f"loading Data...  from {os.getcwd()}")
    data = []
    with open("../data/program_descriptions.jsonl", "r", encoding="utf-8") as file:
        for line in file:
            item = json.loads(line)
            data.append(item)

    print(f"loaded: {len(data)} programs")
    print(f"first item {data[0]}, typeof {type(data[0])}")

    return data

#chunking the data 
def chunkingData(data):
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 600,
    chunk_overlap = 30,
    )
    chunks = []
    chunks = []
    for i, item in enumerate(data):
        chunk_texts = text_splitter.split_text(item["description"])
        for j, chunk_text in enumerate(chunk_texts):
            chunk_obj = chunkObject(chunk_text, item["title"], item["url"], j)
            chunks.append(chunk_obj)
    print(f"chunks{len(chunks)}, first item {chunks[0].textExpose()}")

    return chunks



# VectorStore wrap em in documents extract embeddings from the chunks and then attach them in the chroma
def setup_chroma(chunks, persist_dir="data/chroma_db", k=10):
    print(torch.__version__)
    print(torch.cuda.is_available())
    device = "cuda" if torch.cuda.is_available() else "cpu"  # safe
    #need to wrap this in langchain to use chroma db
    embeddingModel = SentenceTransformerEmbeddings(model_name="multi-qa-mpnet-base-dot-v1")
    documents = [
        Document(page_content=c.chunk, metadata={"title": c.title, "url": c.url})
        for c in chunks
    ]
    #extract whats needed for the insertion into the chroma db
    texts = [d.page_content for d in documents]
    metadatas = [d.metadata for d in documents]

    db = Chroma.from_texts(
        texts=texts,
        embedding=embeddingModel,
        metadatas=metadatas,
        persist_directory="data/chroma_db"
    )

    retriever = db.as_retriever(
        search_type="mmr", # Maximum Marginal Relevance, e.g., https://docs.llamaindex.ai/en/stable/examples/vector_stores/SimpleIndexDemoMMR/
        search_kwargs={'20': 10}
    )
    query = "matematik är jättekul vilka program innehåller det?"
    docs = retriever.get_relevant_documents(query)
    print(f"docs: {docs}")
    for i, doc in enumerate(docs):
        print(f"--- Doc {i+1} ---")
        print(doc.page_content)  # first 300 chars
        print(doc.metadata)
    return retriever