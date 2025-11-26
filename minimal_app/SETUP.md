# Minimal App Setup

## Directory Structure

The minimal examples have been organized into the `minimal_app/` subdirectory:

```
minimal_app/
├── mcp_server_minimal.py         # MCP server (loads from minimal_data.json)
├── rag_agent_minimal.py          # RAG agent (loads PDFs from ../knowledge_base_pdfs/)
├── gradio_app_minimal.py         # Gradio UI
├── minimal_data.json             # Sample emails and orders
├── gradio_minimal_styles.css     # Styling
├── README_MINIMAL.md             # Full documentation
└── SETUP.md                      # This file
```

## Path References

All path references have been updated to work from the subdirectory:

- **PDFs**: Loaded from `../knowledge_base_pdfs/` (parent directory)
- **Data**: Loaded from `minimal_data.json` (same directory)
- **CSS**: Loaded from `gradio_minimal_styles.css` (same directory)

## Running the App

From the project root:
```bash
cd minimal_app
python3 gradio_app_minimal.py
```

Or with the full path:
```bash
python3 minimal_app/gradio_app_minimal.py
```

## Testing

All components have been tested and verified:
- MCP server loads 4 emails and 4 orders from minimal_data.json
- RAG agent loads 4 PDFs from ../knowledge_base_pdfs/
- Gradio app creates successfully with CSS styling

## Next Steps

See README_MINIMAL.md for complete documentation and usage examples.
