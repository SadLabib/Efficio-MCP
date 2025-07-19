import asyncio
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Choose your LLM. Using Google's Gemini model
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20"
)

server_params = StdioServerParameters(
    command="python",
    args=["calendar_server.py"],  # Path to your server script
)

async def run_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)
            print("🔔 Agent ready. Ask about your calendar (type 'exit' to quit).")
            while True:
                user_input = input("You: ")
                if user_input.lower() in ("exit", "quit"):
                    print("Goodbye!")
                    break
                response = await agent.ainvoke({"messages": user_input})
                print("Assistant:", response)

if __name__ == "__main__":
    asyncio.run(run_agent())