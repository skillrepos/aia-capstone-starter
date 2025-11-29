#!/usr/bin/env python3
"""
Minimal RAG Agent for OmniTech Support
=======================================

This simplified version demonstrates:
- RAG (Retrieval Augmented Generation): Loading PDFs and using semantic search
- MCP Integration: Calling tools to fetch emails and orders
- LLM Chat: Using Hugging Face models to generate helpful responses

Key Components:
1. PDF Loading: Extracts text from PDF files in knowledge_base_pdfs/
2. Vector Store (ChromaDB): Stores PDF content with embeddings for semantic search
3. MCP Client: Connects to our MCP server to search emails/orders
4. LLM (Hugging Face): Generates natural, helpful responses

Perfect for learning how real RAG + MCP work together!
"""

import os
import re
import json
from pathlib import Path
from huggingface_hub import InferenceClient
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import chromadb
from chromadb.utils import embedding_functions
import pypdf

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Hugging Face setup
HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
HF_CLIENT = InferenceClient(token=HF_TOKEN) if HF_TOKEN else None

if not HF_TOKEN:
    print("WARNING: HF_TOKEN not set. LLM calls will be limited.")
    print("Set it with: export HF_TOKEN='your_token_here'")
    print("Get a token from: https://huggingface.co/settings/tokens")
    print()

# Knowledge base directory - where the PDF files live (in parent directory)
KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent / "knowledge_base_pdfs"

# ═══════════════════════════════════════════════════════════════════════════
# CLASSIFICATION KEYWORDS (for determining query category)
# ═══════════════════════════════════════════════════════════════════════════

# Keywords that indicate specific support categories
CATEGORY_KEYWORDS = {
    "account_security": [
        "password", "reset", "login", "account", "locked", "security",
        "authentication", "sign in", "signin", "log in", "2fa", "two-factor"
    ],
    "device_troubleshooting": [
        "won't turn on", "not working", "broken", "device", "repair",
        "troubleshoot", "fix", "error", "crash", "frozen", "battery",
        "charging", "screen", "power", "restart", "reboot"
    ],
    "shipping_inquiry": [
        "shipping", "delivery", "tracking", "ship", "arrive", "eta",
        "where is my", "transit", "carrier"
    ],
    "returns_refunds": [
        "return", "refund", "exchange", "money back", "warranty",
        "replacement", "defective"
    ]
}

def classify_query(query: str) -> tuple[str, str]:
    """
    Classify a query into a category based on keywords.

    Returns:
        Tuple of (workflow_type, category_name)
        workflow_type: "classification" or "direct_rag"
        category_name: The detected category or "general_inquiry"
    """
    query_lower = query.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in query_lower:
                return ("classification", category)

    # No specific category matched - use direct RAG
    return ("direct_rag", "general_inquiry")

# ═══════════════════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════════════════

