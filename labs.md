# Capstone Project: Building a Customer Support Chatbot
## Enterprise AI Accelerator Workshop - Day 2 Capstone
## Revision 1.1 - 11/26/25

**Prerequisites:**
- Completed Labs 1-5 in the main workshop (MCP fundamentals, classification server, RAG agent)
- Understanding of MCP protocol, classification workflow, and RAG architecture

**Overview:**
In this capstone project, you will build a complete customer support chatbot with a Gradio web interface. You'll start with classification-enabled MCP server and RAG agent components (similar to what you built in Labs 4-5) and progressively enhance them to create a full-featured application.

**Final Product Features:**
- Web-based chat interface
- Intelligent query classification
- RAG-based knowledge retrieval
- Customer context awareness
- Support ticket creation
- Real-time analytics dashboard
- MCP protocol monitoring

</br></br>

---

**Lab 1 - Setting Up and Testing a Minimal Version**

**Purpose: Verify the starter MCP server and RAG agent work correctly before adding enhancements.**

1. The capstone starter project contains a *minimal version* MCP server and RAG agent. Just to reengage our memory on the basics, let's explore what we have. First, change into the minimal_app subdirectory and let's look at what files we have to work with.

```
cd minimal_app
ls -la
```

   You should see:
   - `mcp_server_minimal.py` - MCP server with classification and knowledge tools
   - `rag_agent_minimal.py` - RAG agent with classification workflow
   - `gradio_app_minimal.py` - Small Gradio interface
   - `minimal_data.json` - data file for the app to use
   - `gradio_minimal_styles.css` - style sheets for gradio web interface
   - `README_MINIMAL.md` - README file about the minimal version
   - `SETUP.md` - A setup doc for the minimal app

<br><br>

2. Let's examine the starter MCP server. Open the file:

```
code mcp_server.py
```

   Scroll through and note the core parts:
   - **Section 1**: DATA LOADING - reads in the sample emails and orders data from the JSON file
   - **Section 2**: MCP SERVER SETUP - defines a tool to list all the tools and one to call a tool
   - **Section 3**: START THE SERVER - allows the server to be started via stdio transport and provides main entry point
  
<br><br>

3. Now examine the RAG agent:

```
code rag_agent_minimal.py
```

   Scroll through and note the core parts:
   - **Section 1**: CONFIGURATION - Specifies model, KB path, and checks for Hugging Face token being in place
   - **Section 2**: AGENT CLASS - Implements a minimal RAG agent with initialization and functions for:
      - `_load_pdf_documents()`: loading and parsing the knowledge base PDF documents
      - `_setup_vector_store()`: creating/refreshing the ChromaDB vector db
      - `connect_mcp()`: connect to MCP server for working with emails and orders (fires up server via stdio)
      - `search_knowledge_base()`: search the vector db for revelant hits
      - `query_llm()`: takes the prompt (with RAG context) and queries the Hugging Face model
      - `query(): the workhorse - searches KB for relevant info, checks to see if need emails/order info, builds augmented prompt, sends it over to LLM and parses and delivers respose    
   - **Section 3**: Interactive mode when run directly

<br><br>

4. Let's run the agent in test mode. This will automatically start the MCP server: (Make sure you've set the *HF_TOKEN* environment variable in the terminal.)

```
python rag_agent_minimal.py
```

   Try these queries:
   - `How do I reset my password?` (should use classification → account_security)
   - `My device won't turn on` (should use classification → device_troubleshooting)
   - `Tell me about OmniTech` (should use direct RAG)

<br>

![Running the agent](./images/aia-3-27.png?raw=true "Running the agent")

<br><br>

5. Observe the workflow output:
   - Searching the knowledge base
   - Getting info from orders (if needed)
   - Generating response with LLM


When done, type `exit` to quit.

<p align="center">
<b>[END OF LAB]</b>
</p>
</br></br>

---

**Lab 2 - Adding a Web Interface**

**Purpose: Add a Gradio interface onto the system.**

1. We've got a pre-configured Gradio interface for our minimal system. Still in the *minimal_app* directory, let's look at the gradio interface.

