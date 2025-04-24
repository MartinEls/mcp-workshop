import sqlite3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SQL Agent Server")

@mcp.tool()
def query_data(sql: str) -> str:
    """Execute SQL queries safely."""
    # log query, something like: logger.info(f"Executing SQL query: {sql}")
    conn = sqlite3.connect("./ecommerce.db")
    try:
        result = conn.execute(sql).fetchall()
        conn.commit()
        return "\n".join(str(row) for row in result)
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting server...")
    mcp.run(transport="stdio")