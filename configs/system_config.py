"""
system_config.py

Contains system-related configuration values such as file paths,
environment variables, and external API keys.
Compatible with Python 3.1 by avoiding variable annotations and f-strings.
"""

import os

class SystemConfig(object):
    """
    System-level configuration class for file paths, environment variables,
    and external API keys.
    """
    # If you're using OpenAIEmbeddings, store or retrieve your API key safely
    OPENAI_API_KEY = os.getenv(
        "OPENAI_API_KEY",
        "YOUR-API-KEY"
    )

    PINECONE_INDEX_NAME = "rag-in-finance-eric"
    PINECONE_API_KEY = "YOUR-PINECONE-API-KEY"
    PINECONE_CLOUD = "aws"
    PINECONE_REGION = "us-east-1"
    PINECONE_NAMESPACE = "patents"

    @classmethod
    def load_from_env(cls):
        """
        Optionally override config values from environment variables.
        For example, if you set OPENAI_API_KEY in your environment,
        it can override the default value.
        """
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            cls.OPENAI_API_KEY = env_key