```
code gradio_app_minimal.py
```

1. In this lab, you'll add customer-related functionality to the MCP server. We'll use the diff-and-merge approach. Open the comparison:

```
code -d mcp_server.py extra/mcp_server_full_solution.txt
```

2. Scroll through and note the various parts.

- GLOBAL STATE: Reads in CSS from (gradio_minimal_styles.css)[./minimal_app/gradio_minimal_styles.css]
- CHAT FUNCTIONS: Implements a `send_message` function to pass the user message on to the agent and get a response
- GRADIO UI: Implements the webpage, buttons, and other controls
- MAIN: Creates and launches the app

<br><br>

3. Now, let's run the gradio app version of the tool. (Again, make sure your Hugging Face token is set.)

```
python gradio_app_minimal.py
```
<br><br>

4. When this starts, you should see a pop-up in the lower right that has a button to click to open the app. If you click that and it instead opens a new codespace instance, just close that new tab, go back and try the process again.

![Running the gradio app](./images/aia-3-27.png?raw=true "Running the gradio app")

<br>

Alternatively, you can get to the running app, by switching to the *PORTS* tab (next to *TERMINAL*) in the codespace, finding the row for the port *7860*, hovering over the second column, and then clicking on the icon that looks like a globe.

![Opening via the PORTS row](./images/aia-3-29.png?raw=true "Opening via the PORTS row")

<br><br>

5. Once the app starts up, you can enter a query in the input area, like "I need to return my headphones".

![Inputting query](./images/aia-3-30.png?raw=true "Inputting query")


6. You should see a response from the chatbot referencing a knowledge base doc.

![RAG response](./images/aia-3-31.png?raw=true "RAG response")


**Lab 2 - Adding a Web Interface**

