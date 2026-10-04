# 🛍️ ShopSense AI: E-commerce Support Agent

A multi-agent customer support system that answers order status, delivery tracking and product questions by querying a live database. A supervisor agent handles the conversation and delegates data lookups to a SQL sub-agent, with read-only database access and optional human approval before queries run.

---

## 📸 Screenshots


| 

![Screenshot 1](Screenshot%202026-09-10%20121718.png)

 | 

![Screenshot 2](Screenshot%202026-09-10%20122048.png)

 | 

![Screenshot 3](Screenshot%202026-09-10%20122148.png)

 |

---

## ✨ What It Does

When a customer asks about an order's status, tracking number, delivery date or a product, the agent writes a SQL query, pulls live data from the database and replies in a natural, friendly tone. Greetings, return-policy questions and general FAQs are answered directly by the agent, and the database is only queried when real data is needed.

**Example queries**

- "Where is my order ORD-1042?"
- "What's the tracking number for my last order?"
- "What products do you sell?"
- "What's your return policy?"
- "Show me all delivered orders for Ali Khan"

---

## 🧩 Key Concepts

**Multi-agent architecture (supervisor pattern).** Instead of one agent doing everything, a *supervisor agent* talks to the customer and decides what is needed. When real data is required, it delegates to a specialised *sub-agent* that only handles order lookups. Separating roles keeps prompts focused and makes each agent easier to test and improve.

**Tool calling.** The LLM does not touch the database directly. It decides when to call a tool (`query_database_tool`), passes it a query, and uses the result to write the final reply. The model reasons, and the tool acts.

**Text-to-SQL.** The agent turns a natural-language question ("Where is order ORD-1042?") into a SQL query, runs it, and explains the result in plain language.

**Model Context Protocol (MCP).** The database is exposed through the MCP Toolbox for Databases, a standard way to give an agent access to external tools. Access is restricted to `SELECT`, so the agent can read order data but cannot change or delete it.

**Conversation memory.** LangGraph's `MemorySaver` checkpointer stores the conversation per `thread_id`, so the agent remembers context across messages within a session (for example, "what about my last order?").

**Human-in-the-loop.** Using the `interrupt_on` option, database queries can be paused for manual approval before they run. This is a safeguard for sensitive actions.

**API layer with validation.** A FastAPI `/chat` endpoint separates the UI from the agent logic. Pydantic validates every request (`text`, `thread_id`) and generates API docs automatically.

---

## 🏗️ Architecture

```
User (Streamlit UI)
        │
        ▼
   FastAPI  /chat  (validated by Pydantic ChatRequest)
        │
        ▼
  Supervisor Agent (LangGraph / DeepAgents)
        │
        ├── Greetings, FAQs, policies → answered directly
        │
        └── Order / tracking / product questions
                    │
                    ▼
          order_support_agent (sub-agent)
                    │
                    ▼
          query_database_tool
                    │
                    ▼
        MCP Toolbox for Databases  →  orders.db (SQLite)
```

---

## 🧠 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Agent orchestration | LangGraph (via DeepAgents) | Supervisor agent that routes the conversation, plus a specialised sub-agent for database lookups |
| LLM | Groq (`openai/gpt-oss-120b`) via LangChain | Reasoning, conversation and tool-calling decisions |
| Database access | MCP Toolbox for Databases | Exposes the SQLite `orders` database as a controlled tool, restricted to `SELECT` only |
| Backend API | FastAPI | Serves a `/chat` endpoint that receives messages and returns agent responses |
| Data validation | Pydantic | Validates the `/chat` request schema (`text`, `thread_id`) |
| Frontend | Streamlit | Custom animated chat UI with quick-action buttons and live session stats |
| Database | SQLite | Order records: order ID, customer, product, quantity, price, status, dates, tracking number |

---

## 📁 Project Structure

```
.
├── agent.py           # FastAPI app + LangGraph supervisor/sub-agent setup
├── tool.py            # query_database_tool, connects to the MCP Toolbox client
├── database.py        # Generates orders.db with sample order data
├── app.py             # Streamlit chat UI
├── orders.db          # Sample SQLite database (regenerate with database.py)
├── requirements.txt   # Python dependencies
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```
git clone https://github.com/HamzaWaseem2005/E-COMMERCE-AGENT-.git
cd E-COMMERCE-AGENT-
```

### 2. Create a virtual environment

```
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Generate the database

```
python database.py
```

### 6. MCP Toolbox

The agent connects to a SQLite database through the MCP Toolbox for Databases. The toolbox config file is not included in this repository.

### 7. Start the backend

```
uvicorn agent:app --reload --port 8000
```

### 8. Start the frontend (in a new terminal)

```
streamlit run app.py
```

---

## 🔒 Safety Notes

- The database tool is restricted to `SELECT` statements, so the agent cannot modify data.
- Optional human-in-the-loop approval (`interrupt_on`) lets you require manual approval before a database query runs.
- API keys are loaded from environment variables and are not stored in the code.

---

## ⚠️ Known Limitations

- **No authentication yet:** the agent can look up any customer's orders, so this is a demo and not ready for real customer data.
- Runs on a small sample database, not production data.
- Session memory is in-process (`MemorySaver`), so it resets when the backend restarts.
- No automated evaluation suite yet.

## 🚀 Future Improvements

- Add authentication so customers only see their own orders
- Build a test set of support queries and report accuracy
- Extend the sub-agent with refund and cancellation tools
- Stream responses token-by-token in the Streamlit UI
- Deploy backend, toolbox and frontend as containerised services

---

## 👤 Author

**Muhammad Hamza Waseem**
[GitHub](https://github.com/HamzaWaseem2005) · [LinkedIn](https://www.linkedin.com/in/muhammad-hamza-waseem-976535336)
