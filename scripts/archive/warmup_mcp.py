#!/usr/bin/env python3
"""
MCP Server Warmup Script

Pre-loads models and initializes resources needed by MCP servers
without causing long startup delays. Only does expensive one-time operations.
"""

import sys
import time
from pathlib import Path

# ANSI color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def warmup_embedding_model():
    """
    Pre-load the sentence-transformers embedding model.
    This is the slowest part of MCP server startup (~2-3s first time).
    After this, it's cached and loads instantly.
    """
    try:
        print(f"{CYAN}Pre-loading embedding model (all-MiniLM-L6-v2)...{RESET}")
        start_time = time.time()

        from sentence_transformers import SentenceTransformer

        # Just load the model - don't run inference (fast)
        model = SentenceTransformer('all-MiniLM-L6-v2')

        end_time = time.time()
        print(f"{GREEN}✓ Embedding model loaded in {end_time - start_time:.2f}s{RESET}")
        return True
    except Exception as e:
        print(f"{RED}✗ Embedding model warmup failed: {e}{RESET}")
        return False

def warmup_chromadb():
    """
    Initialize ChromaDB connection (very fast, ~0.1s).
    Creates the client so the library is loaded.
    """
    try:
        print(f"{CYAN}Initializing ChromaDB client...{RESET}")
        start_time = time.time()

        import chromadb
        from chromadb.config import Settings

        # Just create a client in memory - doesn't persist anything
        client = chromadb.Client(Settings(
            is_persistent=False,
            anonymized_telemetry=False
        ))

        end_time = time.time()
        print(f"{GREEN}✓ ChromaDB initialized in {end_time - start_time:.2f}s{RESET}")
        return True
    except Exception as e:
        print(f"{RED}✗ ChromaDB warmup failed: {e}{RESET}")
        return False

def warmup_fastmcp():
    """
    Import FastMCP to pre-load the library (very fast).
    """
    try:
        print(f"{CYAN}Loading FastMCP library...{RESET}")
        start_time = time.time()

        from fastmcp import FastMCP

        end_time = time.time()
        print(f"{GREEN}✓ FastMCP loaded in {end_time - start_time:.2f}s{RESET}")
        return True
    except Exception as e:
        print(f"{RED}✗ FastMCP warmup failed: {e}{RESET}")
        return False

def check_dependencies():
    """Quick check if required packages are installed."""
    try:
        import sentence_transformers
        import chromadb
        import fastmcp
        return True
    except ImportError as e:
        print(f"{RED}✗ Missing dependency: {e}{RESET}")
        return False

def main():
    print(f"{BOLD}{CYAN}MCP Server Warmup Script{RESET}")
    print("=" * 40)

    # Quick dependency check
    print(f"{YELLOW}Checking dependencies...{RESET}")
    if not check_dependencies():
        print(f"{RED}Error: Required packages not installed{RESET}")
        sys.exit(1)
    print(f"{GREEN}✓ All dependencies available{RESET}")

    print(f"\n{YELLOW}Starting MCP warmup process...{RESET}")
    total_start = time.time()

    success_count = 0
    total_tests = 3

    # Warmup critical components
    # Most important: embedding model (slowest on first load)
    if warmup_embedding_model():
        success_count += 1

    # Fast operations
    if warmup_chromadb():
        success_count += 1

    if warmup_fastmcp():
        success_count += 1

    total_end = time.time()

    print("\n" + "=" * 40)
    print(f"{BOLD}Warmup Summary:{RESET}")
    print(f"✓ {success_count}/{total_tests} components warmed up successfully")
    print(f"⏱  Total warmup time: {total_end - total_start:.2f}s")

    if success_count >= 2:  # Allow 1 failure
        print(f"{GREEN}{BOLD}MCP components are now warmed up!{RESET}")
        print(f"{CYAN}First MCP server start will now be much faster{RESET}")
        sys.exit(0)
    else:
        print(f"{YELLOW}Some components failed, but MCP should still work{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
