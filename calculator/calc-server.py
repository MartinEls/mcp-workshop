# Zur Inspiration: https://github.com/huhabla/calculator-mcp-server/blob/main/calculator_server.py
from mcp.server.fastmcp import FastMCP

# Create the FastMCP instance with stdio transport
mcp = FastMCP()

# Define the tool using the @mcp.tool() decorator
@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Adds two numbers together
    
    :param a: First number
    :param b: Second number
    :return: Sum of the two numbers
    """
    return a + b

# The tool is automatically added to the mcp instance by the decorator

# Run the server if the script is executed directly
if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run(transport="stdio")