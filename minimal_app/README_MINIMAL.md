# Minimal OmniTech Support Examples

This directory contains **simplified, educational versions** of the OmniTech support system. These are perfect for learning how RAG and MCP work without getting overwhelmed by complex features.

## What's Different from the Full Solution?

| Feature | Full Solution | Minimal Version |
|---------|--------------|-----------------|
| **Complexity** | Production-ready, full-featured | Educational, simplified |
| **Knowledge Base** | PDF loading + classification | PDF loading (simplified) |
| **MCP Data** | External JSON files, SQLite | Hardcoded in files |
| **UI Tabs** | Chat + 4 debug tabs | Chat only |
| **State Mgmt** | Complex state tracking | Simple chat history |
| **Metrics** | Detailed timing & analytics | None |
| **Code Size** | ~900 lines total | ~450 lines total |
| **Use Case** | Deploy to production | Learn the basics |

## Files Included

```
mcp_server_minimal.py         # MCP server that loads from data file
minimal_data.json             # Sample emails and orders data
rag_agent_minimal.py          # Simple RAG agent with MCP integration
gradio_app_minimal.py         # Clean chat-only interface
gradio_minimal_styles.css     # External CSS for clean styling
README_MINIMAL.md             # This file
```

## Quick Start

### 1. Install Dependencies

From the project root directory:
```bash
pip install -r requirements/requirements.txt
```

### 2. Set Your Hugging Face Token

```bash
export HF_TOKEN="your-hf-token-here"
```

Get a free token at: https://huggingface.co/settings/tokens

### 3. Run the Chat Interface

From the project root:
```bash
cd minimal_app
python3 gradio_app_minimal.py
```

Then open http://localhost:7860 in your browser!

## Understanding Each Component

### MCP Server (`mcp_server_minimal.py`)

**What it does:** Provides tools for searching emails and orders

**Key concepts:**
- Loads data from `minimal_data.json` (4 emails and 4 orders)
- Exposes 2 tools: `search_emails` and `search_orders`
- Runs as a subprocess that the agent communicates with

**Data file (`minimal_data.json`):**
- JSON format with "emails" and "orders" arrays
- Easy to edit and add new test data
- Keeps code clean by separating data from logic

**Sample data includes:**
- John Smith's laptop issue (ORD-1001)
- Sarah Jones' mouse battery question (ORD-1002)
- Mike Chen's delayed monitor order (ORD-1003)

### RAG Agent (`rag_agent_minimal.py`)

**What it does:** Combines knowledge base search with MCP tool calling

**Key concepts:**
- **PDF Loading:** Loads real PDF files from `../knowledge_base_pdfs/` directory (in parent folder)
- **Vector Store:** Uses ChromaDB to store PDF content with embeddings
- **4 PDF Documents:** Account Security, Device Troubleshooting, Shipping, Returns
- **Semantic Search:** Finds relevant sections of PDFs based on user questions
- **MCP Integration:** Connects to the MCP server to access tools
- **LLM:** Uses Hugging Face models (Llama 3.1 8B Instruct) to generate helpful responses

**Try running it standalone:**
```bash
cd minimal_app
python3 rag_agent_minimal.py
# Runs 3 test queries to demonstrate functionality
```

**The magic happens in `query()`:**
1. Searches vector store (loaded from PDFs) for relevant docs
2. Checks if it needs to search emails/orders (MCP tools)
3. Sends everything to HF LLM to generate response
4. Returns natural language response

### Gradio App (`gradio_app_minimal.py`)

**What it does:** Provides a clean chat interface

**Key concepts:**
- Simple chatbot UI with professional branding
- Customer email selector (dropdown to switch between users)
- Calls `agent.query()` for each message
- Maintains chat history
- Loads CSS from external file (`gradio_minimal_styles.css`) for easy customization
- No complex state or debug features

**Example queries to try:**
- "How do I reset my password?" (RAG - Account Security PDF)
- "What's the status of order ORD-1003?" (MCP tool)
- "Show me emails from john.smith@email.com" (MCP tool)
- "My device won't turn on" (RAG - Device Troubleshooting PDF)
- "What is your return policy?" (RAG - Returns Policy PDF)

## How It All Works Together

```
┌─────────────────────────────────────────────────────────────┐
│                        USER                                  │
│                 (Web Browser)                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  GRADIO APP                                  │
│              (gradio_app_minimal.py)                         │
│                                                              │
│  • Displays chat interface                                  │
│  • Manages chat history                                     │
│  • Calls agent.query()                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   RAG AGENT                                  │
│              (rag_agent_minimal.py)                          │
│                                                              │
│  1. Search Vector Store ─────► ChromaDB (4 PDF docs)        │
│                                                              │
│  2. Call Hugging Face LLM ───► Llama 3.1 8B Instruct        │
│                                                              │
│  3. Execute Tools (if needed) ──────────┐                   │
└──────────────────────────────────────────┼──────────────────┘
                                           │
                                           ▼
                         ┌─────────────────────────────────────┐
                         │         MCP SERVER                  │
                         │     (mcp_server_minimal.py)         │
                         │                                     │
                         │  • search_emails                    │
                         │    (4 hardcoded emails)             │
                         │                                     │
                         │  • search_orders                    │
                         │    (4 hardcoded orders)             │
                         └─────────────────────────────────────┘
```

## Learning Path

