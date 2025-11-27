#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Prepare files for Hugging Face Spaces Deployment
# ═══════════════════════════════════════════════════════════════════════════════
#
# This script copies only the necessary files for deploying the OmniTech
# Customer Support chatbot to Hugging Face Spaces.
#
# Usage:
#   ./scripts/prepare_hf_spaces.sh [output_directory]
#
# If no output directory is specified, it defaults to ./hf_spaces_deploy
#
# Files included:
#   - app.py              (HF Spaces entry point)
#   - gradio_app.py       (Gradio UI)
#   - rag_agent.py        (RAG agent logic)
#   - mcp_server.py       (MCP server)
#   - seed_data.json      (Initial database data)
#   - requirements.txt    (Python dependencies - minimal for HF Spaces)
#   - knowledge_base_pdfs/ (PDF documents for RAG)
#   - README.md           (HF Spaces metadata and description)
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the project root directory (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Output directory (default or from argument)
OUTPUT_DIR="${1:-$PROJECT_ROOT/hf_spaces_deploy}"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Preparing Hugging Face Spaces Deployment${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Source:${NC} $PROJECT_ROOT"
echo -e "${YELLOW}Output:${NC} $OUTPUT_DIR"
echo ""

# Create output directory
if [ -d "$OUTPUT_DIR" ]; then
    echo -e "${YELLOW}Warning: Output directory exists. Cleaning...${NC}"
    # Handle "." specially - clean contents instead of removing directory
    if [ "$OUTPUT_DIR" = "." ] || [ "$OUTPUT_DIR" = "./" ]; then
        rm -rf ./*.py ./*.json ./*.md ./*.txt ./.env* ./.gitignore ./knowledge_base_pdfs 2>/dev/null || true
    else
        rm -rf "$OUTPUT_DIR"
    fi
fi

mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/knowledge_base_pdfs"

# ─────────────────────────────────────────────────────────────────────────────
# Copy Python source files
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${GREEN}Copying Python source files...${NC}"

cp "$PROJECT_ROOT/app.py" "$OUTPUT_DIR/"
cp "$PROJECT_ROOT/gradio_app.py" "$OUTPUT_DIR/"
cp "$PROJECT_ROOT/rag_agent.py" "$OUTPUT_DIR/"
cp "$PROJECT_ROOT/mcp_server.py" "$OUTPUT_DIR/"

# ─────────────────────────────────────────────────────────────────────────────
# Copy seed data
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${GREEN}Copying seed data...${NC}"

cp "$PROJECT_ROOT/seed_data.json" "$OUTPUT_DIR/"

# ─────────────────────────────────────────────────────────────────────────────
# Copy knowledge base PDFs
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${GREEN}Copying knowledge base PDFs...${NC}"

cp "$PROJECT_ROOT/knowledge_base_pdfs/"*.pdf "$OUTPUT_DIR/knowledge_base_pdfs/"

# ─────────────────────────────────────────────────────────────────────────────
# Create minimal requirements.txt for HF Spaces
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${GREEN}Creating requirements.txt...${NC}"

cat > "$OUTPUT_DIR/requirements.txt" << 'EOF'
# Hugging Face Spaces requirements for OmniTech Customer Support Chatbot
# Note: HF Spaces has many packages pre-installed, so we only list what we need

# MCP (Model Context Protocol)
mcp>=1.22.0

# Vector database for RAG
chromadb>=0.4.0

# PDF processing
pypdf>=5.0.0

# Gradio UI (usually pre-installed on HF Spaces, but specify version)
gradio>=4.19.0

# HuggingFace Hub for LLM inference
huggingface_hub>=0.20.0

# Sentence transformers for embeddings (used by ChromaDB)
sentence-transformers>=2.2.0
EOF

# ─────────────────────────────────────────────────────────────────────────────
# Create HF Spaces README.md with metadata
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${GREEN}Creating README.md with HF Spaces metadata...${NC}"

cat > "$OUTPUT_DIR/README.md" << 'EOF'
---
title: OmniTech Customer Support
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
pinned: false
license: mit
---

# OmniTech Customer Support Chatbot

An AI-powered customer support chatbot built with:
- **Gradio** for the web interface
- **MCP (Model Context Protocol)** for tool orchestration
- **ChromaDB** for vector-based document search (RAG)
- **HuggingFace Inference API** for LLM responses

## ⚠️ IMPORTANT: Required Setup

**This Space requires `HF_TOKEN` to be set as a secret, or the LLM won't work!**

Without `HF_TOKEN`, you'll see truncated responses like:
> "Based on our Return policies: OmniTech Solutions Consumer Returns..."

**How to fix:**
1. On the Hugging Face spaces site (huggingface.co/spaces/userid/aia-capstone) click on the **Settings** link in the upper right. 
2. Scroll down until you see the **Variables and secrets** section.
3. Click **New secret** button on right.
4. Fill in the fields with Name: `HF_TOKEN`and Value: Your HuggingFace API token.
5. Click **Save** and the Space will restart automatically
6. You can watch progress back on the **App** tab.

## Features

- 🔍 **RAG-powered responses** - Answers based on product documentation
- 🎫 **Ticket creation** - Automatically creates support tickets when needed
- 👤 **Customer context** - Looks up customer information for personalized responses
- 📊 **Developer mode** - Toggle to see debug info, MCP stats, and knowledge search

## Usage

1. **Set HF_TOKEN first** (see above)
2. Select a customer from the dropdown
3. Type your question in the chat
4. Toggle "Developer Mode" to see debug information

## Support Categories

- Account Security (passwords, 2FA, account recovery)
- Device Troubleshooting (technical issues, setup)
- Shipping & Delivery (order tracking, shipping info)
- Returns & Refunds (return policy, warranties)

---
*Built for the Enterprise AI Accelerator Capstone*
EOF

# ─────────────────────────────────────────────────────────────────────────────
# Create .env.example to document required environment variables
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${GREEN}Creating .env.example...${NC}"

cat > "$OUTPUT_DIR/.env.example" << 'EOF'
# ═══════════════════════════════════════════════════════════════════════════════
# Environment Variables for OmniTech Customer Support
# ═══════════════════════════════════════════════════════════════════════════════
#
# IMPORTANT: On HuggingFace Spaces, set these as "Repository secrets" in Settings
#
# DO NOT commit actual values to git! This file is just documentation.
#
# ═══════════════════════════════════════════════════════════════════════════════

# HuggingFace API Token (REQUIRED)
# Get your token from: https://huggingface.co/settings/tokens
# This is used to call the LLM for generating responses
HF_TOKEN=your_huggingface_token_here

# Optional: Override the default LLM model
# Default: meta-llama/Llama-3.1-8B-Instruct
# HF_MODEL=meta-llama/Llama-3.1-8B-Instruct
EOF

# ─────────────────────────────────────────────────────────────────────────────
# Create .gitignore for the deployment
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${GREEN}Creating .gitignore...${NC}"

cat > "$OUTPUT_DIR/.gitignore" << 'EOF'
# Python
__pycache__/
*.py[cod]
*.so

# Database (will be created at runtime)
*.db

# Logs
*.log

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Gradio cache
.gradio/
flagged/
EOF

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Deployment files prepared successfully!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Files in $OUTPUT_DIR:"
echo ""
ls -la "$OUTPUT_DIR"
echo ""
echo "Knowledge base PDFs:"
ls -la "$OUTPUT_DIR/knowledge_base_pdfs"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. cd $OUTPUT_DIR"
echo "  2. git init"
echo "  3. git add ."
echo "  4. git commit -m 'Initial HF Spaces deployment'"
echo "  5. Create a new Space on huggingface.co/spaces"
echo "  6. Push to the Space repository"
echo ""
echo -e "${YELLOW}⚠️  CRITICAL: Set HF_TOKEN secret${NC}"
echo "  Without this, the LLM won't work and responses will be truncated!"
echo ""
echo "  How to set HF_TOKEN:"
echo "    1. Go to your Space on huggingface.co"
echo "    2. Click 'Settings' tab"
echo "    3. Scroll to 'Repository secrets'"
echo "    4. Click 'New secret'"
echo "    5. Name: HF_TOKEN"
echo "    6. Value: Your HuggingFace API token from"
echo "       https://huggingface.co/settings/tokens"
echo "    7. Save and restart the Space"
echo ""
