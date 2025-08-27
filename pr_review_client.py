import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from google import genai
from google.genai import types

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import ListToolsResult

import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py or .js)
        """

        command = "python"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        tools_response = await self.session.list_tools()
        tools = tools_response.tools

        prompts_response = await self.session.list_prompts()
        prompts = prompts_response.prompts

        print("Connected to server:")
        print("Tools:", [tool.name for tool in tools])
        print("Prompts:", [prompt.name for prompt in prompts])

    async def review_pr(self, pr_number: str):
        await self.session.initialize()
        
        prompt_response = await self.session.get_prompt(
            name="review_pr",
            arguments={
                "pr_number": pr_number
            }
        )

        print("Sending PR content to AI for analysis...")
        
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt_response.messages[0].content.text,
            config=types.GenerateContentConfig(
                temperature=0,
            ),
        )

        print("\n--- AI Suggested Comments ---")
        print(response.model_dump_json())
        print("\n-----------------------------")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    import sys
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <PR_NUMBER>")
        sys.exit(1)

    pr_number = sys.argv[1]
    client = MCPClient()
    try:
        await client.connect_to_server("/home/bokchoi/Workspace/the-nitpicker/pr_review_server.py")
        await client.review_pr(pr_number)
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
