from dotenv import load_dotenv
from deepagents import create_deep_agent, SubAgent
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from tool import query_database_tool
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(title="Ecommerce Support API")

SUBAGENT_INSTRUCTIONS = """You handle order queries, delivery tracking, and product/database lookups.

- The orders table has columns: order_id, customer_name, product_name, quantity, total_price, order_status, order_date, delivery_date, tracking_number.
- Call query_database_tool with a valid SQL SELECT statement to answer the request.
- Only use SELECT statements, never INSERT/UPDATE/DELETE.
"""

SUPERVISOR_PROMPT = """You are a professional, friendly e-commerce customer support supervisor.

- For greetings, return policies, shipping FAQs, or general store info, answer directly from your own knowledge.
- For ANY question needing real data — order status, delivery dates, tracking numbers, customer orders, or available products — invoke the order_support_agent subagent.
- Keep replies warm, concise, and professional.
"""

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_retries=5
)

database_agent = SubAgent(
    name="order_support_agent",
    description="Use this subagent to handle order queries, delivery tracking, and database/product lookups.",
    system_prompt=SUBAGENT_INSTRUCTIONS,
    tools=[query_database_tool]
)

memory = MemorySaver()

deep_agent = create_deep_agent(
    model=llm,
    system_prompt=SUPERVISOR_PROMPT,
    subagents=[database_agent],
    checkpointer=memory,
    
)

class ChatRequest(BaseModel):
    text: str = Field(...)
    thread_id: str = "default_thread_123"

@app.post("/chat")
async def chat_with_agent(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.thread_id}}

        result = await deep_agent.ainvoke(
            {"messages": [{"role": "user", "content": request.text}]},
            config=config
        )
        
        return {
            "status": "success",
            "thread_id": request.thread_id,
            "response": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
