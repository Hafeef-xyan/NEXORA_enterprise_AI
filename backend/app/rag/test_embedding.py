import numpy as np
from embeddings import get_embedding_model


embedding_model = get_embedding_model()

# Test document embedding
document = (
    "Employees must submit expense claims "
    "within 15 days of the transaction."
)

document_vector = embedding_model.embed_documents(
    [document]
)

# Test query embedding
query = "What is the deadline for expense reimbursement?"

query_vector = embedding_model.embed_query(query)

print("Document vector dimensions:", len(document_vector[0]))
print("Query vector dimensions:", len(query_vector))

print("\nFirst 5 document values:")
print(document_vector[0][:5])

print("\nFirst 5 query values:")
print(query_vector[:5])

# Calculate cosine similarity
similarity = np.dot(
    document_vector[0],
    query_vector
)

print("\nCosine similarity:", float(similarity))
