
from loader import load_pdf_documents
from chunker import chunk_documents


# Step 1: Load original documents
documents = load_pdf_documents()

print("Original pages:", len(documents))


# Step 2: Generate chunks
chunks = chunk_documents(documents)

print("Generated chunks:", len(chunks))


# Step 3: Inspect the first three chunks
for chunk in chunks[:3]:

    print("\nChunk ID:")
    print(chunk.metadata["chunk_id"])

    print("\nSource:")
    print(chunk.metadata["document_name"])

    print("Page:")
    print(chunk.metadata["page_number"])

    print("Chunk index:")
    print(chunk.metadata["chunk_index"])

    print("\nContent:")
    print(chunk.page_content)

    print("-" * 60)
