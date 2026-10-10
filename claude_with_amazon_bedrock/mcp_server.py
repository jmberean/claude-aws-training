"""
MCP Server for Document Management

This server implements two tools:
1. read_doc_contents - Read document contents by document ID
2. edit_document - Edit documents with find-and-replace operations

Uses the MCP Python SDK with MCPServer (mcp 2.x).
"""

from mcp.server.mcpserver import MCPServer
from pydantic import Field

# Initialize MCP server
mcp = MCPServer("DocumentMCP")

# In-memory document store
docs = {
    "quantum_intro.md": """
# Introduction to Quantum Computing

Quantum computing uses qubits instead of classical bits.
Qubits can exist in superposition, meaning they can be 0, 1, or both simultaneously.

This fundamental property allows quantum computers to explore multiple solutions in parallel,
making them exponentially faster for certain types of problems.
    """.strip(),

    "quantum_entanglement.md": """
# Quantum Entanglement

Quantum entanglement is a key feature in quantum computing.
It allows qubits to be correlated in ways that have no classical equivalent.

When qubits are entangled, measuring one qubit instantly affects the state of others,
regardless of distance. This property is crucial for quantum algorithms.
    """.strip(),

    "quantum_algorithms.md": """
# Quantum Algorithms

Quantum algorithms can solve certain problems exponentially faster than classical algorithms.

Key Examples:
- Shor's algorithm: Breaks RSA encryption by finding prime factors efficiently
- Grover's algorithm: Searches unsorted databases in O(√N) time instead of O(N)
- Variational algorithms: Used for optimization and machine learning tasks

These algorithms leverage superposition and entanglement to achieve quantum speedup.
    """.strip(),

    "quantum_error.md": """
# Quantum Error Correction

Quantum computers are highly susceptible to errors from environmental interference (decoherence).

Error Correction Strategies:
- Surface codes: Arrange qubits in a 2D grid for error detection
- Topological codes: Use properties of topology to protect quantum information
- Concatenated codes: Nest error correction codes for improved fault tolerance

Building fault-tolerant quantum computers requires overcoming these error correction challenges.
    """.strip(),
}


@mcp.tool(
    name="read_doc_contents",
    description="Read the full contents of a document by its ID. Returns the complete document text."
)
def read_doc_contents(
    doc_id: str = Field(description="ID of the document to read (e.g., 'quantum_intro.md')")
) -> str:
    """Read document contents from the in-memory store."""
    if doc_id not in docs:
        available_docs = ", ".join(docs.keys())
        raise ValueError(f"Doc '{doc_id}' not found. Available documents: {available_docs}")

    return docs[doc_id]


@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing text. Performs a find-and-replace operation on the document contents."
)
def edit_document(
    doc_id: str = Field(description="ID of the document to edit"),
    old_str: str = Field(description="The exact text to find and replace (must match including whitespace)"),
    new_str: str = Field(description="The new text to insert in place of the old text")
) -> str:
    """Edit a document with find-and-replace. Returns the updated content."""
    if doc_id not in docs:
        available_docs = ", ".join(docs.keys())
        raise ValueError(f"Doc '{doc_id}' not found. Available documents: {available_docs}")

    if old_str not in docs[doc_id]:
        raise ValueError(
            f"Text '{old_str[:50]}...' not found in document '{doc_id}'. "
            f"Check exact spelling and whitespace."
        )

    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return f"Document '{doc_id}' updated successfully. New content:\n\n{docs[doc_id]}"


@mcp.tool(
    name="list_documents",
    description="List all available documents in the system."
)
def list_documents() -> str:
    """Return a list of all available document IDs."""
    doc_list = "\n".join([f"  - {doc_id}" for doc_id in docs.keys()])
    return f"Available documents ({len(docs)} total):\n{doc_list}"


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
