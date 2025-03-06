"""
vectorstore_manager.py

Manages the creation, loading, and retrieval of vector stores.
Currently configured to use Chroma as the vector database.
"""

import os
import time
from configs.config import Config
import pinecone
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeEmbeddings, PineconeVectorStore
from langchain.schema import Document


class VectorStoreManager(object):
    """
    Handles the lifecycle of a Chroma-based vector store, including:
      - Creating from a list of Documents
      - Loading from an existing directory
      - Providing a Retriever interface
    """

    def __init__(
            self,
            index_name,
            pinecone_api_key,
            namespace="",
            embeddings_model_name="multilingual-e5-large",
            cloud="",
            region=""
    ):
        """
        Args:
            index_name (str): Name of the Pinecone index.
            pinecone_api_key (str): Your Pinecone API key.
            namespace (str): Namespace to use within the index (for multitenancy).
            embeddings_model_name (str): Name of the embeddings model.
            cloud (str): Cloud provider (e.g., "aws").
            region (str): Cloud region (e.g., "us-east-1").
        """
        self.index_name = index_name
        self.namespace = namespace
        self.pinecone_api_key = pinecone_api_key

        self.cloud = cloud
        self.region = region

        # Set the API key in the environment so internal clients can pick it up.
        os.environ["PINECONE_API_KEY"] = self.pinecone_api_key

        # Ensure the environment variable for the Pinecone environment is set.
        env = os.environ.get('PINECONE_ENVIRONMENT', 'us-east1-gcp')
        os.environ["PINECONE_ENVIRONMENT"] = env

        # Create a Pinecone client instance.
        self.pc = Pinecone(api_key=self.pinecone_api_key)

        # Initialize the embedding function using Pinecone's hosted model.
        self.embedding_function = PineconeEmbeddings(
            model=embeddings_model_name,
            pinecone_api_key=pinecone_api_key
        )

        # Attempt to use the dimension provided by the embedding function.
        if self.embedding_function.dimension is not None:
            self.embedding_dimension = self.embedding_function.dimension
        else:
            # Fallback: assign known dimensions for specific models.
            if embeddings_model_name == "multilingual-e5-large":
                self.embedding_dimension = 1024
            else:
                raise ValueError("Unable to determine embedding dimension for model " + embeddings_model_name)

        self.vectorstore = None


    def create_vectorstore(self, documents):
        """
        Creates a new Pinecone vector store from the given documents.
        This includes creating the index (if it doesn't exist) and upserting embeddings.

        Args:
            documents (list): List of LangChain Document objects.
        """
        spec = ServerlessSpec(cloud=self.cloud, region=self.region)

        if self.index_name not in self.pc.list_indexes().names():
            print(
                f"Index '{self.index_name}' does not exist. Creating new index...")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.embedding_dimension,
                metric="cosine",
                spec=spec
            )
            # Wait until the index is ready.
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)
            print("Index created.")

        self.vectorstore = PineconeVectorStore.from_documents(
            documents=documents,
            index_name=self.index_name,
            embedding=self.embedding_function,
            namespace=self.namespace
        )


    def load_vectorstore(self):
        """
        Loads the Chroma vector store from an existing directory (self.persist_directory).
        Raises an error if the directory does not exist or is invalid.
        """
        # Create a Pinecone client instance.
        pc = Pinecone(api_key=self.pinecone_api_key)
        if self.index_name not in pc.list_indexes().names():
            raise ValueError(
                f"Index '{self.index_name}' does not exist in Pinecone. Nothing to load.")

        self.vectorstore = PineconeVectorStore.from_existing_index(
            index_name=self.index_name,
            embedding=self.embedding_function,
            namespace=self.namespace
        )

    def get_retriever(self, search_kwargs=None):
        """
        Returns a retriever object for querying the vector store.

        Args:
            search_kwargs (dict): Additional keyword args for Chroma's `as_retriever()` method.
                e.g. {"k": 20, "filter": {"cik": "123456"}, "search_type": "mmr"}

        Returns:
            A retriever object that can be used to retrieve relevant documents.
        """
        if self.vectorstore is None:
            raise ValueError("Vector store is not initialized. Call create_vectorstore() or load_vectorstore() first.")

        if search_kwargs is None:
            search_kwargs = {}
        return self.vectorstore.as_retriever(**search_kwargs)

    def upsert_documents(self, documents):
        """
        Upserts new documents into the existing vectorstore.

        Args:
            documents (list): List of LangChain Document objects to be added.
        """
        if self.vectorstore is None:
            raise ValueError(
                "Vector store is not initialized. Call create_vectorstore() or load_vectorstore() first.")

        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        self.vectorstore.add_texts(texts, metadatas=metadatas)