class SyncAgent:
    """
    Minimal RAG Agent that:
    1. Searches knowledge base for relevant info
    2. Can use MCP tools to search emails/orders
    3. Generates helpful responses using Hugging Face LLMs
    """

    def __init__(self, verbose: bool = False):
        """Initialize the agent with vector store and LLM

        Args:
            verbose: If True, print detailed workflow information (for CLI mode)
        """
        self.verbose = verbose

        # Conversation history for multi-turn context
        # Stores recent exchanges as list of {"user": str, "assistant": str}
        self.conversation_history = []
        self.max_history = 3  # Keep last 3 exchanges for context

        # Initialize vector store
        self._setup_vector_store()

        # MCP session (will be set when connecting)
        self.mcp_session = None
        self.mcp_tools = []

    def clear_history(self):
        """Clear conversation history to start fresh."""
        self.conversation_history = []
        if self.verbose:
            print("[HISTORY] Conversation history cleared")

    def _load_pdf_documents(self):
        """Load and parse PDF documents from knowledge base directory."""
        documents = []

        if not KNOWLEDGE_BASE_DIR.exists():
            print(f"✗ Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}")
            print("  Please ensure knowledge_base_pdfs/ directory exists with PDF files")
            return documents

        print(f"Loading PDFs from: {KNOWLEDGE_BASE_DIR}")

        for filename in os.listdir(KNOWLEDGE_BASE_DIR):
            if not filename.endswith('.pdf'):
                continue

            file_path = KNOWLEDGE_BASE_DIR / filename

            try:
                with open(file_path, 'rb') as f:
                    pdf_reader = pypdf.PdfReader(f)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + " "

                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text.strip())

                documents.append({
                    "id": filename.replace('.pdf', ''),
                    "text": text,
                    "source": filename
                })

                print(f"  ✓ Loaded: {filename} ({len(text)} chars)")

            except Exception as e:
                print(f"  ✗ Failed to load {filename}: {e}")

        return documents

    def _setup_vector_store(self):
        """Set up ChromaDB with PDF documentation (real RAG!)"""

        # Create ChromaDB client
        chroma_client = chromadb.Client()

        # Use default embedding function
        embedding_function = embedding_functions.DefaultEmbeddingFunction()

        # Try to delete old collection if it exists
        try:
            chroma_client.delete_collection("omnitech_docs_minimal")
        except:
            pass

        # Create fresh collection
        self.collection = chroma_client.create_collection(
            name="omnitech_docs_minimal",
            embedding_function=embedding_function
        )

        # Load PDF documents
        documents = self._load_pdf_documents()

        if not documents:
            print("✗ No documents loaded! RAG will not work properly.")
            return

        # Add documents to vector store
        for doc in documents:
            self.collection.add(
                documents=[doc["text"]],
                metadatas=[{"source": doc["source"]}],
                ids=[doc["id"]]
            )

        print(f"✓ Knowledge base ready: {self.collection.count()} documents loaded")

    async def connect_mcp(self):
        """Connect to the MCP server to access email/order tools"""

        server_params = StdioServerParameters(
            command="python3",
            args=["mcp_server_minimal.py"],
            env=None
        )

        # Create MCP client session
        self.stdio_transport = stdio_client(server_params)
        self.stdio, self.write = await self.stdio_transport.__aenter__()
        self.mcp_session = ClientSession(self.stdio, self.write)

        await self.mcp_session.__aenter__()
        await self.mcp_session.initialize()

        # Get available tools
        response = await self.mcp_session.list_tools()
        self.mcp_tools = response.tools

        print(f"✓ Connected to MCP server with {len(self.mcp_tools)} tools")

    async def cleanup(self):
        """Clean up MCP connection"""
        if self.mcp_session:
            await self.mcp_session.__aexit__(None, None, None)
        if hasattr(self, 'stdio_transport'):
            await self.stdio_transport.__aexit__(None, None, None)

    def search_knowledge_base(self, query: str, n_results: int = 2) -> str:
        """
        Search the vector store for relevant documentation.

        Args:
            query: User's question
            n_results: How many relevant docs to retrieve

        Returns:
            Relevant documentation as a string
        """

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        if not results['documents'] or not results['documents'][0]:
            return "No relevant documentation found."

        # Combine retrieved documents WITH source attribution
        docs_with_sources = []
        for i, doc in enumerate(results['documents'][0]):
            source = results['metadatas'][0][i].get('source', 'Unknown')
            docs_with_sources.append(f"[Source: {source}]\n{doc}")

        context = "\n\n---\n\n".join(docs_with_sources)
        return context

    def query_llm(self, prompt: str) -> str:
        """
        Query Hugging Face LLM to generate a response.

        Args:
            prompt: The full prompt including context and question

        Returns:
            LLM's response text
        """

        if not HF_CLIENT:
            # Fallback response if no HF token
            return json.dumps({
                "response": "I found relevant information in our knowledge base. However, the AI model is not configured. Please set HF_TOKEN to get AI-generated responses.",
                "action_needed": "none",
                "confidence": 0.5
            })

        try:
            # Use chat_completion for instruct models
            response = HF_CLIENT.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=HF_MODEL,
                max_tokens=500,
                temperature=0.7
            )

            # Extract the response text
            result_text = response.choices[0].message.content
            return result_text

        except Exception as e:
            error_msg = str(e)

            # Check for model loading (503)
            if "503" in error_msg or "loading" in error_msg.lower():
                return json.dumps({
                    "response": "The AI model is warming up. Please try again in a moment (this can take 20-30 seconds for the first request).",
                    "action_needed": "none",
                    "confidence": 0.5
                })

            # General error fallback
            return json.dumps({
                "response": "I encountered an error generating a response. Please try again.",
                "action_needed": "none",
                "confidence": 0.3
            })

    async def query(self, user_message: str) -> str:
        """
        Main query function - this is where the magic happens!

        Process:
        1. Classify the query to determine workflow
        2. Search knowledge base for relevant info
        3. Check if we need to search emails/orders
        4. Send everything to HF LLM to generate response
        """

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Processing: {user_message[:50]}...")
            print(f"{'='*60}")

            # Step 0: Classify the query
            workflow_type, category = classify_query(user_message)
            print(f"\n[WORKFLOW DETECTION]")
            if workflow_type == "classification":
                print(f"  → Query Type: CLASSIFICATION WORKFLOW")
                print(f"  → Category: {category}")
                print(f"  → This query will use category-specific handling")
            else:
                print(f"  → Query Type: DIRECT RAG")
                print(f"  → Category: {category}")
                print(f"  → This query will use general knowledge base search")

            # Step 1: Get relevant docs from knowledge base
            print(f"\n[STEP 1: SEARCHING KNOWLEDGE BASE]")
            print(f"  → Querying vector store for relevant documents...")
        else:
            # Still classify for consistency, just don't print
            workflow_type, category = classify_query(user_message)

        relevant_docs = self.search_knowledge_base(user_message)

        if self.verbose:
            print(f"  ✓ Found relevant documentation from knowledge base")

        # Step 2: Check if we need to search emails or orders
        additional_context = ""
        query_lower = user_message.lower()

        # Check for email-related queries
        if any(word in query_lower for word in ["email", "conversation", "ticket", "support history"]) or "@" in user_message:
            if self.verbose:
                print(f"\n[STEP 2: CHECKING MCP TOOLS - EMAILS]")
                print(f"  → Detected email-related query")
                print(f"  → Calling MCP tool: search_emails")
            try:
                # Extract email address if present, or use keywords
                email_match = re.search(r'[\w\.-]+@[\w\.-]+', user_message)
                search_query = email_match.group(0) if email_match else user_message

                result = await self.mcp_session.call_tool("search_emails", {"query": search_query})
                additional_context += f"\n\nCustomer Email History:\n{result.content[0].text}\n"
                if self.verbose:
                    print(f"  ✓ Retrieved email data from MCP server")
            except Exception as e:
                if self.verbose:
                    print(f"  ✗ Email search failed: {e}")

        # Check for order-related queries
        if any(word in query_lower for word in ["order", "shipping", "delivery", "tracking", "ord-"]):
            if self.verbose:
                print(f"\n[STEP 2: CHECKING MCP TOOLS - ORDERS]")
                print(f"  → Detected order-related query")
                print(f"  → Calling MCP tool: search_orders")
            try:
                # Extract order ID if present, or use keywords
                order_match = re.search(r'ORD-\d+', user_message, re.IGNORECASE)
                search_query = order_match.group(0) if order_match else user_message

                result = await self.mcp_session.call_tool("search_orders", {"query": search_query})
                additional_context += f"\n\nOrder Information:\n{result.content[0].text}\n"
                if self.verbose:
                    print(f"  ✓ Retrieved order data from MCP server")
            except Exception as e:
                if self.verbose:
                    print(f"  ✗ Order search failed: {e}")

        # Step 3: Build prompt for LLM
        if self.verbose:
            print(f"\n[STEP 3: GENERATING LLM RESPONSE]")
            print(f"  → Building augmented prompt with RAG context...")
            if self.conversation_history:
                print(f"  → Including {len(self.conversation_history)} previous exchange(s) for context")
            print(f"  → Sending to Hugging Face LLM ({HF_MODEL})...")

        # Build conversation history context
        history_context = ""
        if self.conversation_history:
            history_lines = []
            for exchange in self.conversation_history[-self.max_history:]:
                history_lines.append(f"Customer: {exchange['user']}")
                history_lines.append(f"Agent: {exchange['assistant']}")
            history_context = "\n".join(history_lines)

        system_prompt = """You are a helpful OmniTech customer support agent.

Product Documentation:
{docs}
{context}
{history_section}
Instructions:
- Be friendly, helpful, and professional
- Use the documentation to answer product questions
- If email or order information is provided, use it to give personalized help
- Keep responses concise (2-4 sentences)
- If you don't know something, say so clearly
- Always provide specific, actionable help
- IMPORTANT: When using information from the documentation, cite the source document (e.g., "According to OmniTech_Returns_Policy_2024.pdf...")
- If there is conversation history, use it to provide continuity and reference previous exchanges when relevant

Customer Question: {question}

Respond with JSON containing:
- "response": your helpful answer (2-4 sentences) - include source citations when referencing documentation
- "action_needed": "none", "create_ticket", or "escalate"
- "confidence": 0-1

JSON Response:"""

        # Build the history section only if we have history
        history_section = ""
        if history_context:
            history_section = f"\nPrevious Conversation:\n{history_context}\n"

        full_prompt = system_prompt.format(
            docs=relevant_docs,
            context=additional_context,
            history_section=history_section,
            question=user_message
        )

        # Step 4: Get LLM response
        llm_response = self.query_llm(full_prompt)

        # Step 5: Parse response (handle JSON wrapped in markdown)
        result = None
        try:
            result = json.loads(llm_response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks (```json ... ```)
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', llm_response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Also try to find raw JSON object in the response
            if result is None:
                json_match = re.search(r'\{[^{}]*"response"[^{}]*\}', llm_response, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        pass

            # Fallback if no valid JSON found
            if result is None:
                clean_response = re.sub(r'```(?:json)?|```', '', llm_response).strip()
                result = {
                    "response": clean_response[:500] if len(clean_response) > 500 else clean_response,
                    "action_needed": "none",
                    "confidence": 0.6
                }

        # Extract just the response text
        final_response = result.get("response", "I'm sorry, I couldn't generate a proper response.")

        # Save this exchange to conversation history
        self.conversation_history.append({
            "user": user_message,
            "assistant": final_response
        })
        # Keep only the last max_history exchanges
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

        if self.verbose:
            print(f"  ✓ LLM response received and parsed")
            print(f"  → Saved to conversation history ({len(self.conversation_history)}/{self.max_history} exchanges)")
            print(f"\n[WORKFLOW COMPLETE]")
            print(f"{'='*60}\n")

        return final_response

# ═══════════════════════════════════════════════════════════════════════════
# Interactive mode (when run directly)
# ═══════════════════════════════════════════════════════════════════════════

async def interactive_agent():
    """Run an interactive REPL for querying the RAG agent."""

    print("\n" + "="*60)
    print("OmniTech RAG Agent - Interactive Mode")
    print("="*60)
    print("\nInitializing agent with verbose output enabled...")
    print("This will show the complete workflow for each query.\n")

    # Create agent with verbose=True for CLI mode
    agent = SyncAgent(verbose=True)

    try:
        # Try to connect to the MCP server; if it fails, keep going so
        # users can still query the knowledge base.
        await agent.connect_mcp()
    except Exception as e:
        print(f"Warning: couldn't connect to MCP server: {e}")

    print("\n" + "-"*60)
    print("Ready! Try these example queries:")
    print("  • 'How do I reset my password?' (classification → account_security)")
    print("  • 'My device won't turn on' (classification → device_troubleshooting)")
    print("  • 'Tell me about OmniTech' (direct RAG)")
    print("-"*60)
    print("Commands: 'exit'/'quit' to stop, 'clear' to reset history")
    print("Note: The agent remembers your last 3 exchanges for context!")

    try:
        while True:
            try:
                user_input = input("\nYou: ").strip()
            except EOFError:
                # Ctrl-D / EOF -> exit
                break

            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                break
            if user_input.lower() == "clear":
                agent.clear_history()
                print("Conversation history cleared. Starting fresh!")
                continue

            try:
                response = await agent.query(user_input)
                print(f"Agent: {response}\n")
            except Exception as e:
                print(f"Error processing query: {e}")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    finally:
        try:
            await agent.cleanup()
        except Exception:
            pass


if __name__ == "__main__":
    import asyncio
    asyncio.run(interactive_agent())