### Step 1: Understand MCP Server
1. Open `minimal_data.json` to see the sample emails and orders
2. Open `mcp_server_minimal.py`
3. See how `load_data()` reads from the JSON file
4. See how `list_tools()` defines available tools
5. See how `call_tool()` implements the search logic

### Step 2: Understand RAG Agent
1. Open `rag_agent_minimal.py`
2. See how `_load_pdf_documents()` extracts text from PDFs
3. See how `_setup_vector_store()` loads PDF content into ChromaDB
4. Understand semantic search in `search_knowledge_base()`
5. Follow the flow in `query()` - this is where RAG + MCP combine!

### Step 3: Run the Full System
1. Run `python3 gradio_app_minimal.py`
2. Try the example queries
3. Watch how it answers from knowledge base vs using tools
4. Check the terminal for debug output

### Step 4: Experiment!
- Add a new PDF to `../knowledge_base_pdfs/` (parent directory) and see it get loaded
- Add a new email or order to `minimal_data.json`
- Try different queries in the chat
- Add `print()` statements to see the RAG retrieval process
- Customize the look by editing `gradio_minimal_styles.css`
- Read the code comments - they explain everything!

## Common Questions

**Q: Where is the data stored?**
A:
- Emails and orders: Stored in `minimal_data.json` file in this directory (easy to edit)
- Product documentation: Loaded from PDF files in `../knowledge_base_pdfs/` (parent directory)
- Vector embeddings: Created by ChromaDB from the PDFs for semantic search

**Q: Can I see the MCP tool calls?**
A: The minimal version doesn't have a debug UI, but you can add `print()` statements in `rag_agent_minimal.py` to see what's happening.

**Q: How is this different from the full solution?**
A: The full solution has developer mode, metrics tracking, external data files, ticket creation, and many more features. This minimal version focuses on the core concepts only.

**Q: Can I deploy this?**
A: This is for learning! Use the full solution files for actual deployment.

**Q: How do I add more emails or orders?**
A: Edit `minimal_data.json`! It's a simple JSON file with "emails" and "orders" arrays. Just add new entries following the same format as the existing ones. This keeps the code clean while making it easy to customize test data.

**Q: How do I customize the look and feel?**
A: Edit `gradio_minimal_styles.css`! All the styling is in this external CSS file, so you can change colors, fonts, spacing, etc. without touching the Python code. The CSS uses standard web styling - modify the gradient colors in the header, change fonts, or adjust the card styles.

**Q: How do I change the current customer?**
A: Use the "Current Customer" dropdown at the top of the chat interface. You can select from:
- john.smith@email.com (has laptop issue emails in the system)
- sarah.jones@email.com (has mouse battery question)
- mike.chen@email.com (has delayed monitor order)
- guest@example.com (no history)

## Next Steps

Once you understand these minimal examples:

1. **Read the full solutions:**
   - `extra/mcp_server_full_solution.txt`
   - `extra/rag_agent_full_solution.txt`
   - `extra/gradio_app_solution.txt`

2. **Explore the differences:**
   - See how metrics are tracked
   - Understand the developer mode features
   - Learn about external data loading

3. **Build your own:**
   - Modify these minimal examples
   - Add new tools to the MCP server
   - Add new products to the knowledge base
   - Experiment with different prompts

## Troubleshooting

**Error: "HF_TOKEN not set" or model loading slowly**
```bash
export HF_TOKEN="your-hf-token-here"
```
Note: The first request may take 20-30 seconds as the model loads. Subsequent requests will be faster.

**Error: "Module not found: mcp"**
```bash
pip install -r requirements/requirements.txt
```

**Error: "ChromaDB not found"**
```bash
pip install chromadb
```

**Port 7860 already in use:**
```bash
# Edit gradio_app_minimal.py and change server_port to 7861 or another port
```

## Architecture Diagram

```
📱 User Question: "What's wrong with John's laptop?"
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  Gradio UI: Sends to agent                                 │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  RAG Agent:                                                │
│  1. Search Vector Store: "laptop troubleshooting"          │
│     → Returns: Device Troubleshooting PDF sections         │
│                                                             │
│  2. Detect need for customer context                       │
│     → Calls MCP: search_emails("john")                     │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  MCP Server: search_emails("john")                         │
│  → Searches hardcoded EMAILS list                          │
│  → Returns: 2 emails from john.smith@email.com             │
│     - "Laptop won't turn on" + "Hard reset didn't work"    │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  RAG Agent: Send everything to HF LLM                      │
│  → LLM combines:                                           │
│     - PDF docs (device troubleshooting steps)              │
│     - Email history (customer already tried hard reset)    │
│     - Generates response with next step                    │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  Gradio UI: Shows response to user                         │
│  "I see John tried the hard reset already. Since the       │
│   charging light isn't coming on, this might be a          │
│   hardware issue. Let's arrange a warranty replacement..." │
└────────────────────────────────────────────────────────────┘
```

## Summary

These minimal examples demonstrate:
- RAG (retrieval augmented generation) with real PDF loading
- ChromaDB vector store with semantic search
- MCP (model context protocol) for tool calling
- LLM integration with Hugging Face (Llama 3.1 8B Instruct)
- Clean Gradio chat interface with customer selector
- ~450 lines of well-commented code
- Real-world RAG with PDF documents
- Perfect for learning!
