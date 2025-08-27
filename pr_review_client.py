import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

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

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        await client.connect_to_server("/home/bokchoi/Workspace/the-nitpicker/pr_review_server.py")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
