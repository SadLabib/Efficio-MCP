import asyncio
from dotenv import load_dotenv
import re
from datetime import datetime, timedelta
from dateutil import parser
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

# def parse_date_time(text: str) -> str:
#     now = datetime.now()
#     # Patterns to match relative keywords and optional times
#     patterns = [
#         (r'\b(today)\b(?:\s+(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm)))?', lambda m: (
#             # “today” → this date at given time or midnight
#             datetime.combine(now.date(), datetime.min.time())
#             .replace(hour=int(datetime.strptime(m.group(2) or "00:00", "%H:%M").hour),
#                      minute=int(datetime.strptime(m.group(2) or "00:00", "%H:%M").minute))
#             .isoformat()[:19]  # drop microseconds
#         )),
#         (r'\b(tomorrow)\b(?:\s+(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm)))?', lambda m: (
#             datetime.combine(now.date()+timedelta(days=1), datetime.min.time())
#             # similar time parsing as above
#             .isoformat()[:19]
#         )),
#         # ... similarly for “yesterday” ...
#         (r'next (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)(?:\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)))?',
#          lambda m: (
#             # compute days ahead to next given weekday
#             (datetime.combine(now.date()+timedelta(
#                 days=((
#                     {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6} 
#                     [m.group(1).lower()] - now.weekday()) % 7 or 7)
#             ), datetime.min.time()))
#             .isoformat()[:19]
#          )),
#         (r'next week(?:\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)))?',
#          lambda m: (
#             (datetime.combine(now.date()+timedelta(days=7), datetime.min.time()))
#             .isoformat()[:19]
#          )),
#         (r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:,\s*(\d{4}))?(?:\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)))?',
#         lambda m: (
#             # Combine date and optional time
#             parser.parse(
#                 f"{m.group(1)} {m.group(2)} {m.group(3) or datetime.now().year} {m.group(4) or '00:00'}"
#             ).isoformat()
#         )),
#     ]
#     for pattern, repl in patterns:
#         text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
#     return text

async def run_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            print("Loaded tools:", [t.name for t in tools])
            # Add system prompt here
            agent = create_react_agent(
                model,
                tools,
                prompt = (
                    "You are a smart calendar assistant. When the user mentions a date or time, always extract and convert it to full ISO 8601 format "
                    "(YYYY-MM-DDTHH:MM:SS±HH:MM) as required by the Google Calendar API. If a timezone is mentioned (e.g., PST, EST, IST, UTC+6), "
                    "correctly interpret it and apply it to the final output. If no timezone is provided, assume GMT+6. "
                    "If the time or timezone is ambiguous or missing, ask the user to clarify explicitly. "
                    "Always prefer precision to avoid scheduling errors."
                )

            )
            print("Agent ready. Ask about your calendar (type 'exit' to quit').")

            context = []
            while True:
                user_input = input("You: ")
                if user_input.lower() in ("exit", "quit"):
                    print("Goodbye!")
                    break
                context.append({"role": "user", "content": user_input})
                if len(context) > 10:
                    context.pop(0)
                result = await agent.ainvoke({"messages": context})
                print("Agent result:", result)

                assistant_reply = result["messages"][-1].content
                print("Assistant:", assistant_reply)
                context.append({"role": "assistant", "content": assistant_reply})
                if len(context) > 10:
                    context.pop(0)

if __name__ == "__main__":
    asyncio.run(run_agent())