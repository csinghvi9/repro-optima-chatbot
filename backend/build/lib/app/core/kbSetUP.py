# from langchain_community.document_loaders import JSONLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import Chroma
# from app.utils.config import ENV_PROJECT

# vectorstore=None

# def get_vectorstore():
#     global vectorstore
#     if vectorstore is None:
#         raise RuntimeError("Vectorstore not initialized yet")
#     return vectorstore

# async def KBSetup():
#     # JSON (you need to tell which field to extract)
#     global vectorstore
#     json_loader = JSONLoader(
#         file_path="app/datasets/faq.json",
#         jq_schema=".[] | {text: (.question + \"\\n\" + .answer)}",  # adjust depending on your JSON structure
#         content_key="text"
#     )
#     json_docs = json_loader.load()

#     if not json_docs:
#         raise ValueError("No documents loaded! Check your jq_schema or JSON structure.")

#     text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1000,
#     chunk_overlap=200
#     )
#     docs = text_splitter.split_documents(json_docs)
#     embeddings = OpenAIEmbeddings(model="text-embedding-3-small",api_key=ENV_PROJECT.OPENAI_API_KEY)

# # Store in ChromaDB
#     vectorstore = Chroma.from_documents(
#         documents=docs,
#         embedding=embeddings,
#         persist_directory="chroma_db"  # folder to save
#     )
#     # vectorstore.persist()

from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from app.utils.config import ENV_PROJECT

vectorstore = None
docs = None


def get_vectorstore():
    global vectorstore
    if vectorstore is None:
        raise RuntimeError("Vectorstore not initialized yet")
    return vectorstore


def get_docs():
    global docs
    if docs is None:
        raise RuntimeError("Docs not initialized yet")
    return docs


async def KBSetup():
    global vectorstore, docs

    # Load JSON (Q & A separate)
    json_loader = JSONLoader(
        file_path="app/datasets/faq.json",
        jq_schema='.[] | {text: (.question + " " + .answer)}',
        content_key="text",
    )
    json_docs = json_loader.load()

    if not json_docs:
        raise ValueError("No documents loaded! Check your JSON structure.")

    # Clean and split
    for d in json_docs:
        d.page_content = d.page_content.replace("\n", " ").strip()

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    docs = splitter.split_documents(json_docs)

    # Embeddings
    # embeddings = OpenAIEmbeddings(
    #     model="text-embedding-3-large",
    #     api_key=ENV_PROJECT.OPENAI_API_KEY
    # )
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=ENV_PROJECT.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        api_key=ENV_PROJECT.AZURE_OPENAI_API_KEY,
        azure_endpoint=ENV_PROJECT.AZURE_OPENAI_ENDPOINT,
        api_version=ENV_PROJECT.AZURE_OPENAI_API_VERSION,
    )

    # Store in Chroma
    vectorstore = Chroma.from_documents(
        documents=docs, embedding=embeddings, persist_directory="chroma_db"
    )
