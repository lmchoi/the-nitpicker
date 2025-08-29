import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from google import genai
from google.genai import types

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    async def connect_to_server(self):
        """Connect to an MCP server."""

        command = "np-server"
        server_params = StdioServerParameters(
            command=command,
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        tools_response = await self.session.list_tools()
        self.tools = tools_response.tools
        self.gemini_tools = self._convert_tools_to_gemini_format()

        prompts_response = await self.session.list_prompts()
        self.prompts = prompts_response.prompts

        print("Connected to server:")
        print("Tools:", [tool.name for tool in self.tools])
        print("Prompts:", [prompt.name for prompt in self.prompts])

    def _convert_tools_to_gemini_format(self):
        return [
            types.Tool(
                function_declarations=[
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            k: v
                            for k, v in tool.inputSchema.items()
                            if k not in ["additionalProperties", "$schema"]
                        },
                    }
                ]
            )
            for tool in self.tools
        ]

    async def review_pr(self, pr_number: str):
        prompt_response = await self.session.get_prompt(
            name="review_pr",
            arguments={
                "pr_number": pr_number
            }
        )

        print("Sending PR content to AI for analysis...")

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_response.messages[0].content.text,
            config=types.GenerateContentConfig(
                temperature=0,
                tools=self.gemini_tools
            ),
        )

        print("\n--- AI Suggested Comments ---")
        print(response.model_dump_json())
        print("\n-----------------------------")
        results = []
        for part in response.candidates[0].content.parts:
            if part.function_call:
                func_call = part.function_call
                tool_result = await self.session.call_tool(
                    func_call.name, 
                    func_call.args
                )
                results.append(tool_result)
                
        print("\n--- Action Taken ---")
        print(results)
        print("\n--------------------")

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
        await client.connect_to_server()
        await client.review_pr(pr_number)
    finally:
        await client.cleanup()

# Synchronous wrapper for the command-line entry point
def run_cli_tool():
    asyncio.run(main())

if __name__ == "__main__":
    run_cli_tool()

