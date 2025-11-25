#!/bin/bash
# Combined warmup script for MCP components
# Optimized to minimize container startup time

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting lightweight warmup..."

# MCP warmup (fast: ~2-3s, pre-loads embedding model)
# This is the most important for MCP servers
echo ""
echo "═══════════════════════════════════"
echo "  MCP Component Warmup (Fast)"
echo "═══════════════════════════════════"
python3 "$SCRIPT_DIR/warmup_mcp.py"
MCP_EXIT=$?

# Only warm up Ollama if it's running AND we have time
# Skip this during container creation to save time
if [ "${SKIP_OLLAMA_WARMUP:-0}" == "0" ]; then
    echo ""
    echo "═══════════════════════════════════"
    echo "  Ollama Model Warmup (Optional)"
    echo "═══════════════════════════════════"

    # Check if Ollama is running (quick check)
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "Ollama detected, warming up models..."
        python3 "$SCRIPT_DIR/warmup_model.py" || echo "⚠️  Ollama warmup failed (non-critical)"
    else
        echo "⏩ Ollama not running, skipping model warmup"
    fi
else
    echo "⏩ Skipping Ollama warmup (SKIP_OLLAMA_WARMUP=1)"
fi

echo ""
if [ $MCP_EXIT -eq 0 ]; then
    echo "✅ Warmup complete! MCP components ready."
    exit 0
else
    echo "⚠️  MCP warmup had issues, but should still work"
    exit 0  # Don't fail container creation
fi
