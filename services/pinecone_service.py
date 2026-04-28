import uuid
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

class PineconeService:
    """
    Vector Search Service for India Election Knowledge Graph Assistant.
    Embeds and stores Election Acts, Section texts, Local Lore, and Descriptions.
    """
    
    def __init__(self, api_key: str, environment: str, index_name: str = "india-election-kg"):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        
        # 'all-MiniLM-L6-v2' is fast, lightweight, and standard for sentence embeddings (384 dims)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
        
        self._ensure_index_exists(environment)
        self.index = self.pc.Index(index_name)

    def _ensure_index_exists(self, environment: str):
        """Creates the Pinecone index if it does not already exist."""
        existing_indexes = [index_info.name for index_info in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=environment)
            )

    def upsert_document(self, text_content: str, doc_type: str, jurisdiction_id: str, 
                        act_id: str = None, language: str = "en") -> str:
        """
        Embeds the text using sentence-transformers and upserts into Pinecone.
        Returns the generated UUID (which corresponds to the vector_id in Neo4j).
        
        Metadata tracks multilingual support and relationship mapping to the Graph.
        """
        vector_id = str(uuid.uuid4())
        
        # Generate embedding
        embedding = self.model.encode(text_content).tolist()
        
        # Construct metadata
        metadata = {
            "type": doc_type, # e.g., 'Act_Section', 'Local_Lore', 'Jurisdiction_Description'
            "jurisdiction_id": jurisdiction_id,
            "language": language,
            "text": text_content # Storing snippet for immediate context retrieval
        }
        
        if act_id:
            metadata["act_id"] = act_id
            
        self.index.upsert(vectors=[
            {
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            }
        ])
        
        return vector_id

    def semantic_search(self, query_text: str, top_k: int = 5, filters: dict = None):
        """
        Perform a semantic search against the Pinecone index.
        Filters can be applied based on jurisdiction_id, language, or doc_type.
        """
        query_embedding = self.model.encode(query_text).tolist()
        
        search_args = {
            "vector": query_embedding,
            "top_k": top_k,
            "include_metadata": True
        }
        
        if filters:
            # E.g., filters = {"language": {"$eq": "hi"}, "type": {"$eq": "Act_Section"}}
            search_args["filter"] = filters
            
        results = self.index.query(**search_args)
        
        return [
            {
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            }
            for match in results.matches
        ]
