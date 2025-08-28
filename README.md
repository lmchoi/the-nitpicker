# the-nitpicker: Adds comments to Pull Requests for you to approve

This is a command-line tool that uses a large language model (LLM) to help you review GitHub Pull Requests (PRs). By providing an AI-powered analysis of a Git diff, the tool offers suggested comments that you can use to streamline your code review process.

The tool is designed to provide you with suggestions as a starting point, keeping you in control of what gets added to the actual PR review.

## Prerequisites

You'll need the following installed and configured on your system:

- **uv**: https://docs.astral.sh/uv/
- **Git Hub CLI**: https://cli.github.com/

## Getting Started

First, install the dependencies with:

```bash
uv sync
```

Create a `.env` configuration file in you working directory containing your API key.

```
GOOGLE_API_KEY=<gemini api key>
```

