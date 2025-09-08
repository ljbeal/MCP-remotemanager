import ast
from typing import Any
from mcp.server.fastmcp import FastMCP

from remotemanager import URL, Dataset
from remotemanager.storage.function import Function
from remotemanager.dataset.runner import RunnerFailedError
import logging
from remotemanager import Logger

# Configure the logging module
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Set the logging level to DEBUG for all loggers
logger = logging.getLogger("remote")  # Create a logger with the name "remote"
file_handler = logging.FileHandler("remoterun.log")  # Add a file handler to log to the specified file
logger.addHandler(file_handler)  # Add the file handler to the logger

# update remotemanager Logger settings
Logger.level = "Debug"


mcp = FastMCP("RemoteRun")


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
        return f"Invalid hostname or unable to connect: {e}"
    logger.info("Hostname is valid.")
    return ""

@mcp.tool()
async def run_code(function_source: str, hostname: str, **kwargs: Any) -> dict[str, Any]:
    """
    Run a function defined by its source code string with the given arguments.

    Args:
        function_source (str): The source code of the function to run. This must be a single, valid python function that can be executed directly with no imports.
        hostname (str): The hostname of the remote server to execute the function on.
        **kwargs (Any): Keyword arguments to pass to the function.

    Returns:
        str: The result of the function execution.
    """
    logger.info("Starting function execution.")
    validation_error = validate_function(function_source)
    if validation_error:
        return {"Error": validation_error}
    
    validation_error = validate_url(hostname)
    if validation_error:
        return {"Error": validation_error}

    logger.info(f"Creating remote URL with hostname {hostname}")
    url = URL(hostname, verbose=0)

    ds = Dataset(Function(function_source), url=url, skip=False, verbose=False)

    ds.append_run(args=kwargs)

    ds.run()
    ds.wait(1, 10)
    ds.fetch_results()
    
    result = ds.results[0]
    if isinstance(result, RunnerFailedError):
        logger.error(f"Function execution failed: {result}")
        return {"Error": f"Function execution failed: {result}"}

    logger.info(f"Function executed successfully. Result: {result}")
    return {"Result": str(result)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