**Purpose: Add a Gradio interface onto the system.**


  1. Overview & Documentation (Lines 1-78)

  Header documentation explaining what MCP (Model Context Protocol) is, the server's purpose, architecture diagram, and how the client-server
   communication works via stdio/JSON-RPC.

  2. Imports (Lines 80-136)

  Standard library, MCP library, ChromaDB, and pypdf imports with logging configuration.

  3. Section 1: Configuration and Constants (Lines 138-186)

  File paths (KNOWLEDGE_BASE_DIR, CUSTOMER_DB_PATH, SEED_DATA_PATH), LLM configuration, and DOCUMENT_CATEGORIES mapping PDFs to support
  categories.

  4. Section 2: Canonical Query Definitions (Lines 187-332)

  The CANONICAL_QUERIES dictionary defining 5 support categories (account_security, device_troubleshooting, shipping_inquiry,
  returns_refunds, general_support), each with description, prompt template, example queries, and keyword lists for classification.

  5. Section 3: MCP Server Class (Lines 334-1347)

  The OmniTechSupportServer class containing:
  - Database Setup Methods (Lines 391-536): SQLite initialization, schema creation, seeding, and helper queries
  - Knowledge Base Setup (Lines 537-626): PDF loading and ChromaDB vector store initialization
  - Classification Tool Handlers (Lines 627-729): classify_query, get_query_template, list_categories
  - Knowledge Tool Handlers (Lines 731-818): search_knowledge, get_knowledge_for_query
  - Customer Tool Handlers (Lines 820-921): lookup_customer, create_support_ticket
  - Statistics/Ticket Handlers (Lines 923-1046): get_server_stats, get_tickets, request logging
  - Tool Registration (Lines 1047-1212): MCP @list_tools and @call_tool decorator setup
  - Resource Registration (Lines 1213-1347): MCP resources (config://llm, config://database, config://categories, data://tickets)

  6. Section 4: Main Entry Point (Lines 1349-1407)


rag_agent

  1. Header & Imports (Lines 1-36)

  Documentation header describing the full RAG agent with classification workflow, customer context integration, and Gradio support. Includes
   imports for asyncio, MCP client, and HuggingFace InferenceClient.

  2. Section 1: Configuration (Lines 38-67)

  HuggingFace token/model setup (HF_TOKEN, HF_MODEL, HF_CLIENT), SUPPORT_KEYWORDS dictionary for routing queries to categories, and ANSI
  color codes for terminal output.

  3. Section 2: Helper Functions (Lines 69-110)

  - is_support_query(): Determines if a query is support-related vs exploratory using keyword matching and regex patterns
  - unwrap_mcp_result(): Extracts and parses JSON data from MCP result objects

  4. Section 3: RAG Agent Class (Lines 113-543)

  The OmniTechAgent class containing:
  - MCP Connection (Lines 126-164): connect() starts the MCP server subprocess and establishes session; disconnect() cleans up
  - MCP Tool Calls (Lines 165-196): call_tool() invokes MCP tools, logs calls, and handles errors
  - Customer Context (Lines 197-218): get_customer_context() looks up customer info by email for personalization
  - LLM Integration (Lines 219-263): query_llm() calls HuggingFace Inference API with error handling for model loading
  - Classification Workflow (Lines 264-419): handle_support_query() implements the 4-step workflow: classify → get template → retrieve
  knowledge → generate LLM response with optional ticket creation
  - Direct RAG Workflow (Lines 420-518): handle_exploratory_query() handles non-support queries with simple knowledge search
  - Main Query Handler (Lines 519-534): process_query() routes to classification or direct RAG based on is_support_query()
  - Server Stats (Lines 535-543): get_server_stats() fetches MCP server metrics

  5. Section 4: Synchronous Wrapper (Lines 545-600)

  The SyncAgent class wrapping async operations for Gradio integration. Provides synchronous methods (process_query(), get_mcp_log(),
  get_server_stats(), get_available_tools()) by running async code in a dedicated event loop.

  6. Section 5: Command-Line Interface (Lines 602-686)

  The interactive_mode() async function providing a CLI for testing. Supports commands: exit, demo (run sample queries), stats, and email:xxx
   (set customer context). Also the __main__ block that runs the interactive mode.


gradio

  1. Header & Imports (Lines 1-71)

  Documentation header describing the Gradio web interface with 5 tabs (Chat, Agent Dashboard, MCP Monitor, Knowledge Search, Tickets).
  Imports Gradio, JSON, datetime, and attempts to import SyncAgent from rag_agent.py with fallback to demo mode.

  2. Section 1: Application State (Lines 73-173)

  The AppState class managing centralized application state:
  - initialize_agent(): Lazy initialization of the MCP agent
  - process_query(): Routes queries to agent or returns demo response
  - get_mcp_stats(): Fetches server statistics
  - search_knowledge(): Direct knowledge base search via MCP tool
  - get_tickets(): Retrieves tickets with optional filters
  - Also stores conversation history, metrics (total queries, resolved, tickets), and last prompt/response for debugging

  3. Section 2: Custom CSS Styles (Lines 175-295)

  CUSTOM_CSS string containing:
  - Font styling (Inter font family)
  - Debug toggle styling
  - Typing indicator animation (keyframes)
  - .nav-button, .metric-card, .chat-message-user, .chat-message-agent, .tool-card class definitions

  4. Section 3: Helper Functions (Lines 297-683)

  Utility functions for UI operations:
  - format_message(): Formats chat messages as styled HTML
  - process_query_handler(): Main handler for query submission, updates chat history, metrics, and debug info
  - generate_agent_dashboard(): Generates HTML for RAG metrics dashboard with query count, resolution rate, tickets created, and recent RAG
  operations
  - generate_mcp_monitor(): Generates HTML for MCP server stats, available tools list, and recent MCP call log
  - generate_tickets_display(): Generates HTML table of support tickets with status/priority badges and filters
  - clear_chat(): Resets conversation history and metrics
  - get_status(): Returns system status string
  - search_knowledge_direct(): Searches knowledge base and formats results as HTML with similarity bars

  5. Section 4: Gradio Interface Definition (Lines 685-978)

  The complete UI layout using gr.Blocks():
  - Header Row: Title banner with gradient background + Developer Mode checkbox
  - Chat Tab (always visible): Customer dropdown, chat display, message input, send button, quick action buttons
  - Agent Dashboard Tab (Developer Mode): Performance metrics, recent RAG operations, LLM prompt/response debug textboxes
  - MCP Monitor Tab (Developer Mode): Server metrics, available tools list, recent MCP calls
  - Knowledge Search Tab (Developer Mode): Search input, results slider, category cards
  - Tickets Tab (Developer Mode): Customer/status filter dropdowns, ticket list display
  - Footer: Branding and copyright
  - Event Handlers: Debug toggle, send button, submit, clear, quick actions, refresh buttons, tab select auto-refresh, knowledge search,
  ticket filters

  6. Section 5: Main Entry Point (Lines 980-1001)

  The __main__ block that prints a startup banner and launches the Gradio demo on 0.0.0.0:7860 with sharing enabled.

2. As you scroll through, you'll see the additions:
   - **Customer database** (around line 115): A dictionary with sample customers
   - **Ticket storage**: A list to track created tickets
   - **`_handle_lookup_customer()`**: Look up customer by email
   - **`_handle_create_ticket()`**: Create support tickets
   - **`_handle_get_server_stats()`**: Server statistics
   - **Tool registrations**: New tools in `_setup_tools()`

<br><br>

3. Merge each section by clicking the left-pointing arrows:
   - First, merge the `self.customers` dictionary in `__init__`
   - Then merge `self.tickets = []`
   - Merge all three new handler methods
   - Merge the new Tool definitions in `_setup_tools()`
   - Merge the tool routing in `call_tool()`

   Save and close when done.

<br><br>

4. Verify the syntax:

```
python -c "import mcp_server; print('MCP server OK')"
```

<br><br>

5. Now let's update the agent to use customer context. Open the comparison:

```
code -d rag_agent.py extra/rag_agent_full_solution.txt
```

<br><br>

6. Key additions to merge:
   - **`self.available_tools`**: Track available MCP tools
   - **`get_customer_context()`**: New method to build customer context string
   - **Updated `handle_support_query()`**: Includes customer context and ticket creation
   - **Updated `handle_exploratory_query()`**: Includes customer context
   - **`get_server_stats()`**: New method to get server statistics
   - **Updated `SyncAgent`**: New methods for stats and tools

   Merge all changes, save, and close.

<br><br>

7. Verify the agent:

```
python -c "import rag_agent; print('RAG agent OK')"
```

<br><br>

8. Test the enhanced system:

```
python rag_agent.py
```

   Now try:
   - `email:john.doe@email.com` (sets customer context)
   - `How do I reset my password?` (should show customer context in output)
   - `stats` (shows server statistics)

   The agent now knows about the customer and can create tickets when needed.

<p align="center">
<b>[END OF LAB]</b>
</p>
</br></br>

---

**Lab 3 - Building the Gradio Web Interface**

**Purpose: Create a web-based chat interface using Gradio.**

1. Now we'll add a Gradio interface. First, let's create a starter file:

```
code gradio_app.py
```

<br><br>

2. Add this basic structure to get started:

```python
#!/usr/bin/env python3
"""
OmniTech Customer Support Chatbot - Gradio Interface
"""

import gradio as gr
import json
from datetime import datetime
from typing import Dict, List, Any

# Import the agent
try:
    from rag_agent import SyncAgent
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    print("Warning: rag_agent not found")

# Application state
class AppState:
    def __init__(self):
        self.agent = None
        self.conversation_history = []
        self.metrics = {'total_queries': 0, 'resolved_queries': 0}

    def initialize_agent(self):
        if AGENT_AVAILABLE and not self.agent:
            try:
                self.agent = SyncAgent()
                return True
            except Exception as e:
                print(f"Agent init failed: {e}")
        return False

app_state = AppState()

# TODO: Add interface components in next steps

if __name__ == "__main__":
    print("Starting Gradio app...")
    # demo.launch() - will add after building interface
```

   Save the file.

<br><br>

3. Now let's use the full solution to build out the interface. Open the comparison:

```
code -d gradio_app.py extra/gradio_app_solution.txt
```

<br><br>

4. This is a larger merge. Work through it section by section:

   **Section 1 - AppState class**: Merge the complete `AppState` class with all methods

   **Section 2 - CSS**: Merge the `CUSTOM_CSS` constant

   **Section 3 - Helper functions**: Merge `format_message()`, `process_query_handler()`, `generate_agent_dashboard()`, `generate_mcp_monitor()`, `clear_chat()`, `get_status()`

   **Section 4 - Gradio interface**: Merge the entire `with gr.Blocks(...) as demo:` block

   **Section 5 - Main**: Merge the `if __name__ == "__main__":` block

   Save and close when done.

<br><br>

5. Verify the app:

```
python -c "import gradio_app; print('Gradio app OK')"
```

<br><br>

6. Launch the chatbot!

```
python gradio_app.py
```

Since we're running in a Codespace, use the public Gradio link (the *.gradio.live URL) shown in the terminal to access the interface.

<br><br>

7. Test the interface:
   - Select a customer email from the dropdown
   - Type "How do I reset my password?" and click Send
   - Click the **Agent Dashboard** button to see RAG analytics
   - Click **MCP Monitor** to see server statistics and available tools
   - Try the Quick Action buttons

<br><br>

8. Observe the **Debug Info** section at the bottom of the chat view:
   - **LLM Prompt**: Shows the complete prompt sent to the model
   - **Full Response**: Shows the JSON response with metadata

   This transparency helps debug and understand the RAG pipeline.

<p align="center">
<b>[END OF LAB]</b>
</p>
</br></br>

---

**Lab 4 - Understanding the Complete Architecture**

**Purpose: Review the full system architecture and understand how components interact.**

1. Let's trace through a complete query to understand the architecture:

```
User types: "How do I reset my password?"
     ↓
Gradio UI (gradio_app.py)
     ↓ process_query_handler()
SyncAgent.process_query()
     ↓ is_support_query() returns True
OmniTechAgent.handle_support_query()
     ↓
MCP Server (via stdio)
     │
     ├─→ classify_query("How do I reset my password?")
     │   └─→ Returns: {suggested_query: "account_security", confidence: 0.85}
     │
     ├─→ get_query_template("account_security")
     │   └─→ Returns: {template: "You are an OmniTech specialist...", description: "..."}
     │
     ├─→ get_knowledge_for_query("account_security", "password reset")
     │   └─→ Returns: {knowledge: "...", sources: ["OmniTech_Account_Security_Handbook.pdf"]}
     │
     └─→ lookup_customer("john.doe@email.com")
         └─→ Returns: {name: "John Doe", tier: "Premium", ...}
     ↓
Agent formats prompt with template + knowledge + customer context
     ↓
HuggingFace Inference API
     ↓
Response displayed in Gradio UI
```

<br><br>

2. Open all three files side by side to see the full stack:

```
code mcp_server.py rag_agent.py gradio_app.py
```

<br><br>

3. Key architectural principles demonstrated:

   **Separation of Concerns:**
   - MCP Server: Data layer (knowledge, customers, tickets)
   - RAG Agent: Orchestration layer (workflow, LLM interaction)
   - Gradio App: Presentation layer (UI, user interaction)

   **MCP Protocol Benefits:**
   - Tools are discoverable (`list_tools()`)
   - Schema validation on tool calls
   - Standardized error handling
   - Logging and monitoring built-in

   **Classification Workflow Benefits:**
   - Accurate routing to relevant documentation
   - Category-specific prompt templates
   - Consistent response quality
   - Focused knowledge retrieval

<br><br>

4. Experiment with modifications:

   **Add a new support category:**

   In `mcp_server.py`, add to `CANONICAL_QUERIES`:
   ```python
   "billing_inquiry": {
       "description": "Billing, payments, and invoices",
       "prompt_template": """You are an OmniTech billing specialist...""",
       "example_queries": ["What payment methods do you accept?"],
       "keywords": ["bill", "payment", "invoice", "charge", "credit card"]
   }
   ```

   **Add a new customer:**

   In `mcp_server.py`, add to `self.customers`:
   ```python
   "test@example.com": {
       "name": "Test User",
       "tier": "Standard",
       "orders": [],
       "support_tickets": 0
   }
   ```

   Restart the app and test your changes!

<br><br>

5. When done exploring, stop the Gradio server with CTRL+C.

<p align="center">
<b>[END OF LAB]</b>
</p>
</br></br>

---

**Lab 5 - Deployment Preparation (Optional)**

**Purpose: Prepare the chatbot for deployment to Hugging Face Spaces.**

1. For deployment, we need to create a few additional files. First, create an `app.py` entry point:

```
code app.py
```

   Add:
```python
#!/usr/bin/env python3
"""Entry point for HF Spaces deployment."""
import os
os.environ['PDF_DIRECTORY'] = './knowledge_base_pdfs'

from gradio_app import demo

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
```

<br><br>

2. Create a `README.md` for Hugging Face Spaces:

```
code README.md
```

   Add:
```markdown
---
title: OmniTech Support Chatbot
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.19.0
app_file: app.py
pinned: false
---

# OmniTech Customer Support Chatbot

AI-powered customer support with:
- Intelligent query classification
- RAG-based knowledge retrieval
- MCP protocol integration
- Real-time analytics
```

<br><br>

3. The project structure for deployment:

```
capstone-starter/
├── app.py                 # Entry point
├── gradio_app.py          # Main Gradio interface
├── rag_agent.py           # RAG agent
├── mcp_server.py          # MCP server
├── knowledge_base_pdfs/   # PDF documents
├── requirements.txt       # Dependencies
└── README.md              # HF Spaces config
```

<br><br>

4. To deploy to Hugging Face Spaces:
   - Create a new Space at huggingface.co/spaces
   - Select Gradio as the SDK
   - Upload all files or connect a Git repository
   - The app will automatically build and deploy

<p align="center">
<b>[END OF LAB]</b>
</p>
</br></br>

---

**Lab 6 - Adding a New Support Category (Optional)**

**Purpose: Extend the classification system by adding a new "billing_inquiry" category.**

1. The classification system uses the `CANONICAL_QUERIES` dictionary to define support categories. Each category has:
   - A description
   - A prompt template for the LLM
   - Example queries for classification
   - Keywords for matching

   Let's add a new billing category. Open the MCP server:

```
code mcp_server.py
```

<br><br>

2. Find the `CANONICAL_QUERIES` dictionary (around line 30) and add the new category after `general_support`:

```python
    "billing_inquiry": {
        "description": "Questions about billing, payments, invoices, and charges",
        "prompt_template": """You are an OmniTech billing specialist helping a customer with their billing inquiry.

Context about our billing policies:
- We accept all major credit cards, PayPal, and bank transfers
- Invoices are generated monthly on the 1st
- Payment is due within 30 days of invoice date
- Late payments may incur a 1.5% monthly fee
- Refunds are processed within 5-7 business days

Customer's billing question: {query}

Relevant billing information:
{context}

Provide clear, helpful information about their billing inquiry. If they need to make changes to their payment method or dispute a charge, explain the process step by step.""",
        "example_queries": [
            "What payment methods do you accept?",
            "When is my payment due?",
            "I see an unexpected charge on my account",
            "How do I update my credit card?",
            "Can I get a copy of my invoice?"
        ],
        "keywords": ["bill", "billing", "payment", "invoice", "charge", "credit card", "pay", "price", "cost", "fee", "refund"]
    }
```

   Save the file.

<br><br>

3. Verify the syntax:

```
python -c "import mcp_server; print(f'Categories: {len(mcp_server.CANONICAL_QUERIES)}')"
```

   You should see `Categories: 6` (up from 5).

<br><br>

4. Test the new category. Start the agent:

```
python rag_agent.py
```

   Try these billing queries:
   - `What payment methods do you accept?`
   - `I see an unexpected charge on my bill`
   - `When is my next payment due?`

   You should see `[1/4] Classifying...` identify these as `billing_inquiry`.

<br><br>

5. The classification works because:

   **Keyword Matching**: The `_find_best_category()` method scores queries against keywords:
   ```python
   # In mcp_server.py _find_best_category()
   for keyword in info["keywords"]:
       if keyword in query_lower:
           keyword_score += 1
   ```

   **Example Similarity**: It also compares against example queries using basic text overlap.

<br><br>

6. (Optional) Add a billing-specific customer to test context. In `mcp_server.py`, find the `self.customers` dictionary and add:

```python
        "billing@example.com": {
            "name": "Alex Finance",
            "account_id": "CUST-2024-004",
            "tier": "Enterprise",
            "payment_method": "Invoice (NET-30)",
            "outstanding_balance": 1250.00,
            "last_payment_date": "2024-10-15",
            "orders": [
                {"id": "ORD-401", "product": "OmniHub Enterprise", "amount": 2499.00, "date": "2024-09-01"},
                {"id": "ORD-402", "product": "Annual Support Plan", "amount": 999.00, "date": "2024-09-01"}
            ],
            "support_tickets": 1
        }
```

<br><br>

7. (Optional) Add a quick action button in the Gradio interface. In `gradio_app.py`, find the Quick Actions row and add:

```python
                with gr.Row():
                    q1 = gr.Button("Password Reset")
                    q2 = gr.Button("Device Issue")
                    q3 = gr.Button("Return Policy")
                    q4 = gr.Button("Track Order")
                    q5 = gr.Button("Billing Question")  # Add this
```

   And add the click handler with the others:
```python
    q5.click(lambda: "What payment methods do you accept?", outputs=query_input)
```

<br><br>

8. Restart the Gradio app and test the complete flow:
   - Select "billing@example.com" from the dropdown (if you added the customer)
   - Click the "Billing Question" button (if you added it)
   - Observe the classification workflow handling the billing category

<p align="center">
<b>[END OF LAB]</b>
</p>
</br></br>

---

## Summary

You have built a complete customer support chatbot with:

✅ **MCP Server** providing:
- Query classification into 5+ support categories (extensible via Lab 6)
- Category-specific prompt templates
- RAG-based knowledge retrieval
- Customer database lookup
- Support ticket creation
- Server statistics

✅ **RAG Agent** with:
- Intelligent query routing (support vs. exploratory)
- 4-step classification workflow
- Customer context integration
- HuggingFace API integration
- Synchronous wrapper for Gradio

✅ **Gradio Interface** featuring:
- Customer chat view with email selection
- Agent dashboard with RAG analytics
- MCP protocol monitor
- Knowledge base search view
- Debug information display
- Quick action buttons

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           Gradio Web Interface                               │
│  ┌────────┐  ┌────────────────┐  ┌─────────────┐  ┌───────────────────┐     │
│  │  Chat  │  │ Agent Dashboard│  │ MCP Monitor │  │ Knowledge Search  │     │
│  └───┬────┘  └───────┬────────┘  └──────┬──────┘  └─────────┬─────────┘     │
└──────┼───────────────┼──────────────────┼───────────────────┼────────────────┘
       │               │                  │                   │
       └───────────────┴──────────────────┴───────────────────┘
                                  │
                       ┌──────────▼──────────┐
                       │     SyncAgent       │
                       │  (rag_agent.py)     │
                       └──────────┬──────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
           ┌────▼────┐      ┌─────▼─────┐     ┌─────▼─────┐
           │Classify │      │  Retrieve │     │  Customer │
           │ Query   │      │ Knowledge │     │  Lookup   │
           └────┬────┘      └─────┬─────┘     └─────┬─────┘
                │                 │                 │
                └─────────────────┼─────────────────┘
                                  │
                       ┌──────────▼──────────┐
                       │     MCP Server      │
                       │  (mcp_server.py)    │
                       │                     │
                       │  ┌───────────────┐  │
                       │  │   ChromaDB    │  │
                       │  │ (Knowledge)   │  │
                       │  └───────────────┘  │
                       │                     │
                       │  ┌───────────────┐  │
                       │  │   Customers   │  │
                       │  │   Tickets     │  │
                       │  └───────────────┘  │
                       └─────────────────────┘
```

### Next Steps

- Integrate with a real LLM (Ollama, OpenAI, Anthropic)
- Add conversation history persistence
- Implement user authentication
- Add more sophisticated analytics
- Create additional support categories (see Lab 6 for the pattern)

**Congratulations on completing the capstone project!**

</br></br>

---

**THE END**
