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
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════════════════

class SyncAgent:
    """
    Minimal RAG Agent that:
    1. Searches knowledge base for relevant info
    2. Can use MCP tools to search emails/orders
    3. Generates helpful responses using Hugging Face LLMs
    """

    def __init__(self):
        """Initialize the agent with vector store and LLM"""

        # Initialize vector store
        self._setup_vector_store()

        # MCP session (will be set when connecting)
        self.mcp_session = None
        self.mcp_tools = []

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

        # Combine retrieved documents
        context = "\n\n---\n\n".join(results['documents'][0])
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
            print("  → Calling Hugging Face LLM...")

            # Use chat_completion for instruct models
            response = HF_CLIENT.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=HF_MODEL,
                max_tokens=500,
                temperature=0.7
            )

            # Extract the response text
            result_text = response.choices[0].message.content
            print(f"  ✓ LLM response received ({len(result_text)} chars)")
            return result_text

        except Exception as e:
            error_msg = str(e)
            print(f"  ✗ LLM error: {error_msg}")

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
        1. Search knowledge base for relevant info
        2. Check if we need to search emails/orders
        3. Send everything to HF LLM to generate response
        """

        print(f"\n{'='*60}")
        print(f"Processing: {user_message[:50]}...")
        print(f"{'='*60}")

        # Step 1: Get relevant docs from knowledge base
        print("Step 1: Searching knowledge base...")
        relevant_docs = self.search_knowledge_base(user_message)
        print(f"  ✓ Found relevant documentation")

        # Step 2: Check if we need to search emails or orders
        additional_context = ""
        query_lower = user_message.lower()

        # Check for email-related queries
        if any(word in query_lower for word in ["email", "conversation", "ticket", "support history"]) or "@" in user_message:
            print("Step 2: Searching emails...")
            try:
                # Extract email address if present, or use keywords
                email_match = re.search(r'[\w\.-]+@[\w\.-]+', user_message)
                search_query = email_match.group(0) if email_match else user_message

                result = await self.mcp_session.call_tool("search_emails", {"query": search_query})
                additional_context += f"\n\nCustomer Email History:\n{result.content[0].text}\n"
                print(f"  ✓ Found email data")
            except Exception as e:
                print(f"  ✗ Email search failed: {e}")

        # Check for order-related queries
        if any(word in query_lower for word in ["order", "shipping", "delivery", "tracking", "ord-"]):
            print("Step 2: Searching orders...")
            try:
                # Extract order ID if present, or use keywords
                order_match = re.search(r'ORD-\d+', user_message, re.IGNORECASE)
                search_query = order_match.group(0) if order_match else user_message

                result = await self.mcp_session.call_tool("search_orders", {"query": search_query})
                additional_context += f"\n\nOrder Information:\n{result.content[0].text}\n"
                print(f"  ✓ Found order data")
            except Exception as e:
                print(f"  ✗ Order search failed: {e}")

        # Step 3: Build prompt for LLM
        print("Step 3: Generating response with LLM...")

        system_prompt = """You are a helpful OmniTech customer support agent.

Product Documentation:
{docs}
{context}

Instructions:
- Be friendly, helpful, and professional
- Use the documentation to answer product questions
- If email or order information is provided, use it to give personalized help
- Keep responses concise (2-4 sentences)
- If you don't know something, say so clearly
- Always provide specific, actionable help

Customer Question: {question}

Respond with JSON containing:
- "response": your helpful answer (2-4 sentences)
- "action_needed": "none", "create_ticket", or "escalate"
- "confidence": 0-1

JSON Response:"""

        full_prompt = system_prompt.format(
            docs=relevant_docs,
            context=additional_context,
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

        print(f"  ✓ Response generated")
        print(f"{'='*60}\n")

        return final_response

# ═══════════════════════════════════════════════════════════════════════════
# Interactive mode (when run directly)
# ═══════════════════════════════════════════════════════════════════════════

async def interactive_agent():
    """Run an interactive REPL for querying the RAG agent."""

    agent = SyncAgent()

    try:
        # Try to connect to the MCP server; if it fails, keep going so
        # users can still query the knowledge base.
        await agent.connect_mcp()
    except Exception as e:
        print(f"Warning: couldn't connect to MCP server: {e}")

    print("\nInteractive OmniTech RAG Agent")
    print("Type 'exit' or 'quit' to stop. Press Ctrl-C to abort.")

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

