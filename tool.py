from langchain_core.tools import tool
from toolbox_langchain import ToolboxClient


@tool
async def query_database_tool(query: str) -> str:
    """Executes a raw SQL SELECT statement against the SQLite orders database
    and returns the result. Use this to answer questions about order status,
    delivery dates, tracking numbers, available products, or customer orders.

    The orders table has these columns: order_id, customer_name, product_name,
    quantity, total_price, order_status, order_date, delivery_date, tracking_number.

    Only use SELECT statements — never INSERT, UPDATE, or DELETE.

    Args:
        query (str): A complete, valid SQL SELECT statement to execute
            (e.g. "SELECT DISTINCT product_name FROM orders LIMIT 5;").
            This argument MUST be named "query".

    Returns:
        str: The result rows returned by the database.
    """
    async with ToolboxClient("http://127.0.0.1:5000") as toolbox:
        tools = toolbox.load_toolset()

        for t in tools:
            if "sql" in t.name.lower() or "query" in t.name.lower():
                return await t.ainvoke({"sql": query})

        return f"No matching database tool found via MCP Toolbox for query: {query}"