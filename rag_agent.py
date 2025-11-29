#!/usr/bin/env python3
"""
OmniTech Customer Support RAG Agent - FULL VERSION
═══════════════════════════════════════════════════════════════════════════════

Complete agent with:
"""

import asyncio
import json
import logging
import re
import sys
from contextlib import AsyncExitStack
from datetime import datetime
from typing import Any, Dict, List, Optional

# MCP Client
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("MCP not installed. Install with: pip install mcp")
    sys.exit(1)

import os
from huggingface_hub import InferenceClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("omnitech-agent")

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ 1. Configuration                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# HuggingFace Inference API

if not HF_TOKEN:
    print("WARNING: HF_TOKEN not set. LLM calls will be skipped.")
    print("Set it with: export HF_TOKEN='your_token_here'")
    print("Get a token from: https://huggingface.co/settings/tokens")
    print()

# Support detection keywords (for routing decision)

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ Security: Suspicious Pattern Detection (Goal-Hijacking Prevention)       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# Patterns that may indicate prompt injection or goal-hijacking attempts

# ANSI colors for terminal output
BLUE = "\033[34m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RESET = "\033[0m"

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ 2. Helper Functions                                                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def is_support_query(query: str) -> bool:
    query_lower = query.lower()

    # Check for support-related keywords
    for category, keywords in SUPPORT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in query_lower:
                return True


    for pattern in support_patterns:
        if re.search(pattern, query_lower):
            return True

    return False


def unwrap_mcp_result(obj):
    """Unwrap MCP result objects to get the actual data."""
    if hasattr(obj, "content") and obj.content:
        content = obj.content[0].text if obj.content else "{}"
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content
    return obj


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ 3. RAG Agent Class                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class OmniTechAgent:
    """RAG Agent for OmniTech Customer Support using MCP."""

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack: Optional[AsyncExitStack] = None
        self.mcp_calls_log: List[Dict] = []
        self.available_tools: List[str] = []

        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 3  # Keep last 3 exchanges

        self.security_log: List[Dict] = []
        self.max_security_log = 50  # Keep last 50 security events

    def clear_history(self):
        """Clear conversation history to start a fresh conversation."""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    # ─── Security Methods ─────────────────────────────────────────────────

    def _log_security_event(self, event_type: str, severity: str, details: str,
                            query: str = None, customer_email: str = None):
        """
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details,
            "query": query[:200] if query else None,  # Truncate for safety
            "customer_email": customer_email
        }

        # Keep log bounded
        if len(self.security_log) > self.max_security_log:
            self.security_log = self.security_log[-self.max_security_log:]

        # Also log to standard logger for server-side visibility
        log_msg = f"[SECURITY:{severity.upper()}] {event_type}: {details}"
        if severity == "high":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

    def _inspect_input(self, query: str, customer_email: str = None) -> Dict[str, Any]:
        """
        """
        query_lower = query.lower()
        patterns_matched = []


        flagged = len(patterns_matched) > 0

        # Log if suspicious patterns detected
        if flagged:
            self._log_security_event(
                event_type="suspicious_input",
                severity=risk_level,
                details=f"Detected patterns: {', '.join(patterns_matched)}",
                query=query,
                customer_email=customer_email
            )

        return {
            "flagged": flagged,
            "patterns_matched": patterns_matched,
            "risk_level": risk_level
        }

    def get_security_log(self) -> List[Dict]:
        """Return the security log for monitoring."""
        return self.security_log.copy()

    def clear_security_log(self):
        """Clear the security log."""
        self.security_log = []
        logger.info("Security log cleared")

    def _build_history_context(self) -> str:
        """Build conversation history context for prompts."""
        if not self.conversation_history:
            return ""

        history_lines = []
        for exchange in self.conversation_history[-self.max_history:]:
            history_lines.append(f"Customer: {exchange['user']}")
            history_lines.append(f"Agent: {exchange['assistant']}")

        return "\nPrevious Conversation:\n" + "\n".join(history_lines) + "\n"

    def _save_exchange(self, user_message: str, assistant_response: str):
        """Save an exchange to conversation history."""
        self.conversation_history.append({
            "user": user_message,
            "assistant": assistant_response
        })
        # Keep only the last max_history exchanges
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    # ─── MCP Connection ────────────────────────────────────────────────────

    async def connect(self) -> bool:
        try:
            self.exit_stack = AsyncExitStack()


            # Verify connection and get available tools

        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            return False

    async def disconnect(self):
        """Clean up MCP connection."""
        if self.exit_stack:
            await self.exit_stack.aclose()

    # ─── MCP Tool Calls ────────────────────────────────────────────────────

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool and return the result."""
        if not self.session:
            raise Exception("MCP session not initialized")

        start_time = datetime.now()
        try:
            result = await self.session.call_tool(tool_name, arguments)
            duration = (datetime.now() - start_time).total_seconds()

            parsed = unwrap_mcp_result(result)

            # Log the call
            self.mcp_calls_log.append({
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "arguments": arguments,
                "duration_ms": round(duration * 1000, 2),
                "success": "error" not in str(parsed).lower()
            })

            if len(self.mcp_calls_log) > 20:
                self.mcp_calls_log = self.mcp_calls_log[-20:]

            return parsed

        except Exception as e:
            logger.error(f"Tool call failed ({tool_name}): {e}")
            return {"error": str(e)}

    # ─── Customer Context ──────────────────────────────────────────────────

    async def get_customer_context(self, email: str) -> str:
        """Get customer context string for prompts."""
        if "lookup_customer" not in self.available_tools:
            return "Customer: Unknown"

        customer = await self.call_tool("lookup_customer", {"email": email})

        if customer.get("found"):
            name = customer.get("name", "Unknown")
            tier = customer.get("tier", "Standard")
            tickets = customer.get("support_tickets", 0)

            context = f"Customer: {name} ({tier} tier)"
            if tickets > 0:
                context += f" - {tickets} previous tickets"

            return context
        else:
            return f"Customer: {email} (not in database)"

    # ─── LLM Integration ───────────────────────────────────────────────────

    def query_llm(self, prompt: str) -> str:
        """Query HuggingFace Inference API using InferenceClient."""
        if not HF_CLIENT:
            logger.warning("HF_TOKEN not set. Get a token from https://huggingface.co/settings/tokens")
            return json.dumps({
                "response": "KNOWLEDGE_BASE_ONLY",
                "action_needed": "none",
                "confidence": 0.7
            })

        try:

        except Exception as e:
            error_msg = str(e)
            logger.error(f"LLM error: {error_msg}")

            # Check for model loading (503)
            if "503" in error_msg or "loading" in error_msg.lower():
                return json.dumps({
                    "response": "The AI model is warming up. Please try again in a moment.",
                    "action_needed": "none",
                    "confidence": 0.5
                })

            return json.dumps({
                "response": "KNOWLEDGE_BASE_ONLY",
                "action_needed": "none",
                "confidence": 0.7
            })

    # ─── Classification Workflow ───────────────────────────────────────────

    async def handle_support_query(self, query: str, customer_email: str = None) -> Dict[str, Any]:
        """

        """
        workflow_log = []
        start_time = datetime.now()

        try:
            # Get customer context if email provided
            customer_context = ""
            if customer_email:
                customer_context = await self.get_customer_context(customer_email)
                workflow_log.append(f"[INFO] {customer_context}")

            # Step 1: Classify
            workflow_log.append("[1/4] Classifying query...")
            classification = await self.call_tool("classify_query", {"user_query": query})

            if "error" in classification:
                return {"error": f"Classification failed: {classification['error']}"}

            category = classification.get("suggested_query", "general_support")
            confidence = classification.get("confidence", 0)
            workflow_log.append(f"[Result] Category: {category} (confidence: {confidence:.2f})")

            # Step 2: Get template
            workflow_log.append("[2/4] Getting template...")
            template_info = await self.call_tool("get_query_template", {"query_name": category})

            template = template_info.get("template", "") if "error" not in template_info else ""
            description = template_info.get("description", category)

            # Step 3: Retrieve knowledge
            workflow_log.append(f"[3/4] Retrieving knowledge for {category}...")
            knowledge_info = await self.call_tool("get_knowledge_for_query", {
                "category": category,
                "query": query,
                "max_results": 3
            })

            knowledge = knowledge_info.get("knowledge", "No documentation found.")
            sources = knowledge_info.get("sources", [])
            workflow_log.append(f"[INFO] Retrieved {len(sources)} source(s)")

            # Step 4: Execute LLM
            workflow_log.append("[4/4] Generating response...")


            llm_response = self.query_llm(full_prompt)

            # Parse response - handle JSON wrapped in markdown code blocks
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
                    # Clean up the response - remove JSON artifacts if present
                    clean_response = re.sub(r'```(?:json)?|```', '', llm_response).strip()
                    result = {
                        "response": clean_response[:500] if len(clean_response) > 500 else clean_response,
                        "action_needed": "none",
                        "confidence": 0.6
                    }

            # Handle knowledge-base-only fallback
            if result.get("response") == "KNOWLEDGE_BASE_ONLY":
                result["response"] = f"Based on our {description}:\n\n{knowledge[:400]}..."
                result["confidence"] = 0.8

            # Create ticket if needed

            # Add metadata
            result["classification"] = {
                "category": category,
                "confidence": confidence,
                "description": description
            }
            result["workflow"] = "classification"
            result["workflow_log"] = workflow_log
            result["sources"] = sources
            result["llm_prompt"] = full_prompt
            result["llm_model"] = HF_MODEL
            result["customer_email"] = customer_email
            result["processing_time_ms"] = (datetime.now() - start_time).total_seconds() * 1000

            workflow_log.append("[SUCCESS] Response generated")
            return result

        except Exception as e:
            logger.error(f"Classification workflow error: {e}")
            return {
                "response": "I encountered an error. Please try again.",
                "error": str(e),
                "workflow": "classification",
                "workflow_log": workflow_log
            }


    async def handle_exploratory_query(self, query: str, customer_email: str = None) -> Dict[str, Any]:
        """Handle exploratory queries using direct RAG search."""
        start_time = datetime.now()

        try:
            # Get customer context if email provided
            customer_context = ""
            if customer_email:
                customer_context = await self.get_customer_context(customer_email)

            # Search across all knowledge
            search_result = await self.call_tool("search_knowledge", {
                "query": query,
                "max_results": 5
            })

            matches = search_result.get("matches", [])

            if not matches:
                return {
                    "response": "I couldn't find relevant information. Please try rephrasing.",
                    "workflow": "direct_rag",
                    "sources": []
                }

            # Build context
            knowledge_parts = [m["content"] for m in matches[:3]]
            sources = list(set(m["source"] for m in matches[:3]))
            knowledge = "\n\n---\n\n".join(knowledge_parts)

            # Query LLM

            llm_response = self.query_llm(prompt)

            # Parse response - handle JSON wrapped in markdown code blocks
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

            if result.get("response") == "KNOWLEDGE_BASE_ONLY":
                result["response"] = f"Here's what I found:\n\n{knowledge[:400]}..."

            result["workflow"] = "direct_rag"
            result["sources"] = sources
            result["llm_prompt"] = prompt
            result["llm_model"] = HF_MODEL
            result["customer_email"] = customer_email
            result["processing_time_ms"] = (datetime.now() - start_time).total_seconds() * 1000

            # Save this exchange to conversation history
            self._save_exchange(query, result.get("response", ""))

            return result

        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return {
                "response": "Search error. Please try again.",
                "error": str(e),
                "workflow": "direct_rag"
            }

    # ─── Main Query Handler ────────────────────────────────────────────────

    async def process_query(self, query: str, customer_email: str = None) -> Dict[str, Any]:
        """
        Process a customer query, routing to appropriate workflow.

        Support queries → Classification workflow
        Exploratory queries → Direct RAG search
        """

    # ─── Server Stats ──────────────────────────────────────────────────────

    async def get_server_stats(self) -> Dict[str, Any]:
        """Get MCP server statistics."""
        if "get_server_stats" not in self.available_tools:
            return {"error": "Stats not available"}

        return await self.call_tool("get_server_stats", {})


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ 4. Synchronous Wrapper (for Gradio integration)                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class SyncAgent:
    """Synchronous wrapper for use with Gradio."""

    def __init__(self):
        self.agent = OmniTechAgent()
        self.loop = None
        self._initialize()

    def _initialize(self):
        """Initialize async components."""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            success = self.loop.run_until_complete(self.agent.connect())
            if not success:
                raise Exception("Failed to connect to MCP server")
            logger.info("SyncAgent initialized successfully")
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    def process_query(self, query: str, customer_email: str = None) -> Dict[str, Any]:
        """Synchronous query processing."""
        if not self.loop:
            return {"error": "Agent not initialized", "response": "System error"}
        return self.loop.run_until_complete(
            self.agent.process_query(query, customer_email)
        )

    def get_mcp_log(self) -> List[Dict]:
        """Get MCP call log."""
        return self.agent.mcp_calls_log

    def clear_history(self):
        """Clear conversation history."""
        self.agent.clear_history()

    def get_server_stats(self) -> Dict[str, Any]:
        """Get server stats."""
        if not self.loop:
            return {"error": "Agent not initialized"}
        return self.loop.run_until_complete(self.agent.get_server_stats())

    def get_available_tools(self) -> List[str]:
        """Get list of available MCP tools."""
        return self.agent.available_tools

    def get_security_log(self) -> List[Dict]:
        """Get security event log."""
        return self.agent.get_security_log()

    def clear_security_log(self):
        """Clear security log."""
        self.agent.clear_security_log()

    def __del__(self):
        """Cleanup."""
        if self.loop and self.agent:
            try:
                self.loop.run_until_complete(self.agent.disconnect())
                self.loop.close()
            except:
                pass


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ 5. Command-Line Interface                                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝

async def interactive_mode():
    """Run interactive CLI for testing."""
    agent = OmniTechAgent()

    print("=" * 60)
    print("OmniTech Customer Support Agent")
    print("=" * 60)
    print("Connecting to MCP server...")

    if not await agent.connect():
        print("Failed to connect to MCP server!")
        print("Make sure mcp_server.py is in the current directory.")
        return

    print(f"Connected! Available tools: {agent.available_tools}")
    print("\nCommands:")
    print("  'exit' - quit")
    print("  'demo' - run sample queries")
    print("  'stats' - show server statistics")
    print("  'email:xxx' - set customer email for context")
    print("  'clear' - clear conversation history")
    print()
    print("Note: The agent remembers your last 3 exchanges for follow-up context!")
    print()

    customer_email = "john.doe@email.com"
    print(f"Default customer: {customer_email}")

    sample_queries = [
        "How do I reset my password?",
        "My device won't turn on",
        "What is your return policy?",
        "Tell me about OmniTech",
    ]

    while True:
        try:
            user_input = input(f"\n{GREEN}Query:{RESET} ").strip()

            if user_input.lower() == "exit":
                break
            elif user_input.lower() == "demo":
                for q in sample_queries:
                    print(f"\n{GREEN}Query:{RESET} {q}")
                    result = await agent.process_query(q, customer_email)
                    response = result.get("response", "No response")
                    workflow = result.get("workflow", "unknown")
                    print(f"{YELLOW}[{workflow}]{RESET}")
                    print(f"{CYAN}{response}{RESET}")
            elif user_input.lower() == "stats":
                stats = await agent.get_server_stats()
                print(f"\n{BLUE}Server Stats:{RESET}")
                print(json.dumps(stats, indent=2))
            elif user_input.lower() == "clear":
                agent.clear_history()
                print("Conversation history cleared. Starting fresh!")
            elif user_input.lower().startswith("email:"):
                customer_email = user_input[6:].strip()
                print(f"Customer set to: {customer_email}")
            elif user_input:
                result = await agent.process_query(user_input, customer_email)
                response = result.get("response", "No response")
                workflow = result.get("workflow", "unknown")
                sources = result.get("sources", [])
                category = result.get("classification", {}).get("category", "")

                print(f"\n{YELLOW}[{workflow}]{RESET}", end="")
                if category:
                    print(f" {BLUE}({category}){RESET}")
                else:
                    print()
                print(f"{CYAN}{response}{RESET}")
                if sources:
                    print(f"\n{BLUE}Sources: {', '.join(sources)}{RESET}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    await agent.disconnect()
    print("Goodbye!")


if __name__ == "__main__":
    asyncio.run(interactive_mode())

