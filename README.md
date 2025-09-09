# remote-mcp
Basic MCP Wrapper for the [remotemanager](https://gitlab.com/l_sim/remotemanager) package

Developed as part of the 2025 [LLM hackathon](https://llmhackathon.github.io/)

The team github can be found here: https://github.com/BigDFT-group/llm-hackathon-2025

This package is currently very experimental and should not be considered production-ready.

## Installation
Testing is currently done using `uv`. I imagine pip works also, however your mileage may vary.

Using `uv`, first clone the repository then:

```
cd MCP-remotemanager
uv venv
source .venv/bin/activate
uv pip install -e .
uvx mcpo --port 8000 -- uv run remoterun/remote.py
```

The MCP server should now be running at `http://127.0.0.1:8000`

### Testing

Feel free to adjust these parameters to suit your setup.
Once you have integrated these tools into your llm interface, you may use `localhost` as the testing hostname. An example prompt:

> Generate for me the first 10 digits of the fibonacci sequence on the remote machine with the hostname "localhost"

If all goes well, the MCP server should pick up a request for a calculation and execute a python function that does what you ask. You may debug the contents of this execution within the source directories of the repository.

You should find a directory named `staging_fib_localhost_{date}_{time}` within the MCP-remotemanager repository. This is the staging directory created by the tool (via remotemanager).

If you ran using `localhost`, there will also be a `temp_runner_remote` directory. This is the location of the actual execution, and will be located on the remote machine if you specified a hostname other than local.

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
