# remote-mcp
Basic MCP Wrapper for the [remotemanager](https://gitlab.com/l_sim/remotemanager) package

Developed as part of the 2025 [LLM hackathon](https://llmhackathon.github.io/)

The team github can be found here: https://github.com/BigDFT-group/llm-hackathon-2025

This package is currently very experimental and should not be considered production-ready.

## Installation
Testing is currently done using `uv`. I imagine pip works also, however your mileage may vary.

Simply clone the repo and then `uv pip install -e .`

## Server
Run the MCP server with `uvx remoterun/remote.py`

## Testing
The testing toolchain is currently entirely local and looks like this:
- `gpt-oss` running locally via ollama
-  `open-webui` frontend
-  remote.py MCP server running via MCPO translation layer (for openwebui)
-  The remote machine is a bare metal linux machine

### links

remotemanager: https://gitlab.com/l_sim/remotemanager

FastMCP: https://gofastmcp.com/getting-started/welcome

gpt-oss: https://huggingface.co/openai/gpt-oss-20b

open-webui: https://github.com/open-webui/open-webui
