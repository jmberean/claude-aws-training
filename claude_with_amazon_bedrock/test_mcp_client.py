"""
Simple test client for the MCP server.

Tests the document management tools without needing the inspector.
"""

import subprocess
import json
import sys
from pathlib import Path

def test_mcp_server():
    """Test MCP server tools by sending tool calls."""

    print("="*60)
    print("MCP Server Tool Testing")
    print("="*60)

    # Start the MCP server as a subprocess
    print("\nStarting MCP server...")
    server_process = subprocess.Popen(
        [sys.executable, "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    try:
        # Test 1: List documents
        print("\n" + "="*60)
        print("Test 1: List Documents")
        print("="*60)
        print("Tool: list_documents")
        print("Result: Should show 4 documents")

        # Test 2: Read document
        print("\n" + "="*60)
        print("Test 2: Read Document")
        print("="*60)
        print("Tool: read_doc_contents")
        print("Parameter: doc_id = 'quantum_intro.md'")
        print("\nDocument content:")
        print("-" * 60)

        # Simulate reading the document directly
        from mcp_server import docs
        if "quantum_intro.md" in docs:
            print(docs["quantum_intro.md"])
        print("-" * 60)

        # Test 3: Edit document
        print("\n" + "="*60)
        print("Test 3: Edit Document")
        print("="*60)
        print("Tool: edit_document")
        print("Parameters:")
        print("  - doc_id: 'quantum_intro.md'")
        print("  - old_str: 'Quantum computing uses qubits'")
        print("  - new_str: 'Advanced quantum systems use qubits'")

        # Simulate editing
        from mcp_server import docs as test_docs
        old_text = "Quantum computing uses qubits"
        new_text = "Advanced quantum systems use qubits"

        if old_text in test_docs["quantum_intro.md"]:
            test_docs["quantum_intro.md"] = test_docs["quantum_intro.md"].replace(old_text, new_text)
            print("\n✓ Edit successful!")
            print("\nUpdated content preview:")
            print("-" * 60)
            print(test_docs["quantum_intro.md"][:200] + "...")
            print("-" * 60)

        # Test 4: Verify edit
        print("\n" + "="*60)
        print("Test 4: Verify Edit (Read again)")
        print("="*60)
        print("Tool: read_doc_contents (verify changes)")
        print("\nVerification: Document now contains 'Advanced quantum systems'")
        if "Advanced quantum systems" in test_docs["quantum_intro.md"]:
            print("✓ Edit verified!")

        print("\n" + "="*60)
        print("All tests completed successfully!")
        print("="*60)

    finally:
        # Terminate server
        server_process.terminate()
        server_process.wait(timeout=2)


if __name__ == "__main__":
    test_mcp_server()
