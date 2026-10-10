from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
import chromadb
from rank_bm25 import BM25Okapi
import math
import os

load_dotenv()

openai_client = OpenAI()
claude_client = Anthropic()

embedding_model = "text-embedding-3-small"

# Initialize persistent Chromadb client (stores to .vector_db/ directory)
db_path = os.path.join(os.path.dirname(__file__), ".vector_db")
chroma_client = chromadb.PersistentClient(path=db_path)


def generate_embedding(text):
    response = openai_client.embeddings.create(
        model=embedding_model,
        input=text,
    )
    return response.data[0].embedding


def cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))
    return dot_product / (mag1 * mag2)


class RAGSystem:
    def __init__(self, collection_name="documents"):
        """Initialize RAG system with persistent vector database and BM25."""
        self.collection_name = collection_name

        # Get or create collection (persisted on disk)
        self.collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # Initialize BM25 for lexical search
        self.documents = []
        self.bm25 = None

        print(f"Using collection: {collection_name}")
        print(f"Vector database persisted at: {db_path}")
        print("Hybrid search enabled (semantic + BM25 lexical)\n")

    def add_documents(self, documents):
        """Add documents to both vector database and BM25 index."""
        print(f"Processing {len(documents)} documents...\n")

        for i, doc in enumerate(documents):
            # Check if document already exists in vector DB
            existing = self.collection.get(ids=[f"doc_{i}"])

            if not existing["ids"]:
                # New document - embed and store
                embedding = generate_embedding(doc)

                # Store in persistent Chromadb
                self.collection.add(
                    ids=[f"doc_{i}"],
                    embeddings=[embedding],
                    documents=[doc],
                    metadatas=[{"doc_index": i, "source": "training_data"}]
                )
                print(f"✓ {doc[:60]}... (stored in vector DB)")
            else:
                print(f"✓ {doc[:60]}... (already in vector DB)")

            # Add to BM25 index (always, since BM25 is in-memory)
            self.documents.append(doc)

        # Build BM25 index from tokenized documents
        tokenized_docs = [doc.split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        print(f"\n✓ BM25 lexical index built for {len(self.documents)} documents\n")

    def retrieve_semantic(self, query, top_k=3):
        """Retrieve using semantic search (vector embeddings)."""
        query_embedding = generate_embedding(query)

        # Query Chromadb with cosine similarity
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Convert to (document, similarity_score) tuples
        semantic_results = {}
        if results["documents"] and len(results["documents"]) > 0:
            for doc, distance in zip(results["documents"][0], results["distances"][0]):
                similarity = 1 - distance  # Convert distance to similarity
                semantic_results[doc] = similarity

        return semantic_results

    def retrieve_bm25(self, query, top_k=3):
        """Retrieve using BM25 lexical search."""
        if not self.bm25:
            return {}

        # Tokenize query
        query_tokens = query.split()

        # Get BM25 scores
        scores = self.bm25.get_scores(query_tokens)

        # Get top_k results
        bm25_results = {}
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        for idx in top_indices:
            if scores[idx] > 0:  # Only include documents with non-zero scores
                bm25_results[self.documents[idx]] = scores[idx]

        return bm25_results

    def retrieve_hybrid(self, query, top_k=3, k_rrf=60):
        """
        Hybrid search using Reciprocal Rank Fusion (RRF).

        RRF combines results from multiple ranking systems by considering
        each document's rank position across all systems, not their scores.

        Args:
            query: User query
            top_k: Number of results to return
            k_rrf: Constant for RRF formula (default 60, use 1 for clearer results)

        Formula: RRF_score(d) = Σ(1 / (k_rrf + rank_i(d)))
        """
        # Run both searches in parallel
        semantic_results_dict = self.retrieve_semantic(query, top_k=top_k*2)
        bm25_results_dict = self.retrieve_bm25(query, top_k=top_k*2)

        # Convert to ranked lists (highest score = rank 1)
        semantic_ranked = sorted(semantic_results_dict.items(), key=lambda x: x[1], reverse=True)
        bm25_ranked = sorted(bm25_results_dict.items(), key=lambda x: x[1], reverse=True)

        # Create rank dictionaries: {document: rank (1-indexed)}
        semantic_ranks = {doc: rank + 1 for rank, (doc, _) in enumerate(semantic_ranked)}
        bm25_ranks = {doc: rank + 1 for rank, (doc, _) in enumerate(bm25_ranked)}

        # Get all unique documents
        all_docs = set(semantic_ranks.keys()) | set(bm25_ranks.keys())

        # Apply RRF formula
        rrf_scores = {}
        for doc in all_docs:
            rrf_score = 0.0

            # Add contribution from semantic search
            if doc in semantic_ranks:
                rrf_score += 1.0 / (k_rrf + semantic_ranks[doc])

            # Add contribution from BM25 search
            if doc in bm25_ranks:
                rrf_score += 1.0 / (k_rrf + bm25_ranks[doc])

            rrf_scores[doc] = rrf_score

        # Sort by RRF score and return top_k
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return sorted_results

    def answer(self, query, search_type="hybrid"):
        """
        Answer a question using hybrid search (semantic + BM25).

        Args:
            query: User question
            search_type: "hybrid" (default), "semantic", or "bm25"
        """
        # Retrieve relevant chunks
        if search_type == "semantic":
            retrieved = list(self.retrieve_semantic(query, top_k=3).items())
        elif search_type == "bm25":
            retrieved = list(self.retrieve_bm25(query, top_k=3).items())
        else:  # hybrid
            retrieved = self.retrieve_hybrid(query, top_k=3)

        print(f"\nQuery: {query}\n")
        print(f"Retrieved documents ({search_type} search):")
        for i, (chunk, score) in enumerate(retrieved, 1):
            print(f"{i}. (score: {score:.3f}) {chunk}")

        # Build context from retrieved chunks
        context = "\n\n".join([chunk for chunk, _ in retrieved])

        # Call Claude with the context
        print("\nGenerating answer with Claude Haiku...\n")
        response = claude_client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            system="You are a helpful assistant. Answer the user's question based on the provided context. If the context doesn't contain relevant information, say so.",
            messages=[{
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }]
        )

        # Find the text block in the response (skip thinking blocks)
        for block in response.content:
            if block.type == "text":
                return block.text


# Sample documents (as if from a knowledge base)
documents = [
    "Quantum computing uses qubits instead of classical bits. Qubits can exist in superposition, meaning they can be 0, 1, or both simultaneously.",
    "The weather today is sunny with a high of 72 degrees. There is a 10% chance of rain this evening.",
    "Quantum entanglement is a key feature in quantum computing. It allows qubits to be correlated in ways that have no classical equivalent.",
    "I need to buy groceries like milk, eggs, and bread. The store is open until 9 PM.",
    "Quantum algorithms can solve certain problems exponentially faster than classical algorithms. Shor's algorithm and Grover's algorithm are famous examples.",
]

# Initialize RAG system with hybrid search
rag = RAGSystem(collection_name="training_documents")
rag.add_documents(documents)

# Ask a question using hybrid search
print("="*60)
print("HYBRID SEARCH (Semantic + BM25)")
print("="*60)
answer = rag.answer("How does quantum computing work?", search_type="hybrid")
print("Answer:")
print(answer)

# Optional: Compare different search methods
print("\n" + "="*60)
print("COMPARISON: Try different search methods")
print("="*60)
print("\nTo compare search methods on the same query, uncomment below:\n")
print("# answer_semantic = rag.answer('How does quantum computing work?', search_type='semantic')")
print("# answer_bm25 = rag.answer('How does quantum computing work?', search_type='bm25')")
