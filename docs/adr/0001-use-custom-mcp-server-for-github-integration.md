# ADR 0001: Use a custom MCP server for GitHub integration

## Status
Accepted

## Context
The CLI tool requires integration with GitHub for pull request reviews. The core functionality depends on two specific operations:
1. Fetching the diff of a pull request
2. Adding comments to a pull request review

The official GitHub MCP server was evaluated against building a custom solution.

## Decision
A minimal, custom MCP server will be built specifically for the required GitHub integration, rather than using the official GitHub MCP server.

The custom server will expose exactly two tools:
- `get_pr_diff(pr_number: str) -> str`
- `create_pending_review(pr_number: str, comments: list) -> str`

## Consequences

### Positive
- **Focused functionality**: Only implements what is needed, reducing complexity
- **Simplified authentication**: PAT tokens can be used directly without complex app setup
- **Better user experience**: Server process managed automatically via stdio, simplifying user setup.
- **Easier maintenance**: Small codebase focused on the specific use case
- **Optimized prompts**: The LLM interacts with a minimal, curated toolset

### Negative
- **Initial development cost**: The server must be built and maintained
- **Limited extensibility**: Additional GitHub features would require implementation
- **No upstream updates**: Benefits from improvements to the official server are not realized

### Risks
- GitHub API changes may require server updates
- Responsibility for authentication security and token management

## Alternatives Considered

1. **Official GitHub MCP Server**
   - Pros: No build/maintenance required
   - Cons: Excessive for the required functionality, complex setup for users, large attack surface and dependency

2. **Monolithic CLI with direct API calls**
   - Pros: Simplest initial implementation
   - Cons: Tight coupling makes testing and maintenance harder, no separation of concerns, difficult to swap LLM providers

3. **Embedded library model**
   - Pros: Works offline
   - Cons: High resource usage bloats the CLI, does not solve the GitHub integration problem

## Implementation Notes / Future Improvements
- Use stdio transport for seamless integration with the CLI
- Implement proper error handling for GitHub API rate limits and errors
- Consider using the GitHub GraphQL API for efficient data fetching
- Store authentication tokens securely using the system keychain