import asyncio
from typing import cast
import os
from openai import AsyncAzureOpenAI  # Using Azure OpenAI client
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

# Initialize Azure OpenAI client
client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Setup server parameters
server_params = StdioServerParameters(command="python", args=["./mcp_server.py"], env=None)

class Chat:
    def __init__(self):
        self.messages = []
        self.system_prompt = "You are a master SQLite assistant. Your job is to use the tools at your disposal to execute SQL queries and provide the results to the user."
        self.model = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")

    async def process_query(self, session: ClientSession, query: str) -> None:
        # Get available tools
        response = await session.list_tools()
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema
                }
            } for tool in response.tools
        ]
        
        # Add user message to conversation history
        self.messages.append({"role": "user", "content": query})
        
        # Get initial response
        res = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": self.system_prompt}] + self.messages,
            tools=available_tools,
            tool_choice="auto"
        )
        
        response_message = res.choices[0].message
        
        # Handle tool calls if any
        if response_message.tool_calls:
            # Save assistant's response with tool calls
            self.messages.append({
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": response_message.tool_calls
            })
            
            # Process each tool call
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = tool_call.function.arguments
                
                # Call the tool and get result
                result = await session.call_tool(function_name, cast(dict, eval(function_args)))
                result_content = getattr(result.content[0], "text", "")
                
                # Add tool result to messages
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_content
                })
            
            # Get final response after tool use
            final_res = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": self.system_prompt}] + self.messages
            )
            
            print(final_res.choices[0].message.content)
            self.messages.append({
                "role": "assistant",
                "content": final_res.choices[0].message.content
            })
        else:
            # Handle case with no tool calls
            print(response_message.content)
            self.messages.append({
                "role": "assistant",
                "content": response_message.content
            })

    async def chat_loop(self, session: ClientSession):
        while True:
            query = input("\nQuery: ").strip()
            await self.process_query(session, query)

    async def run(self):
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                await self.chat_loop(session)

if __name__ == "__main__":
    chat = Chat()
    asyncio.run(chat.run())