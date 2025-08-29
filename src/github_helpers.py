from urllib.parse import urlparse

def parse_github_pr_url(url: str) -> dict | None:
    """
    Parses a GitHub pull request URL to extract the owner, repo, and PR number.

    Args:
        url: The GitHub PR URL string.

    Returns:
        A dictionary with 'owner', 'repo', and 'pr_number', or None if the URL is invalid.
    """
    try:
        parsed_url = urlparse(url)
        # The path will look like '/lmchoi/alt-f-this/pull/2'
        path_parts = parsed_url.path.strip('/').split('/')

        # A valid PR URL path will have 4 parts: owner, repo, 'pull', number
        if len(path_parts) == 4 and path_parts[2] == 'pull':
            return {
                'owner': path_parts[0],
                'repo': path_parts[1],
                'pr_number': int(path_parts[3])
            }
    except (ValueError, IndexError):
        # Catches errors from malformed URLs or incorrect splitting
        return None
    
    return None

# --- Example Usage ---
pr_url = "https://github.com/lmchoi/alt-f-this/pull/2"
details = parse_github_pr_url(pr_url)

if details:
    print(f"Owner: {details['owner']}")
    print(f"Repo: {details['repo']}")
    print(f"PR Number: {details['pr_number']}")
else:
    print("Invalid GitHub PR URL.")