from mcp.server.fastmcp import FastMCP
import subprocess

mcp = FastMCP("PrReviewServer")

@mcp.tool(
    description="Get the unified diff for a GitHub pull request by PR number"
)
def get_pr_diff(pr_number: str) -> str:
    """Get the diff for a GitHub pull request.
    
    Args:
        pr_number: The pull request number as a string
        
    Returns:
        The diff output from GitHub CLI, or empty string if command fails
    """

    command = ["gh", "pr", "diff", pr_number]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")

@mcp.prompt(
    description="Generate a code review prompt for a pull request diff with specific file and line feedback"
)
def review_pr(diff: str) -> str:
    """Create a prompt to review PR changes with detailed, line-specific comments.
    
    Args:
        diff: Unified diff string from PR
        
    Returns:
        Formatted review prompt with embedded diff
    """
    prompt = "Review the PR and nitpick, for each comment/suggestion, include file and line number"
    return f"{prompt}```diff\n{diff}\n```"

def main():
    """Entry point for the direct execution server."""
    mcp.run()

if __name__ == "__main__":
    main()