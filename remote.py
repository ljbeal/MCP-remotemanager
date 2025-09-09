import ast
import logging
import anyio

from typing import Any, Optional
import anyio.to_thread
from mcp.server.fastmcp import FastMCP
from prompts import server_instructions

from remotemanager import Logger
from remotemanager import URL, Dataset
from remotemanager.storage.function import Function
from remotemanager.dataset.runner import RunnerFailedError

# Configure the logging module
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Set the logging level to DEBUG for all loggers
logger = logging.getLogger("remote")  # Create a logger with the name "remote"
file_handler = logging.FileHandler("remoterun.log")  # Add a file handler to log to the specified file
logger.addHandler(file_handler)  # Add the file handler to the logger

# update remotemanager Logger settings
Logger.level = "Debug"


mcp = FastMCP(name="RemoteRun", instructions=server_instructions)


def validate_function(function_source: str) -> str:
    """
    Validate the provided function source code.

    Args:
        function_source (str): The source code of the function to validate.

    Returns:
        str: An error message if the source code is invalid, otherwise an empty string.
    """
    try:
        ast.parse(function_source)
    except SyntaxError as e:
         logger.error(f"Unable to parse function source code: {e}")
         return f"Unable to parse function source code. Please ensure that it is valid python: {e}"
    logger.info("Function source code is valid.")
    return ""


def validate_url(hostname: str) -> str:
    """
    Validate the provided hostname.

    Args:
        hostname (str): The hostname to validate.

    Returns:
        str: An error message if the hostname is invalid, otherwise an empty string.
    """
    url = URL(hostname, verbose=0)
    
    try:
        url.cmd("pwd", timeout=1, max_timeouts=1)
    except RuntimeError as e:
        logger.error(f"Invalid hostname or unable to connect: {e}")
        return f"Invalid hostname or unable to connect. Validate that the hostname ({hostname}) is accurate:\n{e}"
    logger.info("Hostname is valid.")
    return ""


def generate_name(fn_name: str, hostname: str) -> str:
    """
    Generate a unique name by appending a timestamp to the base name.

    Args:
        fn_name (str): The name of the function.
        hostname (str): The hostname where the function will be executed.

    Returns:
        str: The generated unique name.
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{fn_name}_{hostname}_{timestamp}"


@mcp.tool()
async def run_code(function_source: str, hostname: str, function_args: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """
    Run a function defined by its source code string with the given arguments.
    The function will be executed on a remote server specified by the hostname.
    The function should also take keyword arguments, to be provided to the function_args parameter as a dictionary.

    Args:
        function_source (str): The source code of the function to run. This must be a single, valid python function that can be executed directly with no imports.
        hostname (str): The hostname of the remote server to execute the function on.
        function_args (optional, dict): Keyword arguments to pass to the function.

    Returns:
        dict: The result of the execution. If successful, returns {"Result": <result>}. If there was an error, returns {"Error": <error_message>}.
    """
    if function_args is None:
        function_args = {}

    logger.info("#### New function execution. ####")
    validation_error = validate_function(function_source)
    if validation_error:
        return {"Error": validation_error}
    
    validation_error = validate_url(hostname)
    if validation_error:
        return {"Error": validation_error}

    ### remotemanager setup ###
    logger.info(f"Creating remote URL with hostname {hostname}")
    url = URL(hostname, verbose=0)

    ### Create the Function and Dataset ###
    fn = Function(function_source)
    base_name = generate_name(fn.name, hostname)

    ds = Dataset(fn, name = base_name, local_dir = f"staging_{base_name}", url=url, skip=False, verbose=False)

    ### Append a run, then execute ###
    ds.append_run(args=function_args)

    ds.run()
    await anyio.to_thread.run_sync(ds.wait, 1, 300)
    ds.fetch_results()
    
    ### handle results/errors ###
    result = ds.results[0]
    if isinstance(result, RunnerFailedError):
        logger.error(f"Function execution failed: {result}")
        return {"Error": f"Function execution failed: {result}"}

    logger.info(f"Function executed successfully. Result: {result}")
    return {"Result": str(result)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
