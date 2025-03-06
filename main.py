"""
main.py
"""
import io
import os
import pinecone
from pinecone import Pinecone
import dropbox
import pandas as pd

from configs.config import Config
from data_ingestion.csv_loader import CSVLoader
from data_ingestion.report_loader import ReportLoader
from vectorstore.vectorstore_manager import VectorStoreManager
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def load_parquet():
    dbx = dropbox.Dropbox(
        "sl.u.AFniKtVtgy__nqYto-V9vrO9xOW3D5952wBCzLBT0aRk_NN18avnifz4Yv8XZO-cxtPGKp1m7PlNudnT8tFKgvP-skwLLpeRO2R3LUnHG5OHWK4wIeAI5j8WyitzhWEgK10HALpxCGyjX_1FupyScavqhoFe-dV6cSj1LPodxJLQZ_MBM6_PklLQrgB_SYLa3uWuD5NTaSjl0Ej3cB_RByOMSTZuEAQm-BTHFyAItm01rQAz-zhdzdJ_nfOOJE1PaUSmoQf97RFlqaDldQQdfXQJyaTH7-KTIT1H826ky_W_vakCyGXMw6Y7G0tz11jXP_h3g9dqlvWNYYv7zZphGbW1WYaWrCQ5waOdjuWDYfvjQCNjBGu8V6vvlqJ0fDQrfs0qe89JfohH46x3bBpvVi6RObOfCJFeau0wS3p7ZYf20TvuBZbrwftxZVlBHQq70MuJgwgmMcq6rkdlns0zg8hSlpkLNotSiWVyq1FSGpHSRJTcu26-vEID2A5kxWLQjxOFzpgA377-mJ0WgT8NixQ_ssNDlyGUJ9e1M4fmv1-AgMc9yocLFmOMFr_BeC747C7Z3SQb_gsTLmyjGe4QTNJN8X44oqmblth-gh2dk3w2UExfI2rs7pLXk9IUzYgyOxhQax6X7aWsl4DLgnZGiyoxFBveDBcI50d9jjiqx5qE_msM3z2KlkM3-Xx6gOVviWusvdVBRyeY3mCLbr9sQP4FPSzM5OMkmvFanxSlwPnEN7LCV7ed0u8k-AYbgiZ_F1u46T3wYxgDygkuGY91Y6wy2SDfdzn6wOQ4JG4YB-2GhVDrxSDrZ381eVWPMdRADJ7QiLP8gRZb7KYT-spNxId96MagspaxaLCTpGRVrMGz2WjXvZyLWNz4_isPeuywG2CiwKiUHnIuugH117vtJGguxtgEUmzVb-DjdOXqMXb8NqjnnfJn4Iq-DGRAYGoCyO56qLXvAi92WOYb8fV-znSytxKR3acJRdyPpLpONWpEFnvmEGt6OMQ79rgBwsCQnfMIOQd2zuKttzZHfCg40NYS2-6yRwSbRTDAAQr3rNOLO2na-jjT8OhakG8zTFR1BDh_tOhg68j2rGljmIUS4iJpDg61gPUo6BjvpZJ5I8ZNij3PAFtH6PdWxgGilZ6P2782SKEtgGm3ATVtVrzwYXDi_04SFoiJ7BczGES9_3DpibGdlJo8D5KqUvkTkBEbLpj-USblVchyAysPmpxJ8ceru9V0PnriDyyr1QrzDvgzgoE2Yn75YNS8yOrOvwPw45mgdJFg35_8HRlxpnoeH1mEQPtfAtKVfJtuaWUZsG5-sTuJqenY-UcOX9tB5AqZIUfaxrnAkoDr36FM_KoARV-qk2TeyGrU1GhgKvWAkH1qKR_Eff6UHwPlq7IVnfk7Amyyg3TMbtV28Y6ruwodagZKXqcrBWU4J_T8ThUr4GaeCw")
    path = '/data/patents/USPTO-patent_level-metrics-76_20.pqt.gzip'
    metadata, f = dbx.files_download(path)
    print(f.content[:4])
    df = pd.read_parquet(io.BytesIO(f.content))
    df = df[['gvkey', 'filing_year', 'claim_text', 'patent_abstract', 'patent_title']]
    return df

def main():
    # Load environment variables if needed
    Config.System.load_from_env()
    #
    # # Load CIK -> SICH mapping
    # csv_loader = CSVLoader(Config.System.CSV_FILE_PATH)
    # cik_maping = csv_loader.load_cik_sich_mapping()
    #
    # # Ingest 10-k reports
    # report_loader = ReportLoader(Config.System.REPORTS_DIRECTORY, cik_maping)
    # documents = report_loader.load_all_documents(desired_sections=["Item 1", "Item 7"])

    df = load_parquet()
    df = df.dropna(subset=['claim_text'])

    # Convert each row into a document format expected by the embedding pipeline.
    # Here, claim_text is the text to embed, while gvkey and issue_year are set as metadata.
    documents = []
    for _, row in df.iterrows():
        doc = Document(
            page_content=row['claim_text'],
            metadata={
                "gvkey": row['gvkey'],
                "filing_year": row['filing_year'],
                'patent_abstract': row['patent_abstract'],
                'patent_title': row['patent_title']
            }
        )
        documents.append(doc)

    # Split documents into smaller chunks (optional)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.Project.CHUNK_SIZE,
        chunk_overlap=Config.Project.CHUNK_OVERLAP,
        length_function=len
    )
    split_docs = splitter.split_documents(documents)
    print("After splitting, we have " + str(len(split_docs)) + " chunks.")

    # Create a Pinecone client instance.
    pc = Pinecone(api_key=Config.System.PINECONE_API_KEY)

    # Create or load Chroma vector store
    vs_manager = VectorStoreManager(
        index_name=Config.System.PINECONE_INDEX_NAME,
        pinecone_api_key=Config.System.PINECONE_API_KEY,
        namespace=Config.System.PINECONE_NAMESPACE,
        embeddings_model_name=Config.Project.EMBEDDINGS_MODEL_NAME,
        cloud=Config.System.PINECONE_CLOUD,
        region=Config.System.PINECONE_REGION
    )

    # Check if the index already exists
    if Config.System.PINECONE_INDEX_NAME in pc.list_indexes().names():
        print(
            "Loading existing vectorstore from Pinecone index: " + Config.System.PINECONE_INDEX_NAME)
        vs_manager.load_vectorstore()
        # Now upsert new documents into the current vectorstore.
        print("Upserting new vectors...")
        vs_manager.upsert_documents(split_docs)
    else:
        print(
            "Creating new vectorstore in Pinecone index: " + Config.System.PINECONE_INDEX_NAME)
        vs_manager.create_vectorstore(split_docs)

if __name__ == "__main__":
    main()
