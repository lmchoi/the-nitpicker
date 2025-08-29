# The Nitpicker: An AI-Powered Pull Request Review Assistant

This is a command-line tool that uses a large language model (LLM) to help you review GitHub Pull Requests (PRs). By providing an AI-powered analysis of a Git diff, the tool offers suggested comments that you can use to streamline your code review process.

The tool is designed to provide you with suggestions as a starting point, keeping you in control of what gets added to the actual PR review.

## Prerequisites

You'll need the following installed and configured on your system:

- **uv**: https://docs.astral.sh/uv/
- **GitHub CLI**: https://cli.github.com/

## Getting Started

Navigate to the project directory and install the application in editable mode:

```bash
uv pip install -e .
```

Create a `.env` configuration file in you working directory containing your API key.

```
GOOGLE_API_KEY=<gemini api key>
```

To nitpick a pull request:

```
nitpick --repo-path <path-to-your-repo> --pr-number <pr-number>
```

Example:

```Bash
nitpick --repo-path /Users/mickey/projects/my-git-repo --pr-number 123
```

