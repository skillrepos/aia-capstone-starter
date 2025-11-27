# Capstone Project: Building a Customer Support Chatbot
## Enterprise AI Accelerator Workshop - Day 3 Capstone
## Revision 1.3 - 11/26/25

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

**Lab 1 - Setting Up and Testing a Minimum Viable Product**

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


<p align="center">
<b>[END OF LAB]</b>
</p>
</br></br>


**Lab 3 - The Full MCP Server**

**Purpose: Building out the full MCP server for the enhanced app.**


1. In this lab, we'll use the usual compare and merge process to build out the full version of the MCP Server with the following features:

- Query classification into 5+ support categories (extensible via Lab 6)
- Category-specific prompt templates
- RAG-based knowledge retrieval
- Customer database lookup
- Support ticket creation
- Server statistics

<br><br>

2. Start the process by running the command below.

```
code -d extra/mcp_server_full_solution.txt mcp_server.py
```

<br>

![Updating full server](./images/aia-3-32.png?raw=true "Updating full server")

<br><br>

3. This is a large file with a lot of pieces. Just proceed through and observe and merge, being careful to merge all the changes. The information is just fyi if you're interested in what is implemented where in the code.

  A. **Overview & Documentation** (Lines 1-78)

  Header documentation explaining what MCP (Model Context Protocol) is, the server's purpose, architecture diagram, and how the client-server
   communication works via stdio/JSON-RPC.

  
  B. **Imports** (Lines 80-136)

  Standard library, MCP library, ChromaDB, and pypdf imports with logging configuration.

  
  C. **Section 1: Configuration and Constants** (Lines 138-186)

  File paths (KNOWLEDGE_BASE_DIR, CUSTOMER_DB_PATH, SEED_DATA_PATH), LLM configuration, and DOCUMENT_CATEGORIES mapping PDFs to support
  categories.

  D. **Section 2: Canonical Query Definitions** (Lines 187-332)

  The CANONICAL_QUERIES dictionary defining 5 support categories (account_security, device_troubleshooting, shipping_inquiry,
  returns_refunds, general_support), each with description, prompt template, example queries, and keyword lists for classification.

  E. **Section 3: MCP Server Class** (Lines 334-1347)

  The OmniTechSupportServer class containing:
  - `Database Setup Methods` (Lines 391-536): SQLite initialization, schema creation, seeding, and helper queries
  - `Knowledge Base Setup` (Lines 537-626): PDF loading and ChromaDB vector store initialization
  - `Classification Tool Handlers` (Lines 627-729): classify_query, get_query_template, list_categories
  - `Knowledge Tool Handlers` (Lines 731-818): search_knowledge, get_knowledge_for_query
  - `Customer Tool Handlers` (Lines 820-921): lookup_customer, create_support_ticket
  - `Statistics/Ticket Handlers` (Lines 923-1046): get_server_stats, get_tickets, request logging
  - `Tool Registration` (Lines 1047-1212): MCP @list_tools and @call_tool decorator setup
  - `Resource Registration` (Lines 1213-1347): MCP resources (config://llm, config://database, config://categories, data://tickets)

  F. **Section 4: Main Entry Point** (Lines 1349-1407)

<br><br>

4. Once you've merged the code, you can close the diff tab as usual.

<br><br>

5. When done, you can verify the syntax is valid with the command below:

```
python -c "import mcp_server; print('MCP server OK')"
```

![Verifying syntax](./images/aia-3-33.png?raw=true "Verifying syntax")

<p align="center">
<b>[END OF LAB]</b>
</p>
</br></br>

**Lab 4 - The Full RAG Agent**

**Purpose: Building out the full RAG agent for the enhanced app.**


1. In this lab, we'll use the usual compare and merge process to build out the full version of the RAG agent with the following features:

- Intelligent query routing (support vs. exploratory)
- 4-step classification workflow
- Customer context integration
- HuggingFace API integration
- Synchronous wrapper for Gradio
  
<br><br>


2. Start the process by running the command below.
   
```
code -d extra/mcp_server_full_solution.txt mcp_server.py
```

<br>

![Updating full agent](./images/aia-3-34.png?raw=true "Updating full agent")

<br><br>

3. This is a large file with a lot of pieces. Just proceed through and observe and merge, being careful to merge all the changes. The information is just fyi if you're interested in what is implemented where in the code.


  A. **Header & Imports** (Lines 1-36)

  Documentation header describing the full RAG agent with classification workflow, customer context integration, and Gradio support. Includes
   imports for asyncio, MCP client, and HuggingFace InferenceClient.

  B. **Section 1: Configuration** (Lines 38-67)

  HuggingFace token/model setup (HF_TOKEN, HF_MODEL, HF_CLIENT), SUPPORT_KEYWORDS dictionary for routing queries to categories, and ANSI
  color codes for terminal output.

  C. **Section 2: Helper Functions** (Lines 69-110)

  - is_support_query(): Determines if a query is support-related vs exploratory using keyword matching and regex patterns
  - unwrap_mcp_result(): Extracts and parses JSON data from MCP result objects

  D. **Section 3: RAG Agent Class** (Lines 113-543)

  The OmniTechAgent class containing:
  - `MCP Connection` (Lines 126-164): connect() starts the MCP server subprocess and establishes session; disconnect() cleans up
  - `MCP Tool Calls` (Lines 165-196): call_tool() invokes MCP tools, logs calls, and handles errors
  - `Customer Context` (Lines 197-218): get_customer_context() looks up customer info by email for personalization
  - `LLM Integration` (Lines 219-263): query_llm() calls HuggingFace Inference API with error handling for model loading
  - `Classification Workflow` (Lines 264-419): handle_support_query() implements the 4-step workflow: classify → get template → retrieve
  knowledge → generate LLM response with optional ticket creation
  - `Direct RAG Workflow` (Lines 420-518): handle_exploratory_query() handles non-support queries with simple knowledge search
  - `Main Query Handler` (Lines 519-534): process_query() routes to classification or direct RAG based on is_support_query()
  - `Server Stats` (Lines 535-543): get_server_stats() fetches MCP server metrics

  E. **Section 4: Synchronous Wrapper** (Lines 545-600)

  The SyncAgent class wrapping async operations for Gradio integration. Provides synchronous methods (process_query(), get_mcp_log(),
  get_server_stats(), get_available_tools()) by running async code in a dedicated event loop.

  F. **Section 5: Command-Line Interface** (Lines 602-686)

  The interactive_mode() async function providing a CLI for testing. Supports commands: exit, demo (run sample queries), stats, and email:xxx
   (set customer context). Also the __main__ block that runs the interactive mode.


4. Once you've merged the code, you can close the diff tab as usual.

<br><br>

5. When done, you can verify the syntax is valid with the command below:

```
python -c "import rag_agent; print('RAG agent OK')"
```

![Verifying syntax](./images/aia-3-33.png?raw=true "Verifying syntax")

<p align="center">
<b>[END OF LAB]</b>
</p>
</br></br>


**Lab 5 - The Full Gradio Interface**

**Purpose: Building out the full Gradio interface for the enhanced app.**


1. In this lab, we'll use the usual compare and merge process to build out the full version of the Gradio interface with the following features:

- Customer chat view with email selection
- *Developer mode* toggle to see additional functionality
- Agent dashboard with RAG analytics
- MCP protocol monitor
- Knowledge base search view
- Ticket list
- Quick action buttons
  
<br><br>


2. Start the process by running the command below.
   
```
code -d extra/gradio_app_solution.txt gradio_app.py
```

<br><br>

3. This is a large file with a lot of pieces. Just proceed through and observe and merge, being careful to merge all the changes. The information is just fyi if you're interested in what is implemented where in the code.

![Updating full interface](./images/aia-3-35.png?raw=true "Updating full interface")

<br><br>

  A. **Header & Imports** (Lines 1-71)

  Documentation header describing the Gradio web interface with 5 tabs (Chat, Agent Dashboard, MCP Monitor, Knowledge Search, Tickets).
  Imports Gradio, JSON, datetime, and attempts to import SyncAgent from rag_agent.py with fallback to demo mode.

  B. **Section 1: Application State** (Lines 73-173)

  The AppState class managing centralized application state:
  - `initialize_agent()`: Lazy initialization of the MCP agent
  - `process_query()`: Routes queries to agent or returns demo response
  - `get_mcp_stats()`: Fetches server statistics
  - `search_knowledge()`: Direct knowledge base search via MCP tool
  - `get_tickets()`: Retrieves tickets with optional filters
  - Also stores conversation history, metrics (total queries, resolved, tickets), and last prompt/response for debugging

  3. **Section 2: Custom CSS Styles** (Lines 175-295)

  CUSTOM_CSS string containing:
  - Font styling (Inter font family)
  - Debug toggle styling
  - Typing indicator animation (keyframes)
  - .nav-button, .metric-card, .chat-message-user, .chat-message-agent, .tool-card class definitions

  4. **Section 3: Helper Functions** (Lines 297-683)

  Utility functions for UI operations:
  - `format_message()`: Formats chat messages as styled HTML
  - `process_query_handler()`: Main handler for query submission, updates chat history, metrics, and debug info
  - `generate_agent_dashboard()`: Generates HTML for RAG metrics dashboard with query count, resolution rate, tickets created, and recent RAG
  operations
  - `generate_mcp_monitor()`: Generates HTML for MCP server stats, available tools list, and recent MCP call log
  - `generate_tickets_display()`: Generates HTML table of support tickets with status/priority badges and filters
  - `clear_chat()`: Resets conversation history and metrics
  - `get_status()`: Returns system status string
  - `search_knowledge_direct()`: Searches knowledge base and formats results as HTML with similarity bars

  5. **Section 4: Gradio Interface Definition** (Lines 685-978)

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

  6. **Section 5: Main Entry Point** (Lines 980-1001)

<br><br>

4. Once you've merged the code, you can close the diff tab as usual.

<br><br>

5. When done, you can run the full application to see it in action! You should see a pop-up with a button to click to open the webpage. Click on that. If it starts another version of the codespace, just close that, kill the running python process and run again. The second time it should startup.

```
python gradio_app
```
<br>

![Running full app](./images/aia-3-36.png?raw=true "Running full app")

<br><br>


6. Now you can enter a message into the chat interface like:

```
I need to return my headphones
```

![Input](./images/aia-3-37.png?raw=true "Input")

<br><br>

7. When you click on *Send Message*, the app will go off and search in the RAG docs and find information about the topic and then build a prompt for the LLM to process. After the LLM processes it, it will return a response.


![Response](./images/aia-3-38.png?raw=true "Response")

<br><br>

8. Click on the *Developer Mode* checkbox in the upper right. This will enable additional tabs with more information about the running app and what it has done. You'll see new tabs for *Agent Dashboard*, *MCP Monitor*, *Knowledge Search*, and *Tickets*.


![Dev mode](./images/aia-3-39.png?raw=true "Dev mode")

<br><br>

9. If you click on the *Agent Dashboard*, you'll see statistics about the total queries, resolution rate, and # of tickets at the top. Then below that, you'll see info on recent RAG opertions. At the bottom, on the left you'll see the full prompt with RAG info that was constructed and sent to the LLM. On the bottom right, you'll see the full response from the LLM.

![Agent dashboard](./images/aia-3-44.png?raw=true "Agent dashboard")

<br><br>

10. Clicking on the *MCP Monitor* dashboard shows total requests and some other info at the top. Then you'll see recent MCP calls. Further down this shows the available MCP calls.

![MCP monitor](./images/aia-3-45.png?raw=true "MCP monitor")

<br><br>

11. The *Knowledge Search* tab lets you see search the RAG datastore to see what matching items are found and how similar they are.

![Knowledge Search](./images/aia-3-46.png?raw=true "Knowledge Search")

<br><br>

12. Finally, the *Tickets* tab shows information about any support tickets that have been created by the system automatically.

![Knowledge Search](./images/aia-3-47.png?raw=true "Knowledge Search")

When done running the app, you can stop the gradio instance that's running in the terminal and close the app page.

<br><br>

<p align="center">
<b>[END OF LAB]</b>
</p>
</br></br>


**Lab 6 - Deploying to Hugging Face**

**Purpose: Deploying the full app into a Hugging Face Space.**

1. You will need the Hugging Face userid and token value that you created in the README at the beginning of the labs. Make sure you have those handy.

<br><br>

2. Make sure you are logged into huggingface.co. Go to [https://huggingface.co/spaces](https://huggingface.co/spaces) and click on the *New Space* button on the right.

![New space](./images/aia-3-48.png?raw=true "New space")

<br><br>

3. On the form for the new Space, provide a name, optionally a description and license. Make sure Gradio is selected as the *Space SDK*. You can just accept the rest of the defaults on that page. Scroll to the bottom and click to save the Space.

![New space](./images/aia-3-50.png?raw=true "New space")

<br><br>

4. While you are on that space, we need to setup a secret with our HF token. Click on the *Settings* link on the top right.

![Settings](./images/aia-3-51.png?raw=true "Settings")

<br><br>


5. On the Settings page, scroll down until you find the *Variables and secrets* section. Then click on *New secret*.

![Settings](./images/aia-3-52.png?raw=true "Settings")

<br><br>

6. In the dialog, provide the name, description, and your actual token value, then click *Save*.


![Secret values](./images/aia-3-9.png?raw=true "Secret values")


<br><br>

7. Now, in the root of the project in a terminal in the codespace, run the following commands to get setup to update the space. Replace HF_USERID with your actual Hugging Face userid.

```
git clone https://huggingface.co/spaces/*HF_USERID*/capstone
cd capstone
```

<br><br>

8. We have a script to get files setup for Hugging Face deployment. Run the script from this directory as follows:

```
../scripts/prepare_hf_spaces.sh .
```

This should copy necessary files over that are needed for the deployment. It also sets up a README file with some needed values.

<br><br>

9. Now, you can do the usual Git commands to get your files into the new space.

```
git add .
git commit -m "initial commit"
git push
```

<br><br>

10. When you run that last command, VS Code/the codespace will prompt you at the *top* of the screen for your Hugging Face username. Enter your username there and hit *Enter*.

![Enter HF username](./images/aia-3-53.png?raw=true "Enter HF username")

<br><br>

11. You will then be prompted for your password. **This is your Hugging Face token value.** Just copy and paste the token value into the box.

![Enter HF token](./images/aia-3-54.png?raw=true "Enter HF token")

<br><br>

12. Switch back to your Space on Hugging Face and click on the *App* link at the top. You should see that your app is in the process of building.

![App building](./images/aia-3-55.png?raw=true "App building")

<br><br>

13. After a bit of time, the app screen should refresh and show the running app. You can click on it to start using it.

![App running](./images/aia-3-56.png?raw=true "App running")

<br><br>

14. Now, you can interact with the app as you did when running it local.

![App interaction](./images/aia-3-57.png?raw=true "App interaction")

<br><br>

<p align="center">
<b>[END OF LAB]</b>
</p>
</br></br>


 

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
