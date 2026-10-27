import time 
from pinecone import Pinecone , ServerlessSpec 
from langchain_community.embeddings import JinaEmbeddings
from langchain_pinecone import PineconeVectorStore
from app.core.config import get_settings

settings = get_settings()

_embeddings = None 

_vectorstore = None 


def get_embeddings():
    global _embeddings 
    
    if _embeddings is None: 
        if not settings.jina_api_key: 
            raise RuntimeError("Jina Embedding key is missing")
        
        _embeddings = JinaEmbeddings(
            jina_api_key=settings.jina_api_key,
            model_name=settings.jina_embed_model, 
            model_kwargs={"dimensions": settings.embedding_dimensions}
        )
        
        return _embeddings


def ensure_index():
    if not settings.pinecone_api_key:
        raise RuntimeError("Pinecone API Key is missing")
    
    desired_dimension = settings.embedding_dimensions
    
    pc = Pinecone(api_key=settings.pinecone_api_key)
    names = [x["name"] for x in pc.list_indexes()]
    
    
    if settings.pinecone_index_name in names: 
        
        index_info = pc.describe_index(settings.pinecone_index_name)
        current_dimension = getattr(index_info, "dimension", None)
        
        if current_dimension is None and isinstance(index_info, dict):
            current_dimension = index_info.get("dimension")
        
        if current_dimension is not None and current_dimension != desired_dimension: 
            pc.delete_index(name=settings.pinecone_index_name)
            
            while settings.pinecone_index_name in [x["name"] for x in pc.list_indexes()]:
                time.sleep(1)
                
    if settings.pinecone_index_name not in [x["name"] for x in pc.list_indexes()]:
        pc.create_index(
            name=settings.pinecone_index_name, 
            dimension = desired_dimension, 
            metric="cosine", 
            spec= ServerlessSpec(cloud="aws", region="us-east-1")
        )
        
        while not pc.describe_index(settings.pinecone_index_name).status["ready"]:
            time.sleep(1)
            
    return pc.Index(settings.pinecone_index_name)


def get_vectorstore():
    global _vectorstore
    
    if _vectorstore is None: 
        index = ensure_index()
        
        _vectorstore = PineconeVectorStore(
            index=index, 
            embedding=get_embeddings(), 
            namespace=settings.pinecone_namespace
        )
    
    return _vectorstore


def get_retriever():
    return get_vectorstore().as_retriever(search_kwargs={"k":settings.top_k})


def add_documents(chunks):
    store = get_vectorstore()
    return store.add_documents(chunks)