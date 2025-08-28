import json
import logging
from mcp.server.fastmcp import FastMCP
import subprocess

mcp = FastMCP("PrReviewServer")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# A logger for this specific module
logger = logging.getLogger(__name__)

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

@mcp.tool(
    description="Create a pending review for a pull request"
)
async def create_pending_review(pr_number: str, comments: list):
    """
    Post a review comment to a specific line in a GitHub PR.
    """
    # TODO update these
    owner = "lmchoi"
    repo = "the-nitpicker"
    
    logger.info(f"Comments: {comments}")

    payload = {
        "comments": comments
    }
    
    json_payload = json.dumps(payload)

    command = ["gh", "api", "--method", "POST"]
    command += ["-H", "Accept: application/vnd.github+json"]
    command += ["-H", "X-GitHub-Api-Version: 2022-11-28"]
    command += [f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews"]
    command += ["--input", "-"]

    try:
        result = subprocess.run(
            command,
            input=json_payload,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"gh API call failed. Status Code: {e.returncode}")
        logger.error(f"Command executed: {' '.join(command)}")
        logger.error(f"Stderr: {e.stderr}")
        logger.error(f"Output: {e.output}")
        
        raise ValueError(f"Failed to create a review: {e.stderr}")

@mcp.prompt(
    description="Generate a code review prompt given a PR number to provide file and line feedback"
)
def review_pr(pr_number: str) -> str:
    """Create a prompt to review PR changes with detailed, line-specific comments.
    
    Args:
        pr_number: Unified diff string from PR
        
    Returns:
        Formatted review prompt with embedded diff
    """
    diff = get_pr_diff(pr_number)
    prompt = f"""
    Please create a pending review for PR #{pr_number} and provide specific, actionable nitpicks.
    
    **IMPORTANT**: Aggregate all the issues found into a single list 
    and call the create_pending_review tool exactly once with a list of comments, 
    where each contains the following fields:
    - path: the file path (e.g., "src/main.py")
    - line: the line number where the issue occurs
    - body: your constructive feedback
    - side: the side of the diff where the change is located ("LEFT" for the original file, "RIGHT" for the new file)
    
    After posting all comments, you can provide a brief text summary.
    """
    return f"{prompt}```diff\n{diff}\n```"

def main():
    """Entry point for the direct execution server."""
    mcp.run()

if __name__ == "__main__":
    main()