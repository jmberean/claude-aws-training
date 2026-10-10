# Claude Training Project

## Overview
This project is for learning and testing RAG (Retrieval-Augmented Generation) pipelines and embedding systems.

## Cost Control Guidelines

### Model Selection - ALWAYS USE CHEAPEST MODELS

**This is a testing/learning project. Do not use expensive models.**

#### Anthropic Models
- **Default:** `claude-haiku-4-5` ($1/$5 per 1M tokens)
- **Never use:** `claude-opus-5-5`, `claude-opus-5`, `claude-sonnet-5-5`
- Exception: Only upgrade to Sonnet if you need better quality for comparison testing, and only after discussing

#### OpenAI Models (Embeddings)
- **Default:** `text-embedding-3-small` ($0.02 per 1M tokens) - already in use ✓
- **Never use:** `text-embedding-3-large` (6.5x more expensive)

#### Other Providers
- For any new provider integration, research the cheapest tier first
- Always start with free tiers or trial credits when available

### Token Limits
- Keep `max_tokens` reasonable - Haiku can generate good responses with 256-512 tokens
- Use lower `max_tokens` in testing (512 is typical, not 1024+)

### Monitoring
- Run `python embeddings.py` periodically to check costs in the API dashboards
- Set up alerts if you start noticing unexpected usage spikes

## Development Guidelines

### RAG Pipeline Architecture

**Step 1-3: Preprocessing (one-time)**
1. Chunk documents
2. Generate embeddings via OpenAI API
3. **Store in two indices:**
   - Vector database: Chromadb (semantic/similarity search)
   - BM25 index: rank-bm25 (lexical/keyword search)

**Step 4-6: Query time (per user question) - HYBRID SEARCH**
4. Run both searches in parallel:
   - **Semantic search**: Embed query → find similar vectors → rank by score
   - **BM25 search**: Tokenize query → find keyword matches → rank by score
5. **Merge with Reciprocal Rank Fusion (RRF)**:
   - Convert scores to ranks (position in result list)
   - Apply RRF formula: `RRF_score(d) = Σ(1 / (k_rrf + rank_i(d)))`
   - Combine rank contributions from both methods
6. Send top results + query to Claude for answer

### Hybrid Search Benefits
- **Semantic**: Finds conceptually related content (e.g., "training" matches "learning")
- **BM25**: Finds exact keywords (e.g., "INC-2023-Q4-011" incident IDs, specific terms)
- **RRF Fusion**: Mathematically sound merging - doesn't require score normalization
- **Combined**: Best of both worlds - meaning + precision

### RRF Advantage Over Weighted Scoring
- Uses **rank positions** not raw scores (more robust to different scoring scales)
- No need to normalize scores between systems
- Mathematically proven to combine multiple ranking systems
- `k_rrf` parameter (default 60) controls how much we penalize lower-ranked items

### File Structure
- `embeddings.py` - Complete RAG pipeline (chunking → embedding → storage → retrieval → answering)
- `mcp_server.py` - MCP server with document management tools (read/edit/list documents)
- `.vector_db/` - Persistent vector database (auto-created by Chromadb)
- `.env` - API keys (never commit)

### MCP Server Tools

The `mcp_server.py` provides three tools:

1. **read_doc_contents** - Read full document text by ID
2. **edit_document** - Find-and-replace editing on documents
3. **list_documents** - List all available documents

These tools can be used by Claude via MCP to interact with the document store.

### Testing New Features
1. Always test with Haiku first
2. If output quality is insufficient, test with Sonnet
3. Only move to Opus if absolutely necessary

### Example: Adding New Functionality
```python
# CORRECT - Start with Haiku
model = "claude-haiku-4-5"
max_tokens = 512

# Only change these if testing quality, not in production code
```

## Useful Commands
```bash
# Run the RAG pipeline
python embeddings.py

# Check API usage (requires logging into provider dashboards)
# Anthropic: console.anthropic.com
# OpenAI: platform.openai.com
```

## Notes
- This project uses OpenAI for embeddings (can't use Anthropic) + Claude for generation
- Haiku is perfectly capable for RAG answer generation
- Keep this guideline file updated as the project evolves
